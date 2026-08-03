"""Statistics view window for PulseTask.

Displays group execution statistics, charts, and historical data.
"""
# mypy: ignore-errors

from __future__ import annotations

import gi  # noqa: E402

gi.require_version("Gtk", "4.0")  # noqa: E402
gi.require_version("Adw", "1")  # noqa: E402

from gi.repository import Adw, Gtk  # noqa: E402 # type: ignore[import-untyped]

from pulse_task.core.stats import GroupStatsService  # noqa: E402


class StatsWindow(Gtk.ApplicationWindow):
    """Statistics window showing execution metrics."""

    def __init__(
        self,
        app: Adw.Application,
        stats_service: GroupStatsService,
    ) -> None:
        """Initialize stats window.

        Args:
            app: Adwaita application
            stats_service: GroupStatsService for metrics
        """
        super().__init__(application=app)
        self.stats_service = stats_service

        # Window setup
        self.set_title("PulseTask Statistics")
        self.set_default_size(800, 600)
        self.add_css_class("stats-window")

        # Main container
        header_bar = Adw.HeaderBar()

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        vbox.append(header_bar)

        # Scrollable content
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        content.set_margin_top(24)
        content.set_margin_bottom(24)
        content.set_margin_start(24)
        content.set_margin_end(24)

        # Title
        title = Gtk.Label(label="Execution Statistics")
        title.add_css_class("title-1")
        content.append(title)

        # Get current period stats
        period_7 = self.stats_service.get_period_stats(7)

        # 7-day summary section
        summary_box = self._build_summary_box(period_7)
        content.append(summary_box)

        # Heatmap section
        heatmap_box = self._build_heatmap_box()
        content.append(heatmap_box)

        # Export section
        export_box = self._build_export_box()
        content.append(export_box)

        scroll.set_child(content)
        vbox.append(scroll)

        self.set_child(vbox)

    def _build_summary_box(self, period_stats):  # type: ignore[no-untyped-def]
        """Build summary statistics box."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.add_css_class("stats-section")

        heading = Gtk.Label(label="Last 7 Days")
        heading.add_css_class("heading-3")
        box.append(heading)

        # Grid of stats
        grid = Gtk.Grid()
        grid.set_column_spacing(32)
        grid.set_row_spacing(12)

        rows = [
            ("Groups Executed", str(period_stats.groups_executed)),
            ("Tasks Completed", str(period_stats.tasks_completed)),
            (
                "Focus Time",
                f"{period_stats.total_focus_time_seconds // 3600}h "
                f"{(period_stats.total_focus_time_seconds % 3600) // 60}m",
            ),
            (
                "Avg Group Duration",
                f"{period_stats.avg_group_duration_seconds // 60}m",
            ),
            ("Completion Rate", f"{period_stats.completion_rate:.1%}"),
            (
                "Interruption Rate",
                f"{period_stats.interruption_rate:.2f} avg/group",
            ),
        ]

        for i, (label, value) in enumerate(rows):
            label_widget = Gtk.Label(label=label)
            label_widget.add_css_class("stats-label")
            grid.attach(label_widget, 0, i, 1, 1)

            value_widget = Gtk.Label(label=value)
            value_widget.add_css_class("stats-value")
            grid.attach(value_widget, 1, i, 1, 1)

        box.append(grid)
        return box

    def _build_heatmap_box(self) -> Gtk.Box:
        """Build weekly activity heatmap."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.add_css_class("stats-section")

        heading = Gtk.Label(label="Weekly Activity Heatmap")
        heading.add_css_class("heading-3")
        box.append(heading)

        heatmap = self.stats_service.get_focus_heatmap(days=7)

        heatmap_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        heatmap_box.set_halign(Gtk.Align.START)

        for day, intensity in heatmap.items():
            day_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

            # Color block (4 intensity levels)
            intensity_level = min(4, int(intensity * 4))

            color_block = Gtk.Box()
            color_block.set_size_request(32, 32)
            color_block.add_css_class("heatmap-block")
            color_block.set_css_classes([f"heatmap-{intensity_level}", "heatmap-block"])
            day_box.append(color_block)

            day_label = Gtk.Label(label=day[:3])
            day_label.add_css_class("stats-small")
            day_box.append(day_label)

            heatmap_box.append(day_box)

        box.append(heatmap_box)
        return box

    def _build_export_box(self) -> Gtk.Box:
        """Build export controls."""
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.add_css_class("stats-section")

        heading = Gtk.Label(label="Export Data")
        heading.add_css_class("heading-3")
        box.append(heading)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        csv_btn = Gtk.Button(label="Download CSV")
        csv_btn.connect("clicked", self._on_csv_export)
        button_box.append(csv_btn)

        json_btn = Gtk.Button(label="Download JSON")
        json_btn.connect("clicked", self._on_json_export)
        button_box.append(json_btn)

        box.append(button_box)
        return box

    def _on_csv_export(self, button: Gtk.Button) -> None:
        """Handle CSV export."""
        _ = button  # Unused
        csv_data = self.stats_service.export_csv(days=30)
        # In production: trigger file save dialog
        print(f"CSV Export:\n{csv_data}")

    def _on_json_export(self, button: Gtk.Button) -> None:
        """Handle JSON export."""
        _ = button  # Unused
        json_data = self.stats_service.export_json(days=30)
        # In production: trigger file save dialog
        print(f"JSON Export:\n{json_data}")
