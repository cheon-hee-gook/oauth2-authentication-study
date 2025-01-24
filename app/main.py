from fastapi import FastAPI, Depends, HTTPException, status, Form, Request, Body
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta, datetime
from starlette.middleware.sessions import SessionMiddleware

from app.auth import create_access_token, verify_password, decode_access_token, create_refresh_token, \
    verify_refresh_token, role_required, add_token_to_blacklist, is_token_blacklisted
from app.database import fake_users_db
from app.schemas import Token
from app.routes import router as auth_router

# OAuth2 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

app = FastAPI()

# OAuth2 라우터 추가
app.include_router(auth_router)

# 세션 미들웨어 추가
app.add_middleware(SessionMiddleware, secret_key="super_secret_key")

# 사용자 인증 함수
def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["password"]):
        return None
    return user


# Form 데이터를 처리하는 의존성
def get_form_data(
        username: str = Form(None),
        password: str = Form(None)
):
    return {"username": username, "password": password}


# JSON 및 Form 데이터를 모두 처리하는 의존성
async def get_credentials(
        request: Request,
        form_data: dict = Depends(get_form_data)
):
    if form_data["username"] and form_data["password"]:
        # Form 데이터가 존재할 경우 반환
        return form_data
    else:
        # JSON 데이터로 처리
        json_data = await request.json()
        return {"username": json_data.get("username"), "password": json_data.get("password")}


# 토큰 발급 엔드포인트
@app.post("/token", response_model=Token)
async def login_for_access_token(
        credentials: dict = Depends(get_credentials)
):
    username = credentials.get("username")
    password = credentials.get("password")

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing username or password",
        )

    user = authenticate_user(username, password)
    role = user.get("role")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": user["username"], "role": role}, expires_delta=timedelta(minutes=30))
    refresh_token = create_refresh_token({"sub": user["username"], "role": role })
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


@app.post("/refresh-token")
async def refresh_access_token(refresh_data: dict = Body(...)):
    """
    Refresh Token을 사용해 새로운 Access Token을 생성
    """
    refresh_token = refresh_data.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Missing refresh_token in request body",
        )
    try:
        # Refresh Token 검증
        payload = verify_refresh_token(refresh_token)
        user_id = payload.get("sub")
        user_role = payload.get("role")

        if not user_id or not user_role:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token payload"
            )

        # 새로운 Access Token 생성
        access_token = create_access_token({"sub": user_id, "role":user_role}, expires_delta=timedelta(minutes=30))
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


# 보호된 리소스 엔드포인트
@app.get("/protected")
async def protected_route(token: str = Depends(oauth2_scheme)):
    try:
        if is_token_blacklisted(token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is blacklisted")
        payload = decode_access_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"message": f"Hello, {username}!"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@app.get("/admin")
async def admin_route(payload: dict = Depends(role_required("admin"))):
    username = payload.get("sub")   # 인증된 사용자 정보
    role = payload.get("role")
    return {"message": f"Welcome, {role}: {username}!"}


@app.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token)
        expires_in = int(payload["exp"] - datetime.utcnow().timestamp())
        add_token_to_blacklist(token, expires_in)
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
