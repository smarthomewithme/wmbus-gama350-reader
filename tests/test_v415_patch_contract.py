"""v4.15: one isolated retry policy change for long payloads."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
PATCH=ROOT/"patches/0014-v4_15-unstable-long-payload-fast-retry.patch"

class TestV415Scope(unittest.TestCase):
    def test_exact_scope_and_backoff(self):
        s=PATCH.read_text()
        paths=[x.removeprefix("diff --git a/").split(" b/")[0] for x in s.splitlines() if x.startswith("diff --git a/")]
        self.assertEqual(paths,["components/wmbus_radio/cc1101_fifo.h","components/wmbus_radio/transceiver_cc1101.cpp","components/wmbus_radio/component.cpp"])
        self.assertIn("+      if (rx_should_backoff_after_unstable(offset, length))",s)
        self.assertIn("+        delayMicroseconds(100);",s)
        self.assertIn("-      delayMicroseconds(100);",s)
        self.assertIn("return offset != 3u || length < 250u;",s)
        self.assertIn("SHWM wMBus v4.15 ACTIVE",s)
        added="\n".join(x for x in s.splitlines() if x.startswith("+") and not x.startswith("+++"))
        for forbidden in ("CC1101_MDMCFG4","CC1101_FIFOTHR","CC1101_FREQ","read_burst(","read_status_register(","restart_rx(","wakeup_receiver_task_from_isr(","decode3of6","this->strobe("):
            self.assertNotIn(forbidden,added)

    def test_loader_ci_and_patch_order(self):
        boot=(ROOT/"components/_bootstrap_v4.py").read_text()
        sh=(ROOT/"scripts/prepare_cc1101_v4.sh").read_text()
        for s in (boot,sh):
            self.assertLess(s.index("0013-v4_14-preallocate-packet-before-irq.patch"),s.index(PATCH.name))
            self.assertIn("SHWM wMBus v4.15 ACTIVE",s)
        self.assertIn("shwm-wmbus-v4.15-fast-unstable-retry-v1",boot)
        self.assertTrue((ROOT/"tests/v415_unstable_retry.cpp").is_file())
        official=(ROOT/".github/workflows/official-v4.yml").read_text()
        direct=(ROOT/".github/workflows/direct-esphome-install.yml").read_text()
        for wf in (official,direct):
            self.assertIn("experiment/v4.15-fast-unstable-retry",wf)
            self.assertIn("rx_should_backoff_after_unstable(offset, length)",wf)
        self.assertIn("tests/v415_unstable_retry.cpp",official)

if __name__=="__main__":
    unittest.main()
