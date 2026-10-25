"""Desktop application entry point for the Huffman Coding Visualizer."""
from __future__ import annotations
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from huffman import (build_tree, character_label, compress_to_file, decode, decompress_from_file,
                     encode, generate_codes, statistics, HuffmanError)
from visualizer import TreeCanvas

SAMPLE = "Huffman coding makes repeated symbols use fewer bits.\nHello, Huffman! こんにちは 🌟\n"
DISPLAY_LIMIT = 6000

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Huffman Coding Visualizer"); self.geometry("1280x820"); self.minsize(950, 650)
        self.configure(bg="#101820"); self.root = None; self.freq = {}; self.codes = {}; self.steps = []; self.step_index = 0; self.bits = ""; self.built_text = None
        self._style(); self._widgets(); self._set_status("Ready — enter text or use the sample.")

    def _style(self):
        style = ttk.Style(self); style.theme_use("clam")
        style.configure(".", background="#101820", foreground="#e8eef5", fieldbackground="#17212b")
        style.configure("TFrame", background="#101820"); style.configure("Card.TFrame", background="#17212b")
        style.configure("TLabel", background="#101820", foreground="#e8eef5")
        style.configure("Title.TLabel", font=("TkDefaultFont", 21, "bold"), foreground="#73daca")
        style.configure("Sub.TLabel", foreground="#aab7c4")
        style.configure("TButton", padding=(9, 5), background="#2f7d72", foreground="white")
        style.map("TButton", background=[("active", "#3b988a")])
        style.configure("Treeview", background="#17212b", fieldbackground="#17212b", foreground="#e8eef5", rowheight=24)
        style.configure("Treeview.Heading", background="#30445d", foreground="white", font=("TkDefaultFont", 9, "bold"))

    def _widgets(self):
        header = ttk.Frame(self, padding=(18, 14)); header.pack(fill="x")
        ttk.Label(header, text="Huffman Coding Visualizer", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Explore lossless compression through binary trees", style="Sub.TLabel").pack(anchor="w")
        self.status = ttk.Label(header, text=""); self.status.pack(anchor="e", side="right")
        outer = ttk.PanedWindow(self, orient="horizontal"); outer.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        left = ttk.Frame(outer, padding=10, style="Card.TFrame"); right = ttk.Frame(outer, padding=10, style="Card.TFrame"); outer.add(left, weight=1); outer.add(right, weight=2)
        ttk.Label(left, text="Input text", font=("TkDefaultFont", 12, "bold")).pack(anchor="w")
        self.input = tk.Text(left, height=12, wrap="word", bg="#0d141c", fg="#eef4f8", insertbackground="white", relief="flat", padx=8, pady=8)
        self.input.pack(fill="x", pady=6); self.input.bind("<<Modified>>", self._changed)
        controls = ttk.Frame(left); controls.pack(fill="x")
        for label, command in (("Open .txt", self.open_text), ("Clear", self.clear), ("Use Sample Text", self.sample), ("Build Huffman Tree", self.build)):
            ttk.Button(controls, text=label, command=command).pack(side="left", padx=(0, 5), pady=2)
        ttk.Label(left, text="Character frequencies and codes", font=("TkDefaultFont", 12, "bold")).pack(anchor="w", pady=(12, 3))
        tablebox = ttk.Frame(left); tablebox.pack(fill="both", expand=True)
        cols = ("character", "unicode", "frequency", "code", "length")
        self.table = ttk.Treeview(tablebox, columns=cols, show="headings", height=12)
        for col, heading, width in zip(cols, ("Character", "Unicode", "Frequency", "Huffman code", "Length"), (100, 86, 70, 115, 55)):
            self.table.heading(col, text=heading); self.table.column(col, width=width, anchor="center")
        scroll = ttk.Scrollbar(tablebox, command=self.table.yview); self.table.configure(yscrollcommand=scroll.set)
        self.table.pack(side="left", fill="both", expand=True); scroll.pack(side="right", fill="y")
        actions = ttk.Frame(left); actions.pack(fill="x", pady=(8,0))
        for label, command in (("Encode", self.do_encode), ("Decode", self.do_decode), ("Copy Encoded Bits", self.copy_bits), ("Compress and Save…", self.save_huf), ("Open and Decompress…", self.open_huf)):
            ttk.Button(actions, text=label, command=command).pack(side="left", padx=(0,4), pady=2)
        ttk.Label(left, text="Encoded bit sequence", font=("TkDefaultFont", 11, "bold")).pack(anchor="w", pady=(10,2)); self.encoded = self._output(left, 4)
        ttk.Label(left, text="Decoded output", font=("TkDefaultFont", 11, "bold")).pack(anchor="w", pady=(8,2)); self.decoded = self._output(left, 3)
        ttk.Label(right, text="Huffman binary tree", font=("TkDefaultFont", 12, "bold")).pack(anchor="w")
        self.tree = TreeCanvas(right); self.tree.pack(fill="both", expand=True, pady=(4,9))
        learn = ttk.LabelFrame(right, text=" Algorithm construction (min-priority queue) ", padding=8); learn.pack(fill="x")
        self.queue_label = ttk.Label(learn, text="Build a tree to inspect its priority queue.", wraplength=700); self.queue_label.pack(anchor="w")
        self.log = tk.Text(learn, height=6, state="disabled", bg="#0d141c", fg="#d6e3ee", relief="flat", wrap="word"); self.log.pack(fill="x", pady=5)
        row = ttk.Frame(learn); row.pack(anchor="w")
        for label, command in (("Next Step", self.next_step), ("Reset Steps", self.reset_steps), ("Build Complete Tree", self.complete_steps)):
            ttk.Button(row, text=label, command=command).pack(side="left", padx=(0,5))
        stats = ttk.LabelFrame(right, text=" Compression statistics — payload only ", padding=8); stats.pack(fill="x", pady=(9,0))
        self.stats = ttk.Label(stats, text="Build a tree to calculate UTF-8-aware statistics.", justify="left"); self.stats.pack(anchor="w")
        complexity = "Complexity: frequency counting O(n); merging O(k log k); code generation O(k); encoding O(n + B); decoding O(B).  n = input symbols, k = distinct symbols, B = encoded bits."
        ttk.Label(right, text=complexity, style="Sub.TLabel", wraplength=760, justify="left").pack(anchor="w", pady=(9,0))

    def _output(self, parent, height):
        box = tk.Text(parent, height=height, wrap="word", bg="#0d141c", fg="#d6e3ee", relief="flat", state="disabled", padx=7, pady=5); box.pack(fill="x"); return box
    def _set_output(self, widget, content):
        shown = content if len(content) <= DISPLAY_LIMIT else content[:DISPLAY_LIMIT] + f"\n… display truncated ({len(content):,} total characters; data is retained)."
        widget.configure(state="normal"); widget.delete("1.0", "end"); widget.insert("1.0", shown); widget.configure(state="disabled")
    def _set_status(self, message): self.status.configure(text=message)
    def _changed(self, event=None):
        if self.input.edit_modified():
            self.input.edit_modified(False)
            if self.root is not None and self.text() != self.built_text:
                self.reset_data()
            self._set_status(f"Input changed — {len(self.text()):,} characters. Build tree to refresh views.")
    def text(self): return self.input.get("1.0", "end-1c")
    def reset_data(self):
        self.root = None; self.freq = {}; self.codes = {}; self.steps = []; self.step_index = 0; self.bits = ""; self.built_text = None; self.tree.set_tree(None)
        for item in self.table.get_children(): self.table.delete(item)
        self._set_output(self.encoded, ""); self._set_output(self.decoded, ""); self.queue_label.configure(text="Build a tree to inspect its priority queue."); self._write_log(""); self.stats.configure(text="Build a tree to calculate UTF-8-aware statistics.")
    def clear(self): self.input.delete("1.0", "end"); self.reset_data(); self._set_status("Cleared.")
    def sample(self): self.input.delete("1.0", "end"); self.input.insert("1.0", SAMPLE); self.build()
    def open_text(self):
        path = filedialog.askopenfilename(title="Open UTF-8 text", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not path: return
        try: content = Path(path).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc: messagebox.showerror("Cannot open file", str(exc)); return
        self.input.delete("1.0", "end"); self.input.insert("1.0", content); self.build(); self._set_status(f"Loaded {Path(path).name} — {len(content):,} characters.")
    def build(self):
        content = self.text()
        self.reset_data()
        if not content: self._set_status("Enter one or more characters to build a tree."); messagebox.showinfo("No input", "Please enter text before building a Huffman tree."); return
        self.root, self.freq, self.steps = build_tree(content); self.codes = generate_codes(self.root); self.built_text = content; self.tree.set_tree(self.root)
        for symbol, count in sorted(self.freq.items(), key=lambda pair: (-pair[1], ord(pair[0]))):
            self.table.insert("", "end", values=(character_label(symbol), f"U+{ord(symbol):04X}", count, self.codes[symbol], len(self.codes[symbol])))
        s = statistics(content, self.codes, self.freq)
        self.stats.configure(text=(f"Input: {s['characters']:,} characters, {s['utf8_bytes']:,} UTF-8 bytes | Distinct: {s['distinct']}\nOriginal payload: {s['original_bits']:,} bits | Huffman payload: {s['encoded_bits']:,} bits\nAverage: {s['average']:.3f} bits/character | Ratio: {s['ratio']:.3f}:1 | Savings: {s['savings']:.2f}%\nEncoded payload is {'smaller' if s['smaller'] else 'not smaller'} than UTF-8 payload (file metadata is separate)."))
        self.reset_steps(); self._set_status(f"Tree built — {len(content):,} characters, {len(self.freq)} distinct symbols.")
    def _write_log(self, text): self.log.configure(state="normal"); self.log.delete("1.0", "end"); self.log.insert("1.0", text); self.log.configure(state="disabled")
    def reset_steps(self):
        self.step_index = 0
        if self.root: self.queue_label.configure(text="Start with leaves in the min-priority queue. Click Next Step to merge two minimum nodes.")
        self._write_log("")
    def next_step(self):
        if not self.root: return
        if self.step_index >= len(self.steps): self._write_log(self.log.get("1.0", "end-1c") + "\nComplete: one root remains."); return
        step = self.steps[self.step_index]; q = ", ".join(f"{node.frequency}" for node in step.queue_after)
        line = f"Step {self.step_index + 1}: remove {step.first.frequency} and {step.second.frequency}; combine into {step.parent.frequency}. Queue after: [{q}]\n"
        self._write_log(self.log.get("1.0", "end-1c") + line); self.queue_label.configure(text=f"After step {self.step_index + 1}: [{q}] (frequencies)"); self.step_index += 1
    def complete_steps(self):
        while self.step_index < len(self.steps): self.next_step()
    def do_encode(self):
        if not self.root: self.build()
        if not self.root: return
        self.bits = encode(self.text(), self.codes); self._set_output(self.encoded, self.bits); self._set_status(f"Encoded {len(self.bits):,} meaningful bits.")
    def do_decode(self):
        if not self.root: self.build()
        if not self.root: return
        try: self._set_output(self.decoded, decode(self.bits or encode(self.text(), self.codes), self.root)); self._set_status("Decoded successfully; it matches the tree traversal.")
        except HuffmanError as exc: messagebox.showerror("Decode error", str(exc))
    def copy_bits(self):
        if not self.bits: self.do_encode()
        if self.bits: self.clipboard_clear(); self.clipboard_append(self.bits); self._set_status("Encoded bits copied to clipboard.")
    def save_huf(self):
        if not self.text(): messagebox.showinfo("No input", "Enter text before saving a compressed file."); return
        path = filedialog.asksaveasfilename(title="Save compressed file", defaultextension=".huf", filetypes=[("Huffman files", "*.huf")])
        if not path: return
        try: size = compress_to_file(self.text(), path); self._set_status(f"Saved genuine compressed file: {size:,} bytes including metadata.")
        except OSError as exc: messagebox.showerror("Cannot save file", str(exc))
    def open_huf(self):
        path = filedialog.askopenfilename(title="Open compressed file", filetypes=[("Huffman files", "*.huf"), ("All files", "*.*")])
        if not path: return
        try: content = decompress_from_file(path)
        except (OSError, HuffmanError) as exc: messagebox.showerror("Cannot decompress file", str(exc)); return
        self.input.delete("1.0", "end"); self.input.insert("1.0", content); self.build(); self._set_status(f"Decompressed {Path(path).name} exactly — {len(content):,} characters.")

if __name__ == "__main__": App().mainloop()
