"""SHA256SUMS: every file of the package as released; a changed byte must fail."""
import hashlib
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sums(root):
    with open(os.path.join(root, "SHA256SUMS")) as f:
        return [l.split("  ", 1) for l in f.read().splitlines() if l]


def bad(root, listed):
    out = []
    for digest, name in listed:
        with open(os.path.join(root, name), "rb") as f:
            if hashlib.sha256(f.read()).hexdigest() != digest:
                out.append(name)
    return out


class TestFiles(unittest.TestCase):
    def test_checksums(self):
        listed = sums(ROOT)
        self.assertGreater(len(listed), 10)
        self.assertEqual(bad(ROOT, listed), [])

    def test_a_changed_byte_fails(self):
        listed = sums(ROOT)
        digest, name = listed[0]
        self.assertEqual(bad(ROOT, [("0" * 64, name)]), [name])


if __name__ == "__main__":
    unittest.main()
