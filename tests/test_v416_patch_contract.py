"""v4.16: one isolated scheduling change based directly on v4.14, not v4.15."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
PATCH=ROOT/"patches/0014-v4_16-long-no-progress-short-poll.patch"
class TestV416Scope(unittest.TestCase):
    def test_scope_and_exact_policy(self):
        s=PATCH.read_text()
        paths=[x.removeprefix("diff --git a/").split(" b/")[0] for x in s.splitlines() if x.startswith("diff --git a/")]
        self.assertEqual(paths,["components/wmbus_radio/cc1101_fifo.h","components/wmbus_radio/transceiver_cc1101.cpp","components/wmbus_radio/component.cpp"])
        self.assertIn("+      delayMicroseconds(rx_no_progress_backoff_us(offset, length));",s)
        self.assertIn("return offset == 3u && length >= 250u ? 50u : 200u;",s)
        self.assertIn("SHWM wMBus v4.16 ACTIVE",s)
        added="\n".join(x for x in s.splitlines() if x.startswith("+") and not x.startswith("+++"))
        for forbidden in ("CC1101_MDMCFG4","CC1101_FIFOTHR","CC1101_FREQ",
                          "read_burst(","read_status_register(","restart_rx(",
                          "wakeup_receiver_task_from_isr(","decode3of6",
                          "delayMicroseconds(100);","rx_should_backoff_after_unstable"):
            self.assertNotIn(forbidden,added)
        self.assertNotIn("v4.15",s)
    def test_chain_ci_and_fingerprint(self):
        b=(ROOT/"components/_bootstrap_v4.py").read_text()
        sh=(ROOT/"scripts/prepare_cc1101_v4.sh").read_text()
        for s in (b,sh):
            self.assertLess(s.index("0013-v4_14-preallocate-packet-before-irq.patch"),s.index(PATCH.name))
            self.assertNotIn("0014-v4_15",s)
            self.assertIn("SHWM wMBus v4.16 ACTIVE",s)
        self.assertIn("shwm-wmbus-v4.17-midpoint-long-poll-v1",b)
        self.assertTrue((ROOT/"tests/v416_long_idle_poll.cpp").exists())
        for name in ("official-v4.yml","direct-esphome-install.yml"):
            s=(ROOT/".github/workflows"/name).read_text()
            self.assertIn("experiment/v4.16-long-idle-poll",s)
            self.assertTrue(any(token in s for token in ("rx_no_progress_backoff_us(offset, length)", "rx_v417_no_progress_backoff_us(offset, length)")))
if __name__=="__main__":
    unittest.main()
