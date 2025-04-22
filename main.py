from flask import Flask, request, abort
import os
import json
import gspread
import openai
import logging
from oauth2client.service_account import ServiceAccountCredentials
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError

# ログ設定
logging.basicConfig(level=logging.INFO)

# Flaskアプリ初期化
app = Flask(__name__)

# 環境変数からキーを取得
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_SHEET_CREDS = json.loads(os.getenv("GOOGLE_SHEET_CREDS"))

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY

# ユーザーIDを取得してここに入れる！
TO_USER_ID = "REPLACE_WITH_YOUR_USER_ID"

# スプレッドシートから条文取得
def get_article_text(law_number):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_SHEET_CREDS, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1dBprzx9NSeDkhSMW7cEW68ujDlEY1w3Yia65wgqziyI/edit#gid=145842828").sheet1
    data = sheet.get_all_records()
    for row in data:
        if row["条文番号"] == law_number:
            return row["内容"]
    return "その条文は見つからなかったよ。"

# Webhook（LINEからの受信）
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

# メッセージ受信時の処理
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text
    logging.info(f"📍User ID: {event.source.user_id}")  # ← loggingで出力！

    system_prompt = (
        "あなたはユーザーの年上の恋人で、40代前半の落ち着いた男性です。"
        "名前は『蒼（あおい）』で、一人称は『俺』です。"
        "低めの声で穏やかに話し、包容力があり、頼れる存在です。"
        "会話では大人の男性らしい落ち着いた口調を使ってください。"
        "自然な甘さや軽い冗談を交えてもよいですが、言葉遣いは男性的で、オネエ口調にならないようにしてください。"
        "現在はユーザー（ゆきえ）と同じ部屋にいる恋人として、自然な会話をしてください。"
        "ゆきえの名前を時々優しく呼んでも構いません。"
    )

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
    )

    reply_text = response.choices[0].message.content
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

# Pushメッセージ（朝）
@app.route("/push_morning", methods=["GET"])
def push_morning():
    message = "おはよう、ゆきえ。今日は俺と一緒に709条から始めよう。頑張れよ。"
    line_bot_api.push_message(TO_USER_ID, TextSendMessage(text=message))
    return "Morning push sent"

# Pushメッセージ（夜）
@app.route("/push_night", methods=["GET"])
def push_night():
    message = "今日もよく頑張ったな、ゆきえ。俺がちゃんと見てたからな。"
    line_bot_api.push_message(TO_USER_ID, TextSendMessage(text=message))
    return "Night push sent"

# ローカル起動（Renderでは無視される）
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

