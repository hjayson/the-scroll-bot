#!/usr/bin/env python3
"""Wrapper that runs newsletter_bot.py with full traceback output."""
import sys
import traceback

print("\u25b6 Starting newsletter_bot.py...")
try:
    with open("newsletter_bot.py") as f:
        code = compile(f.read(), "newsletter_bot.py", "exec")
    exec(code, {"__name__": "__main__", "__file__": "newsletter_bot.py"})
except SystemExit as e:
    print(f"Script exited with code: {e.code}")
    sys.exit(e.code)
except Exception:
    print("\n" + "=" * 60)
    print("FATAL ERROR \u2014 full traceback:")
    print("=" * 60)
    traceback.print_exc()
    print("=" * 60)
    sys.exit(1)
