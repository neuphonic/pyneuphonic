#!/usr/bin/env python3
import os
import sys
import subprocess
import shlex


def main():
    cmd = [sys.executable, "agent.py", "console", "--text"]
    env = os.environ.copy()

    print("Running:", " ".join(shlex.quote(c) for c in cmd))

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            cwd=os.path.dirname(os.path.abspath(__file__)),
            text=True,
            timeout=15,  # agent prints success and exits within ~10s
        )
    except subprocess.TimeoutExpired as e:
        print("\nTimeout waiting for agent to finish. Partial output:\n")
        print(e.stdout or "")
        sys.exit(1)

    print(proc.stdout)

    out = proc.stdout or ""
    if "Integration Test Success!" in out:
        print("Assertion passed: Success marker found in output.")
        sys.exit(0)
    else:
        print("Assertion failed: Success marker not found in output.")
        sys.exit(1)


if __name__ == "__main__":
    main()
