"""Accessibility (A11y) Management Layer."""
import hashlib
import html
import logging
import urllib.parse
from enum import Enum
from typing import Literal
import streamlit as st

logger = logging.getLogger(__name__)

class AriaRole(str, Enum):
    ALERT = "alert"
    STATUS = "status"
    MAIN = "main"

class AriaLive(str, Enum):
    POLITE = "polite"
    ASSERTIVE = "assertive"

_A11Y_CSS = """
<style>
.sr-only {
    position: absolute !important; width: 1px !important; height: 1px !important;
    padding: 0 !important; margin: -1px !important; overflow: hidden !important;
    clip: rect(0, 0, 0, 0) !important; white-space: nowrap !important; border: 0 !important;
}
.skip-link {
    position: absolute; top: -100px; left: 16px; background: #D4AF37;
    color: #0B0C10; padding: 12px 24px; z-index: 99999;
    text-decoration: none; font-weight: 600; border-radius: 8px;
}
.skip-link:focus { top: 16px; outline: 3px solid #66FCF1; outline-offset: 2px; }
:focus-visible { outline: 2px solid #66FCF1 !important; outline-offset: 2px !important; }
</style>
"""

def inject_a11y_core_styles() -> None:
    st.markdown(_A11Y_CSS, unsafe_allow_html=True)

def inject_skip_link(target_anchor: str = "main-content", label: str = "Skip to main content") -> None:
    safe_anchor = urllib.parse.quote(target_anchor)
    safe_label = html.escape(label)
    st.markdown(f'<a href="#{safe_anchor}" class="skip-link">{safe_label}</a>', unsafe_allow_html=True)

def announce_to_screen_reader(message: str, assertiveness: Literal["polite", "assertive"] = AriaLive.POLITE.value) -> None:
    safe_message = html.escape(message)
    stable_hash = hashlib.md5(f"{assertiveness}:{message}".encode('utf-8')).hexdigest()[:8]
    html_str = f'<div id="aria-live-{stable_hash}" class="sr-only" aria-live="{assertiveness}" aria-atomic="true">{safe_message}</div>'
    st.markdown(html_str, unsafe_allow_html=True)
  
