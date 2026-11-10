import reflex as rx
from typing import Dict, Any
from .base import AppState

class AuthState(AppState):
    """Authentication and Role-Based Access Control (RBAC) state."""
    current_user: Dict[str, Any] = {
        "operator_id": "fa4e5b22-8356-42d4-bb9e-4e4bf7e9b0e1",
        "username": "palani_mgr",
        "full_name": "Palani",
        "role": "MANAGER",   # 'COLLECTOR', 'SORTER', 'MANAGER', 'CEO'
        "access_level": 2,   # 0..3
    }

    @rx.var
    def user_role(self) -> str:
        return self.current_user.get("role", "GUEST")

    @rx.var
    def access_level(self) -> int:
        return self.current_user.get("access_level", 0)

    @rx.var
    def is_management(self) -> bool:
        return self.access_level >= 2

    def switch_role(self, role: str, level: int, name: str):
        """Dynamically switch user roles for UI testing purposes."""
        self.current_user["role"] = role
        self.current_user["access_level"] = level
        self.current_user["full_name"] = name
