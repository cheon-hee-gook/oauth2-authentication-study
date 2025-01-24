from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# 환경 변수 읽기
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
PROVIDER = os.getenv("PROVIDER")

# 환경 변수가 로드되지 않았을 경우 오류 출력
if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, PROVIDER]):
    raise ValueError("환경 변수를 로드하지 못했습니다. .env 파일을 확인하세요.")
