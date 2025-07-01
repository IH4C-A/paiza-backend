import uuid
import tempfile
import subprocess
import os
import time

def run_python_code(code: str, input_text: str):
    filename = f"temp_{uuid.uuid4().hex}.py"
    filepath = os.path.join(tempfile.gettempdir(), filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(code)

    try:
        start = time.time()
        result = subprocess.run(
            ["python", filepath],
            input=input_text,
            capture_output=True,
            text=True,
            timeout=5,
        )
        end = time.time()

        output = result.stdout.strip()
        return {
            "output": output,
            "error": result.stderr.strip(),
            "execution_time": round(end - start, 3),
        }

    except subprocess.TimeoutExpired:
        return {
            "output": "Time Limit Exceeded",
            "error": "",
            "execution_time": 5.0,
        }

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
