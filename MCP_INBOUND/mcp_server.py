import os
import json
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx

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

    # GPT 호출을 위한 메시지 구성
    messages = [
        {"role": "system", "content": "다음은 입고된 재고 정보입니다. 질문에 이 정보를 활용해 답변해주세요."},
        {"role": "system", "content": json.dumps(context_data["inboundItems"], ensure_ascii=False, indent=2)},
        {"role": "user", "content": request.question}
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
