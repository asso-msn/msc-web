from pathlib import Path


class ChartDoc:
    """
    Helper class for reading chart files.
    """

    class STOP:
        pass

    def __init__(self, path: Path = None):
        if path:
            self.read(path)

    def read(self, path: Path):
        """
        Read the chart file. Each line is passed to `on_line`. If `on_line`
        returns `STOP`, reading is stopped. Values in `self.keys` are then set
        as attributes on the object.
        """
        self.keys = {}
        with path.open() as f:
            for line in f:
                line = line.strip()
                line = line.strip("\ufeff")
                if self.on_line(line) is self.STOP:
                    break
        for key, value in self.keys.items():
            setattr(self, key, value)

    def on_line(self, line: str):
        """
        Called for each line in the chart file. Should return `STOP` if reading
        should stop.
        """
        return self.STOP


class KSHDoc(ChartDoc):
    """Reads a K-Shoot MANIA chart file."""

    def on_line(self, line):
        if line.startswith("--"):
            return self.STOP
        if "=" in line:
            key, value = line.split("=", 1)
            if key in ("level",):
                value = int(value)
            self.keys[key] = value
