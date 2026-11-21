from fastapi.testclient import TestClient

from game_agent.api import create_app
from game_agent.session import SessionManager
from game_agent.telemetry import Telemetry


def test_local_status_and_stop_controls():
    telemetry = Telemetry()
    telemetry.record_inference(0.2)
    session = SessionManager(lambda: None)
    session.start("window", "goal")
    client = TestClient(create_app(session, telemetry))
    assert client.get("/status").json()["selected_window"] == "window"
    assert client.post("/session/stop").json()["state"] == "stopped"
