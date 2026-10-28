#!/usr/bin/env python3
"""One-time opt-in cleanup via trusted GitHub Actions: exact refs and SHAs only."""
from __future__ import annotations
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REPO="smarthomewithme/wmbus-gama350-reader"
BRANCH="diagnostics/v4.27-v49-passive-observer"
ARCHIVE=Path(__file__).resolve().parents[1]/"docs"/"LEGACY_REF_ARCHIVE_20261028.json"

def request(url, method="GET"):
    token=os.environ.get("GH_TOKEN")
    if not token: raise RuntimeError("GH_TOKEN missing (requires contents: write)")
    r=urllib.request.Request(url,method=method,headers={
        "Accept":"application/vnd.github+json",
        "Authorization":f"Bearer {token}",
        "X-GitHub-Api-Version":"2022-11-28",
        "User-Agent":"SHWM-exact-ref-archive-20261028"})
    try:
        with urllib.request.urlopen(r,timeout=35) as f:
            raw=f.read()
            return json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        if e.code==404: return None
        raise RuntimeError(f"GitHub HTTP {e.code} at {method} {url} (no token disclosed)") from None

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--execute",action="store_true",help="Actually delete exact archived legacy refs.")
    args=parser.parse_args()
    manifest=json.loads(ARCHIVE.read_text(encoding="utf-8"))
    assert manifest["repository"]==REPO
    keep=manifest["preserve"]
    targets=manifest["delete_exact_refs"]
    assert len(targets)==34 and len(set(r["name"] for r in targets))==34
    assert set(keep)=={"main","experiment/v4.9-stable-marcstate-eof",BRANCH}
    assert keep["experiment/v4.9-stable-marcstate-eof"]=="11b09de7f87ade632453f772c37940dbdb470c94"
    assert not set(keep).intersection(x["name"] for x in targets)
    assert all(len(x["sha"])==40 for x in targets)
    assert os.environ.get("GITHUB_REPOSITORY")==REPO, "Unexpected repository"
    assert os.environ.get("GITHUB_REF")==f"refs/heads/{BRANCH}", "Wrong branch"
    assert os.environ.get("GITHUB_EVENT_NAME")=="push", "Ref prune requires push event"
    api=f"https://api.github.com/repos/{REPO}"
    observed=request(api+"/branches?per_page=100")
    assert isinstance(observed,list) and len(observed)<100, "Pagination unknown: STOP"
    observed_by_name={x["name"]:x for x in observed}
    assert set(observed_by_name)==set(keep)|set(x["name"] for x in targets), (
        "Branch inventory differs from signed archive: STOP", sorted(observed_by_name))
    for name,sha in keep.items():
        actual=observed_by_name[name]["commit"]["sha"]
        if name==BRANCH:
            assert actual==os.environ.get("GITHUB_SHA"),"Observer branch HEAD moved: STOP"
        else:
            assert actual==sha,("Preserved branch moved: STOP",name,actual)
    for x in targets:
        if observed_by_name[x["name"]]["protected"]:
            raise RuntimeError(f"Protected branch in delete list: {x['name']}")
        if observed_by_name[x["name"]]["commit"]["sha"]!=x["sha"]:
            raise RuntimeError(f"Branch {x['name']} moved after inventory: STOP")
    prs=request(api+"/pulls?state=open&per_page=100")
    assert isinstance(prs,list) and len(prs)<100
    target_names={x["name"] for x in targets}
    blocked=[(x["number"],x["head"]["ref"]) for x in prs if x["head"]["ref"] in target_names]
    assert not blocked,("Legacy PRs still open: STOP",blocked)
    print(f"PRECHECK PASS: {len(targets)} exact legacy refs, 3 protected-by-script refs, no open old PRs.")
    if not args.execute:
        for x in targets: print("WOULD_DELETE",x["name"],x["sha"])
        print("DRY RUN ONLY. No deletion.")
        return
    deleted=[]
    for x in targets:
        ref=urllib.parse.quote("heads/"+x["name"],safe="/")
        request(api+"/git/refs/"+ref,method="DELETE")
        deleted.append(x["name"])
        print("DELETED",x["name"],flush=True)
    remaining=request(api+"/branches?per_page=100")
    assert isinstance(remaining,list)
    expected=set(keep)
    actual={x["name"] for x in remaining}
    assert actual==expected,("Post-cleanup branch set mismatch",actual,expected)
    print(f"SUCCESS: removed {len(deleted)} old branch refs; preserved {sorted(expected)}")
if __name__=="__main__":
    try: main()
    except Exception as e:
        print("PRUNE FAILED/CANCELLED:",str(e),file=sys.stderr)
        sys.exit(1)
