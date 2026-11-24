"""Markdown heading hierarchy -> positioned mind-map nodes. Pure Python."""
import re

BRANCH_COLORS = ["#e8923a", "#a07cd6", "#b9c23c", "#4fb3bf", "#d9627a"]
ROOT_COLOR = "#5aa9dc"
CHAR_WIDTH = 6.3

VIEW_W = 835
VIEW_H = 560
ROOT_X = 132
LEVEL_DX = 164.5
LEAF_DY = 38.6


def parse_markdown(md: str):
    """Return a nested dict tree built from '#' headings (first heading = root)."""
    root, stack, counter = None, [], 0
    for line in md.splitlines():
        m = re.match(r"^(#{1,6})\s+(.*\S)\s*$", line)
        if not m:
            continue
        level, label = len(m.group(1)), m.group(2)
        node = {"id": f"n{counter}", "label": label, "children": []}
        counter += 1
        if root is None:
            root, stack, root_level = node, [(level, node)], level
            continue
        while stack and stack[-1][0] >= level:
            stack.pop()
        if not stack:
            stack = [(root_level, root)]   # another top-level heading: hang it off the root
        stack[-1][1]["children"].append(node)
        stack.append((level, node))
    return root


def layout(root):
    """Flatten the tree into a list of nodes with x/y/colour/parent."""
    if root is None:
        return []
    flat = []
    leaf_counter = [0]

    def place(node, depth, color, parent_id):
        node["depth"] = depth
        node["x"] = ROOT_X + depth * LEVEL_DX
        node["color"] = color
        node["parent"] = parent_id
        node["text_w"] = len(node["label"]) * CHAR_WIDTH + 8
        if not node["children"]:
            node["y"] = leaf_counter[0] * LEAF_DY
            leaf_counter[0] += 1
        else:
            for i, child in enumerate(node["children"]):
                child_color = (BRANCH_COLORS[i % len(BRANCH_COLORS)]
                               if depth == 0 else color)
                place(child, depth + 1, child_color, node["id"])
            ys = [c["y"] for c in node["children"]]
            node["y"] = sum(ys) / len(ys)
        flat.append(node)

    place(root, 0, ROOT_COLOR, None)
    root["color"] = ROOT_COLOR
    span = (leaf_counter[0] - 1) * LEAF_DY
    offset = (VIEW_H - span) / 2
    for n in flat:
        n["y"] += offset
    flat.sort(key=lambda n: int(n["id"][1:]))
    return flat
