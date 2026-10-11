"""Read-only gate for obvious leaks in Git-tracked public files.

Heuristic defense in depth, not a substitute for full history and asset review.
Outputs paths only; never echoes a matching secret or private value.
"""
import pathlib, re, subprocess, sys

paths=subprocess.check_output(["git","ls-files","-z"]).decode().split("\0")
bad=[]
patterns=[
    re.compile(r"mongodb(?:\+srv)?://[^@\s]{1,200}:[^@\s]{1,200}@", re.I),
    re.compile(r"(?i)(?:sk[_-]|xi-api-key[=:][ \t]*)(?:[A-Za-z0-9_\-]{25,})"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]
for p in filter(None,paths):
    name=pathlib.PurePath(p).name
    if name==".env" or name.startswith(".env.") and name!=".env.example" or name.endswith((".pem",".p12",".key")):
        bad.append(p+":FORBIDDEN_PATH");continue
    try:
        txt=pathlib.Path(p).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        continue
    if any(pattern.search(txt) for pattern in patterns):
        bad.append(p+":POTENTIAL_SECRET")
if bad:
    for error in bad:
        print("FAIL_PUBLIC_SCAN:"+error)
    sys.exit(1)
print("PASS_PUBLIC_SCAN tracked_paths_checked="+str(sum(bool(p) for p in paths)))
