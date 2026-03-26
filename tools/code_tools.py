import subprocess


def run_python(code: str) -> str:
    try:
        result = subprocess.run(
            ["python", "-c", code], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout or "Success, no output"
        else:
            return f"ERROR: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "ERROR: Execution timeout"
