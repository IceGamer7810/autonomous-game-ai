"""FastAPI app bound by deployment to localhost."""

from fastapi import FastAPI, HTTPException

from game_agent.session import SessionManager, SessionState
from game_agent.telemetry import Telemetry


def create_app(session: SessionManager, telemetry: Telemetry) -> FastAPI:
    app = FastAPI(title="Autonomous Game Agent", docs_url=None, redoc_url=None)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/status")
    def status():
        snapshot = telemetry.snapshot()
        return {
            "session_state": session.state,
            "selected_window": session.context.window_id if session.context else None,
            "goal": session.context.goal if session.context else None,
            "telemetry": snapshot.__dict__,
        }

    @app.post("/session/pause")
    def pause():
        try:
            session.pause()
        except ValueError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        return {"state": SessionState.PAUSED}

    @app.post("/session/resume")
    def resume():
        try:
            session.resume()
        except ValueError as error:
            raise HTTPException(status_code=409, detail=str(error)) from error
        return {"state": SessionState.RUNNING}

    @app.post("/session/stop")
    def stop():
        session.stop()
        return {"state": SessionState.STOPPED}

    return app
