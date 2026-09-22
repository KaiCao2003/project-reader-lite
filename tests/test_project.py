from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from project_reader_lite import CATEGORIES, Project


class ProjectTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.root = self.base / "session"
        self.root.mkdir()

    def file(self, relative, content=b""):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return path

    def folder(self, relative):
        path = self.root / relative
        path.mkdir(parents=True, exist_ok=True)
        return path

    def test_manual_inputs_cover_every_category_and_custom_labels(self):
        project = Project(
            self.root,
            basler=["left.avi", Path("right.avi")],
            motive_tak="trial.tak",
            motive_csv="trial.csv",
            oe="Record Node 102",
            kilosort=(path for path in ["ProbeA", "ProbeB"]),
            result="data/result",
            others={"lab_notes": "notes.txt", "sync": ["sync.json"]},
        )
        project.add("basler", self.root / "left.avi").add("sync", "events.tsv")
        self.assertEqual(project.basler, [self.root / "left.avi", self.root / "right.avi"])
        for label in CATEGORIES:
            self.assertTrue(project[label], label)
            self.assertTrue(all(path.is_absolute() for path in project[label]))
            self.assertEqual(getattr(project, label), project[label])
        self.assertEqual(project["lab_notes"], [self.root / "notes.txt"])
        self.assertEqual(project.others["sync"], [self.root / "sync.json", self.root / "events.tsv"])
        self.assertEqual(project.kilosort, [self.root / "ProbeA", self.root / "ProbeB"])
        project.index["basler"].clear()
        self.assertEqual(len(project.basler), 2)

    def test_scan_discovers_all_builtin_categories_and_multiple_recordings(self):
        video = self.file("Camera.AVI")
        take = self.file("trial.TAK")
        csv = self.file("trial.csv")
        recording_a = self.file("Record Node 102/experiment1/recording1/structure.oebin").parent
        recording_b = self.file("Record Node 102/experiment1/recording2/structure.oebin").parent
        sorting = self.folder("pipeline/ProbeA/kilosort4")
        result = self.folder("data/results")
        self.file("notes.txt")
        project = Project.scan(self.root)
        self.assertEqual(project.basler, [video])
        self.assertEqual(project.motive_tak, [take])
        self.assertEqual(project.motive_csv, [csv])
        self.assertEqual(project.oe, [recording_a, recording_b])
        self.assertEqual(project.kilosort, [sorting])
        self.assertEqual(project.result, [result])
        self.assertEqual(project.others, {})

    def test_motive_csv_detection_does_not_collect_arbitrary_csv(self):
        header = self.file(
            "export.csv",
            '\ufeff"Format Version",1.23,"Take Name","trial, one"\nFrame,Time\n'.encode("utf-8"),
        )
        date = self.file("260921.CSV")
        pair = self.file("paired.csv")
        self.file("paired.tak")
        self.file("unrelated.csv", b"frame,x,y\n1,2,3\n")
        self.file("another/paired.csv", b"frame,x,y\n1,2,3\n")
        self.file("empty.csv")
        self.file("non_utf8.csv", b"\xff\xfeplain data\n")
        self.assertEqual(Project.scan(self.root).motive_csv, [date, header, pair])

    def test_basler_video_conventions(self):
        avi = self.file("camera.avi")
        named = self.file("basler_side.MP4")
        in_folder = self.file("Basler/capture.mkv")
        self.file("presentation.mp4")
        self.assertEqual(Project.scan(self.root).basler, [named, avi, in_folder])

    def test_named_and_marker_based_folders(self):
        legacy = self.file("legacy/100_CH1.continuous").parent
        sorting = self.file("arbitrary/ProbeB/spike_times.npy").parent
        self.file("arbitrary/ProbeB/spike_clusters.npy")
        named = [self.folder(name) for name in ("OE", "open_ephys", "kilosort_3", "result")]
        project = Project.scan(self.root)
        self.assertEqual(set(project.oe), {legacy, named[0], named[1]})
        self.assertEqual(set(project.kilosort), {sorting, named[2]})
        self.assertEqual(project.result, [named[3]])
        self.assertEqual(Project.scan(sorting).kilosort, [sorting])

    def test_aggregate_folders_are_pruned_without_opening_contained_files(self):
        for folder in ("oe", "kilosort", "result", "custom"):
            self.file(f"{folder}/deep/hidden.avi")
            self.file(f"{folder}/deep/hidden.csv", b"Format Version,1.23,Take Name,trial")
        with patch.object(Path, "open", side_effect=AssertionError("Data file was opened")):
            project = Project.scan(self.root, labels={"analysis": "custom"})
        self.assertEqual(project.basler, [])
        self.assertEqual(project.motive_csv, [])
        self.assertEqual(project["analysis"], [self.root / "custom"])

    def test_custom_rules_precede_builtins_and_support_multiple_patterns(self):
        movie = self.file("preview.avi")
        notes = self.file("nested/notes.md")
        events = self.file("behavior/trial/events.tsv")
        mp4 = self.file("camera.mp4")
        project = Project.scan(
            self.root,
            labels={
                "preview": "preview.avi",
                "notes": ["*.txt", "*.md"],
                "events": "behavior/*.tsv",
                "basler": "*.mp4",
                "second_match": "*.avi",
            },
        )
        self.assertEqual(project["preview"], [movie])
        self.assertEqual(project["notes"], [notes])
        self.assertEqual(project["events"], [events])
        self.assertEqual(project.basler, [mp4])
        self.assertEqual(project["second_match"], [])

    def test_save_load_survives_move_and_preserves_external_paths_and_labels(self):
        video = self.file("camera.avi")
        external = self.base / "external.txt"
        external.write_text("notes", encoding="utf-8")
        external_label = "external_\u03b1"
        project = Project(self.root, basler=video, others={external_label: external, "empty": []})
        saved = project.save("meta/index.json")
        data = json.loads(saved.read_text(encoding="utf-8"))
        self.assertEqual(data["root"], "..")
        self.assertEqual(data["basler"], ["camera.avi"])
        self.assertEqual(data["others"][external_label], [str(external)])
        self.assertEqual(Project.load(saved).index, project.index)

        moved = self.base / "moved"
        shutil.move(str(self.root), moved)
        (moved / "camera.avi").unlink()
        with patch("project_reader_lite.os.walk", side_effect=AssertionError("Unexpected scan")):
            loaded = Project.load(moved / "meta/index.json")
        self.assertEqual(loaded.root, moved)
        self.assertEqual(loaded.basler, [moved / "camera.avi"])
        self.assertEqual(loaded.others, {external_label: [external], "empty": []})

    def test_saved_scan_is_repeatable_and_skips_hidden_and_build_paths(self):
        visible = self.file("camera.avi")
        for ignored in (".git", ".hidden", "__pycache__", "build", "dist", "example.egg-info"):
            self.file(f"{ignored}/ignored.avi")
        self.file(".hidden.avi")
        first = Project.scan(self.root)
        saved = first.save()
        second = Project.scan(self.root)
        self.assertEqual(first.basler, [visible])
        self.assertEqual(first.index, second.index)
        self.assertEqual(Project.load(saved).index, first.index)
        self.assertEqual(set(first.index), set(CATEGORIES))

    def test_directory_symlinks_are_not_followed(self):
        self.file("nested/camera.avi")
        try:
            (self.root / "nested/back").symlink_to(self.root, target_is_directory=True)
        except OSError as error:
            self.skipTest(str(error))
        self.assertEqual(Project.scan(self.root).basler, [self.root / "nested/camera.avi"])

    def test_invalid_root_labels_and_foreign_manifests_fail_clearly(self):
        with self.assertRaises(FileNotFoundError):
            Project.scan(self.root / "missing")
        with self.assertRaises(NotADirectoryError):
            Project.scan(self.file("file.txt"))
        with self.assertRaisesRegex(ValueError, "non-empty"):
            Project(self.root).add(" ", "file.txt")
        with self.assertRaisesRegex(ValueError, "built-in"):
            Project(self.root, others={"basler": "camera.avi"})
        with self.assertRaises(KeyError):
            Project(self.root)["unknown"]
        for data in ({"schema_version": 1}, {"format": "project-reader-lite", "version": 2}, []):
            source = self.file("foreign.json", json.dumps(data).encode())
            with self.assertRaisesRegex(ValueError, "version 1"):
                Project.load(source)


if __name__ == "__main__":
    unittest.main()
