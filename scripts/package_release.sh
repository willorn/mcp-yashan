#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RELEASE_DIR="$ROOT_DIR/release"
DIST_NAME="mcp-yashan-macos"
STAGE_DIR="$RELEASE_DIR/$DIST_NAME"
ARCHIVE_PATH="$RELEASE_DIR/$DIST_NAME.zip"

rm -rf "$STAGE_DIR"
mkdir -p "$STAGE_DIR"

copy_path() {
  local path="$1"
  cp -R "$ROOT_DIR/$path" "$STAGE_DIR/"
}

copy_path ".env.example"
copy_path "LICENSE"
copy_path "README.md"
copy_path "docs"
copy_path "requirements.txt"
copy_path "server.py"
copy_path "start.sh"
copy_path "core"
copy_path "runtime"
copy_path "yashandb-jdbc-1.9.3.jar"

find "$STAGE_DIR" -type d -name "__pycache__" -prune -exec rm -rf {} +
find "$STAGE_DIR" -type f -name "*.pyc" -delete
find "$STAGE_DIR" -type f -name ".DS_Store" -delete

mkdir -p "$RELEASE_DIR"
rm -f "$ARCHIVE_PATH"

(
  cd "$RELEASE_DIR"
  zip -qr "$(basename "$ARCHIVE_PATH")" "$DIST_NAME"
)

echo "Release package created:"
echo "  Directory: $STAGE_DIR"
echo "  Archive:   $ARCHIVE_PATH"
