# Project: Huffman Coding Visualizer — Complete Python DSA Application

Act as a senior Python developer, software architect, and DSA educator. Build a complete, polished, working desktop application named **Huffman Coding Visualizer** using Python.

Do not merely explain how to build it. Actually create the project files, implement the application, run available tests, fix errors, and leave the project ready to run and demonstrate.

Prioritize a fully working project over unnecessary complexity. I have only one evening to complete this project, so keep the implementation focused, reliable, and easy to understand during a college demonstration and viva.

## 1. Project objectives

The application must demonstrate the Huffman Coding algorithm, a lossless compression technique that assigns variable-length prefix-free binary codes to characters according to their frequencies.

The application must let a user:

1. Enter text manually or open a UTF-8 text file.
2. Calculate and visualize character frequencies.
3. Construct the Huffman tree using a min-priority queue.
4. Visualize the complete binary tree.
5. Inspect the Huffman code assigned to each character.
6. Encode the input into a binary bit sequence.
7. Decode the sequence back into the original text.
8. Compare the original and encoded sizes.
9. Save a genuine compressed binary file and reopen it for decompression, if this can be implemented reliably within the project scope.
10. Understand each algorithmic step through explanations and visual feedback.

## 2. Technology requirements

Use the following technologies:

- **Language:** Python 3.
- **GUI:** Tkinter and `tkinter.ttk`.
- **Tree visualization:** Tkinter Canvas.
- **Priority queue:** Python's standard-library `heapq`.
- **File operations:** `pathlib`, `struct`, and other appropriate standard-library modules.
- **Testing:** Python's built-in `unittest`.

Avoid unnecessary dependencies. The core application should work without installing third-party packages.

Do not use a web application, browser interface, notebook, or command-line-only interface. The primary application must be a native desktop GUI.

Do not use a third-party Huffman library. Implement the algorithm and tree data structure yourself.

## 3. Required application interface

Create a polished desktop application with a modern, dark-themed interface. Use a reasonable minimum window size, resizable panels where practical, readable fonts, consistent spacing, and a restrained color palette.

Organize the interface into the following sections.

### A. Header

Display:

- Application title: `Huffman Coding Visualizer`
- Subtitle: `Explore lossless compression through binary trees`
- A small section showing the selected input's character count and current status.

### B. Input panel

Include:

- A multiline text editor.
- An `Open .txt` button.
- A `Clear` button.
- A `Build Huffman Tree` button.
- A `Use Sample Text` button.

Use UTF-8 when opening text files. Preserve whitespace, punctuation, line breaks, and Unicode characters.

For long input, keep the GUI responsive and avoid unnecessarily redrawing every element.

### C. Character frequency and code table

Show a scrollable table with these columns:

- Character, with special labels for spaces, tabs, and newlines.
- Unicode code point where useful.
- Frequency.
- Huffman code.
- Code length.

Sort the table deterministically, preferably by descending frequency and then character/code point.

Use a clear representation for special characters. Do not confuse an actual space with an empty value.

### D. Huffman tree visualization

Draw the actual Huffman binary tree on a Tkinter Canvas.

Requirements:

- Internal nodes display their combined frequency.
- Leaf nodes display the character and its frequency.
- Left edges are labeled `0`.
- Right edges are labeled `1`.
- Leaves and internal nodes have visually distinct styles.
- Draw connecting edges behind nodes.
- Keep node labels readable.
- Support scrolling or another sensible way to inspect larger trees.
- Recalculate node positions when the tree is rebuilt or the window is resized.
- Handle a single-character input correctly.
- Show an informative empty state before a tree has been built.

Implement a simple tree-layout algorithm using node depth and subtree structure. Do not rely on hardcoded positions for one example.

If there are too many distinct characters for the available screen space, make the tree scrollable rather than letting the interface become unusable.

### E. Algorithm construction and learning panel

Provide a panel explaining how the Huffman tree is built.

