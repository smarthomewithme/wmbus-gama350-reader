"""Provenance of three experimental ESPHome builds. Never flashes, publishes or reads user secrets."""
from __future__ import annotations
import base64
import difflib
import hashlib
import re
import subprocess
import sys
from pathlib import Path

REPO = "https://github.com/smarthomewithme/wmbus-gama350-reader.git"
VERSIONS = (
    ("control", "experiment/v4.9-stable-marcstate-eof", "11b09de7f87ade632453f772c37940dbdb470c94"),
    ("diagnostics", "experiment/v4.25a-v49-diagnostics-only", "7b8c5e948f0c3029372bc999d5b823def7edfd63"),
    ("combined", "experiment/v4.25-v49-targeted-backports", "1eae2327ce176592513ede8212bf9eb8b1cec971"),
)
PARTS = ("wmbus_radio", "wmbus_common", "wmbus_meter", "socket_transmitter")
EXT = {".c", ".cpp", ".h", ".hpp", ".cc"}
FAKE = {
    "wifi_ssid": "SHWM-FORENSIC-NO-RADIO",
    "wifi_password": "CI-not-an-actual-password",
    "api_encryption_key": base64.b64encode(bytes([42]) * 32).decode(),
    "ota_password": "NO-DEVICE-ACCESS-CI",
    "gama350_meter_id": "0x12345678",
    "apator_meter_id": "0x87654321",
    "gama350_aes_key": "0123456789abcdef0123456789abcdef",
    "apator_aes_key": "abcdef0123456789abcdef0123456789",
}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def require_ref(branch, commit):
    p = subprocess.run(
        ["git", "ls-remote", REPO, "refs/heads/" + branch],
        capture_output=True, check=True, text=True, timeout=30,
    )
    matches = p.stdout.strip().splitlines()
    assert len(matches) == 1 and matches[0].split()[0] == commit, (
        "A source branch moved since exact physically-tested commit", branch, matches
    )

def prepare(roots):
    assert [str(x) for x in roots] == [v[0] for v in VERSIONS], "Only fixed pinned build paths"
    for name, branch, commit in VERSIONS:
        root = Path(name)
        current = subprocess.check_output(["git", "-C", name, "rev-parse", "HEAD"], text=True).strip()
        assert current == commit, (name, current)
        require_ref(branch, commit)
        config = root / "config"
        raw = (config / "wmbus-gama350.yaml").read_text()
        old = "  - source:\n      type: local\n      path: ../vendor/upstream/components"
        assert raw.count(old) == 1
        source = "  - source: github://smarthomewithme/wmbus-gama350-reader@" + branch + "\n    refresh: always"
        (config / "wmbus-gama350-forensics.yaml").write_text(raw.replace(old, source))
        (config / "secrets.yaml").write_text("".join(f'{key}: "{value}"\n' for key,value in FAKE.items()))
    assert len({(Path(n)/"config"/"secrets.yaml").read_bytes() for n,_,_ in VERSIONS}) == 1
    print("3 source refs pinned at tested SHAs, same synthetic YAML secrets, no hardware access")

def sources(root):
    cache = root/"config"/".esphome"/"external_components"
    match = list(cache.rglob("components/wmbus_radio/transceiver_cc1101.cpp"))
    assert len(match) == 1, (root, "CC1101 source ambiguity", match)
    component_root = match[0].parent.parent
    items = {}
    for part in PARTS:
        assert (component_root/part).is_dir()
        for item in (component_root/part).rglob("*"):
            if item.is_file() and item.suffix in EXT:
                items[item.relative_to(component_root).as_posix()] = item
    return items

def elf_path(root):
    found = list((root/"config"/".esphome"/"build").rglob("firmware.elf"))
    assert len(found)==1, (root, found)
    return found[0]

def sizes_and_layout(elf):
    # pyelftools is installed by ESPHome, and can read Xtensa DWARF generically.
    from elftools.elf.elffile import ELFFile
    with elf.open("rb") as fh:
        e = ELFFile(fh)
        interesting = (".bss", ".data", ".rodata", ".text", ".iram0.text", ".dram0.data", ".dram0.bss")
        sections = {s.name: s["sh_size"] for s in e.iter_sections() if s.name in interesting}
        layouts = []
        if e.has_dwarf_info():
            di = e.get_dwarf_info()
            for cu in di.iter_CUs():
                for die in cu.iter_DIEs():
                    if die.tag not in ("DW_TAG_class_type", "DW_TAG_structure_type"):
                        continue
                    attr = die.attributes.get("DW_AT_name")
                    sz = die.attributes.get("DW_AT_byte_size")
                    if not attr or attr.value not in (b"Radio", b"CC1101") or not sz:
                        continue
                    members = []
                    for child in die.iter_children():
                        if child.tag == "DW_TAG_member" and child.attributes.get("DW_AT_name"):
                            label = child.attributes["DW_AT_name"].value.decode(errors="replace")
                            if label in ("radio", "receiver_task_handle_", "packet_queue_", "frame_converted_", "frame_conversion_failed_", "last_diag_window_",
                                         "irq_notifications_", "last_diag_log_ms_"):
                                offset = child.attributes.get("DW_AT_data_member_location")
                                members.append((label,offset.value if offset else "?"))
                    if "receiver_task_handle_" in dict(members) or "frame_converted_" in dict(members):
                        layouts.append({"name":attr.value.decode(), "bytes":sz.value, "members":members})
        return sections, layouts

