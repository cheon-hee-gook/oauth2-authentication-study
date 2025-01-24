from fastapi import APIRouter, Request, HTTPException
from authlib.integrations.starlette_client import OAuthError
from app.auth import oauth
from app.settings import REDIRECT_URI


router = APIRouter()


@router.get("/auth/login")
async def login_via_oauth(request: Request):
    """
    Google OAuth2 인증 요청을 보냄
    """
    try:
        redirect_uri = REDIRECT_URI  # 리디렉션 URI 설정
        return await oauth.google.authorize_redirect(request, redirect_uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")



@router.get("/auth/callback")
async def auth(request: Request):
    """
    OAuth2 인증 후 사용자 정보를 처리
    """
    try:
        # 액세스 토큰 가져오기
        token = await oauth.google.authorize_access_token(request)

        # ID 토큰 확인
        if "id_token" not in token:
            raise HTTPException(
                status_code=400,
                detail="ID token is missing in the token response",
            )

        # 사용자 정보 가져오기
        user_info = await oauth.google.get("userinfo", token=token)
        return {"user": user_info.json()}

    except OAuthError as e:
        raise HTTPException(
            status_code=400,
            detail=f"OAuth Error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: {str(e)}",
        )