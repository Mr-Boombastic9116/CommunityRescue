"""
Backend Forwarder / Runner for Community Food Rescue Network Verification Script.
Invokes the canonical verification script in the root scripts/ directory.
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
CANONICAL_VERIFIER = os.path.join(PROJECT_ROOT, "scripts", "verify_seed_data.py")

if not os.path.exists(CANONICAL_VERIFIER):
    CANONICAL_VERIFIER = os.path.join(os.path.dirname(SCRIPT_DIR), "scripts", "verify_seed_data.py")

with open(CANONICAL_VERIFIER, "r", encoding="utf-8") as f:
    code = compile(f.read(), CANONICAL_VERIFIER, "exec")
    exec(code, {"__name__": "__main__", "__file__": CANONICAL_VERIFIER})

