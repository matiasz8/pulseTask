"""GNOME Shell search provider integration for PulseTask."""

from __future__ import annotations

import logging
import time
import unicodedata
import zlib
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from pulse_task.core.group import GroupStatus, TaskGroup
from pulse_task.core.group_service import GroupService

try:
    import gi  # type: ignore[import-untyped]

    gi.require_version("Gio", "2.0")
    gi.require_version("GLib", "2.0")
    from gi.repository import Gio, GLib  # type: ignore[import-untyped]
except (ImportError, ValueError):
    Gio = None
    GLib = None

logger = logging.getLogger(__name__)

SEARCH_BUS_NAME = "org.gnome.Pulse"
SEARCH_OBJECT_PATH = "/org/gnome/Pulse/SearchProvider"
SEARCH_ICON = "org.gnome.Pulse-symbolic"
MAX_RESULTS = 10
RECENT_COMPLETION_WINDOW = timedelta(days=7)

ActivateCallback = Callable[[str, str | None, tuple[str, ...], int], None]
LaunchCallback = Callable[[tuple[str, ...], int], None]
TaskTitleResolver = Callable[[str], str | None]


@dataclass(slots=True)
class SearchResult:
    """Search result returned to GNOME Shell."""

    id: int
    task_id: str
    task_name: str
    group_id: str
    group_name: str
    status: str
    timestamp: int


