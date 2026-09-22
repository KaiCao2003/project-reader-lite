# project-reader-lite

**en** | [zh](README.zh.md)

`project-reader-lite` indexes experiment files and folders by category. Scan a
recording directory or provide paths manually, then save and load the index as
JSON from Python scripts or notebooks.

It needs **Python 3.10 or newer** and has **no third-party runtime dependencies**.

If Python and Git are already installed, install directly from GitHub:

```bash
python -m pip install "git+https://github.com/KaiCao2003/project-reader-lite.git"
```

The package covers these seven groups:

| Your data | Python name | What you get back |
| --- | --- | --- |
| Basler camera recordings | `project.basler` | A list of video paths |
| Motive tracking TAK files | `project.motive_tak` | A list of `.tak` paths |
| Motive CSV exports | `project.motive_csv` | A list of CSV paths |
| Open Ephys recordings | `project.oe` | A list of recording folder paths |
| Kilosort outputs | `project.kilosort` | A list of output folder paths |
| Result folders | `project.result` | A list of result folder paths |
| Custom labels | `project.others` | A dictionary of labels and path lists |

Each built-in list may be empty or contain multiple entries. You do not need
all six types to create a project.

## Contents

1. [What an index contains](#1-what-an-index-contains)
2. [Install the package](#2-install-the-package)
3. [Run the example on a real recording](#3-run-the-example-on-a-real-recording)
4. [Write your first indexing script](#4-write-your-first-indexing-script)
5. [Enter paths manually](#5-enter-paths-manually)
6. [Read and use indexed paths](#6-read-and-use-indexed-paths)
7. [Define automatic labels](#7-define-automatic-labels)
8. [Understand automatic detection](#8-understand-automatic-detection)
9. [Save and load an index](#9-save-and-load-an-index)
10. [Understand paths and moving data](#10-understand-paths-and-moving-data)
11. [Refresh or edit an index](#11-refresh-or-edit-an-index)
12. [API reference](#12-api-reference)
13. [Troubleshooting](#13-troubleshooting)
14. [Development and verification](#14-development-and-verification)

## 1. What an index contains

An **index** is a list of locations grouped by labels. It records where data is
stored so your analysis scripts can find it again. Creating an index does not
copy, move, rename, or modify the indexed data.

| Term | Meaning | Example |
| --- | --- | --- |
| Root | The recording folder used as the base for relative paths | `/data/session` |
| Path | The location of a file or folder | `/data/session/trial.tak` |
| Label | A name used to group paths | `motive_tak`, `notes`, or `sync` |
| Index file | The JSON document written by `save()` | `/data/session/meta/index.json` |

The main operations are:

```python
from project_reader_lite import Project

root = "/Volumes/SenzaiLab/Kai/#Recording/m19/260820/260820_3"
project = Project.scan(root)              # Discover existing files and folders.
project.add("notes", "260820.txt")        # Add an explicitly labeled path.
print(project.motive_tak)                 # Read the indexed TAK paths.
```

Replace `root` with the location of your recording. Examples using `/data/session`
require the same substitution.

Scanning reads directory names and, when needed, a CSV header. The returned
`Path` objects can be passed to your video, tracking, or electrophysiology tools
to load the data.

## 2. Install the package

### 2.1 Where to type commands

- Commands such as `python -m pip install ...` go in a **terminal**.
- Code such as `from project_reader_lite import Project` goes in a **Python
  script**, a Python prompt, or a notebook cell.

On macOS, use Terminal. On Windows, use PowerShell. On Linux, use your usual
terminal. The relevant part of your local repository looks like this:

```text
project-reader-lite/
    pyproject.toml
    README.md
    README.zh.md
    project_reader_lite/
    examples/
        quickstart.py
    tests/
```

**Repository root** means the `project-reader-lite` folder containing
`pyproject.toml`. Run installation and example commands from that folder.

### 2.2 macOS or Linux

First check your Python version:

```bash
python3 --version
```

It must be Python 3.10 or newer. Download the repository with Git:

```bash
git clone https://github.com/KaiCao2003/project-reader-lite.git
cd project-reader-lite
```

Alternatively, download the repository through GitHub's **Code → Download ZIP**,
extract it, and open that folder in your terminal. Its name may end in `-main`.

From the folder containing `pyproject.toml`, create a virtual environment,
activate it, and install:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

Quote paths containing spaces when opening a folder, for example
`cd "/Users/alex/My Projects/project-reader-lite"`.

A virtual environment is a separate place for this project's Python packages.
After activation, `python` uses that environment. Activate it again whenever
you open a new terminal to run these scripts:

```bash
cd /path/to/project-reader-lite
source .venv/bin/activate
```

### 2.3 Windows PowerShell

```powershell
py -3 --version
git clone https://github.com/KaiCao2003/project-reader-lite.git
cd project-reader-lite
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install .
```

If you downloaded a ZIP instead, open its extracted folder before running the
environment commands. If PowerShell blocks activation, use the environment's
Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\python.exe -c "from project_reader_lite import Project; print('Import OK')"
```

In that case, substitute `.\.venv\Scripts\python.exe` for `python` in later
terminal commands.

### 2.4 Confirm installation

Run this in the same terminal:

```bash
python -c "from project_reader_lite import Project; print('Import OK')"
```

Expected output:

```text
Import OK
```

The distribution name uses hyphens, but the Python import uses underscores:

| Context | Correct name |
| --- | --- |
| Installed distribution | `project-reader-lite` |
| Python import | `project_reader_lite` |
| Class used in your code | `Project` |

Always import with `from project_reader_lite import Project`.

### 2.5 Installing a standalone folder or wheel

The folder containing `pyproject.toml` can be installed from anywhere:

```bash
python -m pip install /absolute/path/to/project-reader-lite
```

To install a downloaded wheel:

```bash
python -m pip install /absolute/path/to/project_reader_lite-0.1.0-py3-none-any.whl
```

You can also install from GitHub without retaining a source checkout:

```bash
python -m pip install "git+https://github.com/KaiCao2003/project-reader-lite.git"
```

The GitHub URL installation requires Git. A local folder or wheel can be installed
without Git. To run `examples/quickstart.py`, download or clone the source.

### 2.6 Jupyter notebooks

Use a notebook cell to install into the notebook's own environment:

```python
%pip install /absolute/path/to/project-reader-lite
```

Then use a new cell:

```python
from project_reader_lite import Project
```

`%pip` is notebook syntax. Do not put it in a regular `.py` script. After upgrading
a package already imported by a notebook, restart the kernel to load the new code.

## 3. Run the example on a real recording

### 3.1 Recording directory

Sample session, scanned on **2026-09-21**:

```text
/Volumes/SenzaiLab/Kai/#Recording/m19/260820/260820_3
```

Relevant files and folders:

```text
260820_3/
    260820.csv
    260820.tak
    260820.txt
    260820/
        Record Node 102/
            experiment1/
                recording1/
                    structure.oebin
    kilosort/
        ProbeA/
            kilosort_3/
                spike_times.npy
                spike_clusters.npy
                cluster_KSLabel.tsv
    data/
        result/
        processed/
        rfmapping/
        spike_position/
        spikeinterface_analyzer/
        waveform/
```

The scan returned empty `basler` and `sync` lists. Recognized folders are indexed
as a whole; their contents are excluded from further discovery.

### 3.2 Run the script

[quickstart.py](examples/quickstart.py) scans a recording directory, prints the
paths, saves the index, and verifies that loading it returns the same paths.

From the repository root:

```bash
python examples/quickstart.py "/Volumes/SenzaiLab/Kai/#Recording/m19/260820/260820_3" --output ./session-index.json
```

- The first argument is the existing recording folder.
- `--output` is required. In this example script, it is resolved relative to
  your terminal's working directory. The command above writes `session-index.json`
  in the repository root, outside the recording directory.
- The script prints each label, its count, and each root-relative path.
- It adds custom rules for notes (`*.txt`, `*.md`) and `sync_data.json`.
- It groups the five analysis output folders under `analysis`, collecting each
  as one asset.
- Empty custom categories remain visible with a count of zero.
- Its final line should be `Reloaded index matches: True`.

The count after a folder category counts indexed folders, not all files inside
them. For example, `oe: 1` means one recording folder regardless of its size.

Quote the recording path as shown: it contains spaces, and `#` has a special
meaning in shell commands when used outside quotes.

### 3.3 Actual output

`<checkout>` stands for the absolute path of your local repository:

```text
Root: /Volumes/SenzaiLab/Kai/#Recording/m19/260820/260820_3
basler: 0
motive_tak: 1
  260820.tak
motive_csv: 1
  260820.csv
oe: 1
  260820/Record Node 102/experiment1/recording1
kilosort: 1
  kilosort
result: 1
  data/result
notes: 1
  260820.txt
sync: 0
analysis: 5
  data/processed
  data/rfmapping
  data/spike_position
  data/spikeinterface_analyzer
  data/waveform
Saved: <checkout>/session-index.json
Reloaded index matches: True
```

The saved paths are available in
[m19-260820-3.index.json](examples/m19-260820-3.index.json). Its absolute root points
to the recording's mount location. Running the command creates a new index at
`session-index.json`.

`kilosort: 1` refers to the outer `kilosort` directory. The ProbeA output is at
`kilosort/ProbeA/kilosort_3`. `analysis: 5` counts the five folders assigned to
the custom `analysis` label.

## 4. Write your first indexing script

Create a file named `index_my_session.py`. Copy this code and change the `root`
line to your recording folder:

```python
from pathlib import Path

from project_reader_lite import Project

root = Path("/Volumes/SenzaiLab/Kai/#Recording/m19/260820/260820_3")

project = Project.scan(
    root,
    labels={
        "notes": ["*.txt", "*.md"],
        "sync": "sync_data.json",
        "analysis": [
            "data/processed",
            "data/rfmapping",
            "data/spike_position",
            "data/spikeinterface_analyzer",
            "data/waveform",
        ],
    },
)

print(f"Session root: {project.root}")
for label, paths in project.index.items():
    print(f"{label}: {len(paths)}")
    for path in paths:
        print(f"  {path}")

output = Path.cwd() / "m19-260820-3.index.json"
saved = project.save(output)
print(f"Saved index: {saved}")

loaded = Project.load(saved)
print(f"Loaded Basler videos: {len(loaded.basler)}")
```

On Windows, the root can use forward slashes or a raw string:

```python
root = Path("D:/recordings/mouse01/session01")
# Equivalent Windows spelling:
root = Path(r"D:\recordings\mouse01\session01")
```

Run the script from the terminal in the folder where you saved it:

```bash
python index_my_session.py
```

What happens, step by step:

1. `Path(...)` identifies the recording folder; it does not create that folder.
2. `Project.scan(...)` discovers supported paths under it.
3. `labels` supplies optional rules for notes and sync files. Missing matches
   produce empty lists rather than errors.
4. The loop prints every label and the absolute paths assigned to it.
5. `Path.cwd()` chooses the folder you ran the script from. `save(output)` writes
   the JSON there, using the absolute destination in `output`.
6. `Project.load(saved)` reads that index without rescanning the data.

The directory names in the `analysis` rule are specific to this recording's
layout. Replace or omit those patterns for a different layout. Later snippets
assume you already have a `project` object unless they construct one explicitly.

The shortest automatic workflow is:

```python
from project_reader_lite import Project

project = Project.scan("/absolute/path/to/your/session")
project.save()
```

This writes `<your session>/project-index.json`.

## 5. Enter paths manually

Use the constructor when you know the paths, your filenames do not match the
automatic rules, or the data drive is disconnected.

**`Project(root)` creates an empty index. `Project.scan(root)` scans a folder.**

### 5.1 Manual input for the sample session

Pass the sample session's paths directly:

```python
from pathlib import Path

from project_reader_lite import Project

project = Project(
    root="/Volumes/SenzaiLab/Kai/#Recording/m19/260820/260820_3",
    basler=[],
    motive_tak="260820.tak",
    motive_csv="260820.csv",
    oe="260820/Record Node 102/experiment1/recording1",
    kilosort="kilosort",
    result="data/result",
    others={
        "notes": "260820.txt",
        "sync": [],
        "analysis": [
            "data/processed",
            "data/rfmapping",
            "data/spike_position",
            "data/spikeinterface_analyzer",
            "data/waveform",
        ],
    },
)

saved = project.save(Path.cwd() / "m19-260820-3.manual.index.json")
print(saved)
```

`"260820.tak"` is relative to `root`. Custom labels can contain file or directory
paths. The Basler list is empty for this session.

### 5.2 Accepted inputs

Each built-in argument and each value in `others` accepts:

| Input | Example | Result |
| --- | --- | --- |
| A string | `basler="camera.avi"` | One path |
| A `Path` object | `basler=Path("camera.avi")` | One path |
| A list or another iterable | `basler=["left.avi", "right.avi"]` | Multiple paths |
| `None` | `basler=None` | Empty list |
| An empty list | `basler=[]` | Empty list |
| Omitted argument | No `basler` argument | Empty list |

Explicit inputs are not checked for existence, suffix, or file/directory type.
You can describe offline data. Use `path.exists()` to check availability later.

A project with only one category is valid:

```python
project = Project("/data/session", motive_tak="trial.tak")
print(project.motive_tak)
print(project.basler)  # []
```

### 5.3 Add entries later

```python
project.add("notes", "260820.txt")
project.add("tracking", ["260820.tak", "260820.csv"])
project.add("probe_a", "kilosort/ProbeA/kilosort_3")
```

`add()` accepts built-in and custom labels and returns the same project, so you
can chain calls:

```python
project.add("tracking_source", "260820.tak").add("tracking_export", "260820.csv")
```

Within one label, identical resolved paths are stored once, in insertion order.
Adding a duplicate does not increase the count. A path can belong to multiple
labels when you explicitly add it to each one.

`add()` appends; it does not remove earlier labels or save automatically. Call
`save()` after changing the project.

### 5.4 Explicit inputs do not expand wildcards

`basler="*.avi"` records a literal path ending in `*.avi`. To discover matching
files, use scan rules or expand the pattern yourself:

```python
from pathlib import Path

from project_reader_lite import Project

root = Path("/data/session")
project = Project(root, basler=root.glob("*.avi"))
```

`glob("*.avi")` searches the immediate folder. `rglob("*.avi")` recursively
collects matching paths when you choose to do that yourself.

## 6. Read and use indexed paths

### 6.1 Built-in categories return lists

```python
print(project.basler)
print(project.motive_tak)
print(project.motive_csv)
print(project.oe)
print(project.kilosort)
print(project.result)
```

Each item is a `pathlib.Path`. A list may display as
`[PosixPath('/data/session/camera.avi')]` on macOS/Linux or with `WindowsPath` on
Windows. Those objects describe paths, not file contents.

Print plain paths one at a time:

```python
for video in project.basler:
    print(video)
```

Read the first path only when the list is non-empty:

```python
if project.basler:
    first_video = project.basler[0]
    print(first_video.name)
    print(first_video.exists())
else:
    print("No Basler videos were indexed.")
```

`[0]` means the first list item. An empty list has no first item. Automatic
discovery follows sorted directory and file names; list order does not establish
recording chronology or TAK/CSV correspondence.

### 6.2 Access custom labels and the full index

```python
print(project["basler"])       # Equivalent to project.basler.
print(project["notes"])        # A custom label you already created.
print(project.others)          # Custom labels only.
print(project.index)           # Built-in and custom labels.
print(project.others.get("optional_report", []))
```

`project["unknown"]` raises `KeyError` if that label has not been created.
`project.others.get("unknown", [])` returns an empty list instead.

Custom labels use dictionary access. Adding `notes` does not create a
`project.notes` property. Use `project["notes"]`.

Label names are case-sensitive. `"basler"` is built in; `"Basler"` is a separate
custom label. Labels must be non-empty strings.

### 6.3 Pass paths to your analysis tools

Join paths with `/` and convert them to strings when another library requires it:

```python
if project.kilosort:
    sorting_folder = project.kilosort[0]
    spike_times_file = sorting_folder / "ProbeA" / "kilosort_3" / "spike_times.npy"
    print(spike_times_file)
    print(str(spike_times_file))
```

For the sample session, the resulting path is
`kilosort/ProbeA/kilosort_3/spike_times.npy`. If you indexed the `kilosort_3`
directory directly, use `sorting_folder / "spike_times.npy"`. Check
`spike_times_file.is_file()` before opening it.

### 6.4 Returned lists and dictionaries are copies

```python
videos = project.basler
videos.clear()  # Changes this local list only.

project.add("basler", "another_camera.avi")  # Updates the project.
```

The same copy behavior applies to `project[label]`, `project.index`, and
`project.others`. Use section 11.3 when you need to remove or relabel entries.

## 7. Define automatic labels

Use `labels` with `scan()` for patterns, and `others` with the constructor for
exact paths:

| What you have | What to use |
| --- | --- |
| An exact path | `others={"notes": "notes.txt"}` or `add("notes", "notes.txt")` |
| A naming pattern to search for | `labels={"notes": "*.txt"}` |

### 7.1 Match one or several patterns

```python
project = Project.scan(
    "/data/session",
    labels={
        "notes": ["*.txt", "*.md"],
        "sync": "sync_data.json",
        "events": "behavior/*.tsv",
        "my_analysis": "analysis/custom",
        "basler": "*.mp4",
    },
)
```

A label matches when any of its patterns matches. All labels declared in the
rules appear in the index, including those with no matching paths.

### 7.2 Pattern matching rules

Patterns use Python `fnmatchcase`:

| Pattern | What it matches |
| --- | --- |
| `notes.txt` | This basename at any visited depth |
| `*.txt` | A visited path ending in `.txt` |
| `trial_?.csv` | `trial_`, one character, then `.csv` |
| `trial_[12].csv` | `trial_1.csv` or `trial_2.csv` |
| `behavior/*.tsv` | A root-relative path under `behavior` ending in `.tsv` |
| `analysis/custom` | That exact root-relative path |

Patterns containing `/` match root-relative paths. Patterns without `/` also
match basenames at any visited depth. Use forward slashes on every platform.

Custom matching is **case-sensitive**, even on Windows. `*.csv` does not match
`trial.CSV`; use `["*.csv", "*.CSV"]` if both occur in your data.

`*` can match `/`. Therefore `behavior/*.tsv` matches both `behavior/events.tsv`
and `behavior/trial1/events.tsv`. This differs from `Path.glob` traversal.
`**/*.csv` requires a slash and misses `trial.csv` at the root; `*.csv` covers
both root-level and nested paths.

### 7.3 Priority and built-in rules

User rules are checked in dictionary insertion order. **The first matching user
rule wins** for a path. Built-in detection runs only when no user rule matches.

Place specific patterns before broad ones:

```python
project = Project.scan(
    "/data/session",
    labels={"preview": "preview.avi", "basler": "*.avi"},
)
```

This puts `preview.avi` under `preview` and other AVI files under `basler`.

`"basler": "*.mp4"` adds an MP4 convention without disabling built-in AVI
detection. Paths not matched by user rules still reach the built-in rules.

### 7.4 A matching folder is collected as one item

Rules can match files or folders. When a folder matches, the folder is recorded
and its contents are not scanned:

```python
project = Project.scan("/data/session", labels={"archive": "old_analysis"})
```

This collects the `old_analysis` folder as a whole. A rule cannot reach files
under a folder already collected as an asset.

The root folder is considered too. A `"*"` rule matches the root itself and
collects the whole session as one item; it does not mean "index every file."

### 7.5 Keep rules in your script

The saved JSON records matched paths and labels, not wildcard rules. Keep the
`labels` dictionary in your script if you want to repeat the same scan.

## 8. Understand automatic detection

The scanner uses names and a few file markers. These conventions identify likely
assets; they do not validate file contents or inspect camera-brand metadata.
Built-in name checks are case-insensitive.

### 8.1 Exact built-in rules

| Category | Automatic rule |
| --- | --- |
| `basler` | Every `.avi` file; also `.mp4`, `.mkv`, or `.mov` when the filename or immediate parent folder contains `basler`. |
| `motive_tak` | Every `.tak` file. |
| `motive_csv` | A CSV with a same-stem TAK in the same directory; a CSV with a six-digit stem such as `260921`; or a CSV whose first line has the fields `Format Version` and `Take Name`. |
| `oe` | A folder named `oe`, `open_ephys`, `open-ephys`, or `open ephys`; or a folder directly containing `structure.oebin` or a file ending in `.continuous`. |
| `kilosort` | A folder named `kilosort`, optionally followed by a numeric version such as `4` or `2.5`, or an underscore/hyphen and a suffix such as `_3` or `-output`; or a folder directly containing both `spike_times.npy` and `spike_clusters.npy`. |
| `result` | A folder named `result` or `results`. |

Folder classification checks result names first, then OE hints, then Kilosort
hints. User rules take precedence over all three.

The six-digit CSV convention checks the name's shape, not whether it is a valid
calendar date. A generic `measurements.csv` without Motive evidence is not
collected automatically. Supply it manually or assign a user rule.

TAK and CSV paths are separate lists. A TAK without a CSV is still collected;
a recognizable CSV without a TAK is also collected. List positions do not pair
the files for you.

| Example | Classification |
| --- | --- |
| `camera.avi` | `basler`, by the filename convention |
| `basler_side.mp4` or `Basler/capture.mkv` | `basler` |
| `presentation.mp4` | Unmatched unless a custom rule selects it |
| `trial.tak` and `trial.csv` in one folder | One path in each Motive list |
| `trial.tak` and `exports/trial.csv` without a Motive header | TAK is collected; the different-directory CSV does not qualify by pairing |
| `unknown/structure.oebin` | The `unknown` folder is collected as `oe` |
| `ProbeA/spike_times.npy` and `ProbeA/spike_clusters.npy` | The `ProbeA` folder is collected as `kilosort` |

### 8.2 Whole-folder collection and multiple probes

Scanning stops inside recognized OE, Kilosort, result, and custom folders. This
keeps large recording and output trees inexpensive to index.

In the sample session:

```text
260820_3/
    kilosort/
        ProbeA/kilosort_3/
```

The scanner records `260820_3/kilosort` as one asset. To index ProbeA's output
directly, provide its path:

```python
project = Project(
    "/Volumes/SenzaiLab/Kai/#Recording/m19/260820/260820_3",
    kilosort=["kilosort/ProbeA/kilosort_3"],
)
```

An outer folder named `oe` likewise becomes one asset even if it contains
multiple recordings. Under an ordinary parent such as `Record Node 102`, the
scanner descends until it reaches each recording folder with its own descriptor.
For a session with more probes, pass a list containing each probe's output
folder. This sample contains ProbeA only.

### 8.3 What the scanner skips

During traversal, it skips:

- Files and subfolders whose names begin with `.`.
- Subfolders named `__pycache__`, `node_modules`, `build`, or `dist`.
- Subfolders whose names end with `.egg-info`.
- Directory symlinks discovered beneath the scan root.
- Files that match no built-in or custom rule.

An explicitly supplied root is resolved first, including a symlink used as the
root. You can manually record paths that automatic traversal would skip.

There is no catch-all `others` bucket. You choose which extra paths matter by
naming their labels.

### 8.4 What gets read

Scanning enumerates directories. For a CSV not already identified by its name,
it reads at most the first **8 KiB** of its first line. It does not load video
frames, TAK contents, NumPy arrays, or binary recordings. It does not hash or
count the contents of recognized folder assets.

Filesystem and file-reading errors propagate to the caller. A failed scan
raises an exception instead of returning a silently incomplete index.

Format background: [Motive CSV](https://docs.optitrack.com/motive/data-export/data-export-csv),
[Open Ephys binary](https://open-ephys.github.io/gui-docs/User-Manual/Data-formats/Binary-format.html),
and [Kilosort outputs](https://kilosort.readthedocs.io/en/latest/export_files.html).

## 9. Save and load an index

### 9.1 Default and explicit destinations

```python
saved = project.save()
print(saved)
```

For a root of `/data/session`, this writes `/data/session/project-index.json`.
The return value is the absolute path of the saved file.

Choose a different destination:

```python
saved = project.save("meta/session-index.json")
```

This writes `/data/session/meta/session-index.json`. Parent folders are created
when needed. Saving to an existing filename replaces its JSON contents.

An absolute destination can be outside the session:

```python
saved = project.save("/data/catalog/session01.json")
```

### 9.2 Load from another script or notebook

```python
from project_reader_lite import Project

project = Project.load("/data/session/meta/session-index.json")
print(project.root)
print(project.basler)
print(project.others)
```

Loading reads the JSON and resolves its paths. It does not rescan the recording
or check whether each asset exists. You can load an index while data is offline.

`Project("index.json")` does not load an index. Use `Project.load(...)`.

### 9.3 Save after loading

The object does not remember the filename it was loaded from. Calling `save()`
without an argument always writes `<root>/project-index.json`.

To update the same custom index, keep and reuse its path:

```python
from pathlib import Path

from project_reader_lite import Project

index_file = Path("/data/session/meta/session-index.json")
project = Project.load(index_file)
project.add("report", "analysis/report.pdf")
project.save(index_file)
```

### 9.4 The JSON format

Index for the sample session:

```json
{
  "format": "project-reader-lite",
  "version": 1,
  "root": "/Volumes/SenzaiLab/Kai/#Recording/m19/260820/260820_3",
  "basler": [],
  "motive_tak": ["260820.tak"],
  "motive_csv": ["260820.csv"],
  "oe": ["260820/Record Node 102/experiment1/recording1"],
  "kilosort": ["kilosort"],
  "result": ["data/result"],
  "others": {
    "notes": ["260820.txt"],
    "sync": [],
    "analysis": [
      "data/processed",
      "data/rfmapping",
      "data/spike_position",
      "data/spikeinterface_analyzer",
      "data/waveform"
    ]
  }
}
```

`load()` accepts absolute and relative roots. This index uses an absolute mount
path. `save()` computes a relative root where possible: saving to
`<session>/meta/index.json` produces `"root": ".."`. A destination outside the
session can produce several `../` components, depending on its location.

Custom labels live under `others` on disk. In memory, `project.index` presents
all labels in one dictionary.

This is the lite JSON format, separate from the full Project Reader `.proj`
format. Changing a file extension does not convert formats. Use this package's
`save()` and `load()` together.

## 10. Understand paths and moving data

### 10.1 Relative paths and the current working directory

| Operation | Base for its relative path |
| --- | --- |
| `Project("session")` | Python's current working directory |
| `Project.scan("session")` | Python's current working directory |
| Constructor input `basler="camera.avi"` | The project's root |
| `project.add("notes", "notes.txt")` | The project's root |
| `project.save("meta/index.json")` | The project's root |
| `Project.load("meta/index.json")` | Python's current working directory |

`load()` is called before a project object exists, so it cannot use that object's
root. Pass an absolute path or the return value from `save()` to avoid confusion.

Check the current working directory:

```python
from pathlib import Path

print(Path.cwd())
```

If you omit `root` from the constructor, it defaults to the working directory.
Explicit absolute roots are usually easiest in notebooks and scripts. `~` is
expanded to your home directory. Paths are resolved to absolute paths in memory,
including symlink targets.

### 10.2 Moving the whole session

Paths inside the project are saved relative to the root. The root is saved
relative to the JSON file where possible. For example, moving this whole tree:

```text
/old/location/session/
    camera.avi
    meta/index.json
```

to `/new/location/session` lets you load the new location:

```python
project = Project.load("/new/location/session/meta/index.json")
print(project.basler[0])
# /new/location/session/camera.avi
```

Keep the same relationship between the data, root, and index. Moving only the
JSON to an unrelated folder changes the base for its relative paths. An index
saved outside the recording should stay at its saved location or be regenerated
when the recording moves.

### 10.3 External paths

```python
project.add("calibration", "/shared/calibration/camera.json")
```

Paths outside the root are stored as absolute paths. Moving the session does not
update those paths. Rebuild with new paths if the external data moves too.

On Windows, the root must also be stored as an absolute path when the index is
on another drive; a relative path cannot span drives.

## 11. Refresh or edit an index

### 11.1 Rescan after the data changes

An index is a snapshot. Files added later do not appear automatically. Scan again:

```python
from project_reader_lite import Project

rules = {"notes": "*.txt", "sync": "sync_data.json"}
project = Project.scan("/data/session", labels=rules)
project.add("calibration", "/shared/calibration/camera.json")
project.save("meta/index.json")
```

A new scan creates a new index. Reapply any custom rules and manual entries
you want to keep. `load()` alone does not refresh the snapshot.

### 11.2 Check that data is available

```python
for label, paths in project.index.items():
    for path in paths:
        if not path.exists():
            print(f"Missing: {label}: {path}")
```

This checks existence only, not recording completeness or file contents.

### 11.3 Remove or relabel an entry

To remove or relabel a path, edit copies of the lists and construct a replacement
project. This moves `preview.avi` out of the Basler list while preserving the
other entries:

```python
from project_reader_lite import CATEGORIES, Project

preview = (project.root / "preview.avi").resolve()
builtins = {label: project[label] for label in CATEGORIES}
custom = project.others

builtins["basler"] = [path for path in builtins["basler"] if path != preview]
custom.setdefault("preview", []).append(preview)

project = Project(project.root, **builtins, others=custom)
project.save("meta/index.json")
```

To remove the entry entirely, omit the line adding it to `custom`. For future
scans, a rule such as `{"preview": "preview.avi"}` can classify it correctly
from the start.

## 12. API reference

Public exports are `Project` and `CATEGORIES`. The latter is this tuple:

```python
("basler", "motive_tak", "motive_csv", "oe", "kilosort", "result")
```

### Constructor signature

```text
Project(root=".", *, basler=None, motive_tak=None, motive_csv=None,
        oe=None, kilosort=None, result=None, others=None)
```

- `root`: string or `Path`; defaults to the current working directory.
- Each category: string, `Path`, iterable of paths, or `None`.
- `others`: mapping from custom label names to the same accepted inputs.
- Returns a new `Project` without scanning or checking data existence.
- Built-in names cannot be keys inside `others`; use their constructor arguments.

### Methods

| Call | Returns | Behavior |
| --- | --- | --- |
| `Project.scan(root, labels=None)` | New `Project` | Scans an existing directory; `labels` is keyword-only. |
| `project.add(label, paths)` | Same `Project` | Adds paths, deduplicating within the label. |
| `project[label]` | `list[Path]` | Returns a copy; unknown labels raise `KeyError`. |
| `project.save(path="project-index.json")` | Absolute `Path` | Writes JSON; relative destinations use the project root. |
| `Project.load(path)` | New `Project` | Loads a lite version-1 JSON index without scanning. |

### Properties

| Property | Type | Meaning |
| --- | --- | --- |
| `root` | `Path` | Resolved absolute root |
| `basler`, `motive_tak`, `motive_csv`, `oe`, `kilosort`, `result` | `list[Path]` | Paths for that category; copy |
| `others` | `dict[str, list[Path]]` | Custom labels only; copy |
| `index` | `dict[str, list[Path]]` | All built-in and custom labels; copy |

Keep `root` fixed after construction. Assigning another root does not rewrite
paths already stored in the project. Create a new project or scan for a new root.

## 13. Troubleshooting

### `ModuleNotFoundError: No module named 'project_reader_lite'`

The script may be running a different Python from the one used for installation.
Check the interpreter and installed location:

```bash
python -c "import sys; print(sys.executable)"
python -m pip show project-reader-lite
python -m pip install /absolute/path/to/project-reader-lite
```

Use that same interpreter to run the script. In a notebook, use `%pip` as shown
in section 2.6. In your editor, select the environment containing the package.

### The installer cannot find `pyproject.toml`

Run `python -m pip install .` from the folder containing `pyproject.toml`, not
from the inner `project_reader_lite` folder. From elsewhere, pass the absolute
path to the folder containing `pyproject.toml`.

### Scanning raises `FileNotFoundError` or `NotADirectoryError`

Scanning needs an existing folder. Check the exact path:

```python
from pathlib import Path

root = Path("/data/session").expanduser()
print(root.resolve())
print(root.exists())
print(root.is_dir())
```

Replace placeholder paths with your actual recording. To read a saved index,
use `Project.load(...)` instead of `scan(...)`.

### A category is unexpectedly empty

Check these in order:

1. Did you call `Project.scan(root)`? `Project(root)` does not scan.
2. Is the root the folder you intended?
3. Does the item match the rules in section 8?
4. Is it under a folder already collected as one asset?
5. Is it hidden, ignored, or reached through a directory symlink?
6. Did an earlier user rule assign it to another label?

If you know the path, you can record it directly:

```python
project.add("motive_csv", "exports/tracking.csv")
```

### A generic MP4 was not recognized as Basler

Add your own camera naming convention:

```python
project = Project.scan("/data/session", labels={"basler": "camera_*.mp4"})
```

### A CSV was classified incorrectly

The six-digit convention treats date-like CSV names as Motive. Override an
unrelated file with a specific rule:

```python
project = Project.scan("/data/session", labels={"temperature": "260921.csv"})
```

A CSV with no matching TAK, six-digit name, or recognized Motive header needs
an explicit `motive_csv` rule or a manual entry.

### I expected one Kilosort entry per probe

A parent named `kilosort` is collected as one item, stopping traversal into its
probes. Supply explicit probe paths, as shown in section 8.2.

### `project.basler[0]` raises `IndexError`

The list is empty. Check `if project.basler:` first. Missing optional categories
are represented by empty lists.

### `project["notes"]` raises `KeyError`

That label has not been created. Add a path, declare a scan rule, or use
`project.others.get("notes", [])` when the label is optional.

### `others={"basler": ...}` raises `ValueError`

`basler` is built in. Use `Project(root, basler=...)` or
`project.add("basler", ...)`. `others` is for additional labels.

### Appending to `project.basler` does not change the project

Accessors return copies. Use `add()` to append, or reconstruct from edited lists
as shown in section 11.3 when removing or relabeling entries.

### An indexed file does not exist

Manual input and loading allow offline data. Check the drive is mounted and
the path has not moved. Use the existence-check loop in section 11.2. Rescan or
rebuild with current paths if the layout changed.

### Loading reports an unsupported format or version

`Expected a project-reader-lite index with version 1` means the file is not a
supported lite index. It may be a full `.proj`, unrelated JSON, or another
version. Load a file created by this package's `save()`. Invalid JSON raises
`JSONDecodeError` before format checks can run.

### `save()` created a different file after loading

The default is always `<root>/project-index.json`. Pass the same explicit path
each time to update the same custom index file.

### Does saving create a backup of the recordings?

No. It saves path references only. Transfer the actual data along with the index
when moving an experiment. Section 10 explains how relative paths behave.

### Can filenames and user labels contain Unicode?

Yes. Labels and paths support Unicode, and JSON is written as UTF-8.

### Is there a GUI or installed CLI command?

Use the Python API from a script or notebook, or run `examples/quickstart.py`
from the source checkout. The package has no GUI or installed CLI command.

## 14. Development and verification

From the repository root, install editable source for development:

```bash
python -m pip install -e .
```

An editable install uses the code in this folder, so changes are available
without reinstalling. Restart an already-running interpreter or notebook kernel
to reload modules it has imported.

Run tests:

```bash
python -m unittest discover -s tests -v
```

Run the example with your real recording and an explicit output:

```bash
python examples/quickstart.py "/Volumes/SenzaiLab/Kai/#Recording/m19/260820/260820_3" --output ./session-index.json
```

Build a wheel:

```bash
python -m pip wheel --no-deps . --wheel-dir ./dist
```

The wheel is written to `dist/` and can be installed with `python -m pip install`
followed by its path.
