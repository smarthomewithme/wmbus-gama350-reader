"""v4.20 isolated 75us delay after successful long payload FIFO drain from v4.17."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
PATCH=ROOT/"patches/0016-v4_20-post-progress-coalesce-75us.patch"
class TestV420Scope(unittest.TestCase):
    def test_patch_scope(self):
        s=PATCH.read_text(encoding="utf-8")
        paths=[x.removeprefix("diff --git a/").split(" b/")[0] for x in s.splitlines() if x.startswith("diff --git a/")]
        self.assertEqual(paths,["components/wmbus_radio/cc1101_fifo.h","components/wmbus_radio/transceiver_cc1101.cpp","components/wmbus_radio/component.cpp"])
        self.assertIn("made_progress && offset == 3u && length >= 250u ? 75u : 0u",s)
        self.assertIn("delayMicroseconds(progress_wait_us);",s)
        self.assertIn("rx_v417_no_progress_backoff_us(offset, length)",s)
        self.assertIn("SHWM wMBus v4.20 ACTIVE",s)
        additions="\n".join(x for x in s.splitlines() if x.startswith("+") and not x.startswith("+++"))
        for forbidden in ("CC1101_MDMCFG4","CC1101_FIFOTHR","CC1101_FREQ",
                          "read_status_register(","read_burst(","restart_rx(",
                          "wakeup_receiver_task_from_isr(","decode3of6","rx_should_backoff_after_unstable("):
            self.assertNotIn(forbidden,additions)
    def test_bootstrap_ci(self):
        b=(ROOT/"components/_bootstrap_v4.py").read_text()
        sh=(ROOT/"scripts/prepare_cc1101_v4.sh").read_text()
        for s in (b,sh):
            self.assertLess(s.index("0015-v4_17-midpoint-long-idle-poll.patch"),s.index(PATCH.name))
            self.assertNotIn("0016-v4_18-long-no-progress-150us.patch",s)
            self.assertNotIn("0016-v4_19-early-fifo8-irq.patch",s)
            self.assertIn("SHWM wMBus v4.20 ACTIVE",s)
            self.assertIn("rx_v420_post_progress_wait_us(offset, length, made_progress)",s)
        self.assertIn("shwm-wmbus-v4.20-post-progress-75us-v1",b)
        self.assertTrue((ROOT/"tests/v420_coalesce.cpp").is_file())
        for name in ("official-v4.yml","direct-esphome-install.yml"):
            s=(ROOT/".github/workflows"/name).read_text()
            self.assertIn("experiment/v4.20-long-progress-coalesce",s)
            self.assertIn("rx_v420_post_progress_wait_us(offset, length, made_progress)",s)
if __name__=="__main__":
    unittest.main()
