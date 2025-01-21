# oauth2-authentication-study

## 주요 기능
1. **JWT 토큰 발급**: `/token` 엔드포인트를 통해 사용자 인증 및 토큰 발급.
2. **보호된 리소스**: `/protected` 엔드포인트는 인증된 사용자만 접근 가능.

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

4. Swagger UI:
   - http://127.0.0.1:8000/docs에서 API 테스트.


## 데이터 형식 차이로 인한 문제 및 해결 과정
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