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
