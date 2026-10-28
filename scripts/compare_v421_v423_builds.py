"""Read-only firmware provenance: compare two CI-only ESPHome builds."""
from pathlib import Path
import difflib, hashlib, sys
PARTS=("wmbus_radio","wmbus_common","wmbus_meter","socket_transmitter")
SUFFIX={".cpp",".c",".cc",".h",".hpp"}
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def prepared(base):
    p=base/"config"/".esphome"/"external_components"
    matches=list(p.rglob("components/wmbus_radio/transceiver_cc1101.cpp"))
    assert len(matches)==1, ("Unexpected number of CC1101 drivers",matches)
    root=matches[0].parent.parent
    sources={}
    for part in PARTS:
        assert (root/part).is_dir(),part
        for f in (root/part).rglob("*"):
            if f.is_file() and f.suffix in SUFFIX:
                sources[f.relative_to(root).as_posix()]=f
    return sources
def artifact(root,name):
    return list((root/"config"/".esphome"/"build").rglob(name))
def main():
    a,b,out=(Path(x) for x in sys.argv[1:])
    af,bf=prepared(a),prepared(b)
    changed=[x for x in sorted(set(af)|set(bf)) if x not in af or x not in bf or digest(af[x])!=digest(bf[x])]
    lines=["SHWM CI ONLY: paired ESPHome 2026.10.1 builds / fake matching secrets",
           "v4.21=a11d6f8f8efe882351796a981cbeedb73f12071a",
           "v4.23=1bc91749cb9235ed4c564bbbe162479c26cb3666",
           "prepared_sources: control=%d candidate=%d"%(len(af),len(bf)),
           "changed_compiled_source_files: "+repr(changed)]
    assert changed==["wmbus_radio/component.cpp"],"Unexpected changes; stop before interpreting"
    d=list(difflib.unified_diff(af[changed[0]].read_text().splitlines(),bf[changed[0]].read_text().splitlines(),
          fromfile="v4.21/wmbus_radio/component.cpp",tofile="v4.23/wmbus_radio/component.cpp",lineterm=""))
    diff="\n".join(d)
    assert "shwm_last_irq_us" in diff and "SHWM v4.23 IRQ_LATENCY" in diff
    assert "CC1101_FIFOTHR" not in diff
    lines.extend(["","Exact compiled C++ source diff:",*d[:220]])
    for label,root in [("v4.21",a),("v4.23",b)]:
        for filename in ("firmware.elf","firmware.bin","firmware.map","platformio.ini","sdkconfig"):
            found=artifact(root,filename)
            lines.append(f"{label} {filename}: "+(
                f"size={found[0].stat().st_size} sha256={digest(found[0])}" if len(found)==1
                else f"matches={len(found)} (not necessarily produced)"))
            if filename=="firmware.elf":
                assert len(found)==1, f"Expected one compiled ELF for {label}"
    lines.append("Binary hash/size differences alone cannot prove a radio defect or its timing.")
    out.write_text("\n".join(lines)+"\n",encoding="utf8")
    print("\n".join(lines[-12:]))
if __name__=="__main__":
    main()
