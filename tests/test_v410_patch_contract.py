"""v4.10 scope guard: 5-minute reporting only; radio RX path remains v4.9."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches" / "0009-v4_10-five-minute-rx-diag.patch"


class TestV410Scope(unittest.TestCase):
    def test_patch_touches_no_rx_transceiver_or_isr(self):
        source = PATCH.read_text(encoding="utf-8")
        paths = [line.removeprefix("diff --git a/").split(" b/")[0]
                 for line in source.splitlines() if line.startswith("diff --git a/")]
        self.assertEqual(paths, [
            "components/wmbus_radio/rx_diag_window.h",
            "components/wmbus_radio/component.h",
            "components/wmbus_radio/component.cpp",
        ])
        self.assertIn("SHWM v4.10 RX_DIAG_5M", source)
        self.assertIn("frame_conversion_failed_.fetch_add", source)
        self.assertIn("inline RxDiagSnapshot rx_diag_delta(", source)
        self.assertNotIn("CC1101_MDMCFG4", source)
        self.assertNotIn("CC1101_FIFOTHR", source)
        self.assertNotIn("CC1101_MARCSTATE", source)
        self.assertNotIn("receive_frame()", source)
        self.assertNotIn("wakeup_receiver_task_from_isr", source)
        self.assertNotIn("read_in_task(", source)
        self.assertNotIn("restart_rx(", source)

    def test_fingerprint_and_shell_patch_agreement(self):
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
            "0008-v4_9-confirm-marcstate-eof.patch",
            PATCH.name,
        ]
        for text in (bootstrap, shell):
            positions = [text.index(n) for n in names]
            self.assertEqual(positions, sorted(positions))
        # Current cache fingerprint is owned by the newest version contract.
        self.assertIn("SHWM v4.10 RX_DIAG_5M", shell)


if __name__ == "__main__":
    unittest.main()
