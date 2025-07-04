from flask import request, send_file, jsonify, Blueprint, current_app
import requests
import os
import uuid
import google.generativeai as genai
import io
from project.models import Plant # Plantモデルをインポート
# dbオブジェクトのインポートも必要です。通常は __init__.py で定義したものをインポートします
# from . import db # または from your_app_name import db のように適切にインポート


gemini = Blueprint('gemini', __name__)

# 植物の性格設定をFlask側に定義 (moodカラムのIDに対応)
personalities = [
    {
      "id": "cheerful",
      "name": "明るい励まし屋",
      "description": "いつも前向きで、あなたを元気づけてくれます。",
      "traits": ["励まし上手", "ポジティブ", "エネルギッシュ"],
      "prompt_instruction": "あなたは明るい励まし屋の植物です。常にポジティブな言葉でユーザーを元気づけてください。エネルギッシュに、そして優しく励ましましょう。",
    },
    {
      "id": "calm",
      "name": "冷静なアドバイザー",
      "description": "落ち着いていて、的確なアドバイスをくれます。",
      "traits": ["論理的", "冷静", "分析力"],
      "prompt_instruction": "あなたは冷静なアドバイザーの植物です。落ち着いて、論理的で的確なアドバイスを簡潔に提供してください。",
    },
    {
      "id": "gentle",
      "name": "優しい癒し系",
      "description": "温かく見守り、疲れた時に癒してくれます。",
      "traits": ["優しい", "共感力", "癒し"],
      "prompt_instruction": "あなたは優しい癒し系の植物です。ユーザーを温かく見守り、疲れた時に寄り添い、癒しとなる言葉を選んでください。",
    },
    {
      "id": "strict",
      "name": "厳しいコーチ",
      "description": "時には厳しく、あなたの成長を促してくれます。",
      "traits": ["規律正しい", "目標志向", "成長重視"],
      "prompt_instruction": "あなたは厳しいコーチの植物です。ユーザーの成長を促すために、時には厳しくも的確なアドバイスを与えてください。具体的な行動を促す言葉も良いでしょう。",
    },
]

# IDでpersonalityを素早くルックアップできる辞書を作成
PERSONALITY_MAP = {p["id"]: p for p in personalities}

MAX_GEMINI_RESPONSE_TOKENS = 500
@gemini.route("/talk", methods=["POST"])
def talk():
    gemini_api_key = current_app.config.get("GEMINI_API_KEY")
    if not gemini_api_key:
        current_app.logger.error("GEMINI_API_KEY is not configured in app.config.")
        return jsonify({"error": "Gemini API Key is not configured."}), 500

    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        current_app.logger.error(f"Error configuring Gemini API or loading model: {e}")
        return jsonify({"error": f"Error initializing Gemini model: {str(e)}"}), 500

    data = request.json
    user_transcript = data.get("transcript", "") # フロントエンドが 'transcript' を送っているため変更
    plant_id = data.get("character") # フロントエンドが 'character' を plant_id として送っているため変更
    speaker_id = int(data.get("speaker", 1)) # VoicevoxのスピーカーID

    if not user_transcript or not plant_id:
        current_app.logger.error("Missing 'transcript' or 'character' (plant_id) in request.")
        return jsonify({"error": "Missing 'transcript' or 'character' (plant_id)."}), 400

    # 1. データベースから植物の情報を取得
    plant = Plant.query.get(plant_id)
    if not plant:
        current_app.logger.error(f"Plant with ID {plant_id} not found in DB.")
        return jsonify({"error": f"Plant not found: {plant_id}"}), 404

    # 2. plant.mood から対応する性格設定を取得
    personality_info = PERSONALITY_MAP.get(plant.mood)
    if not personality_info:
        current_app.logger.error(f"Personality ID '{plant.mood}' not found in personalities map.")
        return jsonify({"error": f"Unknown personality ID: {plant.mood}"}), 500

    plant_name = plant.plant_name
    # mood_name = personality_info["name"] # 例: "明るい励まし屋"
    # mood_description = personality_info["description"] # 例: "いつも前向きで..."
    # mood_traits = ", ".join(personality_info["traits"]) # 例: "励まし上手, ポジティブ, エネルギッシュ"
    prompt_instruction = personality_info["prompt_instruction"] # Geminiへの具体的な指示

    # 3. プロンプトの構築: 植物の性格設定はバックエンドで結合し、ユーザー入力のみを受け取る
    # 例: より具体的で詳細な指示を盛り込む
    prompt = f"""あなたは[{plant_name}]という植物のキャラクターです。
{prompt_instruction}
ユーザーからのメッセージに日本語で応答してください。
現在の植物の状態：成長段階は[{plant.growth_stage}]、気分は[{plant.mood}]、大きさは[{plant.size}]です。
ユーザー: {user_transcript}
{plant_name}としての返答:"""


    print(f"Generated prompt: {prompt}") # デバッグ用に生成されたプロンプトを出力

    try:
        generation_config = genai.types.GenerationConfig(max_output_tokens=MAX_GEMINI_RESPONSE_TOKENS)
        gemini_response = model.generate_content(prompt,generation_config=generation_config).text
    except Exception as e:
        current_app.logger.error(f"Error calling Gemini API: {e}")
        return jsonify({"error": f"Failed to get response from Gemini API: {str(e)}"}), 500

    # VOICEVOXへ音声合成リクエスト
    try:
        audio_query_params = {
            "text": gemini_response,
            "speaker": speaker_id, # DBから取得したspeaker_idを使うことも可能
        }
        audio_query = requests.post(
            "http://localhost:50021/audio_query",
            params=audio_query_params,
            timeout=10 # タイムアウトを追加
        )
        audio_query.raise_for_status()

        synthesis_params = {
            "speaker": speaker_id, # ここもspeaker_id変数を使う
        }
        synthesis = requests.post(
            "http://localhost:50021/synthesis",
            params=synthesis_params,
            json=audio_query.json(),
            timeout=30 # タイムアウトを追加
        )
        synthesis.raise_for_status()

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
        current_app.logger.error(f"An unexpected error occurred during Voicevox synthesis: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500