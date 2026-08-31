"""Backward-compatible database package exports."""

from app.db.connection import create_connection

__all__ = ["create_connection"]
