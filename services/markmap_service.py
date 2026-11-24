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


MAX_LEVEL = 4


def parse_markdown(md: str):
    """Return a nested dict tree built from '#' headings and nested bullets (max 4 levels)."""
    root, stack, counter = None, [], 0
    last_heading_level = 1
    root_level = 1
    for line in md.splitlines():
        hm = re.match(r"^(#{1,6})\s+(.*\S)\s*$", line)
        bm = None if hm else re.match(r"^(\s*)[-*+]\s+(.*\S)\s*$", line)
        if not hm and not bm:
            continue
        if hm:
            level = min(len(hm.group(1)), MAX_LEVEL)
            label = hm.group(2)
            last_heading_level = level
        else:
            indent = len(bm.group(1).expandtabs(2))
            bullet_depth = indent // 2
            level = min(last_heading_level + 1 + bullet_depth, MAX_LEVEL)
            label = bm.group(2)
        node = {"id": f"n{counter}", "label": label, "children": []}
        counter += 1
        if root is None:
            root, stack, root_level = node, [(level, node)], level
            continue
        while stack and stack[-1][0] >= level:
            stack.pop()
        if not stack:
            stack = [(root_level, root)]   # another top-level heading: hang it off the root
        # Cap visual tree depth at MAX_LEVEL - 1 (root is depth 0)
        if len(stack) >= MAX_LEVEL:
            stack = stack[: MAX_LEVEL - 1]
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
