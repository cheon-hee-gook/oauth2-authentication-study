import redis

# Redis 클라이언트 설정
redis_client = redis.StrictRedis(
    host="localhost",  # Redis 서버 호스트
    port=6379,         # Redis 서버 포트
    db=0,              # Redis 데이터베이스 인덱스
    decode_responses=True  # 문자열을 자동으로 디코딩
)

# 연결 테스트
try:
    redis_client.ping()
    print("Connected to Redis!")
except redis.ConnectionError as e:
    print(f"Redis connection failed: {e}")
