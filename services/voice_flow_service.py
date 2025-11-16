from uuid import uuid4
from typing import Dict, Any

class VoiceFlowManager:
    """Manages a multi-step voice conversation flow."""
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def start_session(self) -> Dict[str, Any]:
        session_id = str(uuid4())
        self.sessions[session_id] = {"step": "intro", "data": {}}
        return {"session_id": session_id, "next": self._response("ask_country", "ask_country.mp3")}

    def next_step(self, session_id: str, user_input: str):
        session = self.sessions.get(session_id)
        if not session:
            return {"error": "Session not found", "play": "error.mp3"}

        step = session["step"]
        data = session["data"]

        # step: ask_country
        if step == "intro":
            data["country"] = user_input
            session["step"] = "ask_risk"
            return {"play": "ask_risk.mp3", "message": "Which risk: economic, political, climate or sanitary?"}

        # step: ask_risk
        elif step == "ask_risk":
            data["risk"] = user_input
            session["step"] = "ask_year"
            return {"play": "ask_year.mp3", "message": "For which year?"}

        # step: ask_year
        elif step == "ask_year":
            data["year"] = user_input
            session["step"] = "done"
            return {
                "play": None,
                "message": "Got it!",
                "data": data
            }

        return {"play": "error_repeat.mp3", "message": "I didn't understand."}

    def _response(self, step: str, audio_file: str):
        return {"play": audio_file, "step": step}
