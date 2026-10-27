"""V4.8 is a fail-closed RXBYTES error-path patch on top of v4.5."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches" / "0008-v4_8-bounded-invalid-rxbytes-recheck.patch"
content = PATCH.read_text(encoding="utf-8")
sections = content.split("diff --git ")[1:]
paths = [s.split("\n", 1)[0].split(" b/")[1] for s in sections]
assert paths == [
    "components/wmbus_radio/transceiver_cc1101.cpp",
    "components/wmbus_radio/cc1101_fifo.h",
], paths

driver = sections[0]
added_driver = "\n".join(line[1:] for line in driver.splitlines()
                         if line.startswith("+") and not line.startswith("+++"))
assert driver.count('if (available > 64) {') == 1
assert driver.count('ESP_LOGW(TAG, "Invalid RX FIFO count: %u"') == 2
assert "retry_invalid_fifo_count(" in added_driver
assert "RXBYTES transient count recovered" in added_driver
assert "delayMicroseconds(60)" in added_driver
assert "return false" in added_driver
assert "restart_rx()" in added_driver  # comment, not a new call
assert "this->radio->restart_rx();" not in added_driver
for forbidden in ("void Radio::", "void CC1101::setup", "CC1101_FIFOTHR",
                  "CC1101_MDMCFG4", "attach_data_interrupt", "read_burst(",
                  "wakeup_receiver_task_from_isr", "vTaskNotifyGiveFromISR",
                  "portYIELD_FROM_ISR", "std::atomic"):
    assert forbidden not in added_driver, forbidden

added_fifo = "\n".join(line[1:] for line in sections[1].splitlines()
                       if line.startswith("+") and not line.startswith("+++"))
assert "inline bool retry_invalid_fifo_count" in added_fifo
assert "attempt < 3" in added_fifo
assert "raw = candidate;" in added_fifo
assert "(candidate & 0x80u) == 0u" in added_fifo
assert "(candidate & 0x7Fu) <= 64u" in added_fifo
assert "read_status_register" not in added_fifo  # injected stable reader only

bootstrap = (ROOT / "components" / "_bootstrap_v4.py").read_text(encoding="utf-8")
assert "shwm-wmbus-v4.8-bounded-rxbytes-recheck-v1" in bootstrap
assert bootstrap.count("0008-v4_8-bounded-invalid-rxbytes-recheck.patch") == 1
assert "0007-v4_5-initialize-isr-woken.patch" in bootstrap
assert "RXBYTES transient count recovered" in bootstrap
assert "inline bool retry_invalid_fifo_count" in bootstrap
assert "v4.7 loop_only" not in bootstrap
print("V48_RXBYTES_ERROR_PATH_CONTRACT_PASS")
