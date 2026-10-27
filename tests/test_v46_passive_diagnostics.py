"""Contract for the isolated v4.6 *passive* CC1101 diagnostic patch."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATCH = ROOT / "patches/0008-v4_6-passive-long-gap-diagnostics.patch"


class TestV46PassiveDiagnostics(unittest.TestCase):
    def test_patch_is_passive_and_scoped(self):
        patch = PATCH.read_text(encoding="utf-8")
        self.assertEqual(patch.count("diff --git a/"), 3)
        for name in ("component.cpp", "component.h", "long_gap_diagnostics.h"):
            self.assertIn("components/wmbus_radio/" + name, patch)
        self.assertIn("RX_DIAG v4.6", patch)
        self.assertIn("estimate_missing_30s_periods", patch)
        self.assertIn("long_candidates_", patch)
        self.assertIn("long_read_failures_", patch)
        self.assertIn("gaps_with_short_", patch)
        # Newly added lines may not alter GPIO, radio registers, SPI or ISR.
        additions = "\n".join(line[1:] for line in patch.splitlines()
                              if line.startswith("+") and not line.startswith("+++"))
        for forbidden in ("read_status_register(", "write_register(", "read_burst(",
                          "attach_data_interrupt(", "vTaskNotifyGiveFromISR(",
                          "portYIELD_FROM_ISR(", "restart_rx(", "CC1101_FIFOTHR"):
            self.assertNotIn(forbidden, additions)
        self.assertEqual(additions.count("ESP_LOGI("), 1)

    def test_empty_gap_is_not_counted(self):
        self.assertIn("gap_ms < 45000u", PATCH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
