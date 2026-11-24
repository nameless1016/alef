from services.markmap_service import layout, parse_markdown


def test_parse_markdown_supports_headings_and_nested_bullets_capped_at_depth_4():
    md = """# Root Game
## Gameplay Systems
- Core Loop
  - Observe
    - Too Deep Node
## Production
* Vertical Slice
"""
    root = parse_markdown(md)
    nodes = layout(root)
    labels = {n["label"]: n["depth"] for n in nodes}
    assert labels["Root Game"] == 0
    assert labels["Gameplay Systems"] == 1
    assert labels["Core Loop"] == 2
    assert labels["Observe"] == 3
    assert labels["Too Deep Node"] <= 3
    assert labels["Vertical Slice"] == 2
