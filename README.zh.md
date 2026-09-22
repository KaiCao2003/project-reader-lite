# project-reader-lite

[en](README.md) | **zh**

`project-reader-lite` 按类别索引实验文件和文件夹。可以扫描 recording 目录自动识别，
也可以手动传入路径，再将索引保存为 JSON，供 Python 脚本或 notebook 加载。

需要 **Python 3.10 或更新版本**，**无第三方运行依赖**。

已有 Python 和 Git 时，可以直接安装：

```bash
python -m pip install "git+https://github.com/KaiCao2003/project-reader-lite.git"
```

支持以下 7 组数据：

| 数据 | Python 属性 | 返回内容 |
| --- | --- | --- |
| Basler 相机录像 | `project.basler` | 视频路径列表 |
| Motive TAK | `project.motive_tak` | `.tak` 路径列表 |
| Motive CSV | `project.motive_csv` | CSV 路径列表 |
| Open Ephys | `project.oe` | recording 文件夹路径列表 |
| Kilosort | `project.kilosort` | 输出文件夹路径列表 |
| Result | `project.result` | 结果文件夹路径列表 |
| 自定义标签 | `project.others` | 标签到路径列表的字典 |

每个内置类别都可以为空，也可以包含多个路径。

## 目录

1. [索引里有什么](#1-索引里有什么)
2. [安装](#2-安装)
3. [运行真实数据样例](#3-运行真实数据样例)
4. [编写索引脚本](#4-编写索引脚本)
5. [手动输入路径](#5-手动输入路径)
6. [读取和使用路径](#6-读取和使用路径)
7. [自定义自动识别规则](#7-自定义自动识别规则)
8. [内置识别规则](#8-内置识别规则)
9. [保存与加载](#9-保存与加载)
10. [相对路径与移动数据](#10-相对路径与移动数据)
11. [更新删除和改标签](#11-更新删除和改标签)
12. [API 参考](#12-api-参考)
13. [常见问题](#13-常见问题)
14. [开发与验证](#14-开发与验证)

## 1. 索引里有什么

索引记录数据存放的位置，并用标签分组。它不会复制、移动、重命名或修改被索引的数据。

| 名称 | 含义 | 例子 |
| --- | --- | --- |
| `root` | 项目根目录，相对数据路径的起点 | `/data/session` |
| Path | 一个文件或文件夹的位置 | `/data/session/trial.tak` |
| Label | 一组路径的名称 | `motive_tak`、`notes`、`sync` |
| 索引文件 | `save()` 写出的 JSON | `/data/session/meta/index.json` |

```python
from project_reader_lite import Project

root = "/Volumes/SenzaiLab/Kai/#Recording/m19/260820/260820_3"
project = Project.scan(root)
project.add("notes", "260820.txt")
print(project.motive_tak)
```

把 `root` 换成你机器上的 recording 目录。使用 `/data/session` 的例子也需要替换路径。

扫描时会读取目录名称，必要时读取一小段 CSV 表头。返回的 `Path` 对象可以交给
视频、tracking 或电生理分析工具，用于加载具体数据。

## 2. 安装

### 2.1 命令在哪里运行

- `python -m pip install ...` 这样的命令在**终端**运行。
- `from project_reader_lite import Project` 这样的代码在 **Python 脚本、Python 交互环境
  或 notebook 单元格**中运行。

macOS 可以打开 Terminal；Windows 可以打开 PowerShell；Linux 使用终端。

下载后的仓库结构如下：

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

**仓库根目录**是包含 `pyproject.toml` 的 `project-reader-lite` 文件夹。
安装、运行样例和测试时，从这个目录执行命令。

### 2.2 macOS / Linux

检查 Python 版本：

```bash
python3 --version
```

版本应为 3.10 或更新版本。下载并进入仓库：

```bash
git clone https://github.com/KaiCao2003/project-reader-lite.git
cd project-reader-lite
```

也可以在 GitHub 点击 **Code → Download ZIP**，解压后在终端进入该文件夹。
解压后的文件夹名可能带有 `-main`。

创建虚拟环境、激活并安装：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

虚拟环境为这个项目单独存放 Python 包。激活后，`python` 使用该环境。
以后重新打开终端时，再进入仓库并激活：

```bash
cd /path/to/project-reader-lite
source .venv/bin/activate
```

路径中有空格时加引号，例如：

```bash
cd "/Users/alex/My Projects/project-reader-lite"
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

如果下载的是 ZIP，先进入解压后的目录，再运行虚拟环境和安装命令。

如果 PowerShell 阻止激活脚本，可以直接调用虚拟环境里的 Python：

```powershell
.\.venv\Scripts\python.exe -m pip install .
.\.venv\Scripts\python.exe -c "from project_reader_lite import Project; print('Import OK')"
```

使用这种方式时，后续终端命令中的 `python` 也替换为
`.\.venv\Scripts\python.exe`。

### 2.4 确认安装成功

在同一个终端运行：

```bash
python -c "from project_reader_lite import Project; print('Import OK')"
```

预期输出：

```text
Import OK
```

安装名和导入名不同：

| 用途 | 名称 |
| --- | --- |
| 安装包名称 | `project-reader-lite` |
| Python 导入名 | `project_reader_lite` |
| 使用的类 | `Project` |

导入写法：

```python
from project_reader_lite import Project
```

### 2.5 从本地目录或 wheel 安装

本地目录应包含 `pyproject.toml`：

```bash
python -m pip install /absolute/path/to/project-reader-lite
```

安装下载好的 wheel：

```bash
python -m pip install /absolute/path/to/project_reader_lite-0.1.0-py3-none-any.whl
```

从 GitHub URL 安装需要 Git；从本地目录或 wheel 安装不需要 Git。
运行 `examples/quickstart.py` 需要下载或 clone 仓库源码。

### 2.6 Jupyter notebook

在 notebook 单元格内安装到当前 kernel 对应的环境：

```python
%pip install /absolute/path/to/project-reader-lite
```

然后在另一个单元格中导入：

```python
from project_reader_lite import Project
```

`%pip` 是 notebook 命令，不能直接放入普通 `.py` 脚本。
如果升级前已经导入过这个包，升级后重启 kernel 再导入。

## 3. 运行真实数据样例

### 3.1 Recording 目录

样例使用 `m19/260820/260820_3`，扫描时间为 **2026-09-21**：

```text
/Volumes/SenzaiLab/Kai/#Recording/m19/260820/260820_3
```

相关文件和文件夹：

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

这次扫描的 `basler` 和 `sync` 列表为空。已识别的文件夹按整体收录，内部文件不再参与扫描。

### 3.2 执行样例

[quickstart.py](examples/quickstart.py) 扫描目录、打印路径、保存索引，再重新加载并核对结果。

在仓库根目录运行：

```bash
python examples/quickstart.py "/Volumes/SenzaiLab/Kai/#Recording/m19/260820/260820_3" --output ./session-index.json
```

参数含义：

- 第一个参数是已存在的 recording 目录，使用其他数据时替换这个路径。
- `--output` 是必填的 JSON 输出路径。样例脚本把它相对**终端当前目录**解析。
  上面的命令会在仓库根目录写入 `session-index.json`。
- 脚本使用 `notes` 规则收录 `*.txt` / `*.md`，使用 `sync` 收录 `sync_data.json`，
  并把 5 个分析文件夹归入 `analysis`。
- 每个类别后的数字是索引条目数。`oe: 1` 表示一个 recording 文件夹，
  不代表这个文件夹里只有一个文件。

路径包含空格时要加引号；路径中的 `#` 也应放在引号内。

### 3.3 实际输出

`<checkout>` 表示你本地仓库的绝对路径：

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

[m19-260820-3.index.json](examples/m19-260820-3.index.json) 保存了这次扫描的路径。
其中的绝对 `root` 指向数据盘的挂载位置。运行命令会在指定位置写入新的索引。

`kilosort: 1` 对应外层 `kilosort` 目录；ProbeA 的输出在
`kilosort/ProbeA/kilosort_3`。`analysis: 5` 表示自定义标签下收录了 5 个文件夹。

## 4. 编写索引脚本

新建 `index_my_session.py`，复制以下代码，把 `root` 换成你的 recording 目录：

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

在脚本所在目录运行：

```bash
python index_my_session.py
```

这段代码依次完成：

1. 用 `Path(...)` 指定已有数据目录。
2. 用 `Project.scan(...)` 发现数据路径。
3. 用 `labels` 匹配笔记、sync 文件和分析目录；没有匹配项时得到空列表。
4. 遍历 `project.index` 打印标签、数量和路径。
5. 用 `Path.cwd()` 获取当前工作目录，把索引写到该目录。
6. 用 `Project.load(saved)` 读取保存的索引。

`analysis` 中的目录名称对应样例数据。换一套目录结构时，修改或删除这些规则。
后续短代码块沿用已创建的 `project` 对象。

Windows 路径可以写成正斜杠形式，或使用带 `r` 前缀的字符串：

```python
root = Path("D:/recordings/mouse01/session01")
# Equivalent Windows spelling:
root = Path(r"D:\recordings\mouse01\session01")
```

只扫描并保存到数据目录的最短写法：

```python
from project_reader_lite import Project

project = Project.scan("/absolute/path/to/your/session")
project.save()
```

保存位置是 `<session>/project-index.json`。

## 5. 手动输入路径

已知文件位置、文件名不符合自动规则，或者数据盘离线时，可以直接调用构造函数。

**`Project(root)` 创建空索引；`Project.scan(root)` 扫描目录。**

### 5.1 手动输入样例数据

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

`"260820.tak"` 相对 `root` 解析。自定义标签既能收录文件，也能收录文件夹。
这个 session 的 Basler 列表为空。

### 5.2 每个参数接受什么

内置类别参数，以及 `others` 中每个标签的值，都支持以下形式：

| 输入 | 例子 | 结果 |
| --- | --- | --- |
| 一个字符串 | `basler="camera.avi"` | 一个路径 |
| 一个 `Path` | `basler=Path("camera.avi")` | 一个路径 |
| 列表或其他可迭代对象 | `basler=["left.avi", "right.avi"]` | 多个路径 |
| `None` | `basler=None` | 空列表 |
| 空列表 | `basler=[]` | 空列表 |
| 不传这个参数 | 省略 `basler` | 空列表 |

手动路径不检查是否存在、后缀是否匹配，或路径指向文件还是文件夹。
需要检查当前是否可用时，调用 `path.exists()`。

只有一个类别也可以创建项目：

```python
project = Project("/data/session", motive_tak="trial.tak")
print(project.motive_tak)
print(project.basler)  # []
```

### 5.3 后续追加路径

```python
project.add("notes", "260820.txt")
project.add("tracking", ["260820.tak", "260820.csv"])
project.add("probe_a", "kilosort/ProbeA/kilosort_3")
```

`add()` 支持内置类别和自定义标签，返回同一个 `Project`，因此也可以连续调用：

```python
project.add("tracking_source", "260820.tak").add("tracking_export", "260820.csv")
```

同一标签下，相同的解析后路径只保存一次，顺序按首次加入的顺序排列。
同一个路径可以被手动加入多个标签。`add()` 只追加，不会删除原标签中的记录。
修改后需要调用 `save()` 才会更新 JSON。

### 5.4 手动路径不会展开通配符

`basler="*.avi"` 会记录一个字面值为 `*.avi` 的路径。
按规则找文件可以使用 `scan(..., labels=...)`，或先用 `Path.glob()` 查找：

```python
from pathlib import Path

from project_reader_lite import Project

root = Path("/data/session")
project = Project(root, basler=root.glob("*.avi"))
```

`glob("*.avi")` 搜索当前目录；`rglob("*.avi")` 会递归搜索子目录。

## 6. 读取和使用路径

### 6.1 内置类别返回列表

```python
print(project.basler)
print(project.motive_tak)
print(project.motive_csv)
print(project.oe)
print(project.kilosort)
print(project.result)
```

列表元素是 `pathlib.Path` 对象。macOS / Linux 上打印列表时可能看到
`PosixPath(...)`，Windows 上可能看到 `WindowsPath(...)`。

逐个打印路径：

```python
for video in project.basler:
    print(video)
```

取第一个路径前，先检查列表是否为空：

```python
if project.basler:
    first_video = project.basler[0]
    print(first_video.name)
    print(first_video.exists())
else:
    print("No Basler videos were indexed.")
```

`[0]` 表示第一个元素；空列表没有这个元素。自动扫描按目录和文件名称排序遍历，
列表顺序不表示录制时间，也不表示 TAK 和 CSV 一一对应。

### 6.2 自定义标签与完整索引

```python
print(project["basler"])
print(project["notes"])
print(project.others)
print(project.index)
print(project.others.get("optional_report", []))
```

- `project["basler"]` 与 `project.basler` 等价。
- `project["notes"]` 返回已创建的自定义标签。
- `project.others` 只包含自定义标签。
- `project.index` 包含全部内置类别和自定义标签。
- 未创建的标签用 `project[label]` 访问会抛出 `KeyError`。
  允许标签缺失时，可以使用 `project.others.get(label, [])`。

自定义标签使用方括号访问，创建 `notes` 不会增加 `project.notes` 属性。
标签区分大小写：`basler` 是内置类别，`Basler` 是另一个自定义标签。

### 6.3 将路径交给分析程序

用 `/` 拼接文件路径，用 `str()` 转换成字符串：

```python
if project.kilosort:
    sorting_folder = project.kilosort[0]
    spike_times_file = sorting_folder / "ProbeA" / "kilosort_3" / "spike_times.npy"
    print(spike_times_file)
    print(str(spike_times_file))
```

这对应样例的自动索引：外层 `kilosort` 下还有 `ProbeA/kilosort_3`。
如果手动索引的已经是 `kilosort_3` 目录，则使用
`sorting_folder / "spike_times.npy"`。打开前可以用 `spike_times_file.is_file()` 检查。

### 6.4 返回值是副本

```python
videos = project.basler
videos.clear()  # Changes this local list only.

project.add("basler", "another_camera.avi")  # Updates the project.
```

直接修改 `project.basler`、`project[label]`、`project.index` 或 `project.others`
返回的列表或字典，不会改变项目里的记录。追加使用 `add()`；删除和改标签的方法见第 11 节。

## 7. 自定义自动识别规则

| 需求 | 写法 |
| --- | --- |
| 已知一个确定路径 | `others={"notes": "notes.txt"}` 或 `add("notes", "notes.txt")` |
| 扫描时按名称匹配 | `labels={"notes": "*.txt"}` |

### 7.1 单个或多个匹配规则

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

一个标签有多个规则时，任一规则匹配即可。声明过但没有匹配项的标签仍会出现在索引中，
值为空列表。

### 7.2 匹配方式

规则使用 Python `fnmatchcase`：

| 规则 | 匹配内容 |
| --- | --- |
| `notes.txt` | 扫描到的任意层级中名为 `notes.txt` 的条目 |
| `*.txt` | 以 `.txt` 结尾的路径 |
| `trial_?.csv` | `trial_` 后面跟一个字符，再跟 `.csv` |
| `trial_[12].csv` | `trial_1.csv` 或 `trial_2.csv` |
| `behavior/*.tsv` | `behavior` 下以 `.tsv` 结尾的相对路径 |
| `analysis/custom` | 这个确定的相对路径 |

包含 `/` 的规则匹配相对 `root` 的路径。不包含 `/` 的规则也匹配任意层级的文件名或目录名。
所有平台都用正斜杠 `/` 写规则。

自定义规则**区分大小写**，Windows 上也一样。`*.csv` 不匹配 `trial.CSV`；
需要同时匹配时写 `["*.csv", "*.CSV"]`。

这里的 `*` 可以跨越 `/`，因此 `behavior/*.tsv` 同时匹配
`behavior/events.tsv` 和 `behavior/trial1/events.tsv`。
`**/*.csv` 要求路径里有 `/`，会漏掉根目录的 `trial.csv`；`*.csv` 可以匹配两种位置。

### 7.3 规则优先级

用户规则按字典中的顺序检查，**第一个匹配的标签生效**。
没有用户规则匹配时，才使用内置规则。具体规则应放在宽泛规则前面：

```python
project = Project.scan(
    "/data/session",
    labels={"preview": "preview.avi", "basler": "*.avi"},
)
```

`preview.avi` 归入 `preview`，其他 AVI 归入 `basler`。

`"basler": "*.mp4"` 会增加 MP4 的收录规则；原本的 AVI 内置识别仍然有效。

### 7.4 文件夹匹配后停止向下扫描

```python
project = Project.scan("/data/session", labels={"archive": "old_analysis"})
```

如果 `old_analysis` 是文件夹，就把整个文件夹收录为一个条目。
其内部文件不会继续被其他规则匹配。根目录本身也会参与匹配，所以规则 `"*"`
会直接收录整个根目录。

保存的 JSON 记录标签和匹配结果，不保存规则。需要重复扫描时，把 `labels` 字典留在脚本中。

## 8. 内置识别规则

内置规则按名称或标志文件识别，名称匹配不区分大小写。

| 类别 | 自动识别条件 |
| --- | --- |
| `basler` | `.avi`；文件名或直接父目录名称包含 `basler` 的 `.mp4` / `.mkv` / `.mov`。 |
| `motive_tak` | `.tak` 文件。 |
| `motive_csv` | 同目录有同名 TAK 的 CSV；文件名主体为六位数字的 CSV；或首行包含 `Format Version` 与 `Take Name` 字段的 CSV。 |
| `oe` | 名为 `oe`、`open_ephys`、`open-ephys`、`open ephys` 的文件夹；或直接包含 `structure.oebin` / `*.continuous` 的文件夹。 |
| `kilosort` | 名为 `kilosort`，可带数字版本如 `4` / `2.5`，或下划线、连字符后缀如 `_3` / `-output` 的文件夹；或直接同时包含 `spike_times.npy` 和 `spike_clusters.npy` 的文件夹。 |
| `result` | 名为 `result` 或 `results` 的文件夹。 |

文件夹内置判断顺序是 result、OE、Kilosort；用户规则优先于这些判断。

六位数字 CSV 只检查名称形式，不检查是否为有效日期。
普通 CSV 没有匹配的 TAK 或 Motive 表头时，需要手动添加或自定义规则。
Basler 视频按命名约定识别，不读取相机品牌信息。

TAK 与 CSV 独立收录。只有 TAK 或只有可识别的 Motive CSV 都可以建立索引。
程序不会自动配对两个列表中的同一位置。

### 8.1 为什么多个 probe 可能只显示一个 Kilosort 条目

样例的结构是：

```text
260820_3/
    kilosort/
        ProbeA/kilosort_3/
```

外层 `kilosort` 已被识别，因此扫描会在这里停止。需要直接索引 ProbeA 的输出时，手动指定：

```python
project = Project(
    "/Volumes/SenzaiLab/Kai/#Recording/m19/260820/260820_3",
    kilosort=["kilosort/ProbeA/kilosort_3"],
)
```

有多个 probe 时，把每个实际输出目录加入列表。
同样，外层目录如果叫 `oe`，会整体收录；如果外层叫 `Record Node 102`，
程序会继续向下找到包含 descriptor 的各个 recording。

### 8.2 跳过哪些目录和文件

- 名称以 `.` 开头的文件和子目录。
- `__pycache__`、`node_modules`、`build`、`dist` 子目录。
- 以 `.egg-info` 结尾的子目录。
- 扫描根目录下面发现的目录符号链接。
- 没有任何内置或用户规则匹配的文件。

显式传入的根目录会先解析到实际路径，因此可以把符号链接作为根目录。
手动输入也可以记录自动扫描时会被跳过的路径。

未识别文件不会自动归入 `others`；额外数据需要用户指定标签。

### 8.3 扫描读取多少数据

扫描会列出目录。名称无法识别的 CSV 最多读取首行的 **8 KiB**。
视频、TAK、NumPy 数组和二进制 recording 不会被加载。
已收录文件夹内部不会继续统计文件数、计算大小或 hash。

读取失败会抛出异常，不会静默返回不完整的索引。

格式参考：[Motive CSV](https://docs.optitrack.com/motive/data-export/data-export-csv)、
[Open Ephys binary](https://open-ephys.github.io/gui-docs/User-Manual/Data-formats/Binary-format.html)、
[Kilosort outputs](https://kilosort.readthedocs.io/en/latest/export_files.html)。

## 9. 保存与加载

### 9.1 选择保存位置

```python
saved = project.save()
print(saved)
```

默认写入 `<root>/project-index.json`，返回保存文件的绝对 `Path`。

相对路径以项目的 `root` 为基准：

```python
saved = project.save("meta/session-index.json")
```

对于 `/data/session`，输出是 `/data/session/meta/session-index.json`。
需要的父目录会自动创建，已有同名 JSON 会被覆盖。

也可以保存到项目外的绝对路径：

```python
saved = project.save("/data/catalog/session01.json")
```

### 9.2 加载保存的索引

```python
from project_reader_lite import Project

project = Project.load("/data/session/meta/session-index.json")
print(project.root)
print(project.basler)
print(project.others)
```

加载只读取 JSON 并解析路径，不重新扫描、不检查每个数据文件是否存在。
数据盘离线时仍然可以查看索引。

`Project("index.json")` 不会加载文件；加载必须调用 `Project.load(...)`。

### 9.3 加载后写回同一个文件

`save()` 不记住上一次加载或保存的文件名。不传参数时，始终写入
`<root>/project-index.json`。要更新指定索引，保存它的路径并再次传入：

```python
from pathlib import Path

from project_reader_lite import Project

index_file = Path("/data/session/meta/session-index.json")
project = Project.load(index_file)
project.add("report", "analysis/report.pdf")
project.save(index_file)
```

### 9.4 JSON 结构

样例 session 的索引：

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

`load()` 接受绝对或相对 `root`。这个索引使用数据盘的绝对路径。
`save()` 会尽可能计算相对路径：保存到 `<session>/meta/index.json` 时，
`root` 为 `".."`，表示 `meta` 的父目录。保存到项目外部时，可能出现多个 `../`。

磁盘上的自定义标签放在 `others` 中；内存中的 `project.index` 则把所有标签放在一个字典中。

此 JSON 格式与完整 Project Reader 的 `.proj` 格式不同，修改后缀不能转换格式。
请用本包的 `save()` 和 `load()` 保存、读取索引。

## 10. 相对路径与移动数据

### 10.1 相对路径从哪里开始

| 操作 | 相对路径的基准 |
| --- | --- |
| `Project("session")` | Python 当前工作目录 |
| `Project.scan("session")` | Python 当前工作目录 |
| 构造参数 `basler="camera.avi"` | 项目的 `root` |
| `project.add("notes", "notes.txt")` | 项目的 `root` |
| `project.save("meta/index.json")` | 项目的 `root` |
| `Project.load("meta/index.json")` | Python 当前工作目录 |

特别注意：`load()` 使用当前工作目录，`save()` 使用项目的根目录。
使用绝对路径或 `save()` 的返回值，可以避免混淆。

查看当前工作目录：

```python
from pathlib import Path

print(Path.cwd())
```

构造时省略 `root`，默认使用当前工作目录。`~` 会展开为用户主目录。
内存中的路径会解析为绝对路径，包括符号链接的目标位置。

### 10.2 移动整个 session

项目内的数据路径相对 `root` 保存，`root` 尽可能相对 JSON 文件保存。
例如原本的结构：

```text
/old/location/session/
    camera.avi
    meta/index.json
```

整体移动到 `/new/location/session` 后：

```python
project = Project.load("/new/location/session/meta/index.json")
print(project.basler[0])
# /new/location/session/camera.avi
```

需要保持数据、根目录和索引之间的相对位置。只移动 JSON 到一个不相关的目录，
会改变相对路径的解析起点。索引放在 session 外时，移动数据后应重新生成索引。

### 10.3 项目外的数据

```python
project.add("calibration", "/shared/calibration/camera.json")
```

项目外路径按绝对路径保存，移动 session 不会自动更新这些路径。
外部文件也移动时，需要使用新路径重建记录。

Windows 上，如果索引与数据根目录在不同盘符，`root` 也会保存为绝对路径。

## 11. 更新、删除和改标签

### 11.1 数据变化后重新扫描

索引是扫描时的快照，新文件不会自动出现。重新扫描并保存：

```python
from project_reader_lite import Project

rules = {"notes": "*.txt", "sync": "sync_data.json"}
project = Project.scan("/data/session", labels=rules)
project.add("calibration", "/shared/calibration/camera.json")
project.save("meta/index.json")
```

重新扫描会创建新索引；需要保留的自定义规则和手动条目，应再次传入。
`load()` 只加载已有快照。

### 11.2 检查文件是否还在

```python
for label, paths in project.index.items():
    for path in paths:
        if not path.exists():
            print(f"Missing: {label}: {path}")
```

这只检查路径是否存在，不验证 recording 是否完整或文件内容是否有效。

### 11.3 删除或修改标签

编辑列表副本，再构造一个替换项目。下面把 `preview.avi` 从 Basler 列表移到 `preview` 标签：

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

只想删除该条目时，去掉加入 `custom` 的那一行。
以后的扫描也可以直接用 `{"preview": "preview.avi"}` 分类。

## 12. API 参考

可导入的公开对象为 `Project` 和 `CATEGORIES`。
`CATEGORIES` 是下面的元组：

```python
("basler", "motive_tak", "motive_csv", "oe", "kilosort", "result")
```

### 构造函数

```text
Project(root=".", *, basler=None, motive_tak=None, motive_csv=None,
        oe=None, kilosort=None, result=None, others=None)
```

- `root`：字符串或 `Path`，默认当前工作目录。
- 每个内置类别：一个路径、多个路径的可迭代对象或 `None`。
- `others`：自定义标签到上述路径输入的映射。
- 构造函数不扫描、不检查数据是否存在。
- `others` 的键不能占用 6 个内置名称；这些名称应通过同名构造参数传入。

### 方法

| 调用 | 返回 | 作用 |
| --- | --- | --- |
| `Project.scan(root, labels=None)` | 新的 `Project` | 扫描已有目录；`labels` 必须以关键字参数传入 |
| `project.add(label, paths)` | 同一个 `Project` | 追加路径，同一标签内去重 |
| `project[label]` | `list[Path]` | 返回副本；未知标签抛出 `KeyError` |
| `project.save(path="project-index.json")` | 绝对 `Path` | 写入 JSON；相对目标路径以 `root` 为基准 |
| `Project.load(path)` | 新的 `Project` | 加载 version 1 的索引，不重新扫描 |

### 属性

| 属性 | 类型 | 含义 |
| --- | --- | --- |
| `root` | `Path` | 解析后的绝对根目录 |
| `basler`、`motive_tak`、`motive_csv`、`oe`、`kilosort`、`result` | `list[Path]` | 对应类别的路径列表副本 |
| `others` | `dict[str, list[Path]]` | 自定义标签字典副本 |
| `index` | `dict[str, list[Path]]` | 全部类别和标签的字典副本 |

创建项目后不要直接改变 `root` 来迁移索引，因为已有路径不会随之更新。
换根目录时，重新扫描或重新构造项目。

## 13. 常见问题

### 导入时报 `ModuleNotFoundError`

运行脚本的 Python 可能不是安装包时使用的 Python。在终端检查：

```bash
python -c "import sys; print(sys.executable)"
python -m pip show project-reader-lite
python -m pip install /absolute/path/to/project-reader-lite
```

使用同一个 Python 安装和运行。notebook 中使用 `%pip`；编辑器中选择对应的 Python 环境。

### 安装时找不到 `pyproject.toml`

进入包含 `pyproject.toml` 的目录再执行 `python -m pip install .`。
不要进入内部的 `project_reader_lite` 包目录执行这条安装命令。

### 扫描时报 `FileNotFoundError` 或 `NotADirectoryError`

扫描要求传入已有文件夹。检查路径：

```python
from pathlib import Path

root = Path("/data/session").expanduser()
print(root.resolve())
print(root.exists())
print(root.is_dir())
```

确认已经替换示例路径，且数据盘已挂载。如果目标是 JSON 索引，使用 `Project.load(...)`。

### 某一类结果为空

依次检查：

1. 是否调用了 `Project.scan(root)`；`Project(root)` 本身不扫描。
2. 根目录是否正确。
3. 文件名称或标志文件是否满足第 8 节的规则。
4. 它是否位于一个已经整体收录的文件夹内部。
5. 它是否被隐藏目录、缓存目录或目录符号链接规则跳过。
6. 是否被更靠前的用户规则归入其他标签。

知道确切路径时可以直接添加：

```python
project.add("motive_csv", "exports/tracking.csv")
```

### MP4 没有识别成 Basler

通用 MP4 名称不会自动判定为 Basler。按你的命名方式增加规则：

```python
project = Project.scan("/data/session", labels={"basler": "camera_*.mp4"})
```

### CSV 分类不符合预期

六位数字 CSV 名称会触发 Motive 规则。其他用途的同名 CSV 可以显式覆盖：

```python
project = Project.scan("/data/session", labels={"temperature": "260921.csv"})
```

需要收录但没有同名 TAK、六位数字文件名或 Motive 表头的 CSV，
使用 `motive_csv` 自定义规则或手动添加。

### 多个 probe 只显示一个 Kilosort 文件夹

外层 `kilosort` 被整体收录后，内部 probe 不再扫描。
需要逐个 probe 时，手动传入各个输出目录。

### `project.basler[0]` 报 `IndexError`

列表为空。先检查 `if project.basler:` 再取第一个元素。

### `project["notes"]` 报 `KeyError`

这个标签还没有创建。手动添加、声明扫描规则，或者使用
`project.others.get("notes", [])` 允许它缺失。

### `others={"basler": ...}` 报 `ValueError`

`basler` 是内置类别。使用 `Project(root, basler=...)` 或
`project.add("basler", ...)`。

### 修改 `project.basler` 或 `project.index` 没有效果

返回值是副本。追加条目使用 `add()`；删除和改标签使用第 11.3 节的重建方式。

### 索引里的路径不存在

手动输入和加载允许离线数据。检查挂载状态和文件位置；目录结构变化后，
重新扫描或用新的路径重建。

### 加载时报格式或版本不支持

`Expected a project-reader-lite index with version 1` 表示不是支持的索引格式或版本。
加载本包 `save()` 生成的文件；如果 JSON 本身格式损坏，会先抛出 `JSONDecodeError`。

### 加载后 `save()` 写出了另一个文件

默认目标始终是 `<root>/project-index.json`。要更新同一个自定义文件，
每次调用 `save()` 都传入它的路径。

### 保存索引是否备份了原始数据

没有。JSON 只保存路径。搬迁实验时，需要同时搬迁数据文件，并保持相关的目录结构。

### 标签和文件名能否包含非英文字符

可以。标签和路径支持 Unicode，JSON 使用 UTF-8 保存。

### 有没有 GUI 或安装后的命令行命令

通过 Python 脚本或 notebook 调用 API，或在源码目录运行 `examples/quickstart.py`。
包本身不提供 GUI 或安装后的 CLI 命令。

## 14. 开发与验证

在仓库根目录安装可编辑源码：

```bash
python -m pip install -e .
```

这种安装方式直接使用当前目录中的代码。代码修改后不必重新安装；
已经导入过模块的 Python 进程或 notebook kernel 需要重启。

运行测试：

```bash
python -m unittest discover -s tests -v
```

运行 recording 样例：

```bash
python examples/quickstart.py "/Volumes/SenzaiLab/Kai/#Recording/m19/260820/260820_3" --output ./session-index.json
```

构建 wheel：

```bash
python -m pip wheel --no-deps . --wheel-dir ./dist
```

wheel 写入 `dist/`。用 `python -m pip install` 加上 wheel 路径即可安装。
