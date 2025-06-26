from sqlalchemy import func
from project.models import Mentorship, MentorshipFeedback, db, Chats, User # db, Chats, User モデルをインポート
from datetime import datetime, timedelta

def calculate_average_dm_response_time(user_id: str) -> float | None:
    """
    指定されたユーザーIDのダイレクトメッセージにおける平均返信時間を計算します。
    ユーザーがDMを受信してから、その相手にDMで返信するまでの平均時間（秒）を返します。

    Args:
        user_id (str): 返信時間を計算したいユーザーのID。

    Returns:
        float | None: 平均返信時間（秒単位）。該当するDMがない場合は None を返します。
    """
    # ユーザーが受信したダイレクトメッセージを、送信者ごとにまとめる
    # key: send_user_id (DMの送り主), value: その送り主からの受信メッセージリスト
    incoming_dms_by_sender = {}
    incoming_query = Chats.query.filter(
        Chats.receiver_user_id == user_id,
        Chats.group_id.is_(None) # グループチャットではない (receiver_user_idがあるため基本DMだが念のため)
    ).order_by(Chats.chat_at).all()

    for msg in incoming_query:
        if msg.send_user_id not in incoming_dms_by_sender:
            incoming_dms_by_sender[msg.send_user_id] = []
        incoming_dms_by_sender[msg.send_user_id].append(msg)

    # ユーザーが送信したダイレクトメッセージを、受信者ごとにまとめる
    # key: receiver_user_id (DMの受け取り主), value: その受け取り主への送信メッセージリスト
    outgoing_dms_by_receiver = {}
    outgoing_query = Chats.query.filter(
        Chats.send_user_id == user_id,
        Chats.group_id.is_(None), # グループチャットではない
        Chats.receiver_user_id.isnot(None) # receiver_user_idが設定されている = ダイレクトメッセージ
    ).order_by(Chats.chat_at).all()

    for msg in outgoing_query:
        if msg.receiver_user_id not in outgoing_dms_by_receiver:
            outgoing_dms_by_receiver[msg.receiver_user_id] = []
        outgoing_dms_by_receiver[msg.receiver_user_id].append(msg)

    response_durations = [] # 各返信にかかった時間（timedeltaオブジェクト）を格納するリスト

    # 各受信メッセージに対して、対応する返信を探す
    for sender_id, incoming_msgs in incoming_dms_by_sender.items():
        if sender_id not in outgoing_dms_by_receiver:
            continue # この送信者に対してユーザーが返信を一度も送っていない

        outgoing_msgs_to_sender = outgoing_dms_by_receiver[sender_id]

        for incoming_msg in incoming_msgs:
            # incoming_msg の後に、sender_id へ送られた最初のoutgoing_msg を探す
            first_response = None
            for outgoing_msg in outgoing_msgs_to_sender:
                if outgoing_msg.chat_at > incoming_msg.chat_at:
                    if first_response is None or outgoing_msg.chat_at < first_response.chat_at:
                        first_response = outgoing_msg
            
            if first_response:
                duration = first_response.chat_at - incoming_msg.chat_at
                response_durations.append(duration)

    if not response_durations:
        return None # 応答データがない場合

    # timedeltaのリストから合計秒数を計算し、平均を出す
    total_seconds = sum(td.total_seconds() for td in response_durations)
    return total_seconds / len(response_durations)

def get_average_mentor_rating(mentor_id: str) -> float | None:
    """
    指定されたメンターの平均評価を計算し、小数点以下第一位で返します。
    """
    # 🔹 指定されたメンターの全てのメンターシップIDを取得
    mentorship_ids = db.session.query(Mentorship.mentorship_id)\
        .filter(Mentorship.mentor_id == mentor_id)\
        .all()
    
    mentorship_ids = [m.mentorship_id for m in mentorship_ids]

    if not mentorship_ids:
        return None # メンターシップが一つもない

    # 🔹 関連する全てのフィードバックのレーティングを対象に平均を計算
    average_rating_result = db.session.query(
        func.avg(MentorshipFeedback.rating)
    ).filter(
        MentorshipFeedback.mentorship_id.in_(mentorship_ids)
    ).scalar()

    if average_rating_result is None:
        return None # フィードバックが一つもない

    return round(float(average_rating_result), 1)