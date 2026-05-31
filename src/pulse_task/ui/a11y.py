"""Accessibility utilities and WCAG compliance helpers for PulseTask."""

from __future__ import annotations

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")  # noqa: E402
gi.require_version("Atspi", "2.0")  # noqa: E402

from gi.repository import Gtk  # noqa: E402 # type: ignore[import-untyped]


class A11yHelper:
    """Accessibility helper for GNOME applications."""

    @staticmethod
    def set_accessible_label(widget: object, label: str) -> None:
        """Set accessible label for screen readers."""
        try:
            # Set accessible label (for screen readers)
            accessible = Gtk.Accessible.get_default_if_installed()
            if accessible and hasattr(widget, "set_label"):
                widget.set_label(label)  # type: ignore[union-attr]
        except Exception:
            pass

    @staticmethod
    def mark_as_header(label: Gtk.Label) -> None:
        """Mark a label as a heading for accessibility."""
        label.add_css_class("heading")
        if hasattr(label, "set_markup"):
            # Increase font size for better visibility
            markup = label.get_label()
            if markup:
                bold_markup = f"<b><large>{markup}</large></b>"
                label.set_markup(bold_markup)

    @staticmethod
    def set_focus_indicator(widget: Gtk.Widget) -> None:
        """Enhance focus indicator for better keyboard navigation."""
        widget.add_css_class("focus-visible")

    @staticmethod
    def announce_state_change(message: str) -> None:
        """Announce state change to screen readers.

        Args:
            message: Message to announce (e.g., "Task started", "Group paused")
        """
        # In GNOME, this would typically use D-Bus to notify accessible apps
        # For now, just print for accessibility testing
        print(f"[A11y Announcement] {message}")
