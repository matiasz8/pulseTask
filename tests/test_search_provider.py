"""Tests for the GNOME search provider integration."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from pulse_task.core.group import GroupStatus
from pulse_task.core.group_service import GroupService
from pulse_task.core.persistence import Database
from pulse_task.system.search_provider import SearchProvider


class FakeSettings:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled

    def get_boolean(self, key: str) -> bool:
        return self.enabled if key == "search-provider-enabled" else True

    def list_keys(self) -> list[str]:
        return ["search-provider-enabled"]


def _build_provider() -> tuple[SearchProvider, GroupService]:
    db = Database(":memory:")
    service = GroupService(db)
    titles = {
        "task-1": "Urgent café review ☕",
        "task-2": "Meeting prep notes",
        "task-3": "Deploy résumé update",
        "task-4": "Archive inbox zero",
    }
    active = service.create_group(
        "Focus Sprint",
        ["task-1", "task-2"],
        description="Morning planning",
    )
    service.start_group_execution(active.id)
    completed = service.create_group(
        "Recent Wins",
        ["task-3", "task-4"],
        description="Completed yesterday",
    )
    completed_group = service.get_group(completed.id)
    assert completed_group is not None
    completed_group.status = GroupStatus.COMPLETED
    completed_group.completed_at = datetime.now(UTC) - timedelta(hours=2)
    completed_group.tasks_completed = len(completed_group.task_ids)
    service.update_group(completed_group)
    provider = SearchProvider(
        service,
        task_title_resolver=titles.get,
        settings=FakeSettings(),
    )
    return provider, service


def _unwrap(meta_value: object) -> object:
    return meta_value.unpack() if hasattr(meta_value, "unpack") else meta_value


def test_get_initial_result_set_matches_unicode_and_ranks_active_first() -> None:
    provider, _ = _build_provider()

    results = provider.GetInitialResultSet(["cafe"])

    assert len(results) == 1
    metas = provider.GetResultMetas(results)
    assert _unwrap(metas[0]["name"]) == "Urgent café review ☕"
    assert "Active" in str(_unwrap(metas[0]["description"]))


def test_get_initial_result_set_supports_fuzzy_group_matching() -> None:
    provider, _ = _build_provider()

    results = provider.GetInitialResultSet(["mtg", "focus"])

    assert results
    metas = provider.GetResultMetas(results)
    names = [_unwrap(meta["name"]) for meta in metas]
    assert "Meeting prep notes" in names


def test_get_result_metas_returns_empty_for_unknown_or_deleted_ids() -> None:
    provider, _ = _build_provider()

    assert provider.GetResultMetas([999999]) == []
    [result_id] = provider.GetInitialResultSet(["meeting"])
    provider.task_title_resolver = lambda _task_id: None
    assert provider.GetResultMetas([result_id]) == []
    assert provider.GetInitialResultSet([]) == []


def test_activate_result_invokes_callback_with_task_context() -> None:
    provider, _ = _build_provider()
    callback_calls: list[tuple[str, str | None, tuple[str, ...], int]] = []
    provider.bind_handlers(
        on_activate=lambda task_id, group_id, terms, ts: callback_calls.append(
            (task_id, group_id, terms, ts)
        )
    )

    [result_id] = provider.GetInitialResultSet(["résumé"])
    provider.ActivateResult(result_id, ["résumé"], 42)

    assert callback_calls == [("task-3", callback_calls[0][1], ("résumé",), 42)]


def test_launch_search_and_set_active_manage_provider_state() -> None:
    provider, _ = _build_provider()
    launches: list[tuple[tuple[str, ...], int]] = []
    provider.bind_handlers(on_launch_search=lambda terms, ts: launches.append((terms, ts)))

    provider.SetActive(False)
    provider.LaunchSearch(["review"], 7)

    assert launches == [(("review",), 7)]
    assert provider.GetResultMetas([1]) == []


def test_disabled_provider_returns_no_results() -> None:
    provider, _ = _build_provider()
    provider.settings = FakeSettings(enabled=False)

    assert provider.GetInitialResultSet(["urgent"]) == []
    assert provider.GetSubsystemQuery(["urgent"]) == ([], [])
