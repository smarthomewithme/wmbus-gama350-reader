"""v4.11: RXBYTES 65 is valid via CC1101 prefetch; never alter RF settings."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches" / "0010-v4_11-rxbytes65-prefetch.patch"


class TestV411Prefetch(unittest.TestCase):
    def test_patch_changes_only_fifo_bounds(self):
        patch = PATCH.read_text(encoding="utf-8")
        paths = [s.removeprefix("diff --git a/").split(" b/")[0]
                 for s in patch.splitlines() if s.startswith("diff --git a/")]
        self.assertEqual(paths, [
            "components/wmbus_radio/cc1101_fifo.h",
            "components/wmbus_radio/transceiver_cc1101.cpp",
        ])
        self.assertIn("kCc1101MaxReportedRxBytes = 65", patch)
        self.assertIn("rx_fifo_incomplete_read(available, remaining)", patch)
        self.assertIn("rx_fifo_complete_read(confirmed & 0x7F, remaining)", patch)
        self.assertIn("!rx_fifo_count_plausible(available)", patch)
        for forbidden in ("CC1101_MDMCFG4", "CC1101_FIFOTHR", "CC1101_FREQ",
                          "CC1101_SRX", "CC1101_SFRX", "wakeup_receiver_task_from_isr",
                          "component.cpp", "receiver_task("):
            self.assertNotIn(forbidden, patch)

    def test_pin_fingerprint_and_order(self):
        b = (ROOT / "components/_bootstrap_v4.py").read_text()
        sh = (ROOT / "scripts/prepare_cc1101_v4.sh").read_text()
        names = [
            "0001-safe-packet-decoder-and-cc1101-fifo.patch",
            "0002-cc1101-long-frame-diagnostics.patch",
            "0003-cc1101-stable-rxbytes.patch",
            "0004-radio-diagnostics-and-key-redaction.patch",
            "0005-experimental-fifo16-threshold.patch",
            "0006-v4_4-clear-stale-irq.patch",
            "0007-v4_5-initialize-isr-woken.patch",
            "0008-v4_9-confirm-marcstate-eof.patch",
            "0009-v4_10-five-minute-rx-diag.patch",
            PATCH.name,
        ]
        for source in (b, sh):
            offsets = [source.index(name) for name in names]
            self.assertEqual(offsets, sorted(offsets))
        # The active cache layout always belongs to the newest experimental revision.
        self.assertIn("shwm-wmbus-v4.17-midpoint-long-poll-v1", b)
        self.assertIn("kCc1101MaxReportedRxBytes = 65", b)
        self.assertIn("kCc1101MaxReportedRxBytes = 65", sh)


if __name__ == "__main__":
    unittest.main()
