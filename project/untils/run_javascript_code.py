def run_javascript_code(code: str, input_text: str):
    import tempfile
    import subprocess
    import os
    import time
    import uuid

    js_wrapper_code = f"""
function solution(input) {{
{code}
}}

const input = `{input_text}`;
try {{
  const result = solution(input);
  console.log(result);
}} catch (err) {{
  console.error("Error:", err.message);
}}
"""

    filename = f"temp_{uuid.uuid4().hex}.js"
    filepath = os.path.join(tempfile.gettempdir(), filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(js_wrapper_code)

    try:
        start = time.time()
        result = subprocess.run(
            ["node", filepath],
            capture_output=True,
            text=True,
            timeout=5,
        )
        end = time.time()
        return {
            "output": result.stdout.strip(),
            "error": result.stderr.strip(),
            "execution_time": round(end - start, 4)
        }

    except subprocess.TimeoutExpired:
        return {
            "output": "",
            "error": "Time Limit Exceeded",
            "execution_time": 5.0
        }

    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
