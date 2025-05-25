import pytest
from fastapi.testclient import TestClient
from app.main import app
import anyio

client = TestClient(app)

def get_token(username="testuser", role="admin"):
    from app.utils.auth import create_access_token
    # Đảm bảo token chứa đủ trường cho UserOut
    return create_access_token({
        "username": username,
        "role": role,
        "email": f"{username}@example.com",
        "is_active": True,
        "is_oauth": False
    })

def test_chat_websocket_auth_and_history():
    token = get_token()
    with client.websocket_connect(f"/ws/chat?token={token}") as ws1:
        # Nhận lịch sử ban đầu (rỗng)
        history = ws1.receive_json()
        assert history["type"] == "history"
        assert isinstance(history["messages"], list)
        # Gửi tin nhắn
        ws1.send_text("hello world")
        msg = ws1.receive_json()
        assert msg["type"] == "chat"
        assert msg["content"] == "hello world"
        # Kết nối user khác, nhận được lịch sử
        token2 = get_token("user2", "employee")
        with client.websocket_connect(f"/ws/chat?token={token2}") as ws2:
            history2 = ws2.receive_json()
            assert history2["type"] == "history"
            assert any(m["content"] == "hello world" for m in history2["messages"])
            # User2 gửi tin nhắn
            ws2.send_text("hi admin")
            msg2 = ws2.receive_json()
            assert msg2["type"] == "chat"
            assert msg2["user"] == "user2"
            assert msg2["content"] == "hi admin"
        # Khi user2 rời đi, user1 nhận được thông báo (có thể là chat hoặc system, do broadcast thứ tự)
        left_msg = ws1.receive_json()
        assert left_msg["type"] in ("system", "chat")

def test_chat_websocket_permission_denied():
    import pytest
    import anyio
    from starlette.websockets import WebSocketDisconnect
    # Không có token
    with pytest.raises((RuntimeError, anyio.ClosedResourceError, WebSocketDisconnect)):
        with client.websocket_connect("/ws/chat") as ws:
            pass
    # Token role không hợp lệ
    bad_token = get_token("baduser", "guest")
    with pytest.raises((RuntimeError, anyio.ClosedResourceError, WebSocketDisconnect)):
        with client.websocket_connect(f"/ws/chat?token={bad_token}") as ws:
            pass
