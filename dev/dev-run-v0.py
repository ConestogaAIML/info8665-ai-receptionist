"""
Execution script called by orchestrator.ipynb.
Starts the FastAPI server in development mode.
"""
import subprocess
import sys


def run():
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        check=True,
    )


if __name__ == "__main__":
    run()
