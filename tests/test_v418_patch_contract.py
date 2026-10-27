"""v4.18: one isolated 150us no-progress scheduling change from v4.17."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
PATCH=ROOT/"patches/0016-v4_18-long-no-progress-150us.patch"
class TestV418Scope(unittest.TestCase):
    def test_scope(self):
        s=PATCH.read_text(encoding="utf-8")
        paths=[x.removeprefix("diff --git a/").split(" b/")[0] for x in s.splitlines() if x.startswith("diff --git a/")]
        self.assertEqual(paths,["components/wmbus_radio/cc1101_fifo.h","components/wmbus_radio/transceiver_cc1101.cpp","components/wmbus_radio/component.cpp"])
        self.assertIn("return offset == 3u && length >= 250u ? 150u",s)
        self.assertIn("+      delayMicroseconds(rx_v418_no_progress_backoff_us(offset, length));",s)
        self.assertIn("-      delayMicroseconds(rx_v417_no_progress_backoff_us(offset, length));",s)
        self.assertIn("SHWM wMBus v4.18 ACTIVE",s)
        additions="\n".join(x for x in s.splitlines() if x.startswith("+") and not x.startswith("+++"))
        for token in ("CC1101_MDMCFG4","CC1101_FIFOTHR","CC1101_FREQ","read_burst(","read_status_register(","restart_rx(","wakeup_receiver_task_from_isr(","decode3of6","delayMicroseconds(100);","rx_should_backoff_after_unstable("):
            self.assertNotIn(token,additions)
    def test_chain_and_ci(self):
        b=(ROOT/"components/_bootstrap_v4.py").read_text(encoding="utf-8")
        sh=(ROOT/"scripts/prepare_cc1101_v4.sh").read_text(encoding="utf-8")
        for txt in (b,sh):
            self.assertLess(txt.index("0015-v4_17-midpoint-long-idle-poll.patch"),txt.index(PATCH.name))
            self.assertNotIn("0014-v4_15",txt)
            self.assertIn("SHWM wMBus v4.18 ACTIVE",txt)
        self.assertIn("shwm-wmbus-v4.18-long-idle-150us-v1",b)
        for fname in ("official-v4.yml","direct-esphome-install.yml"):
            txt=(ROOT/".github/workflows"/fname).read_text()
            self.assertIn("experiment/v4.18-long-idle-150us",txt)
            self.assertIn("rx_v418_no_progress_backoff_us(offset, length)",txt)
        self.assertTrue((ROOT/"tests/v418_idle_150us.cpp").is_file())
if __name__=="__main__":
    unittest.main()
