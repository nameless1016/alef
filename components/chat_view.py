"""Chat transcript, header and the docked composer."""
import streamlit as st

from components.entity_menu import entity_menu
from services.models import Chat
from services.workspace import Workspace
from utils import icons
from utils.actions import send_chat_input, send_chip
from utils.ui import esc, html

CHIPS = ["What should I cut?", "Add a task", "Find the biggest unknown"]


def message_html(role: str, text: str, initials: str) -> str:
    if role == "alef":
        return f"""
        <div class="a-msg a-msg-alef">
          <span class="a-avatar a-avatar-alef">{icons.logo(14)}</span>
          <div><div class="a-msg-label">ALEF</div><div class="a-bubble">{esc(text)}</div></div>
        </div>
        """
    return f"""
    <div class="a-msg a-msg-user">
      <div><div class="a-msg-label">YOU</div><div class="a-bubble">{esc(text)}</div></div>
      <span class="a-avatar a-avatar-user a-avatar-sm">{esc(initials)}</span>
    </div>
    """


def render_header(chat: Chat) -> None:
    with st.container(key="chat_head"):
        left, right = st.columns([30, 1], vertical_alignment="center")
        with left:
            html(f'<div class="a-chat-head"><b>{esc(chat.title)}</b><small>{esc(chat.subtitle)}</small></div>')
        with right:
            entity_menu("chat", chat.id, chat.title)


def render_messages(chat: Chat, user_initials: str) -> None:
    if chat.messages:
        body = "".join(message_html(m.role, m.text, user_initials) for m in chat.messages)
    else:
        body = '<p class="a-empty">Ask about scope, code, or what to do next.</p>'
    html(f'<div class="a-chat-body"><div class="a-date"><span>TODAY</span></div>{body}</div>')


def render_composer(ws: Workspace, chat: Chat) -> None:
    counts = ws.context_counts()
    with st.container(key="composer"):
        chips = st.columns([1.3, 0.85, 1.7, 7], gap="small")
        for i, (col, label) in enumerate(zip(chips[:3], CHIPS)):
            with col:
                with st.container(key=f"chip_{i}"):
                    st.button(label, key=f"chip_btn_{i}_{chat.id}", on_click=send_chip,
                              args=(chat.id, label))
        with chips[3]:
            html('<div class="a-kbd-row"><span class="a-kbd">↵</span> send '
                 '<span class="a-kbd">⇧↵</span> new line</div>')
        st.chat_input("Ask about scope, code, or what to do next…", key=f"chat_input_{chat.id}",
                      on_submit=send_chat_input, args=(chat.id,))
        html(f"""
        <div class="a-context">
          <span class="a-context-label"><i class="a-dot"></i>LOADED CONTEXT</span>
          <span>{counts['documents']} documents</span>
          <span>{counts['maps']} maps</span>
          <span>{counts['tasks']} tasks</span>
          <span class="a-context-lock">Locked to {esc(ws.project.name)}</span>
        </div>
        """)
