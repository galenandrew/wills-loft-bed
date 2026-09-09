#!/bin/bash
# PostToolUse hook (Write|Edit). Reads the tool call JSON on stdin.
#   dimensions.yaml / verify.py            → verify.py; FAIL/WARN lines go back to the model (exit 2)
#   those + drawings/ content/ cad/*.py    → build.py; the one-line change report is injected as context
#   (cad/*.py is in drawings/model.py's KERNEL_INPUTS: editing it can move Drawing 4.)
#   those + sheets/*.py                    → build2.py, which renders docs/ off the kernel
# Runs from the project directory (Claude Code's cwd for hooks).
f=$(jq -r '.tool_input.file_path // empty')
[ -z "$f" ] && exit 0
case "$f" in
  */dimensions.yaml|*/verify.py)      check=1; build=1; build2=1 ;;
  */drawings/*.py|*/cad/*.py)         build=1; build2=1 ;;
  */content/*)                        build=1 ;;
  */sheets/*.py)                      build2=1 ;;
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
if [ -n "$build2" ]; then
  out=$(python3 build2.py --quiet 2>&1); rc=$?
  if [ $rc -ne 0 ]; then
    printf "build2.py FAILED after editing %s:\n%s\n" "$(basename "$f")" "$(echo "$out" | tail -15)" >&2
    exit 2
  fi
  ctx="${ctx:+$ctx · }$out"
fi
jq -n --arg c "$ctx" '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$c}}'
