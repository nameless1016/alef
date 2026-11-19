"""Task board + focus list markup."""
from services.data_service import TASK_COLUMNS, tasks_in
from utils import icons


def _tags(tags: list) -> str:
    return "".join(f'<span class="a-tag">#{t}</span>' for t in tags)


def task_card(task: dict) -> str:
    done_cls = " is-done" if task["done"] else ""
    check = icons.check(10) if task["done"] else ""
    return f"""
    <details class="a-task{done_cls}">
      <summary>
        <span class="a-check">{check}</span>
        <span class="a-task-main"><b>{task['title']}</b><small>{task['meta']}</small></span>
        <span class="a-task-chev">{icons.chevron_right(12)}</span>
      </summary>
      <div class="a-task-body">
        <p>{task['description']}</p>
        <div class="a-task-tags">{_tags(task['tags'])}</div>
        <div class="a-task-foot">
          <span class="a-task-action">{task['action']}</span>
          <span class="a-prio a-prio-{task['priority']}">{task['priority']}</span>
        </div>
      </div>
    </details>
    """


def board_html() -> str:
    cols = []
    for key, label in TASK_COLUMNS:
        items = tasks_in(key)
        cards = "".join(task_card(t) for t in items)
        cols.append(f"""
        <section class="a-col">
          <header><span>{label.upper()}</span><em>{len(items)}</em></header>
          <div class="a-col-body">{cards}</div>
        </section>
        """)
    return f'<div class="a-board">{"".join(cols)}</div>'


def focus_row(index: int, task: dict) -> str:
    tags = task["tags"]
    tag_html = (f'<span class="a-tag a-tag-hot">#{tags[0]}</span>'
                + "".join(f'<span class="a-tag">#{t}</span>' for t in tags[1:]))
    meta = task["meta"].split(" · ")
    return f"""
    <div class="a-focus-row">
      <span class="a-focus-num">{index:02d}</span>
      <div class="a-focus-main">
        <b>{task['title']}</b>
        <p>{task['description']}</p>
        <div class="a-focus-meta">{tag_html}
          <span class="a-meta">{icons.clock(12)}{meta[0]}</span>
          <span class="a-meta">{icons.calendar(12)}{meta[1]}</span>
        </div>
      </div>
      <span class="a-prio a-prio-{task['priority']}">{task['priority']}</span>
    </div>
    """
