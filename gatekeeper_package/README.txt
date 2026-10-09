Prompt Gatekeeper -- Quick Install
===================================

CONTENTS
--------
  gatekeeper.py        - UserPromptSubmit hook (model routing, [check] mode, Option D)
  state_monitor.py     - Stop hook (STATE [CLEAN/DIRTY] after every turn)
  install_gatekeeper.py - Installer script
  README.txt           - This file

REQUIREMENTS
------------
  - Claude Code installed and configured
  - Python 3.8+ (any standard install)

INSTALL
-------
1. Copy this entire folder to your machine.
2. Open a terminal in the folder.
3. Run:
       python install_gatekeeper.py

   The installer will:
   - Create ~/.claude/hooks/
   - Copy both hook scripts into it
   - Create task_state.json (clean state)
   - Register both hooks in ~/.claude/settings.json
   - Append the Task State Convention to ~/.claude/CLAUDE.md
   - Compile both scripts and confirm they are error-free
   - Print smoke test commands

4. Restart Claude Code (or open a new session).

VERIFY
------
Run the smoke tests printed at the end of the installer, or:

  printf '{"user_prompt":"review all the ttl files"}' | python ~/.claude/hooks/gatekeeper.py

Expected: JSON recommending Opus 5.5, effort high.

TOGGLE ON / OFF
---------------
Edit ENABLED = True/False near the top of each script.
Always run:  python -m py_compile gatekeeper.py state_monitor.py  after any edit.

FULL DOCUMENTATION
------------------
See prompt_gatekeeper_model_switcher.md (in the Claude config dir after install,
or wherever you copied the source package from).
