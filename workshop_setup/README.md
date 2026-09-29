# Preparing the workshop computers

*This is for technicians and facilitators, not students. The workshop itself is in the [main README](../README.md).*

## Tools (once per computer)

From an admin account, in the Terminal, in the `Intro-to-LED-Signage` folder:

```
bash workshop_setup/install-tools.sh
```

This needs [Homebrew](https://brew.sh/). It:

- installs **ffmpeg** with Homebrew, and links it into `/usr/local/bin` so it works for every user account (on Apple Silicon, Homebrew's own folder isn't on other users' PATH);
- clones **Alright Fonts** on the `feature/port-to-c17` branch into `/usr/local/share/alright-fonts`, and installs its Python dependencies (`freetype-py`, `simplification`) into a virtual environment there;
- installs an **`afinate`** command into `/usr/local/bin` that runs it with that virtual environment, so students can just type `afinate` from any folder.

It asks for an admin password (`sudo`) only when it needs to write to `/usr/local`. Set `PREFIX` or `AF_DIR` to install somewhere else. Afterwards, open a new Terminal and check that `ffmpeg -version` and `afinate --help` both work, ideally from a student account.

Also install [Thonny](https://thonny.org/) (e.g. `brew install --cask thonny`).

## Boards

1. Download the latest **Interstate 75 W (RP2350)** firmware `.uf2` from the [releases page](https://github.com/pimoroni/interstate75/releases/latest). The "-with-examples" build is not needed, and flashing it **erases any files on the board**.
2. Connect the board with USB-C, hold **BOOT** and tap **RST**. A drive called **RP2350** appears.
3. Drag the `.uf2` onto that drive. The board reboots, ready for Thonny.

## Example assets

The example expects:

- the background frames as PNGs in [example/gif](../example/gif), at the panel's resolution (64x64 by default), named so they sort in order (e.g. `frame_000.png`, `frame_001.png`, ...). The ffmpeg command in [Section 2, Step 3](../README.md#step-3-convert-the-gif) produces exactly this.
- the font as `sign.af` in [example/fonts](../example/fonts), made with `afinate` as in [Section 3, Step 2](../README.md#step-2-convert-it-with-afinate). If you use a different name, update `FONT_FILE` on [line 47 of example/main.py](../example/main.py#L47) and [line 72 of alternative-example/main.py](../alternative-example/main.py#L72).

For 128x64 panels, change `PANEL` on [line 35 of example/main.py](../example/main.py#L35) and [line 36 of alternative-example/main.py](../alternative-example/main.py#L36) to `DISPLAY_INTERSTATE75_128X64`, and supply 128x64 frames.
