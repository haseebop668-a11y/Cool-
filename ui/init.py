"""Presentation tier entry point."""
from .state import StateManager
from .theme import inject_theme
from .accessibility import inject_a11y_core_styles

__all__ = ["StateManager", "inject_theme", "inject_a11y_core_styles"]
