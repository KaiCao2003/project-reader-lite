"""Scan a recording folder, save its index, and verify the saved paths."""

import argparse
from pathlib import Path

from project_reader_lite import Project


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="Existing recording or session folder.")
    parser.add_argument("--output", type=Path, required=True, help="Destination JSON index.")
    args = parser.parse_args()

    project = Project.scan(
        args.root,
        labels={
            "notes": ["*.txt", "*.md"],
            "sync": "sync_data.json",
            # Keep these generated output folders as whole assets.
            "analysis": [
                "data/processed",
                "data/rfmapping",
                "data/spike_position",
                "data/spikeinterface_analyzer",
                "data/waveform",
            ],
        },
    )

    print(f"Root: {project.root}")
    for label, paths in project.index.items():
        print(f"{label}: {len(paths)}")
        for path in paths:
            print(f"  {path.relative_to(project.root).as_posix()}")

    # Interpret the example's output argument relative to the working directory.
    saved = project.save(args.output.expanduser().resolve())
    loaded = Project.load(saved)
    if loaded.index != project.index:
        raise RuntimeError("The saved index did not round-trip correctly.")
    print(f"Saved: {saved}")
    print("Reloaded index matches: True")


if __name__ == "__main__":
    main()
