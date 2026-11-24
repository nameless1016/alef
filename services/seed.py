"""Default demo workspace (matches the design reference). Dates are relative to today."""
import time
from datetime import date, timedelta

from .models import Change, Chat, Document, Message, Project, Task
from .workspace import Workspace

GDD = """# Design pillars

> 1. Every camera is predictable.
> 2. Every intervention leaves a trace.
> 3. Narrative choices alter systemic pressure.

# Scope boundary

Ship one district with four authored missions. Defer procedural patrol generation, companion AI, and the second district until the vertical slice holds 30 FPS on target hardware and tests above 70% comprehension."""

BRIEF = """# Glasshouse Protocol

A narrative stealth puzzle about being observed. The player studies surveillance, alters evidence, and escapes without leaving a readable trace.

# Vertical slice

One archive building, one escape route with two valid solutions, and a working suspicion ledger. The slice gate is 30 FPS on target hardware and 70% comprehension in testing."""

OVERVIEW = """# Glasshouse Protocol
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
### Performance budget"""

SURVEILLANCE = """# Surveillance System
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
### Alert state"""

NOTE = ("Do not prototype the second district this week. The evidence HUD and "
        "camera rules are the same risk wearing two different coats.")


def _iso(offset_days: int) -> str:
    return (date.today() + timedelta(days=offset_days)).isoformat()


def demo_workspace() -> Workspace:
    now = time.time()
    project = Project(
        name="Glasshouse Protocol", tagline="Narrative stealth puzzle",
        description="A stealth puzzle game about being observed", engine="Godot 4.3",
        goal="Prove the surveillance-loop vertical slice before expanding the second district.",
        user_name="Mamdani", branch="scope/vertical-slice", target=_iso(75),
        milestone_title="Evidence readability test", milestone_date=_iso(12),
        scope_load=68, budget_used=68, baseline=13, initialized=True,
    )
    tasks = [
        Task("Define the slice acceptance test", "current", "medium", "30m", None, ["from-chat"],
             "Created directly from the Alef conversation.", id="t1"),
        Task("Lock camera detection rules", "current", "high", "2h", _iso(2),
             ["gameplay", "vertical-slice"], "Write acceptance criteria before tuning values.", id="t2"),
        Task("Build suspicion ledger HUD", "progress", "high", "5h", _iso(5), ["ui", "systems"],
             "Show cause and decay; no animation polish yet.", id="t3"),
        Task("Greybox archive escape route", "backlog", "medium", "1d", _iso(8), ["level-design"],
             "One route with two valid solutions.", id="t4"),
        Task("Playtest evidence readability", "backlog", "high", "3h", _iso(12), ["research"],
             "Test with three players unfamiliar with the rules.", id="t5"),
        Task("Prototype second district", "blocked", "low", "3d", None, ["scope-cut"],
             "Do not start until the slice gate passes.", id="t6"),
        Task("Camera cone shader benchmark", "done", "medium", "4h", None, ["performance"],
             "Target hardware remains within budget.", id="t7"),
    ]
    chats = [
        Chat("Vertical slice", "Planning · Glasshouse Protocol", [
            Message("alef", "The slice is still viable. Lock detection rules before adding content; "
                            "everything downstream depends on players reading surveillance correctly.")],
             id="vertical"),
        Chat("Performance", "Planning · Glasshouse Protocol", [
            Message("alef", "The camera cone shader benchmark is done and sits within budget on target "
                            "hardware. Re-test once the suspicion ledger HUD lands.")], id="performance"),
        Chat("Scope review", "Planning · Glasshouse Protocol", [
            Message("alef", "Scope load is at 68%. The second district is the only item outside the "
                            "slice; keep it blocked until the gate passes.")], id="scope"),
    ]
    docs = [
        Document("Game Design Document", "doc", "Editable design source of truth for the full project.", GDD, role="long", id="gdd"),
        Document("Project Brief", "doc", "Short summary of what the project is and what it is not.", BRIEF, role="short", id="brief"),
        Document("Project Overview", "map", "Explore the project structure directly from its Markdown hierarchy.", OVERVIEW, id="overview"),
        Document("Surveillance System", "map", "Cameras, suspicion, and the feedback players read.", SURVEILLANCE, id="surveillance"),
    ]
    changes = [
        Change("tasks", "Tasks changed",
               "Current priorities or completion state moved since the last context sync.", now, False),
        Change("doc:brief", "Project Brief updated",
               "Vertical slice language is clearer and the scope boundary is explicit.", now - 18 * 60, False),
        Change("map:surveillance", "Map synced",
               "Surveillance feedback nodes were added to Alef's working context.", now - 86400, True),
    ]
    return Workspace(project, tasks, chats, docs, changes, NOTE, last_sync=now - 12 * 60)


def default_workspace() -> Workspace:
    """A clean slate: project identity plus one starter setup chat, uninitialized."""
    project = Project(
        name="Glasshouse Protocol", tagline="Narrative stealth puzzle", engine="Godot 4.3",
        user_name="Mamdani", branch="scope/vertical-slice",
        scope_load=0, budget_used=0, baseline=0, initialized=False,
    )
    setup_chat = Chat("Project setup", f"Setup · {project.name}")
    return Workspace(project, chats=[setup_chat], last_sync=time.time())
