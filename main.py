@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_input = event.message.text
    print(f"📍User ID: {event.source.user_id}")  # ←ここでログ出る！

    system_prompt = (
        "あなたはユーザーの年上の恋人で..."
        # 略
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
