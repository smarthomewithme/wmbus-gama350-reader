"""v4.17: 100us midpoint schedule change based directly on v4.16."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
PATCH=ROOT/"patches/0015-v4_17-midpoint-long-idle-poll.patch"
class TestV417Scope(unittest.TestCase):
    def test_patch_scope_and_scheduling(self):
        s=PATCH.read_text()
        paths=[x.removeprefix("diff --git a/").split(" b/")[0] for x in s.splitlines() if x.startswith("diff --git a/")]
        self.assertEqual(paths,["components/wmbus_radio/cc1101_fifo.h","components/wmbus_radio/transceiver_cc1101.cpp","components/wmbus_radio/component.cpp"])
        self.assertIn("return offset == 3u && length >= 250u ? 100u",s)
        self.assertIn("+      delayMicroseconds(rx_v417_no_progress_backoff_us(offset, length));",s)
        self.assertIn("-      delayMicroseconds(rx_no_progress_backoff_us(offset, length));",s)
        self.assertIn("SHWM wMBus v4.17 ACTIVE",s)
        additions="\n".join(x for x in s.splitlines() if x.startswith("+") and not x.startswith("+++"))
        for forbidden in ("CC1101_MDMCFG4","CC1101_FIFOTHR","CC1101_FREQ","read_burst(",
                          "read_status_register(","restart_rx(","wakeup_receiver_task_from_isr(",
                          "decode3of6","delayMicroseconds(100);","rx_should_backoff_after_unstable("):
            self.assertNotIn(forbidden,additions)
    def test_chain_and_ci(self):
        boot=(ROOT/"components/_bootstrap_v4.py").read_text()
        shell=(ROOT/"scripts/prepare_cc1101_v4.sh").read_text()
        for x in [boot,shell]:
            self.assertLess(x.index("0014-v4_16-long-no-progress-short-poll.patch"),x.index(PATCH.name))
            self.assertNotIn("0014-v4_15",x)
            self.assertIn("SHWM wMBus v4.17 ACTIVE",x)
        self.assertIn("shwm-wmbus-v4.19-fifo8-irq-v1",boot)
        self.assertTrue((ROOT/"tests/v417_midpoint_poll.cpp").exists())
        for p in (ROOT/".github/workflows/official-v4.yml",ROOT/".github/workflows/direct-esphome-install.yml"):
            t=p.read_text()
            self.assertIn("experiment/v4.17-midpoint-long-poll",t)
            self.assertIn("rx_v417_no_progress_backoff_us(offset, length)",t)
if __name__=="__main__":
    unittest.main()
