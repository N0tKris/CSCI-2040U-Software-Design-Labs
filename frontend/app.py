from __future__ import annotations

import os
import socket
from typing import Any

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8080")


def pick_port(start_port: int, max_tries: int = 20) -> int:
    """Pick the first available localhost port starting at start_port."""
    for offset in range(max_tries):
        candidate = start_port + offset
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if sock.connect_ex(("127.0.0.1", candidate)) != 0:
                return candidate
    raise RuntimeError(f"No open port found in range {start_port}-{start_port + max_tries - 1}")


def restaurants_url() -> str:
    return f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants"


def _error_payload(message: str, details: str = "") -> dict[str, Any]:
    return {
        "ok": False,
        "message": message,
        "details": details,
    }


def auth_url(path: str = "") -> str:
    return f"{BACKEND_BASE_URL.rstrip('/')}/api/auth{path}"


@app.get("/")
def index() -> str:
    return render_template("index.html", backend_url=BACKEND_BASE_URL)


@app.get("/health")
def health() -> tuple[dict[str, Any], int]:
    return {"ok": True, "service": "frontend", "backend": BACKEND_BASE_URL}, 200


@app.get("/api/restaurants")
def get_restaurants() -> tuple[dict[str, Any], int]:
    try:
        response = requests.get(restaurants_url(), timeout=5)
        response.raise_for_status()
        return {"ok": True, "data": response.json()}, 200
    except requests.RequestException as exc:
        return _error_payload("Couldn't reach backend to load restaurants", str(exc)), 502


@app.post("/api/restaurants")
def create_restaurant() -> tuple[dict[str, Any], int]:
    payload = request.get_json(silent=True) or {}
    try:
        # Forward Authorization header from the browser (if present)
        headers = {}
        token = request.headers.get('Authorization')
        if token:
            headers['Authorization'] = token
        response = requests.post(restaurants_url(), json=payload, headers=headers, timeout=5)
        body = response.json() if response.content else {}
        return {"ok": response.ok, "data": body}, response.status_code
    except requests.RequestException as exc:
        return _error_payload("Couldn't reach backend to create restaurant", str(exc)), 502


@app.post("/api/auth/login")
def proxy_login() -> tuple[dict[str, Any], int]:
    payload = request.get_json(silent=True) or {}
    try:
        response = requests.post(auth_url('/login'), json=payload, timeout=5)
        # Pass backend JSON (or raw text) through with status code
        try:
            body = response.json()
        except ValueError:
            body = {"error": response.text}
        return body, response.status_code
    except requests.RequestException as exc:
        return _error_payload("Couldn't reach backend for login", str(exc)), 502


@app.post("/api/auth/logout")
def proxy_logout() -> tuple[dict[str, Any], int]:
    token = request.headers.get('Authorization')
    headers = {"Authorization": token} if token else {}
    try:
        response = requests.post(auth_url('/logout'), headers=headers, timeout=5)
        try:
            body = response.json() if response.content else {}
        except ValueError:
            body = {"message": response.text}
        return body, response.status_code
    except requests.RequestException as exc:
        return _error_payload("Couldn't reach backend for logout", str(exc)), 502


@app.get("/api/auth/me")
def proxy_me() -> tuple[dict[str, Any], int]:
    token = request.headers.get('Authorization')
    headers = {"Authorization": token} if token else {}
    try:
        response = requests.get(auth_url('/me'), headers=headers, timeout=5)
        try:
            body = response.json() if response.content else {}
        except ValueError:
            body = {"error": response.text}
        return body, response.status_code
    except requests.RequestException as exc:
        return _error_payload("Couldn't reach backend for auth/me", str(exc)), 502


if __name__ == "__main__":
    requested_port = int(os.getenv("PORT", "5000"))
    port = pick_port(requested_port)
    # Keep a single-process dev server by default (no auto-reloader).
    debug_mode = os.getenv("FLASK_DEBUG", "0") == "1"
    if port != requested_port:
        print(
            f"Port {requested_port} is busy. Starting frontend on http://127.0.0.1:{port} instead."
        )
    app.run(host="127.0.0.1", port=port, debug=debug_mode)
