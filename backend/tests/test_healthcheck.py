import pytest
from fastapi.testclient import TestClient
from app.main import app
import anyio

client = TestClient(app)

def test_healthcheck():
    response = client.get("/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_websocket_chat():
    from app.utils.auth import create_access_token
    token = create_access_token({
        "username": "testuser",
        "role": "admin",
        "email": "testuser@example.com",
        "is_active": True,
        "is_oauth": False
    })
    with client.websocket_connect(f"/ws/chat?token={token}") as websocket:
        # Nhận lịch sử (ban đầu rỗng)
        history = websocket.receive_json()
        assert history["type"] == "history"
        # Gửi tin nhắn
        websocket.send_text("hello")
        msg = websocket.receive_json()
        assert msg["type"] == "chat"
        assert msg["content"] == "hello"

def test_websocket_chat_permission_denied():
    # Không có token
    import pytest
    with pytest.raises(RuntimeError):
        with client.websocket_connect("/ws/chat") as ws:
            pass
    # Token role không hợp lệ
    from app.utils.auth import create_access_token
    bad_token = create_access_token({"username": "baduser", "role": "guest"})
    with pytest.raises(RuntimeError):
        with client.websocket_connect(f"/ws/chat?token={bad_token}") as ws:
            pass