Include:

- A list of current priority-queue entries.
- A step-by-step construction log.
- A `Next Step` button.
- A `Reset Steps` button.
- A `Build Complete Tree` button.

At each construction step, show the two nodes with the smallest frequencies being removed from the min-priority queue, their combination into a new parent node, and the resulting queue.

Keep the step-by-step state consistent with the final tree. Prefer implementing tree construction as an actual sequence of recorded operations, not fabricated explanatory messages.

If implementing the full animation would compromise reliability, prioritize a working step log and a correct final tree.

### F. Encoding and decoding panel

Display:

- The generated encoded bit sequence.
- The decoded output.
- A `Encode` button.
- A `Decode` button.
- A `Copy Encoded Bits` button if practical.

The encoded sequence must be derived from the generated Huffman codes. Decoding must traverse the actual tree or use an equivalent correct decoding structure.

Do not use a hardcoded mapping or sample output.

For a single distinct character, assign a one-bit code such as `0` so that repeated characters can be represented and decoded unambiguously. Handle the empty string separately.

For large input, avoid creating excessively large GUI strings without a practical display limit or truncation strategy. Make clear when displayed content is truncated; never silently truncate the actual data being encoded or saved.

### G. Compression statistics

Show the following statistics:

- Number of input characters.
- Number of distinct characters.
- Original payload size in bits.
- Huffman-encoded payload size in bits.
- Average bits per character.
- Compression ratio.
- Percentage of payload bits saved.
- Whether the encoded payload is smaller than the original payload.

For the theoretical original payload size, use 8 bits per UTF-8 byte, not an incorrect assumption that every Unicode character occupies one byte.

Show both character count and UTF-8 byte count where appropriate.

Use these definitions:

`Original payload bits = len(original_text.encode("utf-8")) * 8`

`Encoded payload bits = sum(frequency(character) * len(code(character)))`

`Average bits per character = encoded payload bits / number of characters`

`Compression ratio = original payload bits / encoded payload bits`

`Payload savings (%) = (1 - encoded payload bits / original payload bits) * 100`

Guard against division by zero and clearly distinguish payload-only statistics from actual compressed-file size.

A negative savings percentage is valid if Huffman coding produces more payload bits than the original representation.

Do not claim that a theoretical bit sequence is a compressed file or that payload savings equal actual disk-space savings.

## 4. Actual compressed-file support

If feasible within the deadline, implement genuine binary compression and decompression.

Add:

- `Compress and Save...`
- `Open and Decompress...`

Use a documented, versioned binary file format that stores enough information to reconstruct the original UTF-8 text exactly.

A practical format may contain:

1. A magic signature identifying the file format.
2. A format version.
3. The original UTF-8 byte length.
4. The number of distinct symbols.
5. The symbol table, including UTF-8 bytes and corresponding frequencies, or another unambiguous representation of the Huffman tree.
6. The exact number of meaningful encoded bits.
7. The packed encoded payload.

Requirements:

- Pack bits into actual bytes, using a consistent documented bit order.
- Track the meaningful bit count so padding bits are not decoded as data.
- Reconstruct the tree deterministically from stored frequencies or the stored tree representation.
- Preserve the original text exactly, including Unicode and newline characters.
- Support empty input and single-symbol input.
- Validate magic signatures, versions, lengths, symbol counts, bit counts, and truncated payloads.
- Reject malformed or unsupported files gracefully.
- Avoid unbounded memory allocations based on untrusted header values.
- Never overwrite the input file accidentally.
- Report the actual compressed file size, including the header and metadata.
- Show the difference between theoretical payload compression and real file compression, which includes metadata overhead.

For a small text file, the compressed file may be larger than the original. Display this honestly.

If time is insufficient for robust file-format support, complete the visualizer and in-memory encode/decode features first. Do not leave fake file-compression buttons or pretend that saving a bit string as ordinary text constitutes genuine binary compression.

## 5. DSA implementation requirements

Implement the following data structures yourself:

### Huffman tree node

Each node should contain suitable fields, such as:

- Character or symbol, with internal nodes distinguishable from leaves.
- Frequency.
- Left child.
- Right child.
- A deterministic tie-breaking identifier.

### Min-priority queue

Use `heapq` to efficiently select the two nodes with the lowest frequencies.

Ensure deterministic behavior when multiple nodes have the same frequency. Use a monotonically increasing tie-breaker rather than comparing incompatible node objects.

### Tree construction

Implement the following algorithm:

1. Count the frequencies of all symbols.
2. Create one leaf node for each distinct symbol.
3. Insert the leaf nodes into a min-priority queue.
4. Remove the two minimum-frequency nodes.
5. Create an internal parent whose frequency equals the sum of the two child frequencies.
6. Insert the parent into the queue.
7. Repeat until one root remains.

For a nonempty input with `k` distinct symbols, the construction should perform `k - 1` merge operations.

### Code generation

Traverse the tree recursively or iteratively.

- Append `0` when moving to the left child.
- Append `1` when moving to the right child.
- Record the path when reaching a leaf.

Ensure that no generated code is a prefix of another code.

### Encoding

Convert each input symbol to its Huffman code and concatenate the codes.

### Decoding

Traverse the Huffman tree according to each encoded bit and emit a symbol whenever a leaf is reached.

Validate invalid bit characters, incomplete codewords, and malformed data.

### Complexity analysis

Include a small educational panel with these complexities:

- Frequency counting: expected `O(n)` using a hash map.
- Building the priority queue: `O(k)` using heap construction, or `O(k log k)` when inserting leaves individually.
- Huffman tree merging: `O(k log k)`.
- Code generation: `O(k)` tree traversal, excluding the total length of generated code strings.
- Encoding: `O(n + B)` as an approximate bound when using efficient code construction and concatenation, where `n` is the number of input symbols and `B` is the number of output bits.
- Decoding: `O(B)` for a valid encoded bitstream, where `B` is the number of encoded bits.

Define `n`, `k`, and `B` in the interface or project documentation. Explain that Huffman coding is lossless and that compression effectiveness depends on symbol frequencies and metadata overhead.

## 6. Suggested project structure

Create a clean, understandable structure similar to:

    huffman_visualizer/
    ├── main.py
    ├── huffman.py
    ├── visualizer.py
    ├── test_huffman.py
    ├── README.md
    └── sample.txt

Responsibilities:

- `huffman.py`: node definitions, frequency counting, priority queue, tree construction, code generation, encoding, decoding, statistics, and binary file-format logic if implemented.
- `visualizer.py`: Canvas-based tree drawing and layout.
- `main.py`: Tkinter application, widgets, event handlers, file dialogs, and integration.
- `test_huffman.py`: unit tests for algorithm correctness and file round trips.
- `README.md`: setup, usage, DSA concepts, algorithms, complexity, limitations, and demonstration steps.
- `sample.txt`: a useful sample input containing repeated characters, spaces, punctuation, and a newline.

Keep the code simple enough for a second-year CSE student to understand and explain. Avoid unnecessary abstraction, excessive classes, and complicated frameworks.

If you choose a slightly different structure for reliability, document the reason.

## 7. User experience and error handling

The application should:

- Start without requiring a file to be selected.
- Include a useful sample input.
- Validate empty input and handle it gracefully.
- Show helpful error messages rather than crashing.
- Disable or reset dependent views when the input changes.
- Keep the tree, code table, encoding, and statistics synchronized.
- Avoid blocking the interface during ordinary use.
- Handle file dialog cancellation safely.
- Use meaningful names and comments for important algorithmic operations.
- Avoid printing debugging output during normal operation.

Use Tkinter's `messagebox` for errors and confirmations where appropriate.

Do not overengineer the interface or add unrelated features such as user accounts, databases, networking, or external APIs.

## 8. Testing requirements

Create automated tests for at least these cases:

1. Empty input.
2. One distinct character repeated many times.
3. Two distinct characters.
4. Multiple symbols with different frequencies.
5. Multiple symbols with equal frequencies.
6. Spaces, punctuation, and newline characters.
7. Unicode text, including non-ASCII characters.
8. Encoding followed by decoding returns the exact original text.
9. Every character receives a valid code.
10. The generated codes satisfy the prefix-free property.
11. Tree frequency equals the sum of all leaf frequencies.
12. The number of merge operations is `k - 1` for `k >= 1`.
13. Invalid encoded bitstreams are rejected appropriately.
14. If binary compression is implemented, compressed-file round trips preserve the exact original UTF-8 bytes.
15. If binary compression is implemented, truncated and malformed files are rejected without crashing.

Use deterministic test cases. Do not rely only on visual inspection.

Run the tests with:

    python -m unittest -v

Fix all discovered failures before declaring the project complete.

## 9. README and viva preparation

Write a clear `README.md` containing:

- Project title and purpose.
- Features.
- Python version and requirements.
- Installation and execution instructions.
- Example input and expected behavior.
- Explanation of Huffman Coding.
- Data structures used and why.
- Algorithm steps.
- Time and space complexity.
- The difference between encoded bits and a genuine compressed file.
- Limitations.
- A short demonstration script suitable for a 3–5 minute college presentation.

Also add a concise section with likely viva questions and answers, including:

1. What is Huffman Coding?
2. Why is it lossless?
3. Why is a min-priority queue used?
4. What is a prefix-free code?
5. Why does the algorithm combine the two lowest-frequency nodes?
6. What is the role of a binary tree?
7. Why can two correct Huffman trees have different codes when frequencies tie?
8. What are the time complexities?
9. Why can a compressed file be larger than the original?
10. How does decoding recover the original text?
11. What is the difference between frequency-table construction and code generation?
12. How does the application demonstrate DSA concepts from the syllabus?

## 10. Execution instructions and environment

First inspect the existing workspace and determine the operating system and available Python version.

Do not delete or overwrite unrelated existing project files.

Create the project in an appropriate directory. If a project already exists in the workspace, inspect it before making changes.

Prefer the Python standard library. Do not install packages unless genuinely necessary.

Run the application if the environment supports a graphical display. If the environment has no graphical display, run the unit tests and perform other available verification instead. Never claim to have visually tested the GUI if you could not run it.

Use a sensible startup command and document it in the README. Ensure that the program can be launched from the project directory without fragile absolute paths.

## 11. Definition of done

The project is complete when:

- The application launches successfully in a supported graphical environment.
- Users can enter text and build a real Huffman tree.
- The tree visualization and code table agree with the algorithm.
- Encoding and decoding produce the exact original input.
- The statistics are calculated correctly.
- The interface handles empty and single-character inputs.
- Automated tests pass.
- The README explains how to run and demonstrate the project.
- Any implemented binary file-compression feature passes round-trip and malformed-file tests.
- No controls are presented as working when their functionality has not been implemented.

## 12. How you should work

Work directly on the project files rather than responding with a long implementation plan.

Start by inspecting the environment. Then implement the smallest complete working version, run tests, fix problems, and improve the interface.

Do not stop after creating a design mockup or a partial code skeleton.

If a feature threatens the one-evening deadline, prioritize in this order:

1. Correct Huffman algorithm.
2. Encoding and decoding.
3. Visual tree and frequency/code table.
4. Correct compression statistics.
5. Tests and README.
6. Genuine binary file compression.
7. Step-by-step animation and visual polish.

At the end, report:

- Files created or modified.
- How to launch the application.
- Test command and actual test results.
- Implemented features.
- Any known limitations.
- A short sequence of actions I should perform to demonstrate the project to my instructor.

Begin implementation now.