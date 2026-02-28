# ultimate_emotion_personal_ai.py

import random
import json
import os
from datetime import datetime

MEMORY_FILE = "ultimate_emotion_chat_memory.json"

# -------------------------------
# メモリ構造
# memory = {
#   "words": {"単語": [{"text":返答, "emotion":"happy","emoji":"😊","count":1,"category":"hobby","last_used":"2026-02-28"}]},
#   "user_profile": {"likes":[],"dislikes":[],"topics":[],"personality":{},"mood":"neutral"},
#   "history":[{"time":"2026-02-28 22:00","user":"input","ai":"response"}]
# }
# -------------------------------

memory = {"words": {}, "user_profile": {"likes": [], "dislikes": [], "topics": [], "personality": {}, "mood": "neutral"}, "history": []}
context_memory = []

if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        memory = json.load(f)

# -------------------------------
# 感情キーワードとモード
# -------------------------------
emotion_keywords = {
    "嬉しい": "happy", "楽しい": "happy", "面白い": "happy", "良い": "happy",
    "悲しい": "sad", "辛い": "sad", "怒った": "angry", "寂しい": "sad", "しんどい": "sad",
    "イライラ": "angry", "疲れた": "sad", "元気": "happy", "リラックス": "neutral"
}

mood_keywords = {
    "元気": "happy", "楽しい": "happy", "面白い": "happy", "疲れた": "sad", "悲しい": "sad",
    "落ち込んでいる": "sad", "イライラ": "angry", "ゆっくり": "neutral", "リラックス": "neutral",
    "穏やか": "neutral"
}

# -------------------------------
# デフォルト返答
# -------------------------------
default_responses = [
    {"text": "なるほど…もっと教えてください。", "emotion": "neutral", "emoji": "🤔", "category": "general"},
    {"text": "それは面白いですね！", "emotion": "happy", "emoji": "😄", "category": "general"},
    {"text": "そうなんですね。", "emotion": "neutral", "emoji": "🙂", "category": "general"},
    {"text": "悲しい気持ちですか…？", "emotion": "sad", "emoji": "😢", "category": "general"},
    {"text": "うれしいですね！", "emotion": "happy", "emoji": "😊", "category": "happy"},
    {"text": "怒ってしまいましたか？", "emotion": "angry", "emoji": "😠", "category": "angry"},
    {"text": "寂しい気分ですか…", "emotion": "sad", "emoji": "😔", "category": "sad"},
    {"text": "冗談も交えて、少しリラックスしていきましょう😂", "emotion": "happy", "emoji": "😂", "category": "fun"},
    {"text": "今日はゆっくり休んで、元気を出していきましょうね！", "emotion": "neutral", "emoji": "🌱", "category": "comfort"}
]

# -------------------------------
# 応答生成
# -------------------------------
def get_response(user_input):
    # ユーザーの気分に応じて返答
    for mood in mood_keywords:
        if mood in user_input:
            mood_type = mood_keywords[mood]
            return random.choice([r for r in default_responses if r["emotion"] == mood_type])

    # 文脈優先（直近20件）
    for past_input, past_response in context_memory[-20:]:
        if past_input in user_input or user_input in past_input:
            return past_response

    # 感情キーワード優先
    for key in emotion_keywords:
        if key in user_input:
            emo = emotion_keywords[key]
            for word in memory["words"]:
                if word in user_input:
                    return random.choice(memory["words"][word])
            emo_candidates = [r for r in default_responses if r["emotion"] == emo]
            if emo_candidates:
                return random.choice(emo_candidates)

    # 学習済み返答
    for word in memory["words"]:
        if word in user_input:
            return random.choice(memory["words"][word])

    # デフォルト返答（ランダム）
    return random.choice(default_responses)

# -------------------------------
# 学習
# -------------------------------
def learn_response(user_input, ai_response):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    words = user_input.split()
    for word in words:
        if word in memory["words"]:
            if not any(r["text"] == ai_response["text"] for r in memory["words"][word]):
                memory["words"][word].append({**ai_response, "count": 1, "last_used": now})
            else:
                for r in memory["words"][word]:
                    if r["text"] == ai_response["text"]:
                        r["count"] += 1
                        r["last_used"] = now
        else:
            memory["words"][word] = [{**ai_response, "count": 1, "last_used": now}]
        
        # ユーザー好み学習
        if ai_response["emotion"] == "happy" and word not in memory["user_profile"]["likes"]:
            memory["user_profile"]["likes"].append(word)
        if ai_response["emotion"] == "sad" and word not in memory["user_profile"]["dislikes"]:
            memory["user_profile"]["dislikes"].append(word)
        if word not in memory["user_profile"]["topics"]:
            memory["user_profile"]["topics"].append(word)

    # 文脈保持
    context_memory.append((user_input, ai_response))
    if len(context_memory) > 50:
        context_memory.pop(0)

    # 履歴記録
    memory["history"].append({"time": now, "user": user_input, "ai": ai_response["text"]})
    if len(memory["history"]) > 200:
        memory["history"].pop(0)

# -------------------------------
# チャット開始
# -------------------------------
def chat():
    print("AI: こんにちは！私はあなたの感情に合わせて会話します。😊")
    while True:
        user_input = input("あなた: ")
        if user_input.lower() in ["さようなら", "終了", "バイバイ"]:
            print("AI: さようなら！また話しましょう。😊")
            break
        response = get_response(user_input)
        print(f"AI: {response['text']} {response['emoji']}")
        learn_response(user_input, response)
        # メモリ保存
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    chat()
