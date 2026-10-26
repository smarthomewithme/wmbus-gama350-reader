#!/usr/bin/env python3
"""Check that the isolated CC1101 filter experiment changes only MDMCFG4."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "vendor/rxfilter_270"
FILE = "components/wmbus_radio/transceiver_cc1101.cpp"

def bandwidth_hz(value: int) -> float:
    exponent = (value >> 6) & 3
    mantissa = (value >> 4) & 3
    return 26_000_000 / (8 * (4 + mantissa) * (2**exponent))

class Filter270Test(unittest.TestCase):
    def test_bandwidth_math_and_rate_bits(self):
        self.assertAlmostEqual(bandwidth_hz(0x5C), 325_000, delta=1)
        self.assertAlmostEqual(bandwidth_hz(0x6C), 270_833.333, delta=1)
        self.assertEqual(0x5C & 0x0F, 0x6C & 0x0F)

    @unittest.skipUnless((SRC / FILE).exists(), 'Isolated source not prepared in this job')
    def test_only_requested_register_value_changes(self):
        self.assertTrue((SRC / FILE).exists(), "Run prepare_rx_filter_270.sh first.")
        before = subprocess.check_output(
            ["git", "-C", str(SRC), "show", f"HEAD:{FILE}"], text=True
        )
        after = (SRC / FILE).read_text()
        reg_before = "this->write_register(CC1101_MDMCFG4, 0x5C);"
        reg_after = "this->write_register(CC1101_MDMCFG4, 0x6C);"
        self.assertEqual(before.count(reg_before), 1)
        self.assertEqual(after.count(reg_after), 1)
        self.assertNotIn(reg_before, after)

        # Remove the experimental comments, then compare the remaining code.
        after_without_comment = "\n".join(
            l for l in after.splitlines()
            if "26 MHz crystal, CHANBW_E=1" not in l
            and "Only the receive-channel bandwidth is changed" not in l
        )
        original_comment = next(
            l for l in before.splitlines()
            if l.strip().startswith("// BW = f_xtal")
        )
        after_without_comment = after_without_comment.replace(
            "  " + reg_after, original_comment + "\n  " + reg_before
        )
        self.assertEqual(after_without_comment.rstrip(), before.rstrip())

    @unittest.skipUnless((SRC / FILE).exists(), 'Isolated source not prepared in this job')
    def test_only_one_upstream_file_modified(self):
        files = subprocess.check_output(
            ["git", "-C", str(SRC), "diff", "--name-only"], text=True
        ).splitlines()
        self.assertEqual(files, [FILE])

if __name__ == "__main__":
    unittest.main(verbosity=2)
