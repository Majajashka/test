import subprocess
import os
import sys
from pathlib import Path


def find_lrelease():
    return Path(r"C:\Qt\6.11.1\mingw_64\bin\lrelease.exe")


LRELEASE = find_lrelease()
DIR = Path(__file__).parent

if not LRELEASE.exists():
    sys.exit(1)

for ts in DIR.glob("stego_*.ts"):
    qm = ts.with_suffix(".qm")
    subprocess.run([str(LRELEASE), str(ts), "-qm", str(qm)], check=True)
    print(f"{ts.name} -> {qm.name}")
