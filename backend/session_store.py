# session_store.py
from typing import Dict, Any
import threading


class InMemorySessionStore:
def __init__(self):
self._lock = threading.Lock()
self._store: Dict[str, Dict[str, Any]] = {}


def get(self, session_id: str):
with self._lock:
return self._store.get(session_id, {})


def set(self, session_id: str, data: Dict[str, Any]):
with self._lock:
self._store[session_id] = data


def append_message(self, session_id: str, role: str, text: str):
with self._lock:
s = self._store.get(session_id, {"messages":[]})
s.setdefault("messages", []).append({"role": role, "text": text})
self._store[session_id] = s