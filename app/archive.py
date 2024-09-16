import shutil
import subprocess
import tempfile
from pathlib import Path

from werkzeug.datastructures import FileStorage

from app.charts import KSHDoc


class ArchiveExtender:
    """
    Helper class to populate the extended attributes of an archive. `on_start`
    is called before any files are processed. `on_file` is called for each file
    in the archive. `on_end` is called after all files have been processed.
    Setting values in `self.attributes` will populate the extended attributes
    of the archive.
    """

    def __init__(self) -> None:
        self.attributes = {}

    def on_file(self, path: Path):
        """
        path is a Path object pointing to a file extracted from the archive,
        currently in a temporary directory.
        """
        pass

    def on_start(self, path: Path):
        """
        path is a Path object pointing to the temporary directory where the
        archive has been extracted.
        """
        pass

    def on_end(self, path: Path):
        """
        path is a Path object pointing to the temporary directory where the
        archive has been extracted.
        """
        pass


class SDVXArchive(ArchiveExtender):
    def on_start(self, path: Path):
        self.charts = []

    def on_end(self, path: Path):
        if not self.charts:
            raise ValueError("No charts found")
        charts = sorted(self.charts, key=lambda c: c.level)
        self.attributes = {
            "title": charts[0].title,
            "artist": charts[0].artist,
            "charts": [
                {
                    "level": chart.level,
                    "difficulty": chart.difficulty,
                    "path": str(chart.path.relative_to(path)),
                }
                for chart in charts
            ],
            "illustration": charts[0].jacket,
        }

    def handle_ksh(self, path: Path):
        doc = KSHDoc(path)
        doc.path = path
        self.charts.append(doc)

    def on_file(self, path: Path):
        if path.suffix == ".ksh":
            self.handle_ksh(path)


def run(*cmd):
    subprocess.run(cmd, check=True, capture_output=True)


def flatten_dir(path: Path):
    max = 100
    while True:
        subfolder = None
        for f in path.iterdir():
            if f.is_file():
                return
            if f.is_dir():
                if subfolder:
                    raise ValueError("Multiple subfolders before files")
                subfolder = f
        if not subfolder:
            return
        for f in subfolder.iterdir():
            f.rename(path / f.name)
        subfolder.rmdir()
        max -= 1
        if max <= 0:
            raise ValueError("Too many subfolders")


def extract(
    file: FileStorage, to, extender: type[ArchiveExtender] = SDVXArchive
):
    """
    Extract an archive to a directory.
    Returns a dict with information about the extracted files.
    The "extended_attributes" contains the extra metadata populated by the
    provided ArchiveExtender.
    Extraction uses 7z from CLI.
    """
    extender = extender()
    to = Path(to)
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_dir = Path(tmp_dir)
        uploaded_file = tmp_dir / file.filename
        tmp_output = tmp_dir / "target"
        file.save(uploaded_file)
        try:
            run("7z", "x", f"-o{tmp_output}", f"{uploaded_file}")
        except subprocess.CalledProcessError as e:
            raise ValueError(
                f"Invalid archive: [{e.returncode}] {e.stderr.decode()}"
            ) from e
        if not tmp_output.iterdir():
            raise ValueError("No files extracted")
        flatten_dir(tmp_output)
        result = {
            "size": 0,
            "files": {},
        }
        extender.on_start(tmp_output)
        for item in tmp_output.rglob("*"):
            if not item.is_file:
                continue
            files_dict = result["files"]
            for part in item.relative_to(tmp_output).parts:
                files_dict.setdefault(part, {})
                files_dict = files_dict[part]
            files_dict["size"] = item.stat().st_size
            result["size"] += files_dict["size"]
            extender.on_file(item)
        extender.on_end(tmp_output)
        shutil.rmtree(to, ignore_errors=True)
        to.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(tmp_output, to)
    result["extended_attributes"] = extender.attributes
    return result
