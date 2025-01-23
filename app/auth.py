from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

from app.redis_client import redis_client  # Redis 클라이언트

# 비밀번호 해싱 설정
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "e8a9b94cb3ed04177330192903b2f043f33bfaca817861738ebc1f2c765057e31090856f695ca9495d4a1b566884f514006041dc8f3f48f2ab4d7239fce97588"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


# 비밀번호 해싱 및 검증 함수
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# JWT 생성 및 디코딩 함수
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    print("to_encode", to_encode)
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")


# Refresh Token 저장소
# refresh_tokens = {}


# Refresh Token 관리 - Redis 사용
def save_refresh_token(user_id: str, token: str, expires_in: int):
    redis_client.setex(f"refresh_token:{user_id}", expires_in, token)


def get_refresh_token(user_id: str) -> str | None:
    return redis_client.get(f"refresh_token:{user_id}")


def delete_refresh_token(user_id: str):
    redis_client.delete(f"refresh_token:{user_id}")


# Refresh Token 생성
def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))  # Refresh Token 유효기간 7일
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # refresh_tokens[data.get("sub")] = token
    save_refresh_token(data.get("sub"), token, int(expire.timestamp() - datetime.utcnow().timestamp()))
    return token


# Refresh Token 검증
def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        stored_token = get_refresh_token(user_id)
        # if not user_id or refresh_tokens.get(user_id) != token:
        if not stored_token or stored_token != token:
            raise Exception("Invalid refresh token")
        return payload  # 페이로드 반환
    except jwt.ExpiredSignatureError:
        raise Exception("Refresh token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid refresh token")


# 블랙리스트 관리 - Redis 사용
def add_token_to_blacklist(token: str, expires_in: int):
    redis_client.setex(f"blacklist:{token}", expires_in, "blacklisted")


def is_token_blacklisted(token: str) -> bool:
    return redis_client.exists(f"blacklist:{token}") > 0


# role 기반 접근 제어 의존성 함수
def role_required(required_role: str):
    def dependency(token: str = Depends(oauth2_scheme)):
        try:
            if is_token_blacklisted(token):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is blacklisted",
                )
            payload = decode_access_token(token)
            user_role = payload.get("role")

            if user_role != required_role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
            )
        return payload  # 인증 및 권함 건증이 통과되면 반환

    return dependency
