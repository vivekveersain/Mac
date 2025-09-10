#!/bin/bash
# Usage: ./latex_compiler.sh <tex-file> <directory>
TEXFILE="$1"
FILEDIR="$2"
echo "Subfile given: $TEXFILE"
echo "Subfile directory: $FILEDIR"
cd "$FILEDIR" || { echo "Failed to cd to $FILEDIR"; exit 1; }
echo "Now in directory: $(pwd)"
BASENAME=$(basename "$TEXFILE")
ROOT_LINE=$(grep '^% *!TeX root *= *' "$BASENAME" | head -1)
if [[ -n "$ROOT_LINE" ]]; then
  ROOT=$(echo "$ROOT_LINE" | sed 's/^% *!TeX root *= *//')
  ROOTFULL=$(python3 -c 'import os,sys;print(os.path.abspath(sys.argv[1]))' "$ROOT")
  ROOTDIR=$(dirname "$ROOTFULL")
  ROOTBASE=$(basename "$ROOTFULL")
  echo "Compiling root file: $ROOTBASE (in $ROOTDIR)"
  cd "$ROOTDIR" || { echo "Failed to cd to $ROOTDIR"; exit 1; }
  xelatex "$ROOTBASE"
else
  echo "Compiling current file: $BASENAME"
  xelatex "$BASENAME"
fi