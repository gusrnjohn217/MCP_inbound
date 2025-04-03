import os
import json
from kafka import KafkaConsumer
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

# 환경변수 로드
load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID")

# context 저장 경로
CONTEXT_PATH = Path("context/recent_inbound.json")

# 메시지를 최대 몇 건 저장할지
MAX_MESSAGES = 10
message_queue = []

# Kafka Consumer 생성
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    group_id=KAFKA_GROUP_ID,
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset='latest',
    enable_auto_commit=True
)

print(f"MCP Kafka Consumer 시작! (Topic: {KAFKA_TOPIC})")

def save_context():
    context = {
        "updatedAt": datetime.utcnow().isoformat() + "Z",
        "inboundItems": message_queue
    }
    CONTEXT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONTEXT_PATH, "w", encoding="utf-8") as f:
        json.dump(context, f, indent=2, ensure_ascii=False)
    print(f"Context 파일 저장됨: {CONTEXT_PATH}")

# Kafka 메시지 수신 루프
for message in consumer:
    data = message.value
    print(f"Kafka 메시지 수신: {data}")

    # 최신 메시지만 유지
    message_queue.insert(0, data)
    message_queue = message_queue[:MAX_MESSAGES]

    save_context()
