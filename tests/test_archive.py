import io
import json

import pytest

from collector import archive as archive_module
from collector.archive import (
    ArchiveError,
    ArchiveInfo,
    download_archive,
    fetch_archive_list,
    has_file,
    open_archive,
    pick_archive,
)

ARCHIVES = [
    ArchiveInfo("2026-10-08", "https://example.invalid/08.zip"),
    ArchiveInfo("2026-10-10", "https://example.invalid/10.zip"),
    ArchiveInfo("2026-10-09", "https://example.invalid/09.zip"),
]


def test_pick_newest_archive_by_default():
    assert pick_archive(ARCHIVES, None).date == "2026-10-10"


def test_pick_archive_for_a_given_date():
    assert pick_archive(ARCHIVES, "2026-10-09").url.endswith("09.zip")


def test_pick_unknown_date_fails():
    with pytest.raises(ArchiveError):
        pick_archive(ARCHIVES, "2020-01-01")


def test_pick_from_empty_list_fails():
    with pytest.raises(ArchiveError):
        pick_archive([], None)


def test_fetch_archive_list_parses_the_api_answer(monkeypatch):
    answer = {"archives": [{"date": "2026-10-10", "url": "https://example.invalid/10.zip", "size": 1}]}
    monkeypatch.setattr(archive_module, "_open_url", lambda url: io.BytesIO(json.dumps(answer).encode()))
    assert fetch_archive_list("https://example.invalid/list") == [ARCHIVES[1]]


def test_fetch_archive_list_reports_network_errors(monkeypatch):
    def fail(url):
        raise OSError("no network")

    monkeypatch.setattr(archive_module, "_open_url", fail)
    with pytest.raises(ArchiveError):
        fetch_archive_list("https://example.invalid/list")


def test_fetch_archive_list_reports_unexpected_answer(monkeypatch):
    monkeypatch.setattr(archive_module, "_open_url", lambda url: io.BytesIO(b'{"oops": []}'))
    with pytest.raises(ArchiveError):
        fetch_archive_list("https://example.invalid/list")


def test_download_retries_and_then_succeeds(monkeypatch, tmp_path):
    answers = [OSError("timeout"), io.BytesIO(b"zip bytes")]

    def open_url(url):
        answer = answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer

    monkeypatch.setattr(archive_module, "_open_url", open_url)
    target = download_archive("https://example.invalid/a.zip", tmp_path / "a.zip", attempts=3, wait_seconds=0)
    assert target.read_bytes() == b"zip bytes"


def test_download_gives_up_after_all_attempts(monkeypatch, tmp_path):
    def fail(url):
        raise OSError("timeout")

    monkeypatch.setattr(archive_module, "_open_url", fail)
    with pytest.raises(ArchiveError):
        download_archive("https://example.invalid/a.zip", tmp_path / "a.zip", attempts=2, wait_seconds=0)


def test_open_archive_rejects_a_broken_file(tmp_path):
    path = tmp_path / "broken.zip"
    path.write_bytes(b"not a zip")
    with pytest.raises(ArchiveError):
        open_archive(path)


def test_has_file(archive):
    assert has_file(archive, "konzum", "prices.csv")
    assert not has_file(archive, "lidl", "prices.csv")
