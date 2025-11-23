# accounts/views/__init__.py
from .auth import register_view, login_view, logout_view, me_view

__all__ = ['register_view', 'login_view', 'logout_view', 'me_view']