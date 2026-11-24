# Alef

    pip install -r requirements.txt
    streamlit run app.py

Everything is functional without an AI. Each project is saved in `data/projects/<id>.json` (index in `data/library.json`)
(created on first change; starts empty; Settings > Load demo data fills it with sample content).

## Architecture
- `services/library.py`: several projects, one active; the project card in the sidebar switches/creates/deletes them.
- `services/workspace.py`: the single store (tasks, chats, docs, changes) + derived stats. Pure Python.
- `services/assistant.py`: **the AI seam.** `LocalAssistant` is a command router today;
  implement `Assistant.reply()` using `ws.context_snapshot()` and return it from `get_assistant()`.
  Replies may carry structured `actions` (add_task, complete_task, move_task, set_note)
  that `Workspace.apply_action()` executes, so AI and UI share one code path.
- `components/`: reusable UI pieces (buttons, dialogs, task board, chat view, mind map, sidebar).
- `views/`: one screen each; `utils/actions.py`: all callbacks; `utils/router.py`: page ids.

## Chat commands (no AI)
`Add task: <title>` · `Complete: <title>` · `What should I cut?` · `Find the biggest unknown` · `Status`
