"""v4.21: unchanged firmware-source control built from exact v4.17 patches."""
import ast
import hashlib
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
EXPECTED=[
  [
    "0001-safe-packet-decoder-and-cc1101-fifo.patch",
    "76c8362853aa6e1c24209d5d0e1f40e498a3c561"
  ],
  [
    "0002-cc1101-long-frame-diagnostics.patch",
    "6e3a55fab69cf3f6850c378485c3b8baaaeda61f"
  ],
  [
    "0003-cc1101-stable-rxbytes.patch",
    "36f717993947e2b619642a5224063f75adef7791"
  ],
  [
    "0004-radio-diagnostics-and-key-redaction.patch",
    "faecc457237908d5f002355633fe52830fd1a2af"
  ],
  [
    "0005-experimental-fifo16-threshold.patch",
    "fb4cfbb58d4ec7601db1ad672ad90382b1f41929"
  ],
  [
    "0006-v4_4-clear-stale-irq.patch",
    "7c9aa74f98f6fac2b09b67d7b35133abbb70b105"
  ],
  [
    "0007-v4_5-initialize-isr-woken.patch",
    "8ff9fc9422df9c5d0e26474c5d3a5df981cfb0aa"
  ],
  [
    "0008-v4_9-confirm-marcstate-eof.patch",
    "b2c6d9f09453e75ff654a7ed53bf61d3f3661e29"
  ],
  [
    "0009-v4_10-five-minute-rx-diag.patch",
    "4fbfb8ab77783e9c6e5103d76fd73c4c24b141fb"
  ],
  [
    "0010-v4_11-rxbytes65-prefetch.patch",
    "989be009ff87f44edd5dc369ee970bb363eccae5"
  ],
  [
    "0011-v4_12-overflow-fastpath.patch",
    "9701d8122dde0e660b1b2ef9d59d4454ea761af7"
  ],
  [
    "0012-v4_13-progress-poll.patch",
    "adea1fba1cabdfff2f7ac42ca697b275a0de6ac5"
  ],
  [
    "0013-v4_14-preallocate-packet-before-irq.patch",
    "67bde003f06452b572dd8eebae5226a191c66d04"
  ],
  [
    "0014-v4_16-long-no-progress-short-poll.patch",
    "b85cb52d918a5daf458356689d5a6aa1d8b4967e"
  ],
  [
    "0015-v4_17-midpoint-long-idle-poll.patch",
    "464521b5e3a591ca26ea777e2f8351e395dcd9c8"
  ]
]

def blob_sha(path):
    data=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\x00"+data).hexdigest()

class TestV421VerbatimControl(unittest.TestCase):
    def test_exact_v417_patch_chain(self):
        b=(ROOT/"components/_bootstrap_v4.py").read_text(encoding="utf-8")
        self.assertIn('a732dd0e52c48973fad57e4950a11d8e2f2d6820', b)
        self.assertIn('shwm-wmbus-v4.22-failure-only-snapshots-v1', b)
        self.assertIn('SHWM v4.22 diagnostic:',b)
        mod=ast.parse(b)
        node=next(n.value for n in mod.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_PATCHES' for t in n.targets))
        chain=ast.literal_eval(node)
        self.assertEqual(chain,tuple(name for name,sha in EXPECTED)+('0016-v4_22-cc1101-failure-only-snapshots.patch',))
        self.assertEqual(len(list((ROOT/'patches').glob('*.patch'))),16)
        for name,sha in EXPECTED:
            with self.subTest(name=name):
                self.assertEqual(blob_sha(ROOT/'patches'/name),sha)
    def test_no_new_compiled_files(self):
        for name in ('wmbus_common','wmbus_radio','wmbus_meter','socket_transmitter'):
            files=sorted(p.name for p in (ROOT/'components'/name).rglob('*') if p.is_file())
            self.assertEqual(files,['__init__.py'])
        for f in ('official-v4.yml','direct-esphome-install.yml'):
            s=(ROOT/'.github/workflows'/f).read_text(encoding='utf-8')
            self.assertIn('experiment/v4.21-verbatim-v417-control',s)
if __name__=='__main__':
    unittest.main()
