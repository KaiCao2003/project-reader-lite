"""Index experiment paths using only the Python standard library."""

from __future__ import annotations

import csv
import json
import os
import re
from collections.abc import Iterable, Mapping
from fnmatch import fnmatchcase
from pathlib import Path

__all__ = ["CATEGORIES", "Project"]

CATEGORIES = ("basler", "motive_tak", "motive_csv", "oe", "kilosort", "result")
PathInput = str | Path | Iterable[str | Path] | None
_IGNORED_DIRECTORIES = {"__pycache__", "node_modules", "build", "dist"}
_KILOSORT_NAME = re.compile(r"kilosort(?:\d+(?:\.\d+)?|[_-].+)?", re.IGNORECASE)


class Project:
    """A path-only index; explicit inputs are relative to ``root``.

    Use ``Project.scan(root)`` for automatic discovery, or pass paths to the
    constructor. Explicit paths can be offline and are not opened or validated.
    """

    def __init__(
        self,
        root: str | Path = ".",
        *,
        basler: PathInput = None,
        motive_tak: PathInput = None,
        motive_csv: PathInput = None,
        oe: PathInput = None,
        kilosort: PathInput = None,
        result: PathInput = None,
        others: Mapping[str, PathInput] | None = None,
    ) -> None:
        self.root = Path(root).expanduser().resolve()
        # Dictionary keys preserve discovery order and deduplicate in O(1).
        self._paths: dict[str, dict[Path, None]] = {}
        for label, paths in zip(CATEGORIES, (basler, motive_tak, motive_csv, oe, kilosort, result)):
            self.add(label, paths)
        for label, paths in (others or {}).items():
            if label in CATEGORIES:
                raise ValueError(f"Use the {label!r} argument for a built-in category.")
            self.add(label, paths)

    def add(self, label: str, paths: PathInput) -> Project:
        """Add one path or multiple paths to a built-in or user-defined label."""
        if not isinstance(label, str) or not label.strip():
            raise ValueError("A label must be a non-empty string.")
        bucket = self._paths.setdefault(label, {})
        if paths is not None:
            for path in (paths,) if isinstance(paths, (str, Path)) else paths:
                bucket[self._resolve(path)] = None
        return self

    def __getitem__(self, label: str) -> list[Path]:
        """Return paths for a label; unknown labels raise KeyError."""
        return list(self._paths[label])

    @property
    def index(self) -> dict[str, list[Path]]:
        """Return a copy of all categories, including user-defined labels."""
        return {label: list(paths) for label, paths in self._paths.items()}

    @property
    def basler(self) -> list[Path]:
        return self["basler"]

    @property
    def motive_tak(self) -> list[Path]:
        return self["motive_tak"]

    @property
    def motive_csv(self) -> list[Path]:
        return self["motive_csv"]

    @property
    def oe(self) -> list[Path]:
        return self["oe"]

    @property
    def kilosort(self) -> list[Path]:
        return self["kilosort"]

    @property
    def result(self) -> list[Path]:
        return self["result"]

    @property
    def others(self) -> dict[str, list[Path]]:
        return {label: list(paths) for label, paths in self._paths.items() if label not in CATEGORIES}

    @classmethod
    def scan(
        cls,
        root: str | Path,
        *,
        labels: Mapping[str, str | Iterable[str]] | None = None,
    ) -> Project:
        """Scan a folder; matching directory assets are indexed as a whole.

        Label rules use case-sensitive fnmatch patterns on root-relative POSIX
        paths, or any basename when the pattern has no slash. User rules take
        precedence; the first match wins. Directory symlinks are not followed.
        """
        project = cls(Path(root).expanduser().resolve(strict=True))
        if not project.root.is_dir():
            raise NotADirectoryError(project.root)
        rules = {}
        for label, patterns in (labels or {}).items():
            project.add(label, None)
            rules[label] = (patterns,) if isinstance(patterns, str) else tuple(patterns)

        for current, dirnames, filenames in os.walk(project.root, onerror=_raise_walk_error):
            folder = Path(current)
            dirnames[:] = sorted(
                name for name in dirnames
                if not name.startswith(".")
                and name not in _IGNORED_DIRECTORIES
                and not name.endswith(".egg-info")
                and not (folder / name).is_symlink()
            )
            names = {name.casefold() for name in filenames}
            label = _match_label(folder, project.root, rules) or _directory_label(folder, names)
            if label is not None:
                project.add(label, folder)
                dirnames.clear()
                continue
            for name in sorted(filenames):
                if name.startswith("."):
                    continue
                path = folder / name
                label = _match_label(path, project.root, rules) or _file_label(path, names)
                if label is not None:
                    project.add(label, path)
        return project

    def save(self, path: str | Path = "project-index.json") -> Path:
        """Save JSON, with in-project asset paths relative to the project root."""
        target = self._resolve(path)
        try:
            root = Path(os.path.relpath(self.root, target.parent)).as_posix()
        except ValueError:
            # Windows cannot express a relative path across different drives.
            root = self.root.as_posix()

        def stored_paths(paths: Iterable[Path]) -> list[str]:
            return [
                item.relative_to(self.root).as_posix() if item.is_relative_to(self.root) else str(item)
                for item in paths
            ]

        data = {
            "format": "project-reader-lite",
            "version": 1,
            "root": root,
            **{label: stored_paths(self._paths[label]) for label in CATEGORIES},
            "others": {label: stored_paths(paths) for label, paths in self.others.items()},
        }
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return target

    @classmethod
    def load(cls, path: str | Path) -> Project:
        """Load a lite JSON index without scanning or opening its data files."""
        source = Path(path).expanduser().resolve()
        data = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("format") != "project-reader-lite" or data.get("version") != 1:
            raise ValueError("Expected a project-reader-lite index with version 1.")
        return cls(
            source.parent / data["root"],
            **{label: data[label] for label in CATEGORIES},
            others=data["others"],
        )

    def _resolve(self, path: str | Path) -> Path:
        return (self.root / Path(path).expanduser()).resolve()


def _match_label(path: Path, root: Path, rules: Mapping[str, tuple[str, ...]]) -> str | None:
    relative = path.relative_to(root).as_posix()
    for label, patterns in rules.items():
        if any(
            fnmatchcase(relative, pattern) or ("/" not in pattern and fnmatchcase(path.name, pattern))
            for pattern in patterns
        ):
            return label
    return None


def _directory_label(path: Path, filenames: set[str]) -> str | None:
    name = path.name.casefold()
    if name in {"result", "results"}:
        return "result"
    if (
        name in {"oe", "open_ephys", "open-ephys", "open ephys"}
        or "structure.oebin" in filenames
        or any(filename.endswith(".continuous") for filename in filenames)
    ):
        return "oe"
    if _KILOSORT_NAME.fullmatch(name) or {"spike_times.npy", "spike_clusters.npy"} <= filenames:
        return "kilosort"
    return None


def _file_label(path: Path, siblings: set[str]) -> str | None:
    suffix = path.suffix.casefold()
    if suffix == ".avi" or (
        suffix in {".mp4", ".mkv", ".mov"}
        and "basler" in f"{path.parent.name}/{path.name}".casefold()
    ):
        return "basler"
    if suffix == ".tak":
        return "motive_tak"
    if suffix == ".csv":
        if f"{path.stem.casefold()}.tak" in siblings or re.fullmatch(r"\d{6}", path.stem):
            return "motive_csv"
        # Only inspect a bounded header, even when the tracking export is huge.
        with path.open("rb") as file:
            header = file.readline(8192).decode("utf-8-sig", errors="replace")
        fields = {field.strip().casefold() for field in next(csv.reader([header]), [])}
        if {"format version", "take name"} <= fields:
            return "motive_csv"
    return None


def _raise_walk_error(error: OSError) -> None:
    raise error