def symbols(elf):
    # Do not assume the toolchain name, ESPHome ESP-IDF installs a toolchain in PlatformIO packages.
    tools = list(Path.home().glob(".platformio/packages/**/bin/*-nm"))
    targets = [p for p in tools if "xtensa" in p.name]
    if not targets:
        return ["Cross-nm unavailable on runner; source/ELF/DWARF checks still valid"]
    cmd = [str(sorted(targets)[0]), "-C", "-S", "--defined-only", str(elf)]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=45, check=True).stdout
    words = ("Radio::receive_frame(", "Radio::wakeup_receiver_task_from_isr(",
             "Radio::loop(", "CC1101::read_in_task(", "CC1101::restart_rx(", "Radio::receiver_task(")
    return [line.strip()[:260] for line in out.splitlines() if any(w in line for w in words)][:30]

def compare(roots, outfile):
    controls = {name:sources(Path(name)) for name,_,_ in VERSIONS}
    base = controls["control"]
    expected = {"wmbus_radio/component.cpp", "wmbus_radio/component.h", "wmbus_radio/rx_diag_window.h"}
    lines = [
        "# v4.9 ↔ v4.25a ↔ v4.25 firmware forensics — CI ONLY, no device access",
        "Toolchain ESPHome 2026.10.1; three exact physically-tested commits; fake identical secrets.",
        "Hardware v4.9: 11/11 GAMA and 43 Apator over ~8min on 2026.10.1, zero FIFO overflow.",
        "Hardware v4.25a: 9 RXBYTES=65 and 6 FIFO overflow in under 2min, zero meters.",
        "Hardware v4.25: 5 RXBYTES=65 and 2 FIFO overflow in ~1min, zero meters.",
        "Hypotheses are not causal proof: build layout, Radio object size, task scheduling.",
    ]
    for name,branch,commit in VERSIONS[1:]:
        current = controls[name]
        changed = sorted(f for f in set(base)|set(current) if
                         f not in base or f not in current or digest(base[f])!=digest(current[f]))
        lines += ["",f"## {name} versus known-good control",f"ref: {branch} @ {commit}",f"changed_compiled_sources={changed}"]
        assert set(changed) == expected, (name,"unexpected scope of C++ changes",changed)
        for checked in ("wmbus_radio/transceiver_cc1101.cpp", "wmbus_radio/cc1101_fifo.h"):
            assert digest(base[checked]) == digest(current[checked]), (name,checked)
        lines.append("CC1101 FIFO DRIVER AND HELPER: byte-identical to v4.9 — verified")
        for filename in ("wmbus_radio/component.cpp","wmbus_radio/component.h"):
            delta = list(difflib.unified_diff(
                base[filename].read_text().splitlines(),
                current[filename].read_text().splitlines(),
                fromfile="v4.9/"+filename,tofile=name+"/"+filename,lineterm=""))
            lines += [f"### {filename} unified source delta",*delta[:150]]
        new_hdr = current["wmbus_radio/rx_diag_window.h"]
        lines.append(f"rx_diag_window.h new bytes={new_hdr.stat().st_size} sha256={digest(new_hdr)}")
    for name,branch,commit in VERSIONS:
        elf = elf_path(Path(name))
        secs,layouts = sizes_and_layout(elf)
        lines += ["",f"## {name} ELF results",f"ELF bytes={elf.stat().st_size} SHA256={digest(elf)}"]
        lines.extend(f"{k}: {v} bytes" for k,v in sorted(secs.items()))
        lines.append("Radio/CC1101 DWARF class candidates: "+repr(layouts[:12]))
        lines += ["Radio + CC1101 task/function symbol sizes (nm):",*symbols(elf)]
    lines += ["",
              "NOTE: file paths, build times, relocations and DWARF affect ELF hashes. " 
              "A changed function size, class size or symbol address is not evidence of a specific runtime race.",
              "NO firmware, binaries, raw secrets, or source files are uploaded; report text only.",
             ]
    outfile.write_text("\n".join(lines)+"\n")
    print(f"Forensic report ready: {len(lines)} lines, {outfile.stat().st_size} bytes")
    print("\n".join(lines[:13]))
    print("\n".join(x for x in lines if "DWARF class candidates:" in x or "changed_compiled_sources=" in x))

if __name__=="__main__":
    if len(sys.argv) < 2: raise SystemExit("usage: prepare|compare control diagnostics combined [output]")
    cmd=sys.argv[1]
    if cmd == "prepare" and len(sys.argv)==5: prepare(sys.argv[2:])
    elif cmd == "compare" and len(sys.argv)==6:
        names = sys.argv[2:5]
        assert names == [x[0] for x in VERSIONS]
        compare([Path(x) for x in names],Path(sys.argv[5]))
    else: raise SystemExit("invalid mode/arguments; no writes made")
