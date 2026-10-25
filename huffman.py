"""Huffman coding algorithm and a small, validated .huf file format."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import heapq
from pathlib import Path
import struct

MAGIC = b"HUFV"
VERSION = 1
HEADER = struct.Struct(">4sBQIQ")  # magic, version, UTF-8 byte length, symbols, meaningful bits
MAX_SYMBOLS = 1_114_112


class HuffmanError(ValueError):
    """Raised for invalid code streams or malformed compressed files."""


@dataclass
class Node:
    frequency: int
    order: int
    symbol: str | None = None
    left: "Node | None" = None
    right: "Node | None" = None

    @property
    def is_leaf(self) -> bool:
        return self.symbol is not None


@dataclass
class BuildStep:
    first: Node
    second: Node
    parent: Node
    queue_after: list[Node]


def character_label(symbol: str) -> str:
    return {" ": "[space]", "\t": "[tab]", "\n": "[newline]", "\r": "[carriage return]"}.get(symbol, symbol)


def frequencies(text: str) -> Counter[str]:
    return Counter(text)


def _make_tree_from_frequencies(freq: Counter[str]) -> tuple[Node | None, list[BuildStep]]:
    """Build deterministically; symbols sort by Unicode code point before heap insertion."""
    heap: list[tuple[int, int, Node]] = []
    order = 0
    for symbol in sorted(freq):
        node = Node(freq[symbol], order, symbol)
        heapq.heappush(heap, (node.frequency, order, node))
        order += 1
    if not heap:
        return None, []
    steps: list[BuildStep] = []
    while len(heap) > 1:
        _, _, first = heapq.heappop(heap)
        _, _, second = heapq.heappop(heap)
        parent = Node(first.frequency + second.frequency, order, None, first, second)
        order += 1
        heapq.heappush(heap, (parent.frequency, parent.order, parent))
        queue = [entry[2] for entry in sorted(heap)]
        steps.append(BuildStep(first, second, parent, queue))
    return heap[0][2], steps


def build_tree(text: str) -> tuple[Node | None, Counter[str], list[BuildStep]]:
    freq = frequencies(text)
    root, steps = _make_tree_from_frequencies(freq)
    return root, freq, steps


def build_tree_from_frequencies(freq: Counter[str]) -> Node | None:
    if any(not isinstance(s, str) or len(s) != 1 or n <= 0 for s, n in freq.items()):
        raise HuffmanError("Symbol table contains an invalid symbol or frequency.")
    return _make_tree_from_frequencies(freq)[0]


def generate_codes(root: Node | None) -> dict[str, str]:
    if root is None:
        return {}
    result: dict[str, str] = {}

    def visit(node: Node, path: str) -> None:
        if node.is_leaf:
            result[node.symbol] = path or "0"  # one-symbol tree
            return
        if node.left:
            visit(node.left, path + "0")
        if node.right:
            visit(node.right, path + "1")
    visit(root, "")
    return result


def encode(text: str, codes: dict[str, str]) -> str:
    try:
        return "".join(codes[symbol] for symbol in text)
    except KeyError as exc:
        raise HuffmanError(f"No code exists for {exc.args[0]!r}.") from exc


def decode(bits: str, root: Node | None) -> str:
    if any(bit not in "01" for bit in bits):
        raise HuffmanError("Encoded input may contain only 0 and 1.")
    if root is None:
        if bits:
            raise HuffmanError("Cannot decode bits without a Huffman tree.")
        return ""
    if root.is_leaf:
        if any(bit != "0" for bit in bits):
            raise HuffmanError("A single-symbol tree accepts only 0 bits.")
        return root.symbol * len(bits)
    output: list[str] = []
    node = root
    for bit in bits:
        node = node.left if bit == "0" else node.right
        if node is None:
            raise HuffmanError("Bitstream does not match this Huffman tree.")
        if node.is_leaf:
            output.append(node.symbol)
            node = root
    if node is not root:
        raise HuffmanError("Bitstream ends in an incomplete codeword.")
    return "".join(output)


def statistics(text: str, codes: dict[str, str], freq: Counter[str] | None = None) -> dict[str, float | int | bool]:
    freq = freq if freq is not None else frequencies(text)
    original = len(text.encode("utf-8")) * 8
    encoded = sum(count * len(codes[symbol]) for symbol, count in freq.items())
    return {
        "characters": len(text), "utf8_bytes": len(text.encode("utf-8")), "distinct": len(freq),
        "original_bits": original, "encoded_bits": encoded,
        "average": encoded / len(text) if text else 0.0,
        "ratio": original / encoded if encoded else 0.0,
        "savings": (1 - encoded / original) * 100 if original else 0.0,
        "smaller": encoded < original if original else False,
    }


def pack_bits(bits: str) -> bytes:
    padding = (-len(bits)) % 8
    padded = bits + "0" * padding
    return bytes(int(padded[index:index + 8], 2) for index in range(0, len(padded), 8))


def unpack_bits(data: bytes, bit_count: int) -> str:
    if bit_count < 0 or bit_count > len(data) * 8:
        raise HuffmanError("Invalid meaningful bit count.")
    return "".join(f"{byte:08b}" for byte in data)[:bit_count]


def compress_to_file(text: str, path: str | Path) -> int:
    root, freq, _ = build_tree(text)
    codes = generate_codes(root)
    bits = encode(text, codes)
    payload = pack_bits(bits)
    table = bytearray()
    for symbol in sorted(freq):
        raw = symbol.encode("utf-8")
        table.extend(struct.pack(">B", len(raw)))
        table.extend(raw)
        table.extend(struct.pack(">Q", freq[symbol]))
    blob = HEADER.pack(MAGIC, VERSION, len(text.encode("utf-8")), len(freq), len(bits)) + table + payload
    destination = Path(path)
    destination.write_bytes(blob)
    return len(blob)


def decompress_from_file(path: str | Path) -> str:
    data = Path(path).read_bytes()
    if len(data) < HEADER.size:
        raise HuffmanError("File is too short to be a HUFV file.")
    magic, version, original_bytes, count, bit_count = HEADER.unpack_from(data)
    if magic != MAGIC:
        raise HuffmanError("Not a Huffman Visualizer (.huf) file.")
    if version != VERSION:
        raise HuffmanError(f"Unsupported HUFV version {version}.")
    if count > MAX_SYMBOLS or original_bytes > len(data) * 1_000_000:
        raise HuffmanError("File header declares an unsafe size.")
    offset = HEADER.size
    freq: Counter[str] = Counter()
    for _ in range(count):
        if offset >= len(data):
            raise HuffmanError("Truncated symbol table.")
        length = data[offset]; offset += 1
        if length == 0 or length > 4 or offset + length + 8 > len(data):
            raise HuffmanError("Malformed or truncated symbol table.")
        try:
            symbol = data[offset:offset + length].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HuffmanError("Symbol table has invalid UTF-8.") from exc
        offset += length
        if len(symbol) != 1 or symbol in freq:
            raise HuffmanError("Symbol table has an invalid or duplicate symbol.")
        number = struct.unpack_from(">Q", data, offset)[0]; offset += 8
        if number == 0:
            raise HuffmanError("Symbol frequencies must be positive.")
        freq[symbol] = number
    payload = data[offset:]
    if bit_count > len(payload) * 8 or (bit_count + 7) // 8 != len(payload):
        raise HuffmanError("Payload length does not match meaningful bit count.")
    root = build_tree_from_frequencies(freq)
    bits = unpack_bits(payload, bit_count)
    text = decode(bits, root)
    if len(text.encode("utf-8")) != original_bytes or Counter(text) != freq:
        raise HuffmanError("Decoded contents do not match file metadata.")
    return text
