import json
import os
import re
import urllib.request
from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
from pyngrok import ngrok
import threading

# === FastAPIサーバーを立てる ===
app = FastAPI()

class InferenceRequest(BaseModel):
    prompt: str
    max_new_tokens: int
    do_sample: bool
    temperature: float
    top_p: float

@app.get("/generate")
async def get_generate_info():
    return {
        "message": "このエンドポイントは POST 用です。JSONで送信してください。",
        "example": {
            "prompt": "こんにちは",
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }
    }

@app.post("/generate")
async def generate(req: InferenceRequest):
    return {"generated_text": f"Echo: {req.prompt}"}

# === ngrokトンネルを張る ===
public_url = ngrok.connect(8501).public_url
print(f"🔗 API公開中： {public_url}/generate")
print("✅ このまま Colab セルやシェルを終了せずに維持してください（CTRL+Cで停止）")

# Lambda風に模倣するための関数
LLM_API_URL = public_url + "/generate"

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        body = json.loads(event["body"])
        message = body["message"]
        conversation_history = body.get("conversationHistory", [])

        print("Processing message:", message)
        print("Using model:", "External")

        messages = conversation_history.copy()
        messages.append({"role": "user", "content": message})

        payload = {
            "prompt": message,
            "max_new_tokens": 512,
            "do_sample": True,
            "temperature": 0.7,
            "top_p": 0.9
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            LLM_API_URL,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req) as res:
            res_body = res.read().decode("utf-8")
        res_json = json.loads(res_body)
        assistant_response = res_json["generated_text"]

        messages.append({"role": "assistant", "content": assistant_response})

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": True,
                "response": assistant_response,
                "conversationHistory": messages
            })
        }

    except Exception as error:
        print("Error:", str(error))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            "body": json.dumps({
                "success": False,
                "error": str(error)
            })
        }

def start_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8501)

if __name__ == "__main__":
    # FastAPIサーバーをバックグラウンドで起動
    threading.Thread(target=start_fastapi, daemon=True).start()

    # サーバー起動を待つ
    import time
    time.sleep(2)

    # テスト用Lambdaイベント
    sample_event = {
        "body": json.dumps({
            "message": "Hello, world!",
            "conversationHistory": []
        })
    }

    response = lambda_handler(sample_event, None)
    print(json.dumps(response, indent=2, ensure_ascii=False))

    # 🔥 ここで無限ループしてサーバーとngrokを生かし続ける
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 プログラムを手動停止しました")
