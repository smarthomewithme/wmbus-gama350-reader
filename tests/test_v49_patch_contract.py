"""Static v4.9 scope check: one receiver decision, based on v4.5."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches" / "0008-v4_9-confirm-marcstate-eof.patch"


class TestV49Scope(unittest.TestCase):
    def test_one_bounded_radio_change_only(self):
        source = PATCH.read_text(encoding="utf-8")
        paths = [line.removeprefix("diff --git a/").split(" b/")[0]
                 for line in source.splitlines() if line.startswith("diff --git a/")]
        self.assertEqual(paths, [
            "components/wmbus_radio/cc1101_fifo.h",
            "components/wmbus_radio/transceiver_cc1101.cpp",
        ])
        self.assertEqual(source.count("SHWM v4.9 MARCSTATE EOF confirmation"), 1)
        self.assertIn("confirm_marcstate_eof(", source)
        self.assertIn("attempt < 3", source)
        self.assertIn("if (!is_terminal(current))", source)
        self.assertIn("if (current == previous)", source)
        self.assertNotIn("CC1101_MDMCFG4", source)
        self.assertNotIn("CC1101_FIFOTHR", source)
        self.assertNotIn("wakeup_receiver_task_from_isr", source)
        self.assertNotIn("restart_rx(", source)

    def test_bootstrap_and_shell_agree_on_exact_patch_order(self):
        bootstrap = (ROOT / "components/_bootstrap_v4.py").read_text()
        shell = (ROOT / "scripts/prepare_cc1101_v4.sh").read_text()
        names = [
            "0001-safe-packet-decoder-and-cc1101-fifo.patch",
            "0002-cc1101-long-frame-diagnostics.patch",
            "0003-cc1101-stable-rxbytes.patch",
            "0004-radio-diagnostics-and-key-redaction.patch",
            "0005-experimental-fifo16-threshold.patch",
            "0006-v4_4-clear-stale-irq.patch",
            "0007-v4_5-initialize-isr-woken.patch",
            PATCH.name,
            "0009-v426-rxbytes65-prefetch-only.patch",
        ]
        for text in (bootstrap, shell):
            positions = [text.index(name) for name in names]
            self.assertEqual(positions, sorted(positions))
        self.assertIn("shwm-wmbus-v4.26-v49-rxbytes65-only-v1", bootstrap)


if __name__ == "__main__":
    unittest.main()
