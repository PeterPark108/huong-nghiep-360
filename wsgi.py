"""Điểm vào WSGI cho production: gunicorn wsgi:app"""
from app import app  # noqa: F401
