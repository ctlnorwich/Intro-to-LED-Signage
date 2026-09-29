#!/usr/bin/env bash
# Installs ffmpeg and afinate (alright-fonts, feature/port-to-c17 branch) on macOS
# so both can be run from any folder, by any user, in the Terminal.
#
# Run once per computer from an admin account:
#   bash workshop_setup/install-tools.sh
#
# Override install locations if needed:
#   PREFIX=/usr/local AF_DIR=/usr/local/share/alright-fonts bash workshop_setup/install-tools.sh

set -euo pipefail

PREFIX="${PREFIX:-/usr/local}"
BIN_DIR="$PREFIX/bin"
AF_DIR="${AF_DIR:-$PREFIX/share/alright-fonts}"
AF_REPO="https://github.com/lowfatcode/alright-fonts"
AF_BRANCH="feature/port-to-c17"

# Use sudo only when the target directory isn't writable by the current user.
as_needed() {
  local target="$1"; shift
  while [[ ! -e "$target" ]]; do target="$(dirname "$target")"; done
  if [[ -w "$target" ]]; then "$@"; else sudo "$@"; fi
}

if [[ "$(uname)" != "Darwin" ]]; then
  echo "This script is for macOS." >&2
  exit 1
fi

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is required: https://brew.sh" >&2
  exit 1
fi

echo "==> ffmpeg"
brew list ffmpeg >/dev/null 2>&1 || brew install ffmpeg

# Apple Silicon Homebrew lives in /opt/homebrew, which isn't on PATH for other user accounts.
BREW_BIN="$(brew --prefix)/bin"
if [[ "$BREW_BIN" != "$BIN_DIR" ]]; then
  as_needed "$BIN_DIR" mkdir -p "$BIN_DIR"
  for tool in ffmpeg ffprobe; do
    as_needed "$BIN_DIR" ln -sf "$BREW_BIN/$tool" "$BIN_DIR/$tool"
  done
fi

echo "==> python3"
if ! command -v python3 >/dev/null 2>&1; then
  brew install python
fi
PYTHON="$(command -v python3)"

echo "==> alright-fonts ($AF_BRANCH) -> $AF_DIR"
if [[ -d "$AF_DIR/.git" ]]; then
  as_needed "$AF_DIR" git -C "$AF_DIR" fetch --depth 1 origin "$AF_BRANCH"
  as_needed "$AF_DIR" git -C "$AF_DIR" checkout -B "$AF_BRANCH" FETCH_HEAD
else
  as_needed "$AF_DIR" git clone --depth 1 --branch "$AF_BRANCH" "$AF_REPO" "$AF_DIR"
fi

echo "==> afinate dependencies"
as_needed "$AF_DIR" "$PYTHON" -m venv "$AF_DIR/.venv"
as_needed "$AF_DIR" "$AF_DIR/.venv/bin/pip" install --quiet --upgrade pip freetype-py simplification

echo "==> afinate command -> $BIN_DIR/afinate"
WRAPPER="$(mktemp)"
cat > "$WRAPPER" <<EOF
#!/bin/sh
exec "$AF_DIR/.venv/bin/python" "$AF_DIR/afinate" "\$@"
EOF
as_needed "$BIN_DIR" mkdir -p "$BIN_DIR"
as_needed "$BIN_DIR" install -m 755 "$WRAPPER" "$BIN_DIR/afinate"
rm -f "$WRAPPER"

echo "==> checking"
"$BIN_DIR/ffmpeg" -version | head -n 1
"$BIN_DIR/afinate" --help | head -n 1
echo "Done. Open a new Terminal window and try: ffmpeg -version && afinate --help"
