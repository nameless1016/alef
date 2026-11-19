"""Chat bubbles and the fixed composer."""
import streamlit as st

from services.data_service import CHAT_CONTEXT, CHAT_SUGGESTIONS, PROJECT
from utils import icons
from utils.state import submit_chat, use_suggestion
from utils.ui import html


def message_html(role: str, text: str) -> str:
    if role == "alef":
        return f"""
        <div class="a-msg a-msg-alef">
          <span class="a-avatar a-avatar-alef">{icons.logo(14)}</span>
          <div><div class="a-msg-label">ALEF</div><div class="a-bubble">{text}</div></div>
        </div>
        """
    return f"""
    <div class="a-msg a-msg-user">
      <div><div class="a-msg-label">YOU</div><div class="a-bubble">{text}</div></div>
      <span class="a-avatar a-avatar-user a-avatar-sm">{PROJECT['user_initials']}</span>
    </div>
    """


def render_composer(chat_key: str) -> None:
    with st.container(key="composer"):
        chips = st.columns([1.25, 0.8, 1.6, 8], gap="small")
        for col, label, i in zip(chips[:3], CHAT_SUGGESTIONS, range(3)):
            with col:
                with st.container(key=f"chip_{i}"):
                    st.button(label, key=f"chip_btn_{i}",
                              on_click=use_suggestion, args=(chat_key, label))
        st.text_area("Message", key="chat_input", height=107,
                     label_visibility="collapsed",
                     placeholder="Ask about scope, code, or what to do next…")
        with st.container(key="composer_hint"):
            html('<span class="a-kbd">↵</span> send <span class="a-kbd">⇧↵</span> new line')
        with st.container(key="send_wrap"):
            st.button("", key="send_btn", icon=":material/send:",
                      on_click=submit_chat, args=(chat_key,))
        html(f"""
        <div class="a-context">
          <span class="a-context-label"><i class="a-dot"></i>LOADED CONTEXT</span>
          <span>{CHAT_CONTEXT['documents']} documents</span>
          <span>{CHAT_CONTEXT['maps']} maps</span>
          <span>{CHAT_CONTEXT['tasks']} tasks</span>
          <span class="a-context-lock">Locked to {PROJECT['name']}</span>
        </div>
        """)
