from pathlib import Path
from enum import Enum
from typing import Any, Optional
from random import Random
import secrets


class FileFormatError(Exception):
    pass
class FileSuffixError(Exception):
    pass
class GameModeError(ValueError):
    pass

class Section(str, Enum):
    GENERAL = "[General]"
    EDITOR = "[Editor]"
    METADATA = "[Metadata]"
    DIFFICULTY = "[Difficulty]"
    COLOURS = "[Colours]"
    EVENTS = "[Events]"
    TIMING_POINTS = "[TimingPoints]"
    HIT_OBJECTS = "[HitObjects]"

class GameMode(int, Enum):
    OSU = 0
    TAIKO = 1
    CATCH = 2
    MANIA = 3
    FRUITS = CATCH

class HitObject:
    def __init__(self, line: str):
        values = line.split(",")

        self.x = int(values[0])
        self.y = int(values[1])
        self.time = int(values[2])
        self.type = int(values[3])
        self.hitsound = int(values[4])
        self.other = ",".join(values[5:]) if len(values) > 5 else ""  # preserve rest of the line as a string
    
    @property
    def is_circle(self) -> bool:
        return bool(self.type & 1)

    # magic bitmask operation bullshit ahead
    def set_don(self) -> None:
        finish = self.hitsound & 4
        self.hitsound = 1 | finish

    def set_kat(self) -> None:
        finish = self.hitsound & 4
        self.hitsound = 2 | finish

    def as_line(self) -> str:
        return ",".join(str(x) for x in list(vars(self).values()))


class OsuFile:
    """
    Vague implementation of the .osu file format definition, targeted for taiko
    hit object editing and slight metadata modifications.
    Refer to https://osu.ppy.sh/wiki/en/Client/File_formats/osu_%28file_format
    """

    # TODO: implement more sections as classes for better readability
    
    def __init__(self, file: Path):
        if file.suffix != ".osu":
            raise FileSuffixError(f"'{file}' does not have a .osu suffix")
        
        self.file = file
        with open(self.file, "r", encoding="utf-8") as f:
            self.lines = [l.strip() for l in f if l.strip()]

        file_format = int(self.lines[0].lstrip("osu file format v"))
        if file_format != 14:
            raise FileFormatError(f"Only osu file format v14 is supported, found v{file_format} instead")

        self.hit_objects: list[HitObject] = []
        self.seed = None
        self.parse()

    @staticmethod
    def to_dict(section: list[str]) -> dict[str, Any]:
        result = {}
        for l in section:
            k, v = tuple(l.split(":"))
            result[k] = v.lstrip()
        return result

    def get_value(self, section: Section, key: str) -> Any:
        return self.to_dict(self.data[section])[key]

    def set_value(self, section: Section, key: str, value: Any) -> None:
        data = self.to_dict(self.data[section])
        data[key] = value
        new_data = []
        for k, v in data.items():
            sep = ": " if section in [Section.GENERAL, Section.EDITOR] else ":"
            new_data.append(f"{k}{sep}{str(v)}")
        
        self.data[section] = new_data

    def parse(self) -> None:
        # find where sections start and keep the indexes
        headers = {}
        for sect in Section:
            try:
                headers[sect] = self.lines.index(sect.value)
            except ValueError:
                continue

        # construct data dict by iterating on indexes
        data = {}
        indexes = list(headers.values())
        offset = indexes[1:].copy() + [len(self.lines) + 1]

        for current, next in zip(indexes, offset):
            key = Section(self.lines[current])
            data[key] = [l for l in self.lines[current+1:next]]

        # set attributes (only some implemented)
        self.data = data
        self.mode = GameMode(int(self.get_value(Section.GENERAL, "Mode")))
        if Section.HIT_OBJECTS in headers.keys():
            self.hit_objects = [HitObject(l) for l in data[Section.HIT_OBJECTS]]

    def detarame(self, seed: Optional[int], weight: float) -> None:
        if self.mode != GameMode.TAIKO:
            raise GameModeError(f"GameMode is {self.mode}, should be {GameMode.TAIKO}")
        
        # prepare seed
        self.seed = ''.join(secrets.choice('1234567890') for _ in range(6)) if seed is None else seed
        rng = Random(self.seed)

        # randomize hit objects
        for o in self.hit_objects:
            if not o.is_circle:
                continue
            if rng.random() < weight:
                o.set_don()
            else:
                o.set_kat()

        # update version and beatmap id
        current_version: str = self.get_value(Section.METADATA, "Version")
        new_version = f"{current_version} - Detarame ({self.seed} - {weight})"
        self.set_value(Section.METADATA, "Version", new_version)
        self.set_value(Section.METADATA, "BeatmapID", 0)
    
    def export(self) -> None:
        # restore hit objects list as strings
        self.data[Section.HIT_OBJECTS] = [o.as_line() for o in self.hit_objects]

        # rebuild list of lines
        lines = ["osu file format v14", ""]
        for section in self.data:
            section: Section
            lines.append(section.value)
            lines.extend(self.data[section])
            lines.append("")

        # build new filename
        artist: str = self.get_value(Section.METADATA, "ArtistUnicode")
        title: str = self.get_value(Section.METADATA, "TitleUnicode")
        creator: str = self.get_value(Section.METADATA, "Creator")
        version: str = self.get_value(Section.METADATA, "Version")
        new_filename = f"{artist} - {title} ({creator}) [{version}].osu"

        # write to new file in original directory
        output_path = Path(self.file.resolve().parent / new_filename)
        output_path.touch()
        output_path.write_text("\n".join(lines), encoding="utf-8")