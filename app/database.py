from app.auth import hash_password

# 사용자 데이터베이스
fake_users_db = {
    "user1": {"username": "user1", "password": hash_password("password1"), "role": "admin"},
    "user2": {"username": "user2", "password": hash_password("password2"), "role": "user"},
}
