# project-reader-lite

[English (en)](README.md) | **简体中文 (zh)**

此页保留原有中文快速指南。安装步骤、可直接运行的完整示例、预期输出、
API 参数说明和常见问题见 [英文完整教程](README.md)。所有示例代码使用英文。
英文教程中的完整样例使用真实的 `m19/260820/260820_3` recording，并包含实际扫描输出。

一个只管理实验数据路径的 Python package。Python 3.10+，零第三方运行依赖。
只做 **手动收录 / 自动索引 / 按类别取路径 / 保存与加载**。

## 安装

从 GitHub 直接安装：

```bash
python3 -m pip install "git+https://github.com/KaiCao2003/project-reader-lite.git"
```

也可以下载独立仓库，在包含 `pyproject.toml` 的目录运行 `python3 -m pip install .`。
如果你拿到的是其他仓库中的 `lite` 子目录，先进入该目录再运行同一命令。
不需要安装完整的 `project-reader`。

## 自动索引

```python
from project_reader_lite import Project

proj = Project.scan("/data/session")

proj.basler       # list[Path]: Basler videos
proj.motive_tak   # list[Path]: Motive .tak
proj.motive_csv   # list[Path]: Motive CSV
proj.oe           # list[Path]: Open Ephys folders
proj.kilosort     # list[Path]: Kilosort folders
proj.result       # list[Path]: result folders
proj.others       # dict[str, list[Path]]: custom labels

proj.save("meta/index.json")
proj = Project.load("/data/session/meta/index.json")
```

每类均支持多个路径，缺失的内置类别返回空列表。TAK 和 CSV 独立收录。
`proj.index` 返回全部类别的路径字典，`proj["basler"]` 与 `proj.basler` 等价。
这些返回值是副本；追加路径用 `add`。

## 手动传入

每个参数接受单个路径或路径列表；相对路径以 `root` 为基准。
手动指定的路径只记录，不要求数据当前在线，也不限制文件名或后缀。

```python
proj = Project(
    root="/data/session",
    basler=["camera_left.avi", "camera_right.avi"],
    motive_tak="trial.tak",
    motive_csv="trial.csv",
    oe="Record Node 102",
    kilosort=["sorting/ProbeA", "sorting/ProbeB"],
    result="data/result",
    others={
        "sync": "sync_data.json",
        "notes": "notes.txt",
        "my_analysis": "analysis/custom",
    },
)

proj.add("events", "events.tsv")
proj.add("basler", "camera_top.avi")
print(proj["events"])
proj.save()
```

同一类别内自动去重，保留加入顺序。一个路径可以被手动加入多个标签。
`others` 的标签不能占用 6 个内置类别名。

## 自定义自动识别规则

```python
proj = Project.scan(
    "/data/session",
    labels={
        "notes": ["*.txt", "*.md"],
        "sync": "sync_data.json",
        "events": "behavior/*.tsv",
        "my_analysis": "analysis/custom",
        "basler": "*.mp4",  # Extend or override built-in classification.
    },
)
```

规则使用 Python `fnmatch`，区分大小写。带 `/` 的规则匹配相对 `root` 的路径；
不带 `/` 的规则也匹配任意层级的文件名或文件夹名。`*` 可跨越 `/`，
例如 `behavior/*.tsv` 也匹配其子文件夹中的 TSV。
用户规则优先，多个规则命中时按字典顺序取第一个。
匹配到文件夹后整文件夹收录，不再扫描内部。
规则仅用于本次扫描；保存的 JSON 记录匹配结果。

## 内置识别规则

| 类别 | 规则（不区分大小写） |
| --- | --- |
| `basler` | 沿用实验命名约定：`.avi`；文件名或直接父目录含 `basler` 的 `.mp4` / `.mkv` / `.mov`。不读取相机品牌信息。 |
| `motive_tak` | `.tak` 文件。 |
| `motive_csv` | 同目录有同名 `.tak` 的 CSV；沿用现有项目的六位日期名 CSV；或首行包含 `Format Version` 与 `Take Name` 的 CSV。 |
| `oe` | 名为 `oe` / `open_ephys` / `open-ephys` / `open ephys` 的目录；或直接含 `structure.oebin` / `*.continuous` 的目录。 |
| `kilosort` | 名为 `kilosort`、`kilosort4`、`kilosort_3`、`kilosort-*` 等的目录；或直接同时含 `spike_times.npy` 和 `spike_clusters.npy` 的目录。 |
| `result` | 名为 `result` 或 `results` 的目录。 |
| 自定义 | `others` 手动路径或 `labels` 匹配规则。 |

OE、Kilosort、result 和自定义目录均作为一个条目，遇到后停止向下扫描。
例如顶层 `kilosort/` 下有多个 probe 时收录整个 `kilosort/`；也可以手动指定各 probe。
未匹配的文件不收录。隐藏文件/目录、常见构建缓存和目录符号链接跳过。
扫描错误会抛出异常，不会静默返回部分结果。

扫描只列出路径，至多读取待识别 CSV 首行的 8 KiB；不加载视频、TAK 或神经数据，
也不统计或 hash 大文件夹内容。
格式依据：[Motive CSV](https://docs.optitrack.com/motive/data-export/data-export-csv)、
[Open Ephys binary](https://open-ephys.github.io/gui-docs/User-Manual/Data-formats/Binary-format.html)、
[Kilosort outputs](https://kilosort.readthedocs.io/en/latest/export_files.html)。

## 保存格式

默认保存到 `<root>/project-index.json`。JSON 仅包含格式版本、root、6 类路径列表和
`others` 字典。项目内路径相对 root 保存，项目外路径保留绝对路径。
root 相对索引文件保存，所以整个项目连同索引文件一起移动后仍可加载。
此格式独立于完整版 `.proj`；使用 `Project.load` 加载 lite JSON。
加载时不重扫、不检查数据是否存在。

## 验证

安装后在仓库根目录运行：

```bash
python3 -m unittest discover -s tests -v
```
