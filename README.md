# 🎲 osu!taiko Detarame tool

A Python tool written (mostly) for Windows to randomize osu!taiko beatmaps on osu!stable.

## Download / How to Use

You can grab an executable build over at the [Releases](https://github.com/glassive/osu-taiko-detarame/releases) tab. To use it, you can either:

- **Drag-and-drop a `.osu` file onto the executable**, or;
- **Run the program in any terminal** by adding your file path as an argument, e.g.:
```bash
detarame.exe "D:/osu!/Songs/12345 - Mapset/Artist - Title (Mapper) [Inner Oni].osu"
```

You will then be prompted to enter a custom seed and weight if you wish. The RNG and weight are both entirely deterministic. The weight controls the colour density (0 = all Kat, 1 = all Don).

When the program is done running, a new difficulty will be directly added to the mapset folder. All you have to do is refresh (`F5`) and the new beatmap will be available. Enjoy!

## Developer Stuff

This is a half-arsed implementation of an OOP-style `.osu` parser that only deals with required sections (`HitObjects`, `Metadata`). The file runs on any `python>=3.9` and is built using `pyinstaller` which is the only dev requirement.

## AI Notice

**This is not a vibe-coded project**. I made this small tool mostly by hand + Google searches, only resorting to AI for slight improvements and fixes. The decision making, code structure, etc. are not affected. The GitHub workflow .yml file was AI-generated because I could not be bothered to deal with that, sorry `:-(`