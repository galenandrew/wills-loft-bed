#!/bin/bash
# PostToolUse hook (Write|Edit). Reads the tool call JSON on stdin.
#   dimensions.yaml / verify.py      → verify.py; FAIL/WARN lines go back to the model (exit 2)
#   those + drawings/ content/ tools/svgview.py → build.py; the one-line change report is injected as context
# Runs from the project directory (Claude Code's cwd for hooks).
f=$(jq -r '.tool_input.file_path // empty')
[ -z "$f" ] && exit 0
case "$f" in
  */dimensions.yaml|*/verify.py)      check=1; build=1 ;;
  */drawings/*.py|*/content/*|*/tools/svgview.py) build=1 ;;
  *) exit 0 ;;
esac
ctx=""
if [ -n "$check" ]; then
  out=$(python3 verify.py --quiet 2>&1); rc=$?
  if [ $rc -ne 0 ]; then
    printf "verify.py FAILED after editing %s:\n%s\n" "$(basename "$f")" "$(echo "$out" | grep -E 'FAIL|WARN|Error|error')" >&2
    exit 2
  fi
  ctx="verify.py: $(echo "$out" | tail -1)"
fi
if [ -n "$build" ]; then
  out=$(python3 build.py --quiet 2>&1); rc=$?
  if [ $rc -ne 0 ]; then
    printf "build.py FAILED after editing %s:\n%s\n" "$(basename "$f")" "$(echo "$out" | tail -15)" >&2
    exit 2
  fi
  ctx="${ctx:+$ctx · }$out"
fi
jq -n --arg c "$ctx" '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$c}}'
