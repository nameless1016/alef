"""Static mock data for the Alef UI.

Pure Python: no Streamlit imports. Swap these constants for real
DB / API calls later without touching the views.
"""

PROJECT = {
    "initials": "GP",
    "name": "Glasshouse Protocol",
    "engine": "Godot 4.3",
    "tagline": "Narrative stealth puzzle",
    "description": "A stealth puzzle game about being observed",
    "target": "Jun 30",
    "progress": 38,
    "scope_load": 68,
    "budget_used": 68,
    "branch": "scope/vertical-slice",
    "status": "Project active",
    "version": "Alef 0.8",
    "format": "Markdown",
    "synced": "Synced 12m ago",
    "user_initials": "JD",
    "user_name": "Mamdani",
    "today_label": "Thursday · April 16",
    "goal": "Prove the surveillance-loop vertical slice before expanding the second district.",
}

MILESTONE = {
    "month": "Apr",
    "day": "28",
    "title": "Evidence readability test",
    "meta": "12 days left · 3 critical tasks",
}

SCOPE_HEALTH = {
    "label": "Needs attention",
    "text": "One blocked item is deliberately parked. Keep it there until the slice gate passes.",
}

SCOPE_NOTE = "Watch the second district. It is outside the current slice."

ALEF_NOTE = (
    "Do not prototype the second district this week. The evidence HUD and "
    "camera rules are the same risk wearing two different coats."
)

NAV_GROUPS = [
    {
        "key": "chat",
        "label": "Chat",
        "action": "+",
        "items": [
            ("chat:vertical", "Vertical slice"),
            ("chat:performance", "Performance"),
            ("chat:scope", "Scope review"),
        ],
    },
    {
        "key": "doc",
        "label": "Document",
        "items": [
            ("doc:gdd", "Game Design Document"),
            ("doc:brief", "Project Brief"),
        ],
    },
    {
        "key": "map",
        "label": "Map",
        "items": [
            ("map:overview", "Project Overview"),
            ("map:surveillance", "Surveillance System"),
        ],
    },
]

# ---------------------------------------------------------------- tasks
TASKS = [
    {
        "id": "t1", "column": "current", "title": "Define the slice acceptance test",
        "meta": "30m · Unscheduled", "priority": "medium", "tags": ["from-chat"],
        "description": "Created directly from the Alef conversation.", "done": False,
        "action": "Mark complete",
    },
    {
        "id": "t2", "column": "current", "title": "Lock camera detection rules",
        "meta": "2h · Apr 18", "priority": "high", "tags": ["gameplay", "vertical-slice"],
        "description": "Write acceptance criteria before tuning values.", "done": False,
        "action": "Mark complete",
    },
    {
        "id": "t3", "column": "progress", "title": "Build suspicion ledger HUD",
        "meta": "5h · Apr 21", "priority": "high", "tags": ["ui", "systems"],
        "description": "Show cause and decay; no animation polish yet.", "done": False,
        "action": "Mark complete",
    },
    {
        "id": "t4", "column": "backlog", "title": "Greybox archive escape route",
        "meta": "1d · Apr 24", "priority": "medium", "tags": ["level-design"],
        "description": "One route with two valid solutions.", "done": False,
        "action": "Mark complete",
    },
    {
        "id": "t5", "column": "backlog", "title": "Playtest evidence readability",
        "meta": "3h · Apr 28", "priority": "high", "tags": ["research"],
        "description": "Test with three players unfamiliar with the rules.", "done": False,
        "action": "Mark complete",
    },
    {
        "id": "t6", "column": "blocked", "title": "Prototype second district",
        "meta": "3d · Unscheduled", "priority": "low", "tags": ["scope-cut"],
        "description": "Do not start until the slice gate passes.", "done": False,
        "action": "Mark complete",
    },
    {
        "id": "t7", "column": "done", "title": "Camera cone shader benchmark",
        "meta": "4h · Unscheduled", "priority": "medium", "tags": ["performance"],
        "description": "Target hardware remains within budget.", "done": True,
        "action": "Move to current",
    },
]

TASK_COLUMNS = [
    ("current", "Current"),
    ("progress", "In progress"),
    ("backlog", "Backlog"),
    ("blocked", "Blocked"),
    ("done", "Done"),
]

SPRINT = {"label": "Sprint 03", "days_left": 12}

FOCUS_TASK_IDS = ["t2", "t3"]

