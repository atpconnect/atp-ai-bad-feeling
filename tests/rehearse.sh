#!/usr/bin/env bash
# Rehearses the night, end to end, in a scratch copy of the repo.
#
# Every scenario runs the real tools against real files: intake from a mock
# Downloads folder, synthesis, schema validation, deck build. Nothing is mocked
# except the model itself, and the model stub is swapped to rehearse its failures
# too. Timings are measured, not estimated.
#
# Usage:
#   tests/rehearse.sh                 run every scenario
#   tests/rehearse.sh happy mixed     run named scenarios
#   tests/rehearse.sh --keep happy    keep the scratch dir and print its path
#   REAL_MODEL=1 tests/rehearse.sh happy    use the actual claude CLI
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FIX="$REPO/tests/fixtures"
STUBS="$REPO/tests/stubs"
DEFAULT_FOLLOW="https://atpconnect.github.io/atp-ai-bad-feeling/closeout/presentation.html"
KEEP=0
[[ "${1:-}" == "--keep" ]] && { KEEP=1; shift; }

ALL=(seed expected happy mixed docx disaster late garbage badschema liar crash nothing noprior fullsize
     hedge-primary hedge-standby hedge-primary-bad hedge-both-bad hedge-disabled
     no-hedge-flag voices voices-partial voices-all-fail voices-launder voices-timid refs-overdone
     project follow qr-decodes demo theming sponsors hints docs)
SCENARIOS=("${@:-}")
[[ -z "${SCENARIOS[0]:-}" ]] && SCENARIOS=("${ALL[@]}")

pass=0; fail=0; FAILURES=()

c_g=$'\033[32m'; c_r=$'\033[31m'; c_y=$'\033[33m'; c_d=$'\033[2m'; c_0=$'\033[0m'
[[ -t 1 ]] || { c_g=""; c_r=""; c_y=""; c_d=""; c_0=""; }

ok()   { pass=$((pass+1)); echo "    ${c_g}PASS${c_0}  $1"; }
skip() { echo "    ${c_y}SKIP${c_0}  $1"; }
bad()  { fail=$((fail+1)); FAILURES+=("$SCEN: $1"); echo "    ${c_r}FAIL${c_0}  $1"; }
check(){ if eval "$2"; then ok "$1"; else bad "$1"; fi; }

# ---------------------------------------------------------------- scratch setup
new_scratch() {
  SCRATCH="$(mktemp -d)"
  cp -r "$REPO"/{stations,tools,assets} "$SCRATCH/"
  mkdir -p "$SCRATCH/closeout" "$SCRATCH/Downloads"
  rm -f "$SCRATCH"/stations/*/questions.md "$SCRATCH"/stations/*/transcript.* \
        "$SCRATCH"/stations/*/expected-transcript.md
  DECK="$SCRATCH/closeout/presentation.html"
}

seed_questions() {  # the pre-event artifact: question lists in place
  for f in "$FIX"/questions/*.md; do
    cp "$f" "$SCRATCH/stations/$(basename "${f%.md}")/questions.md"
  done
}

# The second pre-event artifact: what we wrote that each room is likely to say, in
# transcript shape. A fallback like the question list, with more on it. Taken from the
# real repo rather than from fixtures, because the thing worth rehearsing is the file
# that will actually be sitting there on the night.
seed_expected() {
  for f in "$REPO"/stations/*/expected-transcript.md; do
    cp "$f" "$SCRATCH/stations/$(basename "$(dirname "$f")")/expected-transcript.md"
  done
}

arrive() {  # arrive <station-name-fragment> <ext>   drop a file into mock Downloads
  local frag="$1" ext="${2:-txt}"
  local src; src="$(ls "$FIX"/arrivals/*"$frag"*."$ext" 2>/dev/null | head -1)"
  [[ -n "$src" ]] || { echo "    ${c_r}fixture missing: $frag.$ext${c_0}"; return 1; }
  cp "$src" "$SCRATCH/Downloads/"
}

# The floor: what seed.sh built days before the event. Always the stub, because in
# the real timeline this already happened and is not what we are timing tonight.
establish_floor() {
  ( cd "$SCRATCH" && MODE=seeded CLAUDE_BIN="$STUBS/claude" STUB_MODE=good FAST_MODEL="" \
      ./tools/synthesize-closeout/synthesize.sh ) >"$SCRATCH/seed.log" 2>&1
}

run_synth() {
  local mode="${1:-live}" t0 t1
  t0=$(date +%s%N)
  if [[ "${REAL_MODEL:-0}" == "1" ]]; then
    ( cd "$SCRATCH" && MODE="$mode" CLAUDE_BIN=claude VOICES="${VOICES:-}" \
        ./tools/synthesize-closeout/synthesize.sh ${SYNTH_ARGS:-} ) >"$SCRATCH/synth.log" 2>&1
  else
    ( cd "$SCRATCH" && MODE="$mode" CLAUDE_BIN="$STUBS/claude" STUB_MODE="${STUB_MODE:-good}" \
        STUB_MODE_PRIMARY="${STUB_MODE_PRIMARY:-}" STUB_MODE_FAST="${STUB_MODE_FAST:-}" \
        STUB_DELAY_PRIMARY="${STUB_DELAY_PRIMARY:-0}" STUB_DELAY_FAST="${STUB_DELAY_FAST:-0}" \
        DEADLINE_S="${DEADLINE_S:-150}" GRACE_S="${GRACE_S:-60}" FAST_MODEL="${FAST_MODEL-haiku}" \
        STUB_VOICE_FAIL="${STUB_VOICE_FAIL:-}" STUB_VOICE_VAGUE="${STUB_VOICE_VAGUE:-}" STUB_VOICE_TIMID="${STUB_VOICE_TIMID:-}" STUB_OVERDO_REFS="${STUB_OVERDO_REFS:-}" VOICES="${VOICES:-}" FOLLOW_URL="${FOLLOW_URL-$DEFAULT_FOLLOW}" \
        STUB_SAVE_PROMPT="${STUB_SAVE_PROMPT:-}" \
        ./tools/synthesize-closeout/synthesize.sh ${SYNTH_ARGS:-} ) >"$SCRATCH/synth.log" 2>&1
  fi
  RC=$?
  t1=$(date +%s%N)
  ELAPSED_MS=$(( (t1 - t0) / 1000000 ))
  return $RC
}

deck_says()   { grep -qF "$1" "$DECK" 2>/dev/null; }

# How many distinctive facts from the transcripts survived into the deck. The framework
# demands specific numbers and named examples, and this is the only assertion that
# actually tests whether it got them. Written as alternations because a model will
# legitimately render "400,000" as "four hundred thousand" if the room said it that way.
FACTS=(
  '400,000|four hundred thousand'
  '94|ninety.four'
  '190,000|hundred and ninety thousand'
  '11,000|eleven thousand'
  '310|three hundred and ten'
  '600 pastes|six hundred pastes|600 a month'
  'eleven .*zero|zero in production'
  'nine months|month six'
)
specificity() {
  local n=0
  for re in "${FACTS[@]}"; do grep -Eqi "$re" "$DECK" 2>/dev/null && n=$((n+1)); done
  echo $n
}
# Pull a JS literal out of the deck by matching brackets rather than by regex. The
# values are multi-line JSON and one of them used to sit next to a // comment, which
# is exactly the kind of thing a lazy regex gets quietly wrong.
deck_json() { python3 - "$DECK" "$1" <<'DECKPY'
import sys, json
src, name = open(sys.argv[1]).read(), sys.argv[2]
i = src.index(f"const {name} = ") + len(f"const {name} = ")
open_c = src[i]; close_c = {"[": "]", "{": "}"}[open_c]
depth, j, instr, esc = 0, i, False, False
while j < len(src):
    c = src[j]
    if instr:
        if esc: esc = False
        elif c == "\\": esc = True
        elif c == '"': instr = False
    elif c == '"': instr = True
    elif c == open_c: depth += 1
    elif c == close_c:
        depth -= 1
        if depth == 0: break
    j += 1
print(json.dumps(json.loads(src[i:j + 1])))
DECKPY
}

deck_screens(){ deck_json DECKS | python3 -c "import json,sys; print(len(json.load(sys.stdin)['straight']))" 2>/dev/null || echo 0; }

# ---------------------------------------------------------------- scenarios

scen_seed() {  # days before: build the floor from question lists alone
  new_scratch; seed_questions
  STUB_MODE=good run_synth seeded
  check "seed run exits 0"                      "[[ $RC -eq 0 ]]"
  check "deck exists before the event"          "[[ -f '$DECK' ]]"
  check "all 5 stations marked PREVIEW"         "[[ \$(grep -c 'PREVIEW' '$DECK') -ge 5 ]]"
  check "says the session has not happened yet" "deck_says 'This session has not happened yet'"
  check "does NOT claim a recording failed"     "! deck_says 'did not produce usable audio'"
  check "patterns screen says nobody said this" "deck_says 'Nobody has said any of this yet'"
  check "deck says it was built pre-event"      "deck_says 'before the stations ran'"
  check "title marks it pre-seeded"             "deck_says 'pre-seeded'"
  check "QR code embedded"                      "deck_says 'data:image/png;base64,'"
  check "9 screens: 2 method, 5 stations, patterns, receipts" "[[ \$(deck_screens) -eq 9 ]]"
}

scen_expected() {  # the deeper fallback: an expected transcript outranks a question list, and is still a fallback
  new_scratch; seed_questions; seed_expected
  STUB_SAVE_PROMPT="$SCRATCH/prompt.txt" STUB_MODE=good run_synth seeded
  check "seed run exits 0"                      "[[ $RC -eq 0 ]]"
  check "nothing counted as a transcript"       "grep -q 'Inputs: 0/5 from a transcript' '$SCRATCH/synth.log'"
  check "the model was handed the expected one" "grep -q 'An expected transcript, written by Fleet Command' '$SCRATCH/prompt.txt'"
  check "and not the thinner question list"     "! grep -q 'Question list with pre-filled likely answers' '$SCRATCH/prompt.txt'"
  check "it is labelled a FALLBACK to the model" "[[ \$(grep -c 'Source: FALLBACK' '$SCRATCH/prompt.txt') -ge 5 ]]"
  check "all 5 stations still marked PREVIEW"   "[[ \$(grep -c 'PREVIEW' '$DECK') -ge 5 ]]"
  check "deck never calls it a transcript"      "! deck_says '<span class=\"pill\">TRANSCRIPT</span>'"

  # The same inputs on the night, once the recordings have failed rather than not
  # happened yet. Same content, and the banner has to say the harder thing.
  STUB_MODE=good run_synth live
  check "live run exits 0"                      "[[ $RC -eq 0 ]]"
  check "all 5 flagged as not a transcript"     "[[ \$(grep -c 'Not from a transcript' '$DECK') -eq 5 ]]"
  check "says whose numbers are on the screen"  "deck_says 'is ours, not the room'"

  # An expected transcript must never stand in the way of the real one.
  arrive "Sky City" txt
  ( cd "$SCRATCH" && ./tools/intake-transcript/intake.sh "$SCRATCH/Downloads" ) >"$SCRATCH/intake.log" 2>&1
  check "a real transcript still files fine"    "[[ -f '$SCRATCH/stations/sky-city/transcript.md' ]]"
  check "intake names the deeper fallback"      "grep -q 'FALLBACK to expected-transcript.md' '$SCRATCH/intake.log'"
  STUB_MODE=good run_synth live
  check "the real one wins"                     "grep -q 'Inputs: 1/5 from a transcript' '$SCRATCH/synth.log'"
  check "and only the other four are flagged"   "[[ \$(grep -c 'Not from a transcript' '$DECK') -eq 4 ]]"
}

scen_happy() {  # the night, everything works
  new_scratch; seed_questions; establish_floor
  for s in "Sky City" "Swamp Planet" "Ice Planet" "Snow Monster Cave" "Asteroid Field"; do arrive "$s" txt; done
  ( cd "$SCRATCH" && ./tools/intake-transcript/intake.sh "$SCRATCH/Downloads" ) >"$SCRATCH/intake.log" 2>&1
  check "intake filed all 5"                    "[[ \$(grep -c ' + ' '$SCRATCH/intake.log') -eq 5 ]]"
  check "no station left on fallback"           "! grep -q 'FALLBACK to questions' '$SCRATCH/intake.log'"
  run_synth live
  check "synthesis exits 0"                     "[[ $RC -eq 0 ]]"
  check "5/5 from transcript"                   "grep -q '5/5 stations from a real transcript' '$SCRATCH/synth.log'"
  check "no FALLBACK banner in deck"            "! deck_says 'Not from a transcript'"
  local spec; spec=$(specificity)
  if [[ $spec -ge 5 ]]; then ok "specific facts survived to the deck ($spec/8)"
  else bad "only $spec/8 distinctive facts reached the deck; the synthesis went generic"; fi
  check "provenance says built in the room"     "deck_says 'in the room, minutes ago'"
}

scen_mixed() {  # 3 Teams transcripts, 1 emailed backup, 1 total loss
  new_scratch; seed_questions; establish_floor
  arrive "Sky City" docx; arrive "Swamp Planet" docx; arrive "Ice Planet" docx
  arrive "Snow Monster Cave" txt          # the pilot's own recorder, emailed in
  # Asteroid Field: nothing arrives at all
  ( cd "$SCRATCH" && ./tools/intake-transcript/intake.sh "$SCRATCH/Downloads" ) >"$SCRATCH/intake.log" 2>&1
  check "intake reports asteroid on fallback"   "grep -q 'asteroid-field *FALLBACK' '$SCRATCH/intake.log'"
  run_synth live
  check "synthesis exits 0"                     "[[ $RC -eq 0 ]]"
  check "4/5 from transcript"                   "grep -q '4/5 stations from a real transcript' '$SCRATCH/synth.log'"
  check "asteroid flagged on screen"            "deck_says 'Not from a transcript'"
  check "only one station flagged"              "[[ \$(grep -c 'Not from a transcript' '$DECK') -eq 1 ]]"
  check "the 4 good ones carried real detail"   "grep -Eqi '190,000|hundred and ninety thousand' '$DECK'"
}

scen_docx() {  # the Teams export path specifically
  new_scratch; seed_questions; establish_floor
  for s in "Sky City" "Swamp Planet" "Ice Planet" "Snow Monster Cave" "Asteroid Field"; do arrive "$s" docx; done
  ( cd "$SCRATCH" && ./tools/intake-transcript/intake.sh "$SCRATCH/Downloads" ) >"$SCRATCH/intake.log" 2>&1
  check "docx converted to text on intake"      "[[ -f '$SCRATCH/stations/sky-city/transcript.md' ]]"
  check "no raw .docx left in stations"         "! ls '$SCRATCH'/stations/*/transcript.docx >/dev/null 2>&1"
  check "converted text is not empty"           "[[ \$(wc -c <'$SCRATCH/stations/sky-city/transcript.md') -gt 2000 ]]"
  run_synth live
  check "synthesis exits 0"                     "[[ $RC -eq 0 ]]"
  check "5/5 from transcript"                   "grep -q '5/5 stations from a real transcript' '$SCRATCH/synth.log'"
}

scen_disaster() {  # every recording failed
  new_scratch; seed_questions; establish_floor
  run_synth live
  check "still exits 0"                         "[[ $RC -eq 0 ]]"
  check "0/5 from transcript"                   "grep -q '0/5 stations from a real transcript' '$SCRATCH/synth.log'"
  check "all 5 flagged on screen"               "[[ \$(grep -c 'Not from a transcript' '$DECK') -eq 5 ]]"
  check "live failure says the recording failed" "deck_says 'did not produce usable audio'"
  check "and does not call it a preview"        "! deck_says 'has not happened yet'"
  check "there is still a deck to present"      "[[ -s '$DECK' ]]"
}

scen_late() {  # a transcript arrives after the deck was already built
  new_scratch; seed_questions; establish_floor
  arrive "Sky City" txt; arrive "Swamp Planet" txt
  ( cd "$SCRATCH" && ./tools/intake-transcript/intake.sh "$SCRATCH/Downloads" ) >/dev/null 2>&1
  run_synth live
  check "first pass 2/5"                        "grep -q '2/5 stations from a real transcript' '$SCRATCH/synth.log'"
  local first; first=$(grep -c 'Not from a transcript' "$DECK")
  arrive "Ice Planet" txt
  ( cd "$SCRATCH" && ./tools/intake-transcript/intake.sh "$SCRATCH/Downloads" ) >"$SCRATCH/intake2.log" 2>&1
  check "intake does not re-file what is filed" "grep -q 'already has a transcript' '$SCRATCH/intake2.log'"
  run_synth live
  check "second pass 3/5"                       "grep -q '3/5 stations from a real transcript' '$SCRATCH/synth.log'"
  check "fewer fallbacks than before"           "[[ \$(grep -c 'Not from a transcript' '$DECK') -lt $first ]]"
  check "previous deck kept as .prev"           "[[ -f '$DECK.prev' ]]"
}

scen_garbage() {  # the model returns prose instead of JSON
  new_scratch; seed_questions
  STUB_MODE=good run_synth seeded          # establish a good deck first
  local before; before=$(md5sum "$DECK" | cut -d' ' -f1)
  STUB_MODE=garbage run_synth live
  check "run fails loudly"                      "[[ $RC -ne 0 ]]"
  check "says REJECTED"                         "grep -q 'REJECTED' '$SCRATCH/synth.log'"
  check "existing deck is byte-identical"       "[[ \$(md5sum '$DECK' | cut -d' ' -f1) == '$before' ]]"
  check "tells you the old deck still stands"   "grep -q 'untouched and presentable' '$SCRATCH/synth.log'"
}

scen_badschema() {  # well-formed JSON that breaks the rules
  new_scratch; seed_questions
  STUB_MODE=good run_synth seeded
  local before; before=$(md5sum "$DECK" | cut -d' ' -f1)
  STUB_MODE=badschema run_synth live
  check "run fails loudly"                      "[[ $RC -ne 0 ]]"
  check "names the missing station"             "grep -q 'missing asteroid-field' '$SCRATCH/synth.log'"
  check "existing deck untouched"               "[[ \$(md5sum '$DECK' | cut -d' ' -f1) == '$before' ]]"
}

scen_liar() {  # the dangerous one: model relabels a fallback as a transcript
  new_scratch; seed_questions; establish_floor
  arrive "Sky City" txt
  ( cd "$SCRATCH" && ./tools/intake-transcript/intake.sh "$SCRATCH/Downloads" ) >/dev/null 2>&1
  STUB_MODE=liar run_synth live
  check "run completes"                         "[[ $RC -eq 0 ]]"
  check "model's false claim is noticed"        "grep -q 'Ignoring the model' '$SCRATCH/synth.log'"
  check "deck counts 1/5, not the model's 5/5"  "grep -q '1/5 stations from a real transcript' '$SCRATCH/synth.log'"
  check "the 4 real fallbacks are still flagged" "[[ \$(grep -c 'Not from a transcript' '$DECK') -eq 4 ]]"
  check "the one real transcript is not flagged" "grep -Eqi '400,000|four hundred thousand' '$DECK'"
}

scen_crash() {  # the CLI itself dies
  new_scratch; seed_questions
  STUB_MODE=good run_synth seeded
  local before; before=$(md5sum "$DECK" | cut -d' ' -f1)
  STUB_MODE=fail run_synth live
  check "run fails loudly"                      "[[ $RC -ne 0 ]]"
  check "surfaces the CLI stderr"               "grep -q 'rate_limit_error' '$SCRATCH/synth.log'"
  check "existing deck untouched"               "[[ \$(md5sum '$DECK' | cut -d' ' -f1) == '$before' ]]"
}

scen_nothing() {  # no questions.md either: the one case we refuse to paper over
  new_scratch
  run_synth live
  check "refuses to run"                        "[[ $RC -eq 3 ]]"
  check "names every station it cannot cover"   "grep -q 'sky-city' '$SCRATCH/synth.log'"
  check "explains why it refused"               "grep -q 'silently drops a station' '$SCRATCH/synth.log'"
  check "no deck was written"                   "[[ ! -f '$DECK' ]]"
}

scen_noprior() {  # a bad model run with no seeded deck behind it: the case seed.sh exists to prevent
  new_scratch; seed_questions
  STUB_MODE=garbage run_synth live
  check "run fails loudly"                      "[[ $RC -ne 0 ]]"
  check "says there is nothing to fall back to" "grep -q 'no deck to fall back on' '$SCRATCH/synth.log'"
  check "tells you to run seed.sh"              "grep -q 'Run seed.sh' '$SCRATCH/synth.log'"
  check "and there is indeed no deck"           "[[ ! -f '$DECK' ]]"
}

scen_fullsize() {  # timing against transcripts the length a real 45-minute station produces
  new_scratch; seed_questions; establish_floor
  python3 "$REPO/tests/inflate.py" "$FIX/arrivals" "$SCRATCH/Downloads" 8500
  ( cd "$SCRATCH" && ./tools/intake-transcript/intake.sh "$SCRATCH/Downloads" ) >"$SCRATCH/intake.log" 2>&1
  local words; words=$(cat "$SCRATCH"/stations/*/transcript.md | wc -w)
  echo "    ${c_d}input: ${words} words across 5 stations${c_0}"
  run_synth live
  check "synthesis exits 0"                     "[[ $RC -eq 0 ]]"
  check "5/5 from transcript"                   "grep -q '5/5 stations from a real transcript' '$SCRATCH/synth.log'"
  # Measured, not guessed. Four real-model runs came in at 69s, 102s, 105s and 164s,
  # and the 164s was on the SMALL fixtures: latency varies more than 2x run to run and
  # is not driven by input size. So the run of show gets a 3 minute slice, not the
  # median. If this fails, the run of show needs to know before the event, not during it.
  local synth_budget=$(( 180 * 1000 ))
  if [[ $ELAPSED_MS -lt $synth_budget ]]; then
    ok "synthesis inside its 3-minute slice of the run of show (${ELAPSED_MS}ms)"
  else
    bad "synthesis took ${ELAPSED_MS}ms, over the 3 minutes the run of show allows"
  fi
}

# ---- the hedge: two models in parallel, deliberately not a race -----------------

scen_hedge_primary() {  # primary is fine, standby is irrelevant
  new_scratch; seed_questions; establish_floor
  STUB_DELAY_FAST=4 DEADLINE_S=30 run_synth live
  check "exits 0"                               "[[ $RC -eq 0 ]]"
  check "primary won"                           "grep -q 'from the primary model' '$SCRATCH/synth.log'"
  check "standby never mentioned as the source" "! grep -q 'standby, because' '$SCRATCH/synth.log'"
  check "deck credits the primary"              "deck_says 'Written by the primary model'"
  if [[ $ELAPSED_MS -lt 4000 ]]; then ok "did not wait for the slower standby (${ELAPSED_MS}ms)"
  else bad "waited ${ELAPSED_MS}ms; it should not block on the standby"; fi
}

scen_hedge_standby() {  # primary blows the deadline, standby carries the room
  new_scratch; seed_questions; establish_floor
  STUB_DELAY_PRIMARY=30 DEADLINE_S=3 GRACE_S=10 run_synth live
  check "exits 0"                               "[[ $RC -eq 0 ]]"
  check "says the primary missed the deadline"  "grep -q 'missed the 3s deadline' '$SCRATCH/synth.log'"
  check "standby supplied the content"          "grep -q 'haiku standby' '$SCRATCH/synth.log'"
  check "deck admits it on the provenance line" "deck_says 'haiku standby'"
  check "still has real transcript detail"      "grep -Eqi '400,000|four hundred thousand' '$DECK'"
  if [[ $ELAPSED_MS -lt 15000 ]]; then ok "finished near the deadline, not the primary's 30s (${ELAPSED_MS}ms)"
  else bad "took ${ELAPSED_MS}ms; the deadline did not cut the primary off"; fi
}

scen_hedge_primary_bad() {  # primary returns fast but useless: don't sit out the deadline
  new_scratch; seed_questions; establish_floor
  STUB_MODE_PRIMARY=garbage STUB_MODE_FAST=good DEADLINE_S=60 run_synth live
  check "exits 0"                               "[[ $RC -eq 0 ]]"
  check "names the primary as unusable"         "grep -q 'Primary unusable' '$SCRATCH/synth.log'"
  check "standby supplied the content"          "grep -q 'haiku standby' '$SCRATCH/synth.log'"
  if [[ $ELAPSED_MS -lt 20000 ]]; then ok "switched immediately, did not wait out 60s (${ELAPSED_MS}ms)"
  else bad "waited ${ELAPSED_MS}ms for a deadline it had no reason to wait for"; fi
}

scen_hedge_both_bad() {  # both paths fail: the seeded deck is the whole point
  new_scratch; seed_questions; establish_floor
  local before; before=$(md5sum "$DECK" | cut -d' ' -f1)
  STUB_MODE=garbage DEADLINE_S=3 GRACE_S=3 run_synth live
  check "fails loudly"                          "[[ $RC -ne 0 ]]"
  check "reports both paths"                    "[[ \$(grep -c 'unusable' '$SCRATCH/synth.log') -ge 2 ]]"
  check "points at the deck already on disk"    "grep -q 'untouched and presentable' '$SCRATCH/synth.log'"
  check "and that deck is byte-identical"       "[[ \$(md5sum '$DECK' | cut -d' ' -f1) == '$before' ]]"
}

scen_hedge_disabled() {  # FAST_MODEL empty: single path, no hang waiting on a standby
  new_scratch; seed_questions; establish_floor
  local before; before=$(md5sum "$DECK" | cut -d' ' -f1)
  FAST_MODEL="" STUB_MODE=garbage DEADLINE_S=30 run_synth live
  check "fails loudly"                          "[[ $RC -ne 0 ]]"
  check "no standby was started"                "! grep -q 'running in parallel' '$SCRATCH/synth.log'"
  check "existing deck untouched"               "[[ \$(md5sum '$DECK' | cut -d' ' -f1) == '$before' ]]"
  if [[ $ELAPSED_MS -lt 20000 ]]; then ok "gave up promptly, no phantom standby wait (${ELAPSED_MS}ms)"
  else bad "hung ${ELAPSED_MS}ms waiting for a standby that was never started"; fi
}

# ---- optional extras: the hedge switch, and the character voices ---------------

deck_voices() { deck_json VOICES | python3 -c "import json,sys; print(' '.join(v[0] for v in json.load(sys.stdin)))" 2>/dev/null || echo ""; }

scen_no_hedge_flag() {  # --no-hedge on a run that succeeds: one model, no standby
  new_scratch; seed_questions; establish_floor
  SYNTH_ARGS="--no-hedge" run_synth live
  check "exits 0"                               "[[ $RC -eq 0 ]]"
  check "no standby was started"                "! grep -q 'running in parallel' '$SCRATCH/synth.log'"
  check "primary still produced the deck"       "grep -q 'from the primary model' '$SCRATCH/synth.log'"
  check "deck is complete"                      "[[ \$(deck_screens) -eq 9 ]]"
}

scen_voices() {  # the live toggle
  new_scratch; seed_questions; establish_floor
  SYNTH_ARGS="--voices=sage,admiral" run_synth live
  check "exits 0"                               "[[ $RC -eq 0 ]]"
  check "both voices survived"                  "[[ \"\$(deck_voices)\" == 'straight sage admiral' ]]"
  check "deck carries the sage's text"          "deck_says '[The Sage]'"
  check "deck carries the admiral's text"       "deck_says '[The Admiral]'"
  check "straight text is still there too"      "grep -Eqi '400,000|four hundred thousand' '$DECK'"
  check "voice bar is rendered"                 "deck_says 'id=\"voiceButtons\"'"
  check "method screens excluded from voicing"  "deck_says 'UNVOICED'"
  check "and say so where the reader is looking" "deck_says 'is not narrating this screen'"
  check "inert voice buttons are dimmed"        "deck_says 'b.style.opacity'"
  check "straight deck was up before voices"    "grep -q 'Straight deck up' '$SCRATCH/synth.log'"
}

scen_voices_partial() {  # one voice fails: drop it, keep the rest, never lose the deck
  new_scratch; seed_questions; establish_floor
  STUB_VOICE_FAIL="the admiral" SYNTH_ARGS="--voices=sage,admiral" run_synth live
  check "exits 0"                               "[[ $RC -eq 0 ]]"
  check "the bad voice was dropped"             "grep -q 'admiral: unusable' '$SCRATCH/synth.log'"
  check "the good voice survived"               "[[ \"\$(deck_voices)\" == 'straight sage' ]]"
  check "deck is still complete"                "[[ \$(deck_screens) -eq 9 ]]"
}

scen_voices_all_fail() {  # every voice fails: straight deck stands, exit still clean
  new_scratch; seed_questions; establish_floor
  STUB_VOICE_FAIL="the sage,the admiral" SYNTH_ARGS="--voices=sage,admiral" run_synth live
  check "exits 0 anyway"                        "[[ $RC -eq 0 ]]"
  check "says no voice survived"                "grep -q 'No voice survived' '$SCRATCH/synth.log'"
  check "deck has only the straight voice"      "[[ \"\$(deck_voices)\" == 'straight' ]]"
  check "no voice bar to show"                  "[[ \$(deck_json VOICES | python3 -c 'import json,sys;print(len(json.load(sys.stdin)))') -eq 1 ]]"
  check "deck is still complete and real"       "grep -Eqi '400,000|four hundred thousand' '$DECK'"
}

scen_voices_launder() {  # a voice that quietly drops the numbers must be called out
  new_scratch; seed_questions; establish_floor
  STUB_VOICE_VAGUE=1 SYNTH_ARGS="--voices=sage" run_synth live
  check "exits 0"                               "[[ $RC -eq 0 ]]"
  check "warns that figures went missing"       "grep -q 'WARNING voice sage' '$SCRATCH/synth.log'"
  check "names a specific missing figure"       "grep -q '190,000' '$SCRATCH/synth.log'"
  check "voice is still offered, not dropped"   "[[ \"\$(deck_voices)\" == 'straight sage' ]]"
  check "straight deck keeps its numbers"       "grep -Eqi '400,000|four hundred thousand' '$DECK'"
}

scen_voices_timid() {  # a voice that validates perfectly and is pointless on stage
  new_scratch; seed_questions; establish_floor
  STUB_VOICE_TIMID=1 SYNTH_ARGS="--voices=sage" run_synth live
  check "exits 0"                               "[[ $RC -eq 0 ]]"
  check "warns the voice barely differs"        "grep -q 'were actually rewritten' '$SCRATCH/synth.log'"
  check "tells you which file to strengthen"    "grep -q 'voices/sage.md' '$SCRATCH/synth.log'"
  check "voice is still offered"                "[[ \"\$(deck_voices)\" == 'straight sage' ]]"
}

scen_refs_overdone() {  # film quotes turning up on a slide
  new_scratch; seed_questions; establish_floor
  STUB_OVERDO_REFS=1 run_synth live
  check "exits 0, this is advice not a failure"  "[[ $RC -eq 0 ]]"
  check "flags the crowded screen"               "grep -q 'film quote on a screen' '$SCRATCH/synth.log'"
  check "names which screen"                     "grep -q 'sky-city (2)' '$SCRATCH/synth.log'"
  check "deck is built regardless"               "[[ \$(deck_screens) -eq 9 ]]"
}

# ---- projector legibility and the follow-along link ----------------------------

scen_project() {  # presentation mode has to exist in the file and be self-sizing
  new_scratch; seed_questions; establish_floor
  run_synth live
  check "exits 0"                               "[[ $RC -eq 0 ]]"
  check "P toggles a presenting class"          "deck_says 'classList.toggle(\"presenting\"'"
  check "type scales off one variable"          "deck_says 'calc(var(--base-fs) * var(--s))'"
  check "autofit shrinks to the real screen"    "deck_says 'root.scrollHeight > window.innerHeight'"
  check "manual nudge overrides autofit"        "deck_says 'if (!presenting || scale) return'"
  check "projector shows headlines, not detail" "deck_says ':root.presenting ol.points .d { display: none; }'"
  check "D reveals detail on demand"            "deck_says 'classList.toggle(\"details\")'"
}

scen_follow() {  # every screen carries a link to itself
  new_scratch; seed_questions; establish_floor
  run_synth live
  check "exits 0"                               "[[ $RC -eq 0 ]]"
  check "follow QR is in the deck"              "deck_says 'id=\"followQr\"'"
  check "url is per screen, not just the deck"  "deck_says 'FOLLOW_URL + \"#\" + s.id'"
  check "a QR exists for every screen"          "[[ \$(deck_json QRS | python3 -c 'import json,sys;print(len(json.load(sys.stdin)))') -eq 9 ]]"
  check "deep links land on that screen"        "deck_says 'screens().findIndex(s => s.id === id)'"
  check "address bar tracks the screen"         "deck_says 'history.replaceState'"
  FOLLOW_URL="" run_synth live
  check "--no-follow really removes it"         "[[ \$(deck_json QRS | python3 -c 'import json,sys;print(len(json.load(sys.stdin)))') -eq 0 ]]"
}

scen_qr_decodes() {  # the only check that would have caught a blank QR
  new_scratch; seed_questions; establish_floor
  run_synth live
  if ! command -v chromium >/dev/null || ! command -v zbarimg >/dev/null; then
    skip "QR decode needs chromium and zbarimg"; return
  fi
  python3 - "$DECK" "$SCRATCH" <<'QRPY'
import json, pathlib, re, sys
src = pathlib.Path(sys.argv[1]).read_text()
i = src.index("const QRS = ") + len("const QRS = ")
depth=0;j=i;instr=False;esc=False
while j < len(src):
    c=src[j]
    if instr:
        if esc: esc=False
        elif c=="\\": esc=True
        elif c=='"': instr=False
    elif c=='"': instr=True
    elif c=="{": depth+=1
    elif c=="}":
        depth-=1
        if depth==0: break
    j+=1
qrs=json.loads(src[i:j+1])
svg=qrs["swamp-planet"]
pathlib.Path(sys.argv[2]+"/qr.html").write_text(
  '<body style="margin:0;background:#fff"><style>.followqr{width:300px;aspect-ratio:1;display:block}</style>'+svg+'</body>')
QRPY
  chromium --headless --disable-gpu --no-sandbox --hide-scrollbars --virtual-time-budget=3000     --window-size=320,320 --screenshot="$SCRATCH/qr.png" "file://$SCRATCH/qr.html" >/dev/null 2>&1
  local got; got="$(zbarimg --quiet --raw "$SCRATCH/qr.png" 2>/dev/null | tr -d '\n')"
  if [[ "$got" == "$DEFAULT_FOLLOW#swamp-planet" ]]; then
    ok "QR scans to the right screen's URL"
  else
    bad "QR decoded to '$got'"
  fi
}

scen_demo() {  # a public URL full of invented people has to say so on every screen
  new_scratch; seed_questions
  for st in "Sky City" "Swamp Planet" "Ice Planet" "Snow Monster Cave" "Asteroid Field"; do arrive "$st" txt; done
  ( cd "$SCRATCH" && ./tools/intake-transcript/intake.sh "$SCRATCH/Downloads" ) >/dev/null 2>&1
  MODE=demo run_synth demo
  check "exits 0"                               "[[ $RC -eq 0 ]]"
  check "notice is in the deck"                 "deck_says 'This is a demo build, not the event'"
  check "notice renders on every screen"        "deck_says 'DEMO_NOTICE'"
  check "says nothing was said by anybody"      "deck_says 'Nothing here was said by anybody'"
  check "title marks it a demo"                 "deck_says '(demo)'"
  check "stations say MOCK TRANSCRIPT"          "deck_says 'MOCK TRANSCRIPT'"
  check "and never plain TRANSCRIPT"            "! deck_says '>TRANSCRIPT<'"
  check "live builds are unaffected"            "true"
  run_synth live
  check "live build has no demo notice"         "! deck_says 'This is a demo build'"
  check "live build says TRANSCRIPT"            "deck_says '>TRANSCRIPT<'"
}

scen_theming() {  # one accent per station, and none of them unreadable
  new_scratch; seed_questions; establish_floor
  for st in "Sky City" "Swamp Planet" "Ice Planet" "Snow Monster Cave" "Asteroid Field"; do arrive "$st" txt; done
  ( cd "$SCRATCH" && ./tools/intake-transcript/intake.sh "$SCRATCH/Downloads" ) >/dev/null 2>&1
  run_synth live
  check "exits 0"                               "[[ $RC -eq 0 ]]"
  check "five distinct station themes"          "[[ \$(deck_json THEMES | python3 -c 'import json,sys;d=json.load(sys.stdin);print(len({v[\"surface\"] for v in d.values()}))') -eq 5 ]]"
  check "theme is applied per screen"           "deck_says 'applyTheme(s.id)'"
  check "dark stations really are dark"         "[[ \$(deck_json THEMES | python3 -c 'import json,sys;d=json.load(sys.stdin);print(sum(1 for v in d.values() if int(v[\"surface\"][1:3],16) < 64))') -eq 3 ]]"
  check "print pages carry their theme too"     "deck_says 'themeVars(s.id)'"
  check "method screens keep the default"       "deck_says 'THEMES[id] || DEFAULT_THEME'"

  # Every accent readable from the back of the room, measured rather than eyeballed.
  # Every text colour against its own surface, measured off the built deck rather
  # than trusted. This is the check that has now caught two pre-existing failures.
  local res; res="$(python3 - "$DECK" <<'CONTRASTPY'
import json, re, sys, pathlib
src = pathlib.Path(sys.argv[1]).read_text()
def grab(name):
    i = src.index(f"const {name} = ") + len(f"const {name} = ")
    depth=0;j=i;instr=False;esc=False
    while j < len(src):
        c=src[j]
        if instr:
            if esc: esc=False
            elif c=="\\": esc=True
            elif c=='"': instr=False
        elif c=='"': instr=True
        elif c in "{[": depth+=1
        elif c in "}]":
            depth-=1
            if depth==0: break
        j+=1
    return json.loads(src[i:j+1])
def lum(h):
    h=h.lstrip("#"); ch=[int(h[k:k+2],16)/255 for k in (0,2,4)]
    ch=[c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4 for c in ch]
    return 0.2126*ch[0]+0.7152*ch[1]+0.0722*ch[2]
def ratio(fg,bg):
    a,b=sorted((lum(fg),lum(bg)),reverse=True); return (a+0.05)/(b+0.05)
FLOORS={"ink":7.0,"ink2":4.5,"ink3":4.5,"accent":4.5,"warn":4.0}
themes=grab("THEMES"); themes["default"]=grab("DEFAULT_THEME")
bad=[]; worst=99
for name,t in themes.items():
    for k,floor in FLOORS.items():
        r=ratio(t[k],t["surface"]); worst=min(worst,r)
        if r<floor: bad.append(f"{name}.{k} {r:.2f}:1<{floor}")
print(("FAIL " + ", ".join(bad)) if bad else f"OK {worst:.2f}")
CONTRASTPY
)"
  if [[ "$res" == OK* ]]; then ok "every text colour clears its floor (worst ${res#OK })"
  else bad "a text colour is below its contrast floor: $res"; fi
}

scen_hints() {  # a pilot said out loud that they wanted something in the deck, so the
                # worst outcome is finding the flag and silently dropping it
  new_scratch; seed_questions; establish_floor
  for st in "Sky City" "Swamp Planet" "Ice Planet" "Snow Monster Cave" "Asteroid Field"; do arrive "$st" txt; done
  ( cd "$SCRATCH" && ./tools/intake-transcript/intake.sh "$SCRATCH/Downloads" ) >/dev/null 2>&1

  # Two real flags, and three decoys that must not match: intent with no target, target
  # with no intent, and a fallback station nobody was in.
  cat >> "$SCRATCH/stations/sky-city/transcript.md" <<'FLAGS'

Dana Whitfield 41:02
Our vendor rate limit of six hundred a minute turned out to be shared regionally, so Mondays we got ninety.

Dana Whitfield 41:40
That is a really good point, I'd like to see that get into the presentation.

Marcus Bell 42:10
I want to get this right before we move on.

Marcus Bell 42:35
We will see the summary later anyway.
FLAGS
  cat >> "$SCRATCH/stations/asteroid-field/transcript.md" <<'FLAGS'

Rebecca Ahn 39:12
Our cyber insurer asked three questions about AI on the renewal questionnaire this year.

Rebecca Ahn 39:50
Make sure that one makes it into the closeout deck.
FLAGS

  local out; out="$(cd "$SCRATCH" && python3 tools/synthesize-closeout/hints.py extract \
      --stations "$SCRATCH/stations" \
      --sources "sky-city=transcript,swamp-planet=transcript,ice-planet=transcript,snow-monster-cave=transcript,asteroid-field=transcript" \
      --json "$SCRATCH/h.json" --md "$SCRATCH/h.md" 2>&1)"
  check "finds both flagged moments"            "[[ \$(python3 -c 'import json;print(len(json.load(open(\"$SCRATCH/h.json\"))))') -eq 2 ]]"
  check "on the two stations that flagged"      "[[ \$(python3 -c 'import json;print(\",\".join(sorted(h[\"station\"] for h in json.load(open(\"$SCRATCH/h.json\")))))') == 'asteroid-field,sky-city' ]]"
  check "intent without a target is not a flag" "! grep -q 'want to get this right' '$SCRATCH/h.md'"
  check "target without intent is not a flag"   "! grep -q 'summary later anyway' '$SCRATCH/h.md'"
  check "carries the turns before the flag"     "grep -q 'shared regionally' '$SCRATCH/h.md'"
  check "tells the model it may decline"        "grep -q 'hints, not instructions' '$SCRATCH/h.md'"

  # A fallback station has nobody in it. A flag found there would be us quoting our own
  # guess back at ourselves and calling it a request from the room.
  cat >> "$SCRATCH/stations/swamp-planet/expected-transcript.md" <<'FLAGS'

Station pilot 44:00
I'd like to see that get into the presentation.
FLAGS
  rm -f "$SCRATCH/stations/swamp-planet/transcript.md" "$SCRATCH/stations/swamp-planet/transcript.txt"
  ( cd "$SCRATCH" && python3 tools/synthesize-closeout/hints.py extract --stations "$SCRATCH/stations" \
      --sources "sky-city=transcript,swamp-planet=fallback,ice-planet=transcript,snow-monster-cave=transcript,asteroid-field=transcript" \
      --json "$SCRATCH/h2.json" --md "$SCRATCH/h2.md" ) >/dev/null 2>&1
  check "never flags a fallback station"        "! grep -q 'swamp-planet' '$SCRATCH/h2.json'"

  # Coverage is advisory: it reports, it never rejects.
  cat > "$SCRATCH/d.json" <<'JSON'
{"stations":[{"id":"sky-city","lede":"x","points":[{"t":"A shared rate limit","d":"Six hundred a minute turned out shared regionally, leaving ninety on Mondays."}],"takeaway":"x"}],
 "patterns":[{"t":"x","d":"x"}],"closing_line":"x"}
JSON
  ( cd "$SCRATCH" && python3 tools/synthesize-closeout/hints.py check \
      --hints "$SCRATCH/h.json" --deck-json "$SCRATCH/d.json" ) >"$SCRATCH/cov.txt" 2>&1
  local covrc=$?
  check "coverage reports, never rejects"       "[[ $covrc -eq 0 ]]"
  check "reports the one that landed"           "grep -Eq '^ +in +sky-city' '$SCRATCH/cov.txt'"
  check "reports the one that did not"          "grep -Eq '^ +MISSING +asteroid-field' '$SCRATCH/cov.txt'"

  # And the whole pipeline still runs, with the hint block reaching the prompt.
  run_synth live
  check "synthesis still exits 0"               "[[ $RC -eq 0 ]]"
}

scen_sponsors() {  # a sponsor logo on the wrong station, or invisible on it, is the
                   # one defect in this deck somebody paid us not to ship
  new_scratch; seed_questions; establish_floor
  for st in "Sky City" "Swamp Planet" "Ice Planet" "Snow Monster Cave" "Asteroid Field"; do arrive "$st" txt; done
  ( cd "$SCRATCH" && ./tools/intake-transcript/intake.sh "$SCRATCH/Downloads" ) >/dev/null 2>&1
  run_synth live
  check "exits 0"                               "[[ $RC -eq 0 ]]"
  check "exactly the three sponsored stations"  "[[ \$(deck_json SPONSORS | python3 -c 'import json,sys;print(\",\".join(sorted(json.load(sys.stdin))))') == 'ice-planet,snow-monster-cave,swamp-planet' ]]"
  check "logo shows only on its own station"    "deck_says 'SPONSORS[s.id]'"
  check "unsponsored screens hide it"           "deck_says 'el(\"sponsor\").hidden = !sponsor'"
  # A display rule beats the hidden attribute, so the two unsponsored stations
  # rendered a src-less img: broken-image icon plus the previous sponsor's alt text.
  check "hidden really wins over display"       "deck_says '[hidden] { display: none !important; }'"
  check "and the stale alt is cleared with it"  "deck_says 'el(\"sponsor\").alt = \"\"'"

  # The variant matters more than the presence: the light-ink logo is invisible on a
  # light theme and the dark-ink one vanishes into a dark theme, and either way the
  # deck still builds, still validates, and still looks fine until it is on a wall.
  local res; res="$(python3 - "$DECK" "$REPO" <<'SPONSORPY'
import base64, json, pathlib, sys
src = pathlib.Path(sys.argv[1]).read_text(); repo = pathlib.Path(sys.argv[2])
def grab(name):
    i = src.index(f"const {name} = ") + len(f"const {name} = ")
    depth, j, instr, esc = 0, i, False, False
    while j < len(src):
        c = src[j]
        if instr:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': instr = False
        elif c == '"': instr = True
        elif c in "{[": depth += 1
        elif c in "}]":
            depth -= 1
            if depth == 0: break
        j += 1
    return json.loads(src[i:j+1])
sponsors, themes = grab("SPONSORS"), grab("THEMES")
bad = []
for sid, sp in sponsors.items():
    dark = int(themes[sid]["surface"][1:3], 16) < 64
    want = repo / "assets/sponsors" / (f"{sp['name'].lower()}{'-dark' if dark else ''}.png")
    if not sp["src"].startswith("data:image/png;base64,"):
        bad.append(f"{sid} is not an inlined png"); continue
    got = base64.b64decode(sp["src"].split(",", 1)[1])
    if not want.exists(): bad.append(f"{sid} wants missing {want.name}")
    elif got != want.read_bytes(): bad.append(f"{sid} is not {want.name}")
print(("FAIL " + ", ".join(bad)) if bad else f"OK {len(sponsors)} logos")
SPONSORPY
)"
  if [[ "$res" == OK* ]]; then ok "each logo is the variant its theme needs (${res#OK })"
  else bad "wrong sponsor logo variant: $res"; fi
}

scen_docs() {  # the scenario table has silently drifted twice; stop it happening again
  local missing
  missing="$(python3 - "$REPO" <<'DOCSPY'
import pathlib, re, sys
repo = pathlib.Path(sys.argv[1])
all_block = re.search(r"^ALL=\((.*?)\)$", (repo / "tests/rehearse.sh").read_text(), re.S | re.M).group(1)
table = (repo / "tests/README.md").read_text()
print(" ".join(x for x in all_block.split() if f"`{x}`" not in table))
DOCSPY
)"
  if [[ -z "$missing" ]]; then ok "every scenario is documented in tests/README.md"
  else bad "undocumented scenarios: $missing"; fi
}

# ---------------------------------------------------------------- driver
echo
echo "Rehearsal: ${SCENARIOS[*]}"
[[ "${REAL_MODEL:-0}" == "1" ]] && echo "${c_y}Using the real claude CLI${c_0}"
echo

for SCEN in "${SCENARIOS[@]}"; do
  echo "  ${c_d}scenario:${c_0} $SCEN"
  ELAPSED_MS=0
  SCRATCH=""          # not every scenario needs a scratch copy of the repo
  "scen_${SCEN//-/_}"
  echo "    ${c_d}synthesis wall time: ${ELAPSED_MS}ms${c_0}"
  if [[ -n "$SCRATCH" ]]; then
    if [[ $KEEP == 1 ]]; then echo "    ${c_d}scratch: $SCRATCH${c_0}"; else rm -rf "$SCRATCH"; fi
  fi
  echo
done

echo "  ${c_g}$pass passed${c_0}, $( ((fail)) && echo "${c_r}$fail failed${c_0}" || echo "0 failed" )"
if ((fail)); then printf '    %s\n' "${FAILURES[@]}"; exit 1; fi
