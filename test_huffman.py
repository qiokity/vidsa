import tempfile
import unittest
from collections import Counter
from pathlib import Path

from huffman import (HuffmanError, build_tree, compress_to_file, decode, decompress_from_file,
                     encode, generate_codes, pack_bits, unpack_bits)


class HuffmanTests(unittest.TestCase):
    def round_trip(self, text):
        root, freq, steps = build_tree(text)
        codes = generate_codes(root)
        self.assertEqual(decode(encode(text, codes), root), text)
        self.assertEqual(root.frequency if root else 0, len(text))
        self.assertEqual(len(steps), max(0, len(freq) - 1))
        values = list(codes.values())
        for one in values:
            for other in values:
                if one != other: self.assertFalse(other.startswith(one))
        return root, codes

    def test_empty_input(self):
        root, freq, steps = build_tree("")
        self.assertIsNone(root); self.assertFalse(freq); self.assertFalse(steps)
        self.assertEqual(decode("", root), "")

    def test_one_symbol(self):
        root, codes = self.round_trip("aaaaaa")
        self.assertEqual(codes, {"a": "0"}); self.assertEqual(decode("000", root), "aaa")

    def test_two_symbols(self): self.round_trip("abababab")
    def test_different_frequencies(self): self.round_trip("aaaabbcdef")
    def test_equal_frequencies_deterministic(self):
        _, first = self.round_trip("abcdabcd")
        _, second = self.round_trip("dcbaabcd")
        self.assertEqual(first, second)
    def test_whitespace_punctuation(self): self.round_trip("Hello, world!\n\tHello.")
    def test_unicode(self): self.round_trip("नमस्ते 世界 🌟 café")

    def test_invalid_bits(self):
        root, _ = self.round_trip("abcabc")
        with self.assertRaises(HuffmanError): decode("012", root)
        with self.assertRaises(HuffmanError): decode("1", root)  # incomplete for this tree

    def test_bit_packing(self):
        bits = "10100011101"
        self.assertEqual(unpack_bits(pack_bits(bits), len(bits)), bits)

    def test_file_round_trips_and_malformed(self):
        with tempfile.TemporaryDirectory() as directory:
            for index, text in enumerate(("", "zzzzzz", "Hello\n世界 🌟!")):
                path = Path(directory) / f"{index}.huf"
                compress_to_file(text, path)
                self.assertEqual(decompress_from_file(path), text)
            bad = Path(directory) / "bad.huf"; bad.write_bytes(b"nope")
            with self.assertRaises(HuffmanError): decompress_from_file(bad)
            trunc = Path(directory) / "trunc.huf"; trunc.write_bytes((Path(directory) / "2.huf").read_bytes()[:-1])
            with self.assertRaises(HuffmanError): decompress_from_file(trunc)

if __name__ == "__main__": unittest.main()
