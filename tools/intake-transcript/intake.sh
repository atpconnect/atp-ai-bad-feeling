#!/usr/bin/env bash
# Files the transcripts that land on Fleet Command's laptop during the event.
#
# On the night, transcripts arrive in two ways and both land in ~/Downloads:
#   - Teams exports, once a station's meeting has been ended
#   - email attachments from a station pilot's own second-device recorder
#
# Hand-copying five files into five directories, under time pressure, in a bar,
# is exactly the kind of step that goes wrong. This does it by matching the
# station name in the filename, converting .docx to text, and refusing to guess.
#
# Usage:
#   intake.sh [SOURCE_DIR]          default: ~/Downloads
#   intake.sh --dry-run [SOURCE_DIR]
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
STATIONS_DIR="$REPO_ROOT/stations"

DRY=0
if [[ "${1:-}" == "--dry-run" ]]; then DRY=1; shift; fi
SRC="${1:-$HOME/Downloads}"

[[ -d "$SRC" ]] || { echo "No such directory: $SRC" >&2; exit 1; }

# Match on the distinctive word so "Sky City-20260917.docx", "skycity.txt" and
# "Ice Planet transcript (1).docx" all land correctly.
match_station() {
  local n; n="$(echo "$1" | tr '[:upper:]' '[:lower:]' | tr -d ' _-')"
  case "$n" in
    *skycity*)        echo sky-city ;;
    *swampplanet*)    echo swamp-planet ;;
    *iceplanet*)      echo ice-planet ;;
    *snowmonster*)    echo snow-monster-cave ;;
    *asteroid*)       echo asteroid-field ;;
    *)                echo "" ;;
  esac
}

filed=0; skipped=0; unmatched=()

shopt -s nullglob nocaseglob
for f in "$SRC"/*.docx "$SRC"/*.txt "$SRC"/*.md; do
  base="$(basename "$f")"
  station="$(match_station "$base")"

  if [[ -z "$station" ]]; then
    unmatched+=("$base"); continue
  fi

  dest_dir="$STATIONS_DIR/$station"
  if [[ ! -d "$dest_dir" ]]; then
    echo "  ?  $base -> unknown station dir $station, skipped" >&2
    skipped=$((skipped+1)); continue
  fi

  # A real transcript already filed always wins. Never clobber it.
  if [[ -f "$dest_dir/transcript.md" || -f "$dest_dir/transcript.txt" ]]; then
    echo "  =  $base -> $station already has a transcript, left alone"
    skipped=$((skipped+1)); continue
  fi

  if [[ "$DRY" == 1 ]]; then
    echo "  +  $base -> stations/$station/transcript.md (dry run)"
    filed=$((filed+1)); continue
  fi

  case "$base" in
    *.docx|*.DOCX)
      if command -v pandoc >/dev/null 2>&1; then
        pandoc "$f" -t plain --wrap=none -o "$dest_dir/transcript.md"
      else
        cp "$f" "$dest_dir/transcript.docx"
        echo "  !  pandoc not installed, filed raw .docx for $station" >&2
      fi ;;
    *) cp "$f" "$dest_dir/transcript.md" ;;
  esac
  echo "  +  $base -> stations/$station/transcript.md"
  filed=$((filed+1))
done
shopt -u nullglob nocaseglob

echo
echo "Filed: $filed   Skipped: $skipped   Unmatched: ${#unmatched[@]}"
if [[ ${#unmatched[@]} -gt 0 ]]; then
  echo "Unmatched files (file these by hand, or rename them to include the station):" >&2
  printf '  %s\n' "${unmatched[@]}" >&2
fi

echo
echo "Station status:"
for d in "$STATIONS_DIR"/*/; do
  name="$(basename "$d")"
  if   [[ -f "$d/transcript.md"   ]]; then state="transcript"
  elif [[ -f "$d/transcript.txt"  ]]; then state="transcript"
  elif [[ -f "$d/transcript.docx" ]]; then state="transcript (.docx, needs pandoc)"
  elif [[ -f "$d/expected-transcript.md" ]]; then state="FALLBACK to expected-transcript.md"
  elif [[ -f "$d/questions.md"    ]]; then state="FALLBACK to questions.md"
  else state="NOTHING, synthesis will refuse to run"; fi
  printf '  %-20s %s\n' "$name" "$state"
done
