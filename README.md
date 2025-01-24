# oauth2-authentication-study

## 실행 방법
1. 레포지토리 클론:
   ```bash
   git clone https://github.com/<your-username>/oauth2-jwt-fastapi.git
   cd oauth2-jwt-fastapi
   ```
2. Python 환경 설정:
    ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. 서버 실행:
   ```bash
   uvicorn app.main:app --reload
   ```

4. redis 설치 및 실행:
   ```bash
   docker pull redis
   docker run -d -p 6379:6379 --name redis-server redis
   ```
   
5. Google OAuth2 설정:
   - Google Cloud Console에서 OAuth 클라이언트를 생성하고 승인된 리디렉션 URI를 추가:
     ```bash
     http://127.0.0.1:8000/auth/callback
     ```
   - .env 파일에 클라이언트 ID, 비밀 키, 리디렉션 URI 설정:
     ```bash
     CLIENT_ID=your_google_client_id
     CLIENT_SECRET=your_google_client_secret
     REDIRECT_URI=http://127.0.0.1:8000/auth/callback
     ```

## 주요 기능
1. **JWT 토큰 발급**: 
   - `/token` 엔드포인트를 통해 사용자 인증 및 토큰 발급
   - Access Token은 Redis를 통해 블랙리스트 처리
   - Refresh Token은 Redis에 저장 및 검증
2. **보호된 리소스**: 
   - `/protected` 엔드포인트는 인증된 사용자만 접근 가능
3. **Refresh Token 사용**:
   - `/refresh-token` 엔드포인트를 통해 만료된 Access Token을 갱신 
   - Redis에 저장된 Refresh Token을 통해 유효성 검증
4. **권한 관리**:
   - `/admin` 엔드포인트는 `admin` 역할을 가진 사용자만 접근 가능
   - 역할(Role) 기반의 접근 제어 기능 구현
5. **토큰 블랙리스트 처리**:
   - `/logout` 엔드포인트를 통해 Access Token을 블랙리스트에 등록하여 무효화
6. **Google OAuth2 클라이언트 인증**:
   - `/auth/login` 엔드포인트를 통해 Google 로그인 요청
   - `/auth/callback` 엔드포인트를 통해 Google 인증 응답 처리 및 사용자 정보 반환

## [1~2] 데이터 형식 차이로 인한 문제 및 해결 과정
1. **문제 상황**
   - FastAPI에서 /token 엔드포인트를 구현하여 username과 password를 통해 JWT 토큰을 발급하려고 함
   - Postman과 Swagger UI를 사용하여 /token 엔드포인트를 테스트하는 과정에서 Swagger UI에서 422 Unprocessable Entity 오류가 발생함 
   - 원인은 데이터 형식 차이로, Postman과 Swagger UI가 서버에 데이터를 전송하는 방식이 달랐기 때문
2. **원인 분석**
   1) Postman 요청
      - Postman에서 데이터를 보낼 때 application/json 형식으로 전송
      ```json
      {
          "username": "user1",
          "password": "password1"
      }
      ```
      - 이는 FastAPI에서 pydantic.BaseModel을 사용한 JSON 요청 바디 처리와 호환 됨
   2) Swagger UI 요청 
      - Swagger UI는 OAuth2PasswordBearer를 사용할 때 기본적으로 데이터를 application/x-www-form-urlencoded 형식으로 전송
         ```text
         username=user1&password=password1
         ```
      - 이 형식은 FastAPI에서 Form 데이터를 처리해야만 제대로 수신할 수 있음
3. **해결 방법**
   - Postman과 Swagger UI에서 둘 다 정상적으로 동작하도록 FastAPI 엔드포인트를 수정 
   - FastAPI에서 JSON과 Form 데이터를 모두 처리할 수 있도록 Depends를 활용
   - 클라이언트 요청이 Form 데이터 또는 JSON 데이터 모두 지원되도록 구현

4. 학습한 점
   1) Swagger UI와 Postman 요청 차이 
      - Swagger UI는 기본적으로 application/x-www-form-urlencoded 형식으로 데이터를 전송
      - Postman은 JSON 데이터를 사용하는 경우가 많으므로 이를 함께 지원해야 유연한 API가 됨
   2) FastAPI의 유연한 데이터 처리 
      - FastAPI에서 Depends와 Request 객체를 활용하면 여러 데이터 형식을 쉽게 처리할 수 있음
   3) API 테스트는 다양한 도구로 진행
      - Postman, Swagger UI 등 다양한 도구로 테스트하며 예상하지 못한 문제를 발견할 수 있었음

## [3] Refresh Token을 통한 Access Token 갱신
1. **테스트 방법**
   - URL: `/refresh-token` 
   - 메서드: `POST` 
   - 요청 헤더: `Content-Type: application/json`
   - 요청 본문:
      ```json
      {
        "refresh_token": "<your_refresh_token>"
      }
      ```
   - 응답 본문:
      ```json
      {
        "access_token": "<new_access_token>",
        "token_type": "bearer"
      }
      ```

2. 데이터 흐름
   - 클라이언트는 /token 엔드포인트를 통해 Access Token과 Refresh Token을 발급받음
   - Access Token이 만료되면 /refresh-token 엔드포인트를 호출하여 Refresh Token을 사용해 새로운 Access Token을 발급받음
   - Refresh Token도 만료되었을 경우, 다시 로그인을 통해 새로운 토큰을 발급받아야 함

3. 학습한 점
   1) Refresh Token의 중요성
      - Refresh Token을 통해 Access Token 갱신 기능을 구현하여 사용자 경험을 개선할 수 있음을 배웠음
      - Refresh Token은 더 긴 유효 기간을 가지므로, 사용자 인증 흐름을 간소화할 수 있음
   2) JWT 사용 시 주의점 
      - 만료된 토큰, 잘못된 토큰 등 다양한 시나리오를 고려하여 예외 처리를 구현해야 함
      - Refresh Token은 별도로 관리되어야 하며, 필요 시 데이터베이스에 저장하여 유효성을 검사하는 방식으로 확장 가능함.

## [4] 권한(Role) 관리
1. **테스트 방법**
   - 토큰 발급
   - URL: `/token` 
   - 메서드: `POST`
   - 요청 헤더: `Content-Type: application/json`
   - 요청 본문:
      ```json
      {
          "username": "user1",
          "password": "password1"
      }
      ```
   - 응답 본문:
      ```json
      {
        "access_token": "<access_token>",
        "token_type": "bearer",
        "refresh_token": "<refresh_token>"
      }
      ```

   - 권한 경로 접근
   - URL: `/admin`
   - 메서드: `GET` 
   - 요청 헤더: `Authorization: Bearer <access_token>`
   - 요청 본문(성공):
      ```json
      {
        "message": "Welcome, admin: user1"
      }
      ```
   - 응답 본문(권한 부족:
      ```json
      {
        "detail": "403: Insufficient permissions"
      }
      ```

2. **구현 사항**
   - `/admin` 엔드포인트는 `admin` 역할을 가진 사용자만 접근 가능
   - `role_required` 의존성을 사용해 역할 기반 접근 제어 구현
     - Access Token의 `role` 값을 확인하여 적절한 권한인지 검증
     - 권한 부족 시 HTTP 403 응답 반환

3. **학습한 점**
   1) 역할 기반 접근 제어: 사용자 역할(Role)을 토큰에 포함시켜 API의 권한 관리를 쉽게 구현 가능
   2) JWT 확장성: `role`과 같은 추가 정보를 JWT에 포함하여 다양한 인증/인가 로직을 구현 가능
   3) 의존성을 활용한 권한 관리: FastAPI의 의존성 주입을 통해 코드의 재사용성과 가독성 증가

## [5] 토큰 블랙리스트 처리
1. **구현 사항**
   - `/logout` 엔드포인트를 통해 클라이언트의 Access Token을 블랙리스트에 등록하여 무효화 
   - Redis를 활용해 Access Token을 저장 및 검증
     - Access Token이 블랙리스트에 존재하면 모든 보호된 리소스에 접근 불가 
   - Refresh Token 역시 Redis에 저장 및 관리하여, 로그아웃 시 Refresh Token도 무효화

2. **테스트 방법**
   - 로그아웃 요청 
   - URL: `/logout`
   - 메서드: `POST` 
   - 요청 헤더: `Authorization: Bearer <access_token>`
   - 응답:
     ```json
     {
        "message": "Logged out successfully"
     }
     ```
   
   - 블랙리스트된 토큰으로 접근 
   - URL: `/protected`
   - 메서드: `GET`
   - 요청 헤더: `Authorization: Bearer <blacklisted_access_token>`
   - 응답:
     ```json
     {
        "detail": "Invalid or expired token"
     }
     ```
  
3. **데이터 흐름**
   1) 클라이언트가 /logout 호출 시: 
      - Access Token을 Redis 블랙리스트에 등록 
      - 등록된 토큰은 만료 시간까지 무효 처리
   2) 보호된 리소스 접근 시:
      - Access Token이 Redis 블랙리스트에 있으면 HTTP 401 응답
   
4. 학습한 점
   1) Redis를 활용한 토큰 블랙리스트 관리
      - Redis는 빠른 읽기/쓰기 성능과 만료 기능을 제공하여 토큰 관리에 적합 
      - Redis의 SETEX(만료 시간을 지정해 저장) 명령을 활용하여 자동 만료 처리
   2) 로그아웃 로직의 중요성
      - 클라이언트가 강제로 로그아웃된 경우에도 모든 토큰이 무효화되는 보안 강화
      - Refresh Token 역시 관리함으로써 인증 흐름 전반에 걸친 안전성 확보
   3) JWT 기반 인증의 보안성 증대
      - 블랙리스트와 Refresh Token 관리를 조합하여 JWT의 단점을 보완 가능
      - 실시간으로 토큰 상태를 관리해 사용자의 의도에 맞는 인증 흐름 제공

5. **왜 JWT는 블랙리스트를 사용하지 않을까?**
   - Stateless의 철학 
      - JWT는 자체적으로 필요한 모든 인증 정보를 담고 있으므로, 토큰의 유효성을 검증할 때 서버 상태(세션 데이터 등)에 의존하지 않음 
      - 서버가 상태를 유지하지 않기 때문에 확장성과 성능이 뛰어남
      - 클라이언트는 발급받은 토큰을 서버가 따로 기억하지 않아도, 일정 시간 동안 계속 사용할 수 있음

   - 블랙리스트는 상태를 관리해야 함
     - 블랙리스트를 구현하려면 서버가 어떤 토큰이 유효하지 않은지 기억해야 함
     - 이는 Redis, Memcached, 또는 데이터베이스와 같은 저장소를 통해 구현할 수 있으며, 서버가 상태를 유지하게 만듦
     - 이런 상태 유지 방식은 JWT의 Stateless 철학과 상반 됨
   
   - 토큰의 유효 기간 
     - JWT는 발급 시 유효 기간을 포함
     - 유효 기간이 짧은 경우, 토큰이 만료되면 블랙리스트 없이도 토큰을 재사용할 수 없음
     - 따라서 유효 기간 설정이 잘 이루어진다면 블랙리스트의 필요성이 줄어듦

## [6] Google OAuth2 클라이언트 인증

1. **구현 사항**
   - Google OAuth2 인증 흐름 
   - 로그인 요청:
     - 클라이언트가 /auth/login에 요청을 보냄
     - Google 로그인 페이지로 리디렉션
   - 인증 완료 후 리디렉션:
     - Google 인증 후, 클라이언트는 승인된 리디렉션 URI(/auth/callback)로 돌아옴
     - 서버는 access_token과 id_token을 처리
   - 유저 정보 반환:
     - Google의 userinfo API를 호출하여 사용자 정보를 반환

2. **테스트 방법**
   - Google 로그인 요청
   - URL: `/auth/login`
   - Method: `GET` 
   - 응답:
     - 브라우저가 Google 로그인 페이지로 리디렉션
     - 성공적으로 로그인 시, 승인된 리디렉션 URI(/auth/callback)로 돌아옴

   - Google 인증 응답 처리
   - URL: `/auth/callback`
   - Method: `GET`
   - 성공 시 반환되는 사용자 정보:
     ```
     {
         "id": "1234567890",
         "email": "user@example.com",
         "name": "User Name",
         "picture": "https://example.com/user_picture.png"
     }
     ```

3. **삽질 및 문제 해결 과정**
   - 문제: redirect_uri_mismatch 오류 
   - 원인: Google Cloud Console의 승인된 리디렉션 URI와 FastAPI 설정의 REDIRECT_URI가 불일치
   - 해결:
     - Google Cloud Console에 정확한 URI(http://127.0.0.1:8000/auth/callback) 추가
     - .env 파일에서 동일한 값을 사용

   - 문제: SessionMiddleware must be installed 
   - 원인: authlib를 사용한 OAuth2 구현에서는 세션 데이터를 저장하고 관리하기 위해 SessionMiddleware가 필요
   - 해결:
     - FastAPI 애플리케이션에 SessionMiddleware 추가:
       ```python
       app.add_middleware(SessionMiddleware, secret_key="secret_key")
       ```
   
   - 문제: KeyError: 'id_token' 
   - 원인: Google OAuth2 인증 응답에 id_token 누락
   - 해결:
     - Google OAuth 클라이언트 설정에서 scope에 openid 포함
     - 응답 token에 id_token이 있는데도 에러가 발생하여 아래 방법으로 해결
     - 인증 응답에서 id_token 확인 및 사용자 정보 가져오기 처리 추가:
       ```python
       if "id_token" not in token:
             raise ValueError("ID token is missing in token response")
       # 사용자 정보 가져오기
        user_info = await oauth.google.get("userinfo", token=token)
        return {"user": user_info.json()}
       ```

   - 문제: Missing "jwks_uri" in metadata 
   - 원인: 라이브러리가 자동으로 가져오지 못하는 경우, 수동으로 jwks_uri를 설정하거나 필요한 키를 가져와야 함
   - 해결:
     - oauth.register에 jwks_uri 추가:
       ```python
       jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
       ```
4. **학습한 점**
   1) OAuth2 클라이언트 인증: Google OAuth2 인증을 FastAPI와 Authlib으로 구현하는 방법을 학습
   2) 세션 관리: SessionMiddleware를 활용하여 사용자 인증 상태를 효과적으로 관리
   3) Google Cloud Console 설정 중요성: OAuth2 인증 흐름에서 redirect_uri 설정이 필수적임을 이해
   4) 디버깅 및 예외 처리: 실시간으로 디버깅하며 발생할 수 있는 다양한 문제를 처리하는 경험

## 학습 후기
스터디를 통해 FastAPI와 OAuth2 인증의 흐름을 전반적으로 이해할 수 있었다.

- OAuth2와 JWT를 활용해 인증 시스템을 직접 구축하면서, 실제로 마주칠 수 있는 다양한 문제를 해결해 보는 경험을 통해 실무에서 필요한 디버깅 능력을 키울 수 있었다.
- Redis를 사용한 블랙리스트 처리와 세션 관리 구현 과정을 통해 보안과 확장성을 고려한 시스템 설계에 대해 배울 수 있었다.
- Google OAuth2 클라이언트를 이용해 OAuth2 인증의 흐름을 직접 경험해 보았다. 특히, redirect_uri 설정, id_token 처리, 인증 후 사용자 정보 추출까지의 과정을 구체적으로 이해할 수 있었다.
- FastAPI의 의존성 주입과 라우팅 시스템을 활용해 구조적으로 코드를 작성하는 방법을 익혔다.
- 학습 중 발생했던 다양한 오류와 문제를 해결하며 더 깊이 배우는 계기가 되었다. 특히 Google Cloud Console 설정, SessionMiddleware 추가, Redis와의 통합 과정은 좋은 경험으로 남았다.

이번 스터디를 통해 인증과 인가를 다루는 백엔드 개발의 핵심을 배우는 데 큰 도움이 되었고, 더 나은 코드 설계와 보안을 고려한 시스템 구현의 중요성을 다시 한 번 깨달을 수 있었다.