"""v4.22: failure-only CC1101 snapshots; verify v4.17 successful hot path unchanged."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"patches/0016-v4_22-cc1101-failure-only-snapshots.patch"
class V422DiagnosticScope(unittest.TestCase):
    def test_only_radio_readback_and_error_instrumentation(self):
        s=P.read_text(encoding="utf-8")
        paths=[line.removeprefix("diff --git a/").split(" b/")[0]
               for line in s.splitlines() if line.startswith("diff --git a/")]
        self.assertEqual(paths,["components/wmbus_radio/transceiver_cc1101.cpp","components/wmbus_radio/component.cpp"])
        self.assertIn("SHWM v4.22 RX_ERR",s)
        self.assertIn("SHWM v4.22 BOOT_CONFIG",s)
        self.assertIn("if (rxbytes_raw & 0x80) {",s)
        self.assertIn("this->irq_pin_->digital_read()",s)
        self.assertIn("CC1101_MARCSTATE",s)
        self.assertIn("CC1101_PKTSTATUS",s)
        self.assertIn("CC1101_FIFOTHR",s)
        self.assertIn("CC1101_IOCFG0",s)
        add="\n".join(x for x in s.splitlines() if x.startswith("+") and not x.startswith("+++"))
        for forbidden in ("write_register(","this->strobe(","restart_rx(","delayMicroseconds(",
                          "CC1101_FREQ2","CC1101_SRX","CC1101_SIDLE",
                          "ulTaskNotifyTake(","read_burst(","rx_should_backoff_after_drain(",
                          "rx_v417_no_progress_backoff_us("):
            self.assertNotIn(forbidden,add)
        self.assertEqual(s.count("diff --git a/"),2)
    def test_known_good_sources_pinned(self):
        b=(ROOT/"components/_bootstrap_v4.py").read_text()
        self.assertIn("shwm-wmbus-v4.22-failure-only-snapshots-v1",b)
        self.assertIn("0015-v4_17-midpoint-long-idle-poll.patch",b)
        self.assertIn(P.name,b)
        self.assertLess(b.index("0015-v4_17-midpoint-long-idle-poll.patch"),b.index(P.name))
        self.assertNotIn("0016-v4_18",b)
        self.assertNotIn("0016-v4_19",b)
        self.assertNotIn("0016-v4_20",b)
        for workflow in ("official-v4.yml","direct-esphome-install.yml"):
            t=(ROOT/".github/workflows"/workflow).read_text()
            self.assertIn("experiment/v4.22-error-snapshots",t)
if __name__=="__main__":
    unittest.main()
