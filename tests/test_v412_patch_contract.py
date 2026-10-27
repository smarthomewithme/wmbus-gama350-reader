"""v4.12 contract: shorten status SPI hot path, single RX recovery, keep RF."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches" / "0011-v4_12-overflow-fastpath.patch"


class TestV412Recovery(unittest.TestCase):
    def test_patch_scope_and_recovery(self):
        p = PATCH.read_text(encoding="utf-8")
        paths = [s.removeprefix("diff --git a/").split(" b/")[0]
                 for s in p.splitlines() if s.startswith("diff --git a/")]
        self.assertEqual(paths, [
            "components/wmbus_radio/cc1101_fifo.h",
            "components/wmbus_radio/component.cpp",
            "components/wmbus_radio/transceiver_cc1101.cpp",
        ])
        self.assertIn("rx_should_probe_marcstate(made_progress, total, length)", p)
        self.assertIn("SHWM wMBus v4.12 ACTIVE", p)
        self.assertIn("SHWM v4.12 RX_DIAG_1M", p)
        self.assertIn("SHWM v4.12 RX FIFO overflow:", p)
        self.assertIn("SHWM v4.12 RX FIFO overflow final:", p)
        self.assertIn("-      this->restart_rx();", p)
        self.assertIn("-          this->restart_rx();", p)
        self.assertNotIn("+      this->restart_rx();", p)
        for forbidden in ("CC1101_MDMCFG4", "CC1101_FIFOTHR", "CC1101_FREQ",
                          "this->write_register(", "wakeup_receiver_task_from_isr(",
                          "attach_data_interrupt(", "this->strobe("):
            self.assertNotIn(forbidden, p)

    def test_patch_order_cache_and_ci(self):
        boot = (ROOT / "components/_bootstrap_v4.py").read_text()
        sh = (ROOT / "scripts/prepare_cc1101_v4.sh").read_text()
        for source in (boot, sh):
            self.assertLess(source.index("0010-v4_11-rxbytes65-prefetch.patch"),
                            source.index(PATCH.name))
        self.assertIn("shwm-wmbus-v4.12-overflow-fastpath-v1", boot)
        self.assertIn("SHWM v4.12 RX FIFO overflow", boot)
        self.assertIn("SHWM v4.12 RX_DIAG_1M", sh)
        for workflow in ("official-v4.yml", "direct-esphome-install.yml"):
            self.assertIn("experiment/v4.12-overflow-fastpath",
                          (ROOT / ".github/workflows" / workflow).read_text())
        self.assertTrue((ROOT / "tests/v412_receive_policy.cpp").exists())


if __name__ == "__main__":
    unittest.main()