class SearchProvider:
    """Expose PulseTask tasks to the GNOME Activities search provider API."""

    def __init__(
        self,
        group_service: GroupService,
        *,
        task_title_resolver: TaskTitleResolver | None = None,
        settings: Any | None = None,
        on_activate: ActivateCallback | None = None,
        on_launch_search: LaunchCallback | None = None,
    ) -> None:
        """Initialize the provider with task data and optional UI callbacks."""
        self.group_service = group_service
        self.task_title_resolver = task_title_resolver
        self.settings = settings
        self.on_activate = on_activate
        self.on_launch_search = on_launch_search
        self._active = False
        self._result_cache: dict[int, SearchResult] = {}
        self._connection: Any | None = None
        self._owner_id: int | None = None
        self._registration_id: int | None = None
        self._node_info: Any | None = None

    def bind_handlers(
        self,
        *,
        on_activate: ActivateCallback | None = None,
        on_launch_search: LaunchCallback | None = None,
    ) -> None:
        """Attach callbacks used when GNOME activates a result or launches a search."""
        self.on_activate = on_activate
        self.on_launch_search = on_launch_search

    def register(self) -> bool:
        """Register the SearchProvider2 D-Bus object on the user session bus."""
        if Gio is None or GLib is None or not self._is_enabled():
            return False
        if self._registration_id is not None:
            return True
        try:
            xml = Path(__file__).with_name("search_dbus.xml").read_text(encoding="utf-8")
            self._node_info = Gio.DBusNodeInfo.new_for_xml(xml)
            self._connection = Gio.bus_get_sync(Gio.BusType.SESSION, None)
            self._registration_id = self._connection.register_object(
                SEARCH_OBJECT_PATH,
                self._node_info.interfaces[0],
                self._handle_method_call,
            )
            self._owner_id = Gio.bus_own_name_on_connection(
                self._connection,
                SEARCH_BUS_NAME,
                Gio.BusNameOwnerFlags.NONE,
                None,
                None,
            )
        except Exception:
            logger.exception("Failed to register GNOME search provider")
            self.unregister()
            return False
        logger.debug("Registered GNOME search provider")
        return True

    def unregister(self) -> None:
        """Release the SearchProvider2 D-Bus registration and clear caches."""
        if Gio is not None and self._owner_id is not None:
            Gio.bus_unown_name(self._owner_id)
        if self._connection is not None and self._registration_id is not None:
            self._connection.unregister_object(self._registration_id)
        self._owner_id = None
        self._registration_id = None
        self._connection = None
        self._node_info = None
        self._result_cache.clear()

    def GetInitialResultSet(self, terms: list[str]) -> list[int]:
        """Return up to ten matching task identifiers for the provided search terms."""
        start = time.perf_counter()
        normalized_terms = [self._normalize(term) for term in terms if self._normalize(term)]
        if not normalized_terms or not self._is_enabled():
            self._result_cache.clear()
            return []
        matches = self._search(normalized_terms)
        self._result_cache = {match.id: match for match in matches}
        logger.debug(
            "Search query %s returned %s results in %.2fms",
            terms,
            len(matches),
            (time.perf_counter() - start) * 1000,
        )
        return [match.id for match in matches]

    def GetSubsystemQuery(self, terms: list[str]) -> tuple[list[str], list[str]]:
        """Return an empty refinement payload and let GNOME filter client-side."""
        logger.debug("Ignoring subsystem query refinement for %s", terms)
        return ([], [])

    def GetResultMetas(self, result_ids: list[int]) -> list[dict[str, Any]]:
        """Return GNOME Shell metadata dictionaries for the requested result ids."""
        metas: list[dict[str, Any]] = []
        for result_id in result_ids:
            meta = self._meta_for_result(result_id)
            if meta is not None:
                metas.append(meta)
        return metas

    def ActivateResult(self, result_id: int, terms: list[str], timestamp: int) -> None:
        """Open PulseTask and focus the selected task result when available."""
        result = self._result_cache.get(result_id)
        if result is None or self.on_activate is None:
            return
        self.on_activate(result.task_id, result.group_id, tuple(terms), timestamp)

    def LaunchSearch(self, terms: list[str], timestamp: int) -> None:
        """Open PulseTask for a broader search when the shell requests it."""
        if self.on_launch_search is not None:
            self.on_launch_search(tuple(terms), timestamp)

    def SetActive(self, active: bool) -> None:
        """Track whether GNOME currently considers the search provider active."""
        self._active = active
        if not active:
            self._result_cache.clear()

    def _search(self, terms: list[str]) -> list[SearchResult]:
        candidates: list[tuple[int, SearchResult]] = []
        now = datetime.now(UTC)
        seen_ids: set[int] = set()
        groups = sorted(self.group_service.list_groups(limit=200), key=self._group_rank)
        for group in groups:
            if not self._include_group(group, now):
                continue
            for index, task_id in enumerate(group.task_ids):
                task_name = self._task_title(task_id)
                haystack = self._normalize(f"{task_name} {group.name} {group.description}")
                score = self._match_score(terms, haystack)
                if score < 0:
                    continue
                status = self._task_status(group, index)
                result_id = self._stable_result_id(group.id, task_id, seen_ids)
                seen_ids.add(result_id)
                candidates.append(
                    (
                        score - (0 if status == "active" else 25),
                        SearchResult(
                            id=result_id,
                            task_id=task_id,
                            task_name=task_name,
                            group_id=group.id,
                            group_name=group.name,
                            status=status,
                            timestamp=self._group_timestamp(group),
                        ),
                    )
                )
        ordered = sorted(
            candidates,
            key=lambda item: (
                self._status_rank(item[1].status),
                -item[0],
                -item[1].timestamp,
                item[1].task_name.casefold(),
            ),
        )
        return [result for _, result in ordered[:MAX_RESULTS]]

    def _include_group(self, group: TaskGroup, now: datetime) -> bool:
        if group.status in {GroupStatus.EXECUTING, GroupStatus.PAUSED}:
            return True
        return group.status == GroupStatus.COMPLETED and bool(
            group.completed_at and now - group.completed_at <= RECENT_COMPLETION_WINDOW
        )

    def _group_rank(self, group: TaskGroup) -> tuple[int, int]:
        rank = 0 if group.status in {GroupStatus.EXECUTING, GroupStatus.PAUSED} else 1
        return (rank, -self._group_timestamp(group))

    def _task_status(self, group: TaskGroup, index: int) -> str:
        if (
            group.status in {GroupStatus.EXECUTING, GroupStatus.PAUSED}
            and index == group.current_task_index
        ):
            return "active"
        if (
            index < group.tasks_completed + group.tasks_skipped
            or group.status == GroupStatus.COMPLETED
        ):
            return "completed"
        return "pending"

    def _status_rank(self, status: str) -> int:
        return {"active": 0, "pending": 1, "completed": 2}.get(status, 3)

    def _task_title(self, task_id: str) -> str:
        if self.task_title_resolver is None:
            return task_id
        title = self.task_title_resolver(task_id)
        return title or task_id

    def _match_score(self, terms: list[str], haystack: str) -> int:
        total = 0
        for term in terms:
            if term in haystack:
                total += 100 + len(term)
                continue
            if self._is_fuzzy_match(term, haystack):
                total += 25 + len(term)
                continue
            return -1
        return total

    def _meta_for_result(self, result_id: int) -> dict[str, Any] | None:
        result = self._result_cache.get(result_id)
        if result is None:
            return None
        current_title: str | None = result.task_name
        if self.task_title_resolver is not None:
            current_title = self.task_title_resolver(result.task_id)
            if current_title is None:
                return None
        description = f"{result.group_name} • {result.status.title()}"
        return {
            "id": self._variant("u", result.id),
            "name": self._variant("s", current_title),
            "description": self._variant("s", description),
            "icon": self._variant("s", SEARCH_ICON),
        }

    def _stable_result_id(self, group_id: str, task_id: str, seen_ids: set[int]) -> int:
        result_id = zlib.crc32(f"{group_id}:{task_id}".encode()) & 0xFFFFFFFF
        while result_id in seen_ids:
            result_id = (result_id + 1) & 0xFFFFFFFF
        return result_id

    def _group_timestamp(self, group: TaskGroup) -> int:
        moment = group.completed_at or group.started_at or group.created_at
        return int(moment.timestamp())

    def _normalize(self, value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        without_marks = "".join(char for char in normalized if not unicodedata.combining(char))
        return without_marks.casefold().strip()

    def _is_fuzzy_match(self, needle: str, haystack: str) -> bool:
        position = 0
        for char in needle:
            position = haystack.find(char, position)
            if position < 0:
                return False
            position += 1
        return True

    def _variant(self, signature: str, value: object) -> object:
        if GLib is None:
            return value
        return GLib.Variant(signature, value)

    def _is_enabled(self) -> bool:
        if self.settings is None or not hasattr(self.settings, "get_boolean"):
            return True
        if hasattr(self.settings, "list_keys"):
            keys = set(self.settings.list_keys())
            if "search-provider-enabled" not in keys:
                return True
        return bool(self.settings.get_boolean("search-provider-enabled"))

    def _handle_method_call(
        self,
        _connection: Any,
        _sender: str,
        _path: str,
        _iface: str,
        method_name: str,
        parameters: Any,
        invocation: Any,
    ) -> None:
        args = tuple(parameters.unpack()) if parameters is not None else ()
        if GLib is None:
            invocation.return_dbus_error("org.gnome.Pulse.Error", "GLib unavailable")
            return
        if method_name == "GetInitialResultSet":
            result_ids = self.GetInitialResultSet(list(args[0]))
            invocation.return_value(GLib.Variant("(au)", (result_ids,)))
        elif method_name == "GetSubsystemQuery":
            invocation.return_value(GLib.Variant("(asas)", self.GetSubsystemQuery(list(args[0]))))
        elif method_name == "GetResultMetas":
            invocation.return_value(GLib.Variant("(aa{sv})", (self.GetResultMetas(list(args[0])),)))
        elif method_name == "ActivateResult":
            self.ActivateResult(int(args[0]), list(args[1]), int(args[2]))
            invocation.return_value(None)
        elif method_name == "LaunchSearch":
            self.LaunchSearch(list(args[0]), int(args[1]))
            invocation.return_value(None)
        elif method_name == "SetActive":
            self.SetActive(bool(args[0]))
            invocation.return_value(None)
        else:
            invocation.return_dbus_error("org.gnome.Pulse.Error.UnknownMethod", method_name)
