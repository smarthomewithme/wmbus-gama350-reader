"""v4.19: one isolated earlier RX FIFO IRQ, parent v4.17 not failed v4.18."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
PATCH=ROOT/"patches/0016-v4_19-early-fifo8-irq.patch"
class TestV419(unittest.TestCase):
    def test_patch_scope_and_register(self):
        s=PATCH.read_text(encoding="utf-8")
        paths=[line.removeprefix("diff --git a/").split(" b/")[0] for line in s.splitlines() if line.startswith("diff --git a/")]
        self.assertEqual(paths,["components/wmbus_radio/transceiver_cc1101.cpp","components/wmbus_radio/component.cpp"])
        self.assertIn("-  this->write_register(CC1101_FIFOTHR, 0x03);",s)
        self.assertIn("+  this->write_register(CC1101_FIFOTHR, 0x01);",s)
        self.assertIn("SHWM v4.19 FIFO8 ACTIVE",s)
        self.assertIn("SHWM wMBus v4.19 ACTIVE",s)
        additions="\n".join(line for line in s.splitlines() if line.startswith("+") and not line.startswith("+++"))
        for forbidden in ("CC1101_MDMCFG4","CC1101_FREQ","rx_v417_no_progress_backoff_us(",
                          "delayMicroseconds(","read_status_register(","read_burst(","restart_rx(",
                          "decode3of6","wakeup_receiver_task_from_isr"):
            self.assertNotIn(forbidden,additions)
    def test_chain_and_ci(self):
        boot=(ROOT/"components/_bootstrap_v4.py").read_text(encoding="utf-8")
        sh=(ROOT/"scripts/prepare_cc1101_v4.sh").read_text(encoding="utf-8")
        for s in (boot,sh):
            self.assertLess(s.index("0015-v4_17-midpoint-long-idle-poll.patch"),s.index(PATCH.name))
            self.assertNotIn("0016-v4_18-long-no-progress-150us.patch",s)
            self.assertIn("SHWM wMBus v4.19 ACTIVE",s)
        self.assertIn('shwm-wmbus-v4.19-fifo8-irq-v1',boot)
        for name in ('official-v4.yml','direct-esphome-install.yml'):
            workflow=(ROOT/'.github/workflows'/name).read_text(encoding="utf-8")
            self.assertIn('experiment/v4.19-early-fifo8-irq',workflow)
            self.assertIn('CC1101_FIFOTHR, 0x01',workflow)
            self.assertIn('rx_v417_no_progress_backoff_us(offset, length)',workflow)
if __name__=='__main__':
    unittest.main()
