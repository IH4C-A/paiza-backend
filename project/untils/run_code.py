import uuid
import tempfile
import subprocess
import os
import time

def run_python_code(user_code: str, input_text: str):
    import subprocess
    import tempfile
    import os
    import time
    import uuid

    # 実行用のラッパーコード
    full_code = f"""{user_code}

if __name__ == "__main__":
    result = solution({repr(input_text)})
    print(result)
"""

    filename = f"temp_{uuid.uuid4().hex}.py"
    filepath = os.path.join(tempfile.gettempdir(), filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_code)

    try:
        start = time.time()
        result = subprocess.run(
            ["python", filepath],
            capture_output=True,
            text=True,
            timeout=5
        )
        end = time.time()

        return {
            "output": result.stdout.strip(),
            "error": result.stderr.strip(),
            "execution_time": round(end - start, 3),
        }

    except subprocess.TimeoutExpired:
        return {
            "output": "",
            "error": "Time Limit Exceeded",
            "execution_time": 5.0,
        }

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

