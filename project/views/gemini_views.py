from flask import request, send_file, jsonify, Blueprint, current_app # current_app をインポート
import requests
import os
import uuid
import google.generativeai as genai
import io # send_file でメモリから直接送信するためにioを再追加

gemini = Blueprint('gemini', __name__)


@gemini.route("/talk", methods=["POST"])
def talk():
    # リクエストが来たときに、current_app.config から API キーを取得する
    gemini_api_key = current_app.config.get("GEMINI_API_KEY")
    if not gemini_api_key:
        # API キーが設定されていない場合はエラーを返す
        current_app.logger.error("GEMINI_API_KEY is not configured in app.config.")
        return jsonify({"error": "Gemini API Key is not configured."}), 500

    # Gemini API の初期設定を関数内で（または一度だけ初期化されるように）行う
    try:
        genai.configure(api_key=gemini_api_key)
        # モデルもここで初期化するか、グローバル変数で一度だけ初期化
        # ただし、モデルオブジェクトはリクエストごとに再利用しても問題ない場合が多い
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        current_app.logger.error(f"Error configuring Gemini API or loading model: {e}")
        return jsonify({"error": f"Error initializing Gemini model: {str(e)}"}), 500


    data = request.json
    text = data.get("transcript", "")
    character = data.get("character", "")
    speaker = int(data.get("speaker", 1))

    prompt = f"{character}\nユーザー: {text}\n{character.split('の')[0]}:"
    print(text)
    try:
        gemini_response = model.generate_content(prompt).text
    except Exception as e:
        current_app.logger.error(f"Error calling Gemini API: {e}")
        return jsonify({"error": f"Failed to get response from Gemini API: {str(e)}"}), 500

    # VOICEVOXへ音声合成リクエスト
    try:
        audio_query = requests.post(
            "http://localhost:50021/audio_query",
            params={"text": gemini_response, "speaker": speaker},
            timeout=10 # タイムアウトを追加
        )
        audio_query.raise_for_status()

        # synthesis の speaker は audio_query の結果に含まれるため、paramsは不要な場合が多いですが、
        # 明示的に指定する場合は、audio_query_jsonを操作してから渡すか、paramsも追加します
        synthesis = requests.post(
            "http://localhost:50021/synthesis",
            params={"speaker": speaker}, # ここもspeaker変数を使う
            json=audio_query.json(),
            timeout=30 # タイムアウトを追加
        )
        synthesis.raise_for_status()

        # 一時ファイルに保存せず、メモリ上で音声データを処理して直接返す
        return send_file(
            io.BytesIO(synthesis.content),
            mimetype="audio/wav",
            as_attachment=False
        )
    except requests.exceptions.ConnectionError as e:
        current_app.logger.error(f"Voicevox engine connection error: {e}")
        return jsonify({"error": f"Failed to connect to Voicevox engine. Is it running at http://localhost:50021? Details: {e}"}), 503
    except requests.exceptions.Timeout:
        current_app.logger.error("Voicevox engine request timed out.")
        return jsonify({"error": "Voicevox engine request timed out."}), 504
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error from Voicevox engine: {e}. Response: {e.response.text if e.response else 'N/A'}")
        return jsonify({"error": f"Error from Voicevox engine: {e}. Response: {e.response.text if e.response else 'N/A'}"}), 500
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred during Voicevox synthesis: {e}", exc_info=True) # 詳細なログ出力
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500