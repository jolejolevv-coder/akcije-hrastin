"""Locate, download and read the daily price archive published by cijene.dev."""

import csv
import io
import json
import logging
import time
import urllib.error
import urllib.request
import zipfile
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

DOWNLOAD_ATTEMPTS = 3
RETRY_WAIT_SECONDS = 30
REQUEST_TIMEOUT_SECONDS = 120
CHUNK_BYTES = 1024 * 1024
USER_AGENT = "akcije-hrastin/1.0 (private, non-commercial)"
CSV_ENCODING = "utf-8"

log = logging.getLogger(__name__)


class ArchiveError(Exception):
    """The archive could not be located, downloaded or opened."""


@dataclass(frozen=True)
class ArchiveInfo:
    date: str
    url: str


def fetch_archive_list(list_url: str) -> list[ArchiveInfo]:
    """Return all published archives, as listed by the API."""
    try:
        with _open_url(list_url) as response:
            entries = json.load(response)["archives"]
        return [ArchiveInfo(entry["date"], entry["url"]) for entry in entries]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise ArchiveError(f"Cannot read archive list {list_url}: {error!r}") from error


def pick_archive(archives: list[ArchiveInfo], wanted_date: str | None) -> ArchiveInfo:
    """Pick the archive for one date, or the newest one if no date is given."""
    if not archives:
        raise ArchiveError("The archive list is empty")
    if wanted_date is None:
        return max(archives, key=lambda archive: archive.date)
    for archive in archives:
        if archive.date == wanted_date:
            return archive
    raise ArchiveError(f"No archive published for {wanted_date}")


def download_archive(
    url: str,
    target: Path,
    attempts: int = DOWNLOAD_ATTEMPTS,
    wait_seconds: float = RETRY_WAIT_SECONDS,
) -> Path:
    """Download the archive to target, retrying on network errors."""
    for attempt in range(1, attempts + 1):
        try:
            _download_once(url, target)
            return target
        except OSError as error:
            log.warning("Download attempt %d of %d failed: %r", attempt, attempts, error)
            if attempt < attempts:
                time.sleep(wait_seconds)
    raise ArchiveError(f"Download of {url} failed after {attempts} attempts")


def open_archive(path: Path) -> zipfile.ZipFile:
    try:
        return zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as error:
        raise ArchiveError(f"Cannot open archive {path}: {error!r}") from error


def has_file(archive: zipfile.ZipFile, chain_id: str, file_name: str) -> bool:
    return f"{chain_id}/{file_name}" in archive.namelist()


def read_csv(archive: zipfile.ZipFile, chain_id: str, file_name: str) -> Iterator[dict[str, str]]:
    """Yield the rows of one CSV file of one chain, without unpacking it to disk."""
    with archive.open(f"{chain_id}/{file_name}") as binary:
        text = io.TextIOWrapper(binary, encoding=CSV_ENCODING, newline="")
        yield from csv.DictReader(text)


def _open_url(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS)


def _download_once(url: str, target: Path) -> None:
    with _open_url(url) as response, target.open("wb") as output:
        while chunk := response.read(CHUNK_BYTES):
            output.write(chunk)
