"""Fail closed if the v4.7 patch changes the critical CC1101 receive path."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches" / "0008-v4_7-loop-only-gap-observer.patch"
content = PATCH.read_text(encoding="utf-8")
sections = content.split("diff --git ")[1:]
paths = [s.split("\n", 1)[0].split(" b/")[1] for s in sections]
assert paths == [
    "components/wmbus_radio/component.cpp",
    "components/wmbus_radio/component.h",
    "components/wmbus_radio/loop_gap_observer.h",
], paths

cpp = sections[0]
added_cpp = "\n".join(line[1:] for line in cpp.splitlines()
                      if line.startswith("+") and not line.startswith("+++"))
for forbidden in (
    "void Radio::receive_frame", "void Radio::receiver_task",
    "wakeup_receiver_task_from_isr", "read_in_task", "restart_rx",
    "ulTaskNotifyTake", "vTaskNotifyGiveFromISR", "portYIELD_FROM_ISR",
    "read_status_register", "write_register", "fetch_add",
    "xQueueReceive", "xQueueSend", "attach_data_interrupt",
):
    assert forbidden not in added_cpp, forbidden
for critical in ("void Radio::receive_frame", "void Radio::receiver_task", "wakeup_receiver_task_from_isr"):
    assert critical not in cpp, critical
assert "void Radio::loop()" not in added_cpp  # existing loop is extended, not replaced
assert "RX_DIAG v4.7 loop_only" in added_cpp
assert "loop_gap_last_poll_ms_" in added_cpp
assert "long_radio_frames_.load" in added_cpp
assert "payloads_ok_.load" in added_cpp
assert ">= 1000u" in added_cpp
added_hdr = "\n".join(line[1:] for line in sections[1].splitlines()
                      if line.startswith("+") and not line.startswith("+++"))
assert "std::atomic" not in added_hdr, "new observer state must remain loop-only"
assert "estimate_missing_30s_periods" in sections[2]
assert "CC1101_" not in added_cpp, "no new hardware reads"
assert "RX_DIAG v4.6" not in content, "v4.7 must branch from v4.5"
bootstrap = (ROOT / "components" / "_bootstrap_v4.py").read_text(encoding="utf-8")
assert "0008-v4_7-loop-only-gap-observer.patch" in bootstrap
assert "shwm-wmbus-v4.7-loop-gap-observer-v1" in bootstrap
print("V47_LOOP_ONLY_PATCH_CONTRACT_PASS")