# -------------------------------------------------------------- changes
CHANGES = [
    {"title": "Tasks changed",
     "text": "Current priorities or completion state moved since the last context sync.",
     "when": "Now", "state": "new"},
    {"title": "Project Brief updated",
     "text": "Vertical slice language is clearer and the scope boundary is explicit.",
     "when": "18m", "state": "recent"},
    {"title": "Map synced",
     "text": "Surveillance feedback nodes were added to Alef's working context.",
     "when": "Yesterday", "state": "synced"},
]

# ---------------------------------------------------------------- chats
CHATS = {
    "chat:vertical": {
        "title": "Vertical slice",
        "subtitle": "Planning · Glasshouse Protocol",
        "messages": [
            ("alef", "The slice is still viable. Lock detection rules before adding content; "
                     "everything downstream depends on players reading surveillance correctly."),
            ("user", "Add task: Define the slice acceptance test"),
            ("alef", "Added directly to Current. I kept it small enough to finish before the slice review."),
        ],
    },
    "chat:performance": {
        "title": "Performance",
        "subtitle": "Planning · Glasshouse Protocol",
        "messages": [
            ("alef", "The camera cone shader benchmark is done and sits within budget on target hardware. "
                     "Re-test once the suspicion ledger HUD lands."),
        ],
    },
    "chat:scope": {
        "title": "Scope review",
        "subtitle": "Planning · Glasshouse Protocol",
        "messages": [
            ("alef", "Scope load is at 68%. The second district is the only item outside the slice; "
                     "keep it blocked until the gate passes."),
        ],
    },
}

CHAT_SUGGESTIONS = ["What should I cut?", "Add a task", "Find the biggest unknown"]
CHAT_CONTEXT = {"documents": 2, "maps": 2, "tasks": 7}

# ------------------------------------------------------------ documents
DOCUMENTS = {
    "doc:gdd": {
        "title": "Game Design Document",
        "subtitle": "Editable design source of truth for the full project.",
        "eyebrow": "Document / long design doc",
        "lines": 12,
        "blocks": [
            ("h1", "Design pillars"),
            ("quote", ["1. Every camera is predictable.",
                       "2. Every intervention leaves a trace.",
                       "3. Narrative choices alter systemic pressure."]),
            ("h1", "Scope boundary"),
            ("p", "Ship one district with four authored missions. Defer procedural patrol "
                  "generation, companion AI, and the second district until the vertical slice "
                  "holds 30 FPS on target hardware and tests above 70% comprehension."),
        ],
    },
    "doc:brief": {
        "title": "Project Brief",
        "subtitle": "Short summary of what the project is and what it is not.",
        "eyebrow": "Document / brief",
        "lines": 12,
        "blocks": [
            ("h1", "Glasshouse Protocol"),
            ("p", "A narrative stealth puzzle about being observed. The player studies "
                  "surveillance, alters evidence, and escapes without leaving a readable trace."),
            ("h1", "Vertical slice"),
            ("p", "One archive building, one escape route with two valid solutions, and a "
                  "working suspicion ledger. The slice gate is 30 FPS on target hardware and "
                  "70% comprehension in testing."),
        ],
    },
}

# ----------------------------------------------------------------- maps
MAPS = {
    "map:overview": {
        "title": "Project Overview",
        "subtitle": "Explore the project structure directly from its Markdown hierarchy.",
        "eyebrow": "Markmap / overview",
        "filename": "project-overview.md",
        "markdown": """# Glasshouse Protocol
## Player loop
### Observe
### Plan route
### Alter evidence
### Escape
## Game systems
### Surveillance
#### Camera cones
#### Suspicion ledger
### Stealth
#### Cover
#### Noise
### Narrative
#### Memory choices
## Production
### Vertical slice
### User testing
### Performance budget""",
    },
    "map:surveillance": {
        "title": "Surveillance System",
        "subtitle": "Cameras, suspicion, and the feedback players read.",
        "eyebrow": "Markmap / surveillance",
        "filename": "surveillance-system.md",
        "markdown": """# Surveillance System
## Camera cones
### Field of view
### Range falloff
### Blind spots
## Suspicion ledger
### Cause
### Decay
### Threshold states
## Evidence feedback
### HUD readout
### Audio cue
### Alert state""",
    },
}

# ------------------------------------------------------------- settings
SETTINGS_FIELDS = {
    "engines": ["Godot 4.3", "Godot 4.2", "Unity 6", "Unreal 5.4"],
}


def open_task_count() -> int:
    return sum(1 for t in TASKS if not t["done"])


def change_count() -> int:
    return len(CHANGES)


def task_by_id(task_id: str) -> dict:
    return next(t for t in TASKS if t["id"] == task_id)


def tasks_in(column: str) -> list:
    return [t for t in TASKS if t["column"] == column]
