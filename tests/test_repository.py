import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent

class TestRepository(unittest.TestCase):
    def test_header_fixture(self):
        raw = bytes.fromhex((ROOT / "fixtures/gama350_header_encoded.hex").read_text())
        decoded = bytes.fromhex((ROOT / "fixtures/gama350_header_decoded.hex").read_text())
        self.assertEqual(len(raw), 20)
        self.assertEqual(len(decoded), 13)
        self.assertEqual(decoded[:10].hex().upper(), "BE44ED14785634120102")
        self.assertEqual(decoded[10:12].hex().upper(), "242A")

    def test_key_indirection(self):
        yaml = (ROOT / "config/wmbus-gama350.yaml").read_text()
        self.assertIn("key: !secret gama350_aes_key", yaml)
        self.assertIn("key: !secret apator_aes_key", yaml)
        self.assertNotIn("esphome-components@main", yaml)

    def test_patch_scope(self):
        patch = (ROOT / "patches/0001-safe-packet-decoder-and-cc1101-fifo.patch").read_text()
        for name in ("component.cpp", "decode3of6.cpp", "transceiver_cc1101.cpp"):
            self.assertIn("components/wmbus_radio/" + name, patch)
        self.assertIn("confirmed", patch)

if __name__ == "__main__":
    unittest.main()
