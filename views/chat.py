"""Chat screens."""
import streamlit as st

from components.chat import message_html, render_composer
from services.data_service import CHATS
from utils.ui import html


def render(chat_key: str) -> None:
    chat = CHATS[chat_key]
    messages = list(chat["messages"]) + st.session_state["chat_extra"].get(chat_key, [])
    body = "".join(message_html(role, text) for role, text in messages)
    html(f"""
    <div class="a-chat-head">
      <div><b>{chat['title']}</b><small>{chat['subtitle']}</small></div>
      <span class="a-chat-more">···</span>
    </div>
    <div class="a-chat-body">
      <div class="a-date"><span>TODAY</span></div>
      {body}
    </div>
    """)
    render_composer(chat_key)
