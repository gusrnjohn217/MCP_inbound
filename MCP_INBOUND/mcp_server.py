# FastAPI 앱 실행 파일 (Main 서버 역할)
import os
import json
import threading
import subprocess
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx

# ✅ Kafka consumer.py 자동 실행
def run_kafka_consumer():
    print("Kafka Consumer 백그라운드 실행 시작...")
    subprocess.Popen(["python", "kafka_consumer.py"])

threading.Thread(target=run_kafka_consumer, daemon=True).start()

# 환경 변수 로딩
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GPT_MODEL = os.getenv("GPT_MODEL", "openai/gpt-3.5-turbo")

CONTEXT_PATH = "context/recent_inbound.json"

app = FastAPI()

# 요청 바디 정의
class AskRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(request: AskRequest):
    # context 로드
    try:
        with open(CONTEXT_PATH, "r", encoding="utf-8") as f:
            context_data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context 파일 로드 실패: {e}")

    # GPT 호출을 위한 메시지 구성 (role: system 1개 + user 1개)
    messages = [
        {
            "role": "system",
            "content": "다음은 최근 입고된 재고 데이터입니다. 사용자의 질문에 이 정보를 바탕으로 응답해주세요."
        },
        {
            "role": "user",
            "content": f"""
다음은 입고된 재고 목록입니다:

{json.dumps(context_data["inboundItems"], ensure_ascii=False, indent=2)}

질문: {request.question}
"""
        }
    ]

    # OpenRouter API 호출
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": GPT_MODEL,
                    "messages": messages
                }
            )
            response.raise_for_status()
            result = response.json()
            return {"answer": result["choices"][0]["message"]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GPT 호출 실패: {e}")

