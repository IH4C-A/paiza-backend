from flask import Blueprint, request, jsonify
from project import db
from project.models import Answer, TestCase
import uuid
from project.untils.run_code import run_python_code
from project.untils.run_javascript_code import run_javascript_code
from project.untils.run_html_code import run_html_code
from project.untils.run_code_iroiro import run_bash_code, run_c_code, run_cpp_code, run_dart_code, run_go_code, run_kotlin_code,run_php_code, run_r_code, run_ruby_code, run_rust_code, run_swift_code, run_typescript_code

test_case_api = Blueprint("test_case_api", __name__)

# 作成
@test_case_api.route("/test_cases", methods=["POST"])
def create_test_case():
    data = request.get_json()
    test_case = TestCase(
        problem_id=data["problem_id"],
        input_text=data["input_text"],
        expected_output=data["expected_output"],
        is_public=data.get("is_public", False)
    )
    db.session.add(test_case)
    db.session.commit()
    return jsonify({"message": "テストケースを作成しました", "test_case_id": test_case.test_case_id}), 201

# 一覧取得（問題IDでフィルター可）
@test_case_api.route("/test_cases", methods=["GET"])
def get_test_cases():
    problem_id = request.args.get("problem_id")
    query = TestCase.query
    if problem_id:
        query = query.filter_by(problem_id=problem_id)
    cases = query.all()
    return jsonify([{
        "test_case_id": case.test_case_id,
        "problem_id": case.problem_id,
        "input_text": case.input_text,
        "expected_output": case.expected_output,
        "is_public": case.is_public,
    } for case in cases])

# 単一取得
@test_case_api.route("/test_cases/<test_case_id>", methods=["GET"])
def get_test_case(test_case_id):
    case = TestCase.query.get_or_404(test_case_id)
    return jsonify({
        "test_case_id": case.test_case_id,
        "problem_id": case.problem_id,
        "input_text": case.input_text,
        "expected_output": case.expected_output,
        "is_public": case.is_public,
    })

# 更新
@test_case_api.route("/test_cases/<test_case_id>", methods=["PUT"])
def update_test_case(test_case_id):
    data = request.get_json()
    case = TestCase.query.get_or_404(test_case_id)
    case.input_text = data.get("input_text", case.input_text)
    case.expected_output = data.get("expected_output", case.expected_output)
    case.is_public = data.get("is_public", case.is_public)
    db.session.commit()
    return jsonify({"message": "テストケースを更新しました"})

# 削除
@test_case_api.route("/test_cases/<test_case_id>", methods=["DELETE"])
def delete_test_case(test_case_id):
    case = TestCase.query.get_or_404(test_case_id)
    db.session.delete(case)
    db.session.commit()
    return jsonify({"message": "テストケースを削除しました"})


@test_case_api.route('/run', methods=['POST'])
def run_code():
    data = request.get_json()
    code = data.get("code")
    problem_id = data.get("problem_id")
    language = data.get("language").lower()

    test_cases = TestCase.query.filter_by(problem_id=problem_id).all()
    results = []

    for case in test_cases:
        input_text = case.input_text

        # 言語ごとに関数を選択
        if language == "python":
            result = run_python_code(code, input_text)
        elif language == "javascript":
            result = run_javascript_code(code, input_text)
        elif language == "php":
            result = run_php_code(code, input_text)
        elif language == "ruby":
            result = run_ruby_code(code, input_text)
        elif language == "c":
            result = run_c_code(code, input_text)
        elif language == "c++":
            result = run_cpp_code(code, input_text)
        elif language == "go":
            result = run_go_code(code, input_text)
        elif language == "rust":
            result = run_rust_code(code, input_text)
        elif language == "kotlin":
            result = run_kotlin_code(code, input_text)
        elif language == "swift":
            result = run_swift_code(code, input_text)
        elif language == "dart":
            result = run_dart_code(code, input_text)
        elif language == "typescript":
            result = run_typescript_code(code, input_text)
        elif language == "bash":
            result = run_bash_code(code, input_text)
        elif language == "r":
            result = run_r_code(code, input_text)
        elif language in ["html", "css"]:
            result = run_html_code(code, language)
        else:
            return jsonify({"error": f"{language} is not supported"}), 400

        passed = result["output"].strip() == case.expected_output.strip() if language not in ["html", "css"] else True

        results.append({
            "test_case": {
                "test_case_id": case.test_case_id,
                "problem_id": case.problem_id,
                "input_text": case.input_text,
                "expected_output": case.expected_output,
                "is_public": case.is_public
            },
            "actual_output": result["output"],
            "execution_time": result["execution_time"],
            "passed": passed
        })

    all_passed = all(r["passed"] for r in results)
    return jsonify({"passed": all_passed, "results": results})

