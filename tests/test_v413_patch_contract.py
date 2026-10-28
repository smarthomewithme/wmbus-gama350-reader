"""v4.13: isolated post-drain backoff scheduling; never touch RF/IRQ/decode."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches" / "0012-v4_13-progress-poll.patch"


class TestV413ProgressPolling(unittest.TestCase):
    def test_exact_scope_and_receive_policy(self):
        patch = PATCH.read_text(encoding="utf-8")
        paths = [line.removeprefix("diff --git a/").split(" b/")[0]
                 for line in patch.splitlines() if line.startswith("diff --git a/")]
        self.assertEqual(paths, [
            "components/wmbus_radio/cc1101_fifo.h",
            "components/wmbus_radio/transceiver_cc1101.cpp",
            "components/wmbus_radio/component.cpp",
        ])
        self.assertIn("rx_should_backoff_after_drain(made_progress)", patch)
        self.assertIn("+    if (rx_should_backoff_after_drain(made_progress))", patch)
        self.assertIn("-    delayMicroseconds(200);", patch)
        self.assertIn("+      delayMicroseconds(200);", patch)
        self.assertIn("SHWM v4.13 post-drain polling", patch)
        self.assertIn("SHWM wMBus v4.13 ACTIVE", patch)
        additions = "\n".join(line for line in patch.splitlines()
                               if line.startswith("+") and not line.startswith("+++"))
        for forbidden in ("CC1101_MDMCFG4", "CC1101_FIFOTHR", "CC1101_FREQ",
                          "this->write_register(", "restart_rx(", "this->strobe(",
                          "wakeup_receiver_task_from_isr(", "attach_data_interrupt(",
                          "decode3of6", "rx_fifo_incomplete_read(",
                          "rx_fifo_complete_read("):
            self.assertNotIn(forbidden, additions)

    def test_patch_chain_cache_ci_and_native_fixture(self):
        b = (ROOT / "components/_bootstrap_v4.py").read_text()
        sh = (ROOT / "scripts/prepare_cc1101_v4.sh").read_text()
        for source in (b, sh):
            self.assertLess(source.index("0011-v4_12-overflow-fastpath.patch"),
                            source.index(PATCH.name))
            self.assertIn(PATCH.name, source)
        self.assertIn("shwm-wmbus-v4.20-post-progress-75us-v1", b)
        self.assertIn("SHWM v4.13 post-drain polling", b)
        self.assertIn("rx_should_backoff_after_drain(made_progress)", sh)
        self.assertTrue((ROOT / "tests/v413_receive_backoff.cpp").exists())
        for workflow in ("official-v4.yml", "direct-esphome-install.yml"):
            wf = (ROOT / ".github/workflows" / workflow).read_text()
            self.assertIn("experiment/v4.13-progress-poll", wf)
            self.assertIn("rx_should_backoff_after_drain(made_progress)", wf)


if __name__ == "__main__":
    unittest.main()
