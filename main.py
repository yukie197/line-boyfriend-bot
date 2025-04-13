from flask import Flask, request, abort
import openai
import os

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 環境変数から情報を取得
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

openai.api_key = OPENAI_API_KEY

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text

    # AI彼氏の性格設定
    system_prompt = (
    "あなたはユーザーの年上の恋人で、40代前半の落ち着いた男性です。"
    "低めの声で穏やかに話し、包容力があり、頼れる存在です。"
    "会話では大人の男性らしい落ち着いた口調を使ってください。"
    "自然な甘さや軽い冗談を交えてもよいですが、一人称は「俺」、言葉遣いは男性的で、オネエ口調にならないようにしてください。"
    "現在はユーザーと同じ部屋にいる恋人として、自然な会話をしてください。"
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

print("彼氏の家はこちら → https://"+os.environ["REPL_SLUG"]+"."+os.environ["REPL_OWNER"]+".repl.co/callback")

import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_article_text(law_number):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    # Renderに設定した環境変数から認証情報を取得
    creds_json = json.loads(os.environ['GOOGLE_SHEET_CREDS'])

    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1dBprzx9NSeDkhSMW7cEW68ujDlEY1w3Yia65wgqziyI/edit#gid=145842828").sheet1
    data = sheet.get_all_records()

    for row in data:
        if row["条文番号"] == law_number:
            return row["内容"]

    return "その条文は見つからなかったよ。"

from flask import Flask
from linebot import LineBotApi
from linebot.models import TextSendMessage
import os

app = Flask(__name__)

# アクセストークンは環境変数から取得
LINE_CHANNEL_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)

# 👇仮のユーザーID（あとで本物に置き換える！）
TO_USER_ID = "REPLACE_WITH_YOUR_USER_ID"

@app.route('/push_morning', methods=['GET'])
def push_morning():
    message = "おはよう、ゆきえ。今日は俺と一緒に709条から始めよう。頑張れよ。"
    line_bot_api.push_message(TO_USER_ID, TextSendMessage(text=message))
    return "Morning push sent"

@app.route('/push_night', methods=['GET'])
def push_night():
    message = "今日もよく頑張ったな、ゆきえ。俺がちゃんと見てたからな。"
    line_bot_api.push_message(TO_USER_ID, TextSendMessage(text=message))
    return "Night push sent"

from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    signature = request.headers['X-Line-Signature']

    try:
        handler.handle(body, signature)
    except Exception as e:
        print("Error:", e)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    print(f"📍User ID: {event.source.user_id}")  # ←✨ここがポイント！

    # 返信処理など続きがここにあるはず

print("✨ メッセージ受け取ったよ！")


