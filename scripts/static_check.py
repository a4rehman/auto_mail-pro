"""
Static analysis: byte-compile every source file and run pyflakes if available.
Catches undefined names, unused imports, syntax errors.

Run:  python scripts/static_check.py
"""
import sys
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
TARGET_DIRS = ["app", "config", "core", "database", "discovery", "enrichment",
               "intelligence", "outreach", "exports", "security", "tests", "scripts"]

files = []
for d in TARGET_DIRS:
    files.extend(sorted((ROOT / d).rglob("*.py")))

print(f"Compiling {len(files)} Python files...")
errors = 0
for f in files:
    src = f.read_text(encoding="utf-8")
    try:
        compile(src, str(f), "exec")
    except SyntaxError as e:
        errors += 1
        print(f"  SYNTAX ERROR: {f.relative_to(ROOT)}:{e.lineno}: {e.msg}")
print(f"Compile: {len(files) - errors}/{len(files)} OK")

print("\nRunning pyflakes...")
try:
    import pyflakes  # noqa
    have = True
except ImportError:
    have = False

if not have:
    print("  pyflakes not installed -- installing...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pyflakes"], check=False)
    try:
        import pyflakes  # noqa
        have = True
    except ImportError:
        have = False

if have:
    proc = subprocess.run(
        [sys.executable, "-m", "pyflakes", *[str(f) for f in files]],
        capture_output=True, text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    lines = [ln for ln in out.splitlines() if ln.strip()]
    if not lines:
        print("  pyflakes: clean")
    else:
        for ln in lines:
            print("  " + ln.replace(str(ROOT) + "\\", "").replace(str(ROOT) + "/", ""))
        print(f"  pyflakes findings: {len(lines)}")
