import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import pytest

from app.main import DIO_COUNT, decode_dio_values, listen_for_data, set_digital_io


@pytest.mark.asyncio
async def test_listen_for_data():
    class MockMQTTClass:
        async def ListenForMessage(self):
            return b"test message"

    mock_data = MockMQTTClass()
    result = await listen_for_data(mock_data)
    assert result == "test message", f"Expected 'test message', but got '{result}'"


class DummyController:
    def __init__(self):
        self.calls = []

    def set_do_pin(self, bank, pin, value):
        self.calls.append((bank, pin, value))
        return True


def test_decode_dio_values_returns_integer_list():
    assert decode_dio_values("1,0,1,1") == [1, 0, 1, 1]


def test_decode_dio_values_raises_for_invalid_integer():
    with pytest.raises(ValueError):
        decode_dio_values("1,invalid,0")


def test_set_digital_io_raises_when_length_mismatch(monkeypatch):
    monkeypatch.setattr("app.main.DIO_COUNT", 4)
    controller = DummyController()

    with pytest.raises(ValueError, match="Expected 4 digital IO values"):
        set_digital_io([1, 0, 1], controller)


def test_set_digital_io_calls_controller_for_each_pin(monkeypatch):
    monkeypatch.setattr("app.main.DIO_COUNT", 3)
    controller = DummyController()

    set_digital_io([1, 0, 1], controller)

    assert controller.calls == [
        (1, 0, 1),
        (1, 1, 0),
        (1, 2, 1),
    ]


def test_set_digital_io_preserves_input_values(monkeypatch):
    monkeypatch.setattr("app.main.DIO_COUNT", 3)
    controller = DummyController()
    values = [0, 1, 1]

    set_digital_io(values, controller)

    assert [value for _, _, value in controller.calls] == values

