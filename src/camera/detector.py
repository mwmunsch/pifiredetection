import subprocess

process = subprocess.Popen(
    ["rpicam-detect", "--timeout", "0"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

if process.stdout is None:
    raise RuntimeError("Failed to capture stdout")

for line in process.stdout:
    if "confidence" in line:
        print("[VISION]", line.strip())