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

## 주요 기능
1. **JWT 토큰 발급**: 
   - `/token` 엔드포인트를 통해 사용자 인증 및 토큰 발급
2. **보호된 리소스**: 
   - `/protected` 엔드포인트는 인증된 사용자만 접근 가능
3. **Refresh Token 사용**:
   - `/refresh-token` 엔드포인트를 통해 만료된 Access Token을 갱신 
   - Refresh Token을 검증하여 새로운 Access Token을 발급
4. **권한 관리**:
   - `/admin` 엔드포인트는 `admin` 역할을 가진 사용자만 접근 가능
   - 역할(Role) 기반의 접근 제어 기능 구현

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

2. 구현 사항
   - `/admin` 엔드포인트는 `admin` 역할을 가진 사용자만 접근 가능
   - `role_required` 의존성을 사용해 역할 기반 접근 제어 구현
     - Access Token의 `role` 값을 확인하여 적절한 권한인지 검증
     - 권한 부족 시 HTTP 403 응답 반환

3. 학습한 점
   1) 역할 기반 접근 제어: 사용자 역할(Role)을 토큰에 포함시켜 API의 권한 관리를 쉽게 구현 가능
   2) JWT 확장성: `role`과 같은 추가 정보를 JWT에 포함하여 다양한 인증/인가 로직을 구현 가능
   3) 의존성을 활용한 권한 관리: FastAPI의 의존성 주입을 통해 코드의 재사용성과 가독성 증가
