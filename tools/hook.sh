#!/bin/bash
# PostToolUse hook (Write|Edit). Reads the tool call JSON on stdin.
#   dimensions.yaml / verify.py            → verify.py; FAIL/WARN lines go back to the model (exit 2)
#   those + drawings/ cad/*.py content/    → build2.py, which renders docs/ off the kernel
#   (cad/*.py is in drawings/model.py's KERNEL_INPUTS: editing it can move Drawing 4.)
#   sheets/*.py                            → build2.py
# v1 (build.py / site/) is deprecated (2026-09-09) and no longer built by this hook —
# see CLAUDE.md "Source of truth and workflow". drawings/*.py still matters because the
# v2 reference pages render through its Rev U card builders (schedule.py, site.py cards).
# Runs from the project directory (Claude Code's cwd for hooks).
f=$(jq -r '.tool_input.file_path // empty')
[ -z "$f" ] && exit 0
case "$f" in
  */dimensions.yaml|*/verify.py)                                     check=1; build2=1 ;;
  */drawings/*.py|*/cad/*.py|*/content/*|*/sheets/*.py)               build2=1 ;;
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
if [ -n "$build2" ]; then
  out=$(python3 build2.py --quiet 2>&1); rc=$?
  if [ $rc -ne 0 ]; then
    printf "build2.py FAILED after editing %s:\n%s\n" "$(basename "$f")" "$(echo "$out" | tail -15)" >&2
    exit 2
  fi
  ctx="${ctx:+$ctx · }$out"
fi
jq -n --arg c "$ctx" '{hookSpecificOutput:{hookEventName:"PostToolUse",additionalContext:$c}}'
