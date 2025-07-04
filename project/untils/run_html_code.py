def run_html_code(code: str, language: str):
    from html import escape
    import time

    start = time.time()
    if language == "html":
        html_content = code
    elif language == "css":
        html_content = f"""
        <html>
          <head><style>{code}</style></head>
          <body><h1>CSS Test</h1><div class="box">Box</div></body>
        </html>
        """
    else:
        html_content = "<!-- Unsupported HTML/CSS language -->"

    end = time.time()

    return {
        "output": html_content,
        "error": "",
        "execution_time": round(end - start, 4)
    }
