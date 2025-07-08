import tempfile
import subprocess
import os
import time
import uuid

def run_code_with_subprocess(code: str, input_text: str, ext: str, command: list[str], wrapper: str = "{code}"):
    filename = f"temp_{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(tempfile.gettempdir(), filename)

    wrapped_code = wrapper.format(code=code, input=input_text)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(wrapped_code)

    try:
        start = time.time()
        result = subprocess.run(
            command + [filepath],
            input=input_text,
            capture_output=True,
            text=True,
            timeout=5,
        )
        end = time.time()
        return {
            "output": result.stdout.strip(),
            "error": result.stderr.strip(),
            "execution_time": round(end - start, 4),
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

# 各言語用ラッパー関数（input_text は文字列渡し）
def run_php_code(code: str, input_text: str):
    return run_code_with_subprocess(code, input_text, "php", ["php"])

def run_ruby_code(code: str, input_text: str):
    return run_code_with_subprocess(code, input_text, "rb", ["ruby"])

def run_c_code(code: str, input_text: str):
    c_file = f"temp_{uuid.uuid4().hex}"
    src_path = os.path.join(tempfile.gettempdir(), f"{c_file}.c")
    exe_path = os.path.join(tempfile.gettempdir(), f"{c_file}.out")
    with open(src_path, "w", encoding="utf-8") as f:
        f.write(code)
    try:
        subprocess.run(["gcc", src_path, "-o", exe_path], check=True)
        start = time.time()
        result = subprocess.run([exe_path], input=input_text, capture_output=True, text=True, timeout=5)
        end = time.time()
        return {"output": result.stdout.strip(), "error": result.stderr.strip(), "execution_time": round(end - start, 4)}
    except subprocess.TimeoutExpired:
        return {"output": "", "error": "Time Limit Exceeded", "execution_time": 5.0}
    except subprocess.CalledProcessError as e:
        return {"output": "", "error": str(e), "execution_time": 0.0}
    finally:
        if os.path.exists(src_path): os.remove(src_path)
        if os.path.exists(exe_path): os.remove(exe_path)

def run_cpp_code(code: str, input_text: str):
    cpp_file = f"temp_{uuid.uuid4().hex}"
    src_path = os.path.join(tempfile.gettempdir(), f"{cpp_file}.cpp")
    exe_path = os.path.join(tempfile.gettempdir(), f"{cpp_file}.out")
    with open(src_path, "w", encoding="utf-8") as f:
        f.write(code)
    try:
        subprocess.run(["g++", src_path, "-o", exe_path], check=True)
        start = time.time()
        result = subprocess.run([exe_path], input=input_text, capture_output=True, text=True, timeout=5)
        end = time.time()
        return {"output": result.stdout.strip(), "error": result.stderr.strip(), "execution_time": round(end - start, 4)}
    except subprocess.TimeoutExpired:
        return {"output": "", "error": "Time Limit Exceeded", "execution_time": 5.0}
    except subprocess.CalledProcessError as e:
        return {"output": "", "error": str(e), "execution_time": 0.0}
    finally:
        if os.path.exists(src_path): os.remove(src_path)
        if os.path.exists(exe_path): os.remove(exe_path)

def run_go_code(code: str, input_text: str):
    return run_code_with_subprocess(code, input_text, "go", ["go", "run"])

def run_rust_code(code: str, input_text: str):
    rust_file = f"temp_{uuid.uuid4().hex}"
    src_path = os.path.join(tempfile.gettempdir(), f"{rust_file}.rs")
    exe_path = os.path.join(tempfile.gettempdir(), f"{rust_file}.out")
    with open(src_path, "w", encoding="utf-8") as f:
        f.write(code)
    try:
        subprocess.run(["rustc", src_path, "-o", exe_path], check=True)
        start = time.time()
        result = subprocess.run([exe_path], input=input_text, capture_output=True, text=True, timeout=5)
        end = time.time()
        return {"output": result.stdout.strip(), "error": result.stderr.strip(), "execution_time": round(end - start, 4)}
    except subprocess.TimeoutExpired:
        return {"output": "", "error": "Time Limit Exceeded", "execution_time": 5.0}
    except subprocess.CalledProcessError as e:
        return {"output": "", "error": str(e), "execution_time": 0.0}
    finally:
        if os.path.exists(src_path): os.remove(src_path)
        if os.path.exists(exe_path): os.remove(exe_path)

def run_kotlin_code(code: str, input_text: str):
    return run_code_with_subprocess(code, input_text, "kt", ["kotlinc", "-script"])

def run_swift_code(code: str, input_text: str):
    return run_code_with_subprocess(code, input_text, "swift", ["swift"])

def run_dart_code(code: str, input_text: str):
    return run_code_with_subprocess(code, input_text, "dart", ["dart"])

def run_typescript_code(code: str, input_text: str):
    ts_filename = f"temp_{uuid.uuid4().hex}"
    ts_path = os.path.join(tempfile.gettempdir(), f"{ts_filename}.ts")
    js_path = os.path.join(tempfile.gettempdir(), f"{ts_filename}.js")
    with open(ts_path, "w", encoding="utf-8") as f:
        f.write(code)
    try:
        subprocess.run(["tsc", ts_path], check=True)
        start = time.time()
        result = subprocess.run(["node", js_path], input=input_text, capture_output=True, text=True, timeout=5)
        end = time.time()
        return {"output": result.stdout.strip(), "error": result.stderr.strip(), "execution_time": round(end - start, 4)}
    except subprocess.CalledProcessError as e:
        return {"output": "", "error": str(e), "execution_time": 0.0}
    finally:
        if os.path.exists(ts_path): os.remove(ts_path)
        if os.path.exists(js_path): os.remove(js_path)

def run_bash_code(code: str, input_text: str):
    return run_code_with_subprocess(code, input_text, "sh", ["bash"])

def run_r_code(code: str, input_text: str):
    return run_code_with_subprocess(code, input_text, "R", ["Rscript"])
