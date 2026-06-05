import pytest
from app.main import listen_for_data

@pytest.mark.asyncio
async def test_listen_for_data():
    class MockMQTTClass:
        async def ListenForMessage(self):
            return b"test message"
    
    mock_data = MockMQTTClass()
    result = await listen_for_data(mock_data)
    assert result == "test message", f"Expected 'test message', but got '{result}'"

