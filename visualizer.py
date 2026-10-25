"""Scrollable Tkinter Canvas rendering for a Huffman tree."""
from __future__ import annotations
import tkinter as tk
from tkinter import ttk
from huffman import Node, character_label


class TreeCanvas(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.canvas = tk.Canvas(self, bg="#17212b", highlightthickness=0)
        x = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        y = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=x.set, yscrollcommand=y.set)
        self.canvas.grid(row=0, column=0, sticky="nsew"); y.grid(row=0, column=1, sticky="ns"); x.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1); self.columnconfigure(0, weight=1)
        self.root: Node | None = None
        self.canvas.bind("<Configure>", lambda event: self.draw())

    def set_tree(self, root: Node | None) -> None:
        self.root = root; self.draw()

    def draw(self) -> None:
        c = self.canvas; c.delete("all")
        if not self.root:
            c.create_text(320, 160, text="Build a Huffman tree to see it here.", fill="#b9c7d5", font=("TkDefaultFont", 13))
            c.configure(scrollregion=(0, 0, 650, 320)); return
        positions: dict[int, tuple[int, int]] = {}; leaf_index = 0
        def layout(node: Node, depth: int) -> float:
            nonlocal leaf_index
            if node.is_leaf:
                x = 55 + leaf_index * 112; leaf_index += 1
            else:
                values = [layout(child, depth + 1) for child in (node.left, node.right) if child]
                x = sum(values) / len(values)
            positions[id(node)] = (int(x), 55 + depth * 95); return x
        layout(self.root, 0)
        def edges(node: Node) -> None:
            x, y = positions[id(node)]
            for child, bit in ((node.left, "0"), (node.right, "1")):
                if child:
                    cx, cy = positions[id(child)]
                    c.create_line(x, y + 22, cx, cy - 22, fill="#78909c", width=2)
                    c.create_text((x + cx) / 2, (y + cy) / 2 - 9, text=bit, fill="#f6c177", font=("TkDefaultFont", 10, "bold"))
                    edges(child)
        edges(self.root)
        for node_id, (x, y) in positions.items():
            node = next(n for n in self._walk(self.root) if id(n) == node_id)
            leaf = node.is_leaf; color = "#2f7d72" if leaf else "#465b78"
            c.create_oval(x-32, y-22, x+32, y+22, fill=color, outline="#b9c7d5", width=1)
            label = f"{character_label(node.symbol)}\n{node.frequency}" if leaf else str(node.frequency)
            c.create_text(x, y, text=label, fill="#ffffff", font=("TkDefaultFont", 9, "bold"))
        width = max(650, leaf_index * 112 + 70); depth = max(y for x, y in positions.values())
        c.configure(scrollregion=(0, 0, width, depth + 70))

    @staticmethod
    def _walk(node: Node):
        yield node
        if node.left: yield from TreeCanvas._walk(node.left)
        if node.right: yield from TreeCanvas._walk(node.right)
