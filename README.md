# Huffman Coding Visualizer

A native Python/Tkinter desktop application that teaches Huffman coding through a frequency table, min-priority-queue construction log, binary-tree canvas, encoding/decoding, and real compressed files.

## Run

Requires Python 3.10+ and no external packages.

```bash
python3 main.py
python3 -m unittest -v
```

The application opens UTF-8 text files. `sample.txt` is ready for a quick demo. On a machine without a GUI display, run the tests instead.

## Features

- Deterministic Huffman tree built with `heapq` and monotonic tie-breakers.
- Readable labels for spaces, tabs, and newlines; Unicode-safe encoding.
- Scrollable tree canvas with labelled `0` / `1` edges, leaf and internal node styling.
- Step log that records actual removal and merge operations from the priority queue.
- UTF-8-aware payload statistics. Original payload is `len(text.encode('utf-8')) * 8`, not merely characters × 8.
- Genuine `.huf` binary compression with packed most-significant-bit-first bytes, meaningful-bit count, UTF-8 symbol/frequency table, magic (`HUFV`), and version (`1`). The app validates malformed/truncated files.

## How Huffman coding works

Count every symbol, place leaves in a min-priority queue, then repeatedly combine the two lowest-frequency nodes. A left edge is `0`; a right edge is `1`. The route from root to a leaf is its prefix-free code. Because no code is a prefix of another, decoding can traverse the tree and emit a character at each leaf. It is lossless.

`n` is input symbols, `k` distinct symbols, and `B` output bits:

- Frequency count: expected `O(n)`.
- Heap/tree merging: `O(k log k)`.
- Code generation: `O(k)` excluding code-string length.
- Encoding: approximately `O(n + B)`.
- Decoding: `O(B)`.

The displayed compression ratio is payload-only. A `.huf` file also contains a header and symbol metadata, so small inputs can produce a larger file. Tied frequencies can yield different correct Huffman codes in other implementations; this app is deterministic to make demonstrations repeatable.

## 3–5 minute demonstration

1. Launch `python3 main.py`, click **Use Sample Text**, and point out special-character rows.
2. Click **Next Step** a few times to explain that the two minimum frequencies merge.
3. Inspect a leaf’s path in the tree and corresponding code in the table.
4. Click **Encode**, then **Decode**; explain that decoded text is recovered by tree traversal.
5. Read the UTF-8-aware statistics, then **Compress and Save…** and explain metadata overhead.
6. Use **Open and Decompress…** to show the exact text returns.

## Viva quick answers

1. **What is Huffman coding?** A variable-length, prefix-free, lossless coding scheme based on symbol frequencies.
2. **Why lossless?** Prefix-free paths identify each encoded symbol unambiguously.
3. **Why a min-priority queue?** It efficiently selects the two least frequent nodes at each merge.
4. **Why combine two lowest nodes?** That greedy choice gives an optimal prefix-code length for known frequencies.
5. **Role of binary tree?** Left/right paths form the `0`/`1` codewords and support decoding.
6. **Why can tied trees differ?** Several equal-frequency merge orders are optimal; the app uses tie-breakers for repeatability.
7. **Why could a file be larger?** The header, frequency table, padding, and low repetition can outweigh savings.
8. **Frequency table vs code generation?** The table counts inputs; traversal turns the completed tree’s paths into codes.
9. **How does this show DSA?** Hash-map counting, a heap, linked tree nodes, recursion, traversal, and binary packing.

## Limitations

The tree uses fixed visual spacing and becomes wide for many unique symbols; its canvas scrollbars preserve access. Very long encoded/decoded text is retained internally but its text-box display is explicitly truncated for responsiveness.
