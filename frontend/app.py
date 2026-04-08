from __future__ import annotations

import os
import secrets
import socket
from typing import Any

import requests
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    render_template_string,
    request,
    session,
    url_for,
)
from werkzeug.exceptions import RequestEntityTooLarge

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))
app.config['MAX_CONTENT_LENGTH'] = None  # Disable content length limit

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8080")


@app.errorhandler(413)
def handle_413(e):
    """Handle Payload Too Large errors."""
    print(f"DEBUG: 413 error caught - {e}")
    return jsonify({"error": "File too large"}), 413


# ---------------------------------------------------------------------------
# Admin login page template (inline)
# ---------------------------------------------------------------------------
ADMIN_LOGIN_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Admin Login - PlateRate</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #f5f0eb 0%, #e8e0d8 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #333;
        }
        .login-card {
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
            padding: 40px 36px 36px;
            width: 100%;
            max-width: 400px;
        }
        .login-card .brand {
            text-align: center;
            margin-bottom: 8px;
            font-size: 22px;
            font-weight: 700;
            color: #b85c38;
            letter-spacing: 0.5px;
        }
        .login-card .subtitle {
            text-align: center;
            font-size: 13px;
            color: #888;
            margin-bottom: 28px;
            letter-spacing: 0.3px;
        }
        .form-group { margin-bottom: 18px; }
        .form-group label {
            display: block;
            font-size: 13px;
            font-weight: 600;
            color: #555;
            margin-bottom: 6px;
        }
        .form-group input {
            width: 100%;
            padding: 10px 14px;
            border: 1px solid #d5cfc9;
            border-radius: 8px;
            font-size: 15px;
            background: #faf8f6;
            transition: border-color 0.2s;
        }
        .form-group input:focus {
            outline: none;
            border-color: #b85c38;
            background: #fff;
        }
        .btn-login {
            width: 100%;
            padding: 12px;
            background: #b85c38;
            color: #fff;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            margin-top: 4px;
        }
        .btn-login:hover { background: #a04e2e; }
        .error-msg {
            background: #fdecea;
            color: #b71c1c;
            font-size: 13px;
            padding: 10px 14px;
            border-radius: 8px;
            margin-bottom: 16px;
            text-align: center;
        }
        .back-link {
            display: block;
            text-align: center;
            margin-top: 18px;
            font-size: 13px;
            color: #888;
            text-decoration: none;
        }
        .back-link:hover { color: #b85c38; }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="brand">PlateRate</div>
        <div class="subtitle">Admin Control Panel Access</div>
        {% if error %}
        <div class="error-msg">{{ error }}</div>
        {% endif %}
        <form method="POST" action="{{ url_for('admin_login') }}">
            <div class="form-group">
                <label for="username">Admin Username</label>
                <input type="text" id="username" name="username" required
                       autocomplete="username" placeholder="Enter admin username" />
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required
                       autocomplete="current-password" placeholder="Enter password" />
            </div>
            <button type="submit" class="btn-login">Admin Login</button>
        </form>
        <a href="/" class="back-link">&larr; Back to PlateRate</a>
    </div>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# Admin dashboard template (inline)
# ---------------------------------------------------------------------------
ADMIN_DASHBOARD_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Admin Dashboard - PlateRate</title>
    <style>
        :root {
            --brand: #b85c38;
            --brand-dark: #a04e2e;
            --brand-light: #faf6f3;
            --border: #e0d8d0;
            --text: #333;
            --text-muted: #888;
            --bg: #f2ede8;
            --card-bg: #fff;
            --shadow: 0 2px 16px rgba(0,0,0,0.07);
            --radius: 12px;
            --transition: 0.2s ease;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
        }

        /* ── Top bar ── */
        .topbar {
            background: var(--card-bg);
            border-bottom: 1px solid var(--border);
            padding: 0 28px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 1px 6px rgba(0,0,0,0.06);
        }
        .topbar-left { display: flex; align-items: center; gap: 12px; }
        .topbar .brand {
            font-size: 20px;
            font-weight: 700;
            color: var(--brand);
            letter-spacing: 0.3px;
        }
        .topbar .brand-sub {
            font-size: 13px;
            color: var(--text-muted);
            font-weight: 400;
            padding-left: 12px;
            border-left: 1px solid var(--border);
            margin-left: 4px;
        }
        .topbar-right {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .admin-avatar {
            width: 34px;
            height: 34px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--brand) 0%, var(--brand-dark) 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            font-size: 15px;
            font-weight: 700;
            flex-shrink: 0;
        }
        .topbar .user-label {
            font-size: 14px;
            color: var(--text-muted);
        }
        .topbar .user-label strong {
            color: var(--text);
            font-weight: 600;
        }
        .mode-pill {
            display: inline-flex;
            align-items: center;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 11px;
            font-weight: 700;
            color: #2e7d32;
            background: #e8f5e9;
            border: 1px solid #cde7cf;
            letter-spacing: 0.3px;
            text-transform: uppercase;
        }
        .btn-view-user {
            padding: 7px 14px;
            border-radius: 8px;
            border: 1px solid var(--border);
            background: #f7f2ed;
            color: var(--brand);
            font-size: 13px;
            font-weight: 600;
            text-decoration: none;
            transition: all var(--transition);
            white-space: nowrap;
        }
        .btn-view-user:hover {
            border-color: var(--brand);
            background: var(--brand-light);
        }
        .btn-logout {
            padding: 7px 16px;
            background: transparent;
            border: 1px solid var(--border);
            border-radius: 8px;
            font-size: 13px;
            color: #666;
            cursor: pointer;
            text-decoration: none;
            transition: border-color var(--transition), color var(--transition), background var(--transition);
            white-space: nowrap;
        }
        .btn-logout:hover {
            border-color: var(--brand);
            color: var(--brand);
            background: var(--brand-light);
        }

        /* ── Dashboard wrapper ── */
        .dashboard {
            max-width: 1200px;
            margin: 32px auto;
            padding: 0 24px 40px;
        }
        .dashboard-title {
            font-size: 22px;
            font-weight: 700;
            color: var(--text);
            margin-bottom: 6px;
        }
        .dashboard-subtitle {
            font-size: 14px;
            color: var(--text-muted);
            margin-bottom: 28px;
        }

        /* ── Stats row ── */
        .stats-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 32px;
            animation: fadeSlideIn 0.4s ease both;
        }
        .stat-card {
            background: var(--card-bg);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            padding: 20px 22px;
            display: flex;
            align-items: center;
            gap: 16px;
            transition: transform var(--transition), box-shadow var(--transition);
        }
        .stat-card:hover { transform: translateY(-2px); box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
        .stat-icon {
            font-size: 26px;
            width: 48px;
            height: 48px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        .stat-icon.users  { background: #e8f5e9; }
        .stat-icon.rests  { background: #fff3e0; }
        .stat-icon.menu   { background: #e3f2fd; }
        .stat-icon.revs   { background: #fce4ec; }
        .stat-count {
            font-size: 28px;
            font-weight: 700;
            color: var(--text);
            line-height: 1;
        }
        .stat-label {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }

        /* ── Section cards ── */
        .section {
            background: var(--card-bg);
            border-radius: var(--radius);
            box-shadow: var(--shadow);
            margin-bottom: 28px;
            overflow: hidden;
            animation: fadeSlideIn 0.4s ease both;
        }
        .section:nth-child(1) { animation-delay: 0.05s; }
        .section:nth-child(2) { animation-delay: 0.10s; }
        .section:nth-child(3) { animation-delay: 0.15s; }
        .section:nth-child(4) { animation-delay: 0.20s; }

        .section-header {
            padding: 16px 24px;
            background: var(--brand-light);
            border-bottom: 1px solid #ece5de;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            flex-wrap: wrap;
        }
        .section-header-left { display: flex; align-items: center; gap: 10px; }
        .section-title {
            font-size: 15px;
            font-weight: 700;
            color: var(--brand);
        }
        .section-desc {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 1px;
        }
        .section-actions { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
        .btn-secondary {
            padding: 7px 14px;
            border-radius: 8px;
            border: 1px solid var(--border);
            background: var(--card-bg);
            color: var(--brand);
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: background var(--transition), border-color var(--transition);
            white-space: nowrap;
        }
        .btn-secondary:hover { background: var(--brand-light); border-color: var(--brand); }
        .btn-primary {
            padding: 7px 14px;
            border-radius: 8px;
            border: none;
            background: var(--brand);
            color: #fff;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: background var(--transition);
            white-space: nowrap;
        }
        .btn-primary:hover { background: var(--brand-dark); }

        /* ── Tables ── */
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            text-align: left;
            padding: 11px 24px;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: var(--text-muted);
            font-weight: 700;
            border-bottom: 1px solid #ece5de;
            background: #fdfdfc;
        }
        td {
            padding: 13px 24px;
            font-size: 14px;
            border-bottom: 1px solid #f5f0eb;
            color: #444;
            vertical-align: middle;
        }
        tbody tr:nth-child(even) td { background: #fdf9f6; }
        tbody tr:hover td { background: #faf4f0; }
        tbody tr:last-child td { border-bottom: none; }
        .empty-row td {
            text-align: center;
            color: #bbb;
            padding: 36px;
            font-style: italic;
            font-size: 14px;
        }

        /* hidden rows for "show more" */
        tr.extra-row { display: none; }
        tr.extra-row.visible { display: table-row; }

        /* ── Show More footer ── */
        .section-footer {
            padding: 12px 24px;
            border-top: 1px solid #f0ebe5;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .row-count-label {
            font-size: 12px;
            color: var(--text-muted);
        }
        .btn-show-more {
            padding: 6px 14px;
            border-radius: 8px;
            border: 1px solid var(--border);
            background: var(--card-bg);
            color: var(--brand);
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: background var(--transition), border-color var(--transition);
        }
        .btn-show-more:hover { background: var(--brand-light); border-color: var(--brand); }

        /* ── Badges ── */
        .badge {
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 0.3px;
        }
        .badge-admin { background: #fce4ec; color: #c62828; }
        .badge-user  { background: #e8f5e9; color: #2e7d32; }
        .badge-owner { background: #fff3e0; color: #e65100; }

        /* ── Stars ── */
        .stars { color: #f5a623; letter-spacing: 2px; }

        /* ── Icon action buttons ── */
        .action-btns { display: flex; gap: 6px; align-items: center; }
        .icon-btn {
            width: 32px;
            height: 32px;
            border-radius: 8px;
            border: 1px solid var(--border);
            background: var(--card-bg);
            color: #555;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            transition: background var(--transition), border-color var(--transition), color var(--transition);
            position: relative;
        }
        .icon-btn:hover { background: var(--brand-light); border-color: var(--brand); color: var(--brand); }
        .icon-btn.danger:hover { background: #fdecea; border-color: #e57373; color: #c62828; }

        /* ── Tooltip ── */
        .icon-btn[title]:hover::after {
            content: attr(title);
            position: absolute;
            bottom: calc(100% + 6px);
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.75);
            color: #fff;
            font-size: 11px;
            padding: 4px 8px;
            border-radius: 5px;
            white-space: nowrap;
            pointer-events: none;
            z-index: 10;
        }

        /* ── Modal ── */
        .modal-backdrop {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.35);
            align-items: center;
            justify-content: center;
            padding: 20px;
            z-index: 200;
            animation: modalFadeIn 0.2s ease;
        }
        .modal-backdrop.open { display: flex; }
        @keyframes modalFadeIn {
            from { opacity: 0; }
            to   { opacity: 1; }
        }
        .modal-box {
            width: 100%;
            max-width: 560px;
            background: var(--card-bg);
            border-radius: var(--radius);
            box-shadow: 0 8px 40px rgba(0,0,0,0.18);
            padding: 28px;
            max-height: 90vh;
            overflow-y: auto;
            animation: modalSlideIn 0.25s ease;
        }
        @keyframes modalSlideIn {
            from { transform: translateY(-20px); opacity: 0; }
            to   { transform: translateY(0);     opacity: 1; }
        }
        .modal-title {
            font-size: 18px;
            font-weight: 700;
            color: var(--brand);
            margin-bottom: 4px;
        }
        .modal-subtitle {
            font-size: 13px;
            color: var(--text-muted);
            margin-bottom: 20px;
        }
        .modal-section-label {
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            color: var(--text-muted);
            margin-bottom: 12px;
            margin-top: 20px;
            padding-bottom: 6px;
            border-bottom: 1px solid var(--border);
        }
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 14px;
        }
        .form-full { grid-column: 1 / -1; }
        .form-group { display: flex; flex-direction: column; gap: 5px; }
        .form-label {
            font-size: 12px;
            font-weight: 700;
            color: #555;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }
        .form-input, .form-textarea {
            width: 100%;
            padding: 9px 12px;
            border: 1px solid #d0c9c2;
            border-radius: 8px;
            font-size: 14px;
            font-family: inherit;
            background: #faf8f6;
            transition: border-color var(--transition), background var(--transition);
            outline: none;
        }
        .form-input:focus, .form-textarea:focus {
            border-color: var(--brand);
            background: #fff;
        }
        .form-textarea { min-height: 80px; resize: vertical; }
        .modal-image-box {
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
            background: var(--brand-light);
        }
        .modal-image-box .img-label {
            font-size: 12px;
            font-weight: 700;
            color: #555;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            margin-bottom: 10px;
        }
        .drop-zone {
            border: 2px dashed #d5cfc9;
            border-radius: 8px;
            padding: 20px 16px;
            text-align: center;
            cursor: pointer;
            transition: border-color var(--transition), background var(--transition);
            position: relative;
        }
        .drop-zone:hover { border-color: var(--brand); background: #fff8f5; }
        .drop-zone .dz-icon { font-size: 26px; margin-bottom: 6px; }
        .drop-zone .dz-title { font-size: 13px; color: #555; }
        .drop-zone .dz-hint { font-size: 11px; color: #aaa; margin-top: 4px; }
        .modal-actions {
            margin-top: 22px;
            display: flex;
            gap: 10px;
            justify-content: flex-end;
        }
        .admin-detail-modal {
            max-width: 920px;
        }
        .admin-detail-header {
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 16px;
            margin-bottom: 18px;
        }
        .admin-detail-close {
            width: 40px;
            height: 40px;
            border: none;
            border-radius: 50%;
            background: #f4ece6;
            color: #8d4b2f;
            font-size: 24px;
            line-height: 1;
            cursor: pointer;
            flex: 0 0 auto;
        }
        .admin-detail-close:hover { background: #ebddd3; }
        .admin-detail-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 12px;
        }
        .admin-detail-card {
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 14px;
            background: #faf7f4;
        }
        .admin-detail-card.full { grid-column: 1 / -1; }
        .admin-detail-label {
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 0.6px;
            text-transform: uppercase;
            color: var(--text-muted);
            margin-bottom: 6px;
        }
        .admin-detail-value {
            font-size: 14px;
            color: #3f2a1d;
            line-height: 1.55;
            white-space: pre-line;
        }
        .admin-detail-badges {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .admin-detail-badge {
            display: inline-flex;
            align-items: center;
            padding: 6px 10px;
            border-radius: 999px;
            background: #fff;
            border: 1px solid #e1d8d0;
            color: #6b5141;
            font-size: 12px;
            font-weight: 700;
        }
        .admin-detail-gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 10px;
        }
        .admin-detail-gallery-item {
            border: 1px solid #e1d8d0;
            border-radius: 14px;
            overflow: hidden;
            padding: 0;
            background: #fff;
            cursor: pointer;
            text-align: left;
        }
        .admin-detail-gallery-item img {
            display: block;
            width: 100%;
            height: 132px;
            object-fit: cover;
        }
        .admin-detail-empty {
            color: #9a8b80;
            font-size: 13px;
        }
        tr.admin-detail-row {
            cursor: pointer;
        }
        tr.admin-detail-row:hover td {
            background: #fcf5f1;
        }

        /* ── Animations ── */
        @keyframes fadeSlideIn {
            from { opacity: 0; transform: translateY(14px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        /* ── Responsive ── */
        @media (max-width: 900px) {
            .stats-row { grid-template-columns: repeat(2, 1fr); }
            .form-grid  { grid-template-columns: 1fr; }
            .form-full  { grid-column: 1; }
        }
        @media (max-width: 600px) {
            .topbar { padding: 0 16px; }
            .dashboard { padding: 0 12px 40px; }
            .stats-row { grid-template-columns: repeat(2, 1fr); gap: 10px; }
            .topbar .brand-sub { display: none; }
        }
    </style>
</head>
<body>
    <!-- Top bar -->
    <div class="topbar">
        <div class="topbar-left">
            <div class="brand">PlateRate</div>
            <span class="brand-sub">Admin Dashboard</span>
        </div>
        <div class="topbar-right">
            <div class="admin-avatar">{{ (admin_username or 'A')[0]|upper }}</div>
            <span class="user-label">Logged in as <strong>{{ admin_username }}</strong></span>
            {% if admin_user_view_active %}
            <span class="mode-pill">User View Active</span>
            <a href="{{ url_for('admin_exit_user_view') }}" class="btn-view-user">Resume Admin View</a>
            <a href="{{ url_for('admin_view_as_owner') }}" class="btn-view-user">Switch to Owner View</a>
            {% elif admin_owner_view_active %}
            <span class="mode-pill">Owner View Active</span>
            <a href="{{ url_for('admin_exit_owner_view') }}" class="btn-view-user">Resume Admin View</a>
            <a href="{{ url_for('admin_view_as_user') }}" class="btn-view-user">Switch to User View</a>
            {% else %}
            <a href="{{ url_for('admin_view_as_user') }}" class="btn-view-user">View as User</a>
            <a href="{{ url_for('admin_view_as_owner') }}" class="btn-view-user">View as Owner</a>
            {% endif %}
            <a href="{{ url_for('admin_logout') }}" class="btn-logout">Logout</a>
        </div>
    </div>

    <div class="dashboard">
        <div class="dashboard-title">Database Management</div>
        <div class="dashboard-subtitle">Manage all platform data from one place.</div>

        <!-- Summary Stats -->
        <div class="stats-row">
            <div class="stat-card">
                <div class="stat-icon users">👥</div>
                <div>
                    <div class="stat-count">{{ users|length }}</div>
                    <div class="stat-label">Users</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon rests">🍽️</div>
                <div>
                    <div class="stat-count">{{ restaurants|length }}</div>
                    <div class="stat-label">Restaurants</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon menu">📋</div>
                <div>
                    <div class="stat-count">{{ menu_items|length }}</div>
                    <div class="stat-label">Menu Items</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon revs">⭐</div>
                <div>
                    <div class="stat-count">{{ reviews|length }}</div>
                    <div class="stat-label">Reviews</div>
                </div>
            </div>
            <div class="stat-card">
                <div class="stat-icon" style="background:#fff3e0;color:#e65100;">⏳</div>
                <div>
                    <div class="stat-count" id="pending-reviews-count">{{ pending_reviews|length }}</div>
                    <div class="stat-label">Pending</div>
                </div>
            </div>
        </div>

        <!-- Users Table -->
        <div class="section" id="section-users">
            <div class="section-header">
                <div class="section-header-left">
                    <div>
                        <div class="section-title">👥 Users</div>
                        <div class="section-desc">All registered platform accounts</div>
                    </div>
                </div>
            </div>
            <table>
                <thead>
                    <tr><th>ID</th><th>Username</th><th>Role</th></tr>
                </thead>
                <tbody id="users-tbody">
                {% if users %}
                    {% for u in users %}
                    <tr class="admin-detail-row {% if loop.index > 5 %}extra-row{% endif %}" data-section="users" data-detail='{{ {"type": "user", "id": (u.id or ''), "username": u.username, "role": u.role}|tojson }}'>
                        <td>{{ u.id }}</td>
                        <td>{{ u.username }}</td>
                        <td>
                            {% set role_class = {'ADMIN': 'badge-admin', 'OWNER': 'badge-owner'}.get(u.role, 'badge-user') %}
                            <span class="badge {{ role_class }}">{{ u.role }}</span>
                        </td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr class="empty-row"><td colspan="3">No users found</td></tr>
                {% endif %}
                </tbody>
            </table>
            {% if users|length > 5 %}
            <div class="section-footer">
                <span class="row-count-label">Showing 5 of {{ users|length }}</span>
                <button type="button" class="btn-show-more" data-section="users" data-total="{{ users|length }}">Show all {{ users|length }} →</button>
            </div>
            {% endif %}
        </div>

        <!-- Restaurants Table -->
        <div class="section" id="section-restaurants">
            <div class="section-header">
                <div class="section-header-left">
                    <div>
                        <div class="section-title">🍽️ Restaurants</div>
                        <div class="section-desc">Manage all listed restaurants</div>
                    </div>
                </div>
                <div class="section-actions">
                    <button type="button" id="open-yelp-modal" class="btn-secondary">🔍 Import from Yelp</button>
                    <button type="button" id="open-add-modal" class="btn-primary">+ Add Restaurant</button>
                </div>
            </div>
            <table>
                <thead>
                    <tr><th>ID</th><th>Name</th><th>Cuisine</th><th>Location</th><th>Dietary Tags</th><th>Actions</th></tr>
                </thead>
                <tbody id="restaurants-tbody">
                {% if restaurants %}
                    {% for r in restaurants %}
                    {% set restaurant_image = r.imageUrl or r.image_url or '' %}
                    {% set restaurant_image_src = restaurant_image if (not restaurant_image or restaurant_image.startswith('http://') or restaurant_image.startswith('https://')) else (backend_url.rstrip('/') + restaurant_image) %}
                    <tr class="admin-detail-row {% if loop.index > 5 %}extra-row{% endif %}" data-section="restaurants" data-detail='{{ {"type": "restaurant", "id": (r.id or ''), "name": r.name, "cuisine": r.cuisine, "location": r.location, "dietaryTags": (r.dietaryTags or r.dietary_tags or ''), "description": (r.description or ''), "imageUrl": restaurant_image_src}|tojson }}'>
                        <td>{{ r.id }}</td>
                        <td>{{ r.name }}</td>
                        <td>{{ r.cuisine }}</td>
                        <td>{{ r.location }}</td>
                        <td>{{ r.dietaryTags or r.dietary_tags or '-' }}</td>
                        <td>
                            <div class="action-btns">
                                <button class="icon-btn admin-edit" title="Edit" aria-label="Edit restaurant"
                                    data-id="{{ r.id }}"
                                    data-name="{{ r.name|e }}"
                                    data-cuisine="{{ r.cuisine|e }}"
                                    data-location="{{ r.location|e }}"
                                    data-dietary="{{ (r.dietaryTags or r.dietary_tags)|default('')|e }}"
                                    data-description="{{ (r.description or '')|e }}"
                                    data-image="{{ (r.imageUrl or r.image_url)|default('')|e }}"
                                    data-latitude="{{ (r.latitude)|default('')|e }}"
                                    data-longitude="{{ (r.longitude)|default('')|e }}">✏️</button>
                                <button class="icon-btn admin-upload-img" title="Upload Image" aria-label="Upload image"
                                    data-id="{{ r.id }}"
                                    data-name="{{ r.name|e }}">📷</button>
                                <button class="icon-btn danger admin-delete" title="Delete" aria-label="Delete restaurant" data-id="{{ r.id }}">🗑️</button>
                            </div>
                        </td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr class="empty-row"><td colspan="6">No restaurants found</td></tr>
                {% endif %}
                </tbody>
            </table>
            {% if restaurants|length > 5 %}
            <div class="section-footer">
                <span class="row-count-label">Showing 5 of {{ restaurants|length }}</span>
                <button type="button" class="btn-show-more" data-section="restaurants" data-total="{{ restaurants|length }}">Show all {{ restaurants|length }} →</button>
            </div>
            {% endif %}
        </div>

        <!-- Menu Items Table -->
        <div class="section" id="section-menu">
            <div class="section-header">
                <div class="section-header-left">
                    <div>
                        <div class="section-title">📋 Menu Items</div>
                        <div class="section-desc">All menu items across restaurants</div>
                    </div>
                </div>
            </div>
            <table>
                <thead>
                    <tr><th>Restaurant</th><th>Name</th><th>Price</th><th>Description</th></tr>
                </thead>
                <tbody id="menu-tbody">
                {% if menu_items %}
                    {% for m in menu_items %}
                    <tr class="admin-detail-row {% if loop.index > 5 %}extra-row{% endif %}" data-section="menu" data-detail='{{ {"type": "menu", "id": (m.id or ''), "restaurantName": m.restaurant_name, "restaurantId": (m.restaurant_id or m.restaurantId or ''), "name": m.name, "price": m.price, "description": (m.description or ''), "imageUrl": (m.imageUrl or '')}|tojson }}'>
                        <td>{{ m.restaurant_name }}</td>
                        <td>{{ m.name }}</td>
                        <td>{{ m.price }}</td>
                        <td>{{ m.description or '-' }}</td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr class="empty-row"><td colspan="4">No menu items found</td></tr>
                {% endif %}
                </tbody>
            </table>
            {% if menu_items|length > 5 %}
            <div class="section-footer">
                <span class="row-count-label">Showing 5 of {{ menu_items|length }}</span>
                <button type="button" class="btn-show-more" data-section="menu" data-total="{{ menu_items|length }}">Show all {{ menu_items|length }} →</button>
            </div>
            {% endif %}
        </div>

        <!-- Pending Reviews Moderation Table -->
        <div class="section" id="section-pending-reviews">
            <div class="section-header">
                <div class="section-header-left">
                    <div>
                        <div class="section-title">⏳ Pending Reviews</div>
                        <div class="section-desc">Approve or reject user-submitted reviews before they go live</div>
                    </div>
                </div>
            </div>
            <div id="pending-reviews-feedback" style="display:none;margin-bottom:8px;padding:10px 14px;border-radius:6px;font-size:13px;"></div>
            <table>
                <thead>
                    <tr><th>ID</th><th>User</th><th>Restaurant</th><th>Rating</th><th>Comment</th><th>Images</th><th>Actions</th></tr>
                </thead>
                <tbody id="pending-reviews-tbody">
                {% if pending_reviews %}
                    {% for rv in pending_reviews %}
                    <tr id="pending-row-{{ rv.id }}" class="admin-detail-row {% if loop.index > 5 %}extra-row{% endif %}" data-section="pending-reviews" data-detail='{{ {"type": "pending", "id": (rv.id or ''), "username": (rv.username or rv.userId or ''), "userId": (rv.userId or rv.user_id or ''), "restaurantName": (rv.restaurantName or ''), "restaurantId": (rv.restaurantId or ''), "rating": (rv.rating or 0), "comment": (rv.comment or ''), "imageUrls": (rv.imageUrls or []), "status": "Pending moderation"}|tojson }}'>
                        <td>{{ rv.id }}</td>
                        <td>{{ rv.username or rv.userId or '-' }}</td>
                        <td>{{ rv.restaurantName or rv.restaurantId or '-' }}</td>
                        {% set rating_value = (rv.rating or 0)|float %}
                        {% set star_count = rating_value|round(0, 'common')|int %}
                        <td class="stars">{{ '★' * star_count }}{{ '☆' * (5 - star_count) }} <span style="color:#666;font-size:12px;">({{ '%.1f'|format(rating_value) }})</span></td>
                        <td>{{ rv.comment or '-' }}</td>
                        <td>
                            {% set rv_images = rv.imageUrls or [] %}
                            {% if rv_images %}
                            <div style="display:flex;gap:6px;align-items:center;overflow-x:auto;padding:2px 0;max-width:200px;">
                                {% for img in rv_images[:3] %}
                                <img src="{{ img if (img.startswith('http://') or img.startswith('https://')) else (backend_url.rstrip('/') + img) }}" alt="Review image" class="pending-review-thumb" style="width:42px;height:42px;object-fit:cover;border-radius:8px;border:1px solid #e0d8d0;cursor:pointer;" />
                                {% endfor %}
                                {% if rv_images|length > 3 %}
                                <span style="font-size:11px;font-weight:700;color:#8a6e5c;white-space:nowrap;">+{{ rv_images|length - 3 }}</span>
                                {% endif %}
                            </div>
                            {% else %}
                            <span style="color:#a89b92;font-size:12px;">-</span>
                            {% endif %}
                        </td>
                        <td style="white-space:nowrap;">
                            <button type="button" class="admin-action-btn approve-btn" data-id="{{ rv.id }}" style="background:#e8f5e9;color:#1b5e20;border:1px solid #a5d6a7;padding:4px 10px;border-radius:4px;cursor:pointer;font-size:12px;margin-right:4px;">✅ Approve</button>
                            <button type="button" class="admin-action-btn reject-btn" data-id="{{ rv.id }}" style="background:#fdecea;color:#b71c1c;border:1px solid #ef9a9a;padding:4px 10px;border-radius:4px;cursor:pointer;font-size:12px;">❌ Reject</button>
                        </td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr class="empty-row" id="pending-reviews-empty"><td colspan="7">No pending reviews</td></tr>
                {% endif %}
                </tbody>
            </table>
            {% if pending_reviews|length > 5 %}
            <div class="section-footer">
                <span class="row-count-label">Showing 5 of {{ pending_reviews|length }}</span>
                <button type="button" class="btn-show-more" data-section="pending-reviews" data-total="{{ pending_reviews|length }}">Show all {{ pending_reviews|length }} →</button>
            </div>
            {% endif %}
        </div>

        <!-- Reviews Table -->
        <div class="section" id="section-reviews">
            <div class="section-header">
                <div class="section-header-left">
                    <div>
                        <div class="section-title">⭐ Reviews</div>
                        <div class="section-desc">User reviews and ratings</div>
                    </div>
                </div>
            </div>
            <table>
                <thead>
                    <tr><th>ID</th><th>User</th><th>Restaurant</th><th>Rating</th><th>Comment</th></tr>
                </thead>
                <tbody id="reviews-tbody">
                {% if reviews %}
                    {% for rv in reviews %}
                    <tr class="admin-detail-row {% if loop.index > 5 %}extra-row{% endif %}" data-section="reviews" data-detail='{{ {"type": "review", "id": (rv.id or ''), "username": (rv.username or rv.userId or rv.user_id or ''), "userId": (rv.userId or rv.user_id or ''), "restaurantName": (rv.restaurantName or ''), "restaurantId": (rv.restaurantId or rv.restaurant_id or ''), "rating": (rv.rating or 0), "comment": (rv.comment or ''), "imageUrls": (rv.imageUrls or []), "status": "Published"}|tojson }}'>
                        <td>{{ rv.id }}</td>
                        <td>{{ rv.username or rv.userId or rv.user_id or '-' }}</td>
                        <td>{{ rv.restaurantId or rv.restaurant_id or '-' }}</td>
                        {% set rating_value = (rv.rating or 0)|float %}
                        {% set star_count = rating_value|round(0, 'common')|int %}
                        <td class="stars">{{ '★' * star_count }}{{ '☆' * (5 - star_count) }} <span style="color:#666;font-size:12px;">({{ '%.1f'|format(rating_value) }})</span></td>
                        <td>{{ rv.comment or '-' }}</td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr class="empty-row"><td colspan="5">No reviews found</td></tr>
                {% endif %}
                </tbody>
            </table>
            {% if reviews|length > 5 %}
            <div class="section-footer">
                <span class="row-count-label">Showing 5 of {{ reviews|length }}</span>
                <button type="button" class="btn-show-more" data-section="reviews" data-total="{{ reviews|length }}">Show all {{ reviews|length }} →</button>
            </div>
            {% endif %}
        </div>
    </div>

    {% if error %}
    <div style="max-width:1200px;margin:-12px auto 20px;padding:0 24px;">
        <div style="background:#fdecea;color:#b71c1c;padding:12px 16px;border-radius:8px;font-size:13px;">{{ error }}</div>
    </div>
    {% endif %}

    <!-- Yelp Import modal -->
    <div id="yelp-import-backdrop" class="modal-backdrop" style="z-index:200;">
        <div class="modal-box">
            <div class="modal-title">🔍 Import from Yelp</div>
            <div class="modal-subtitle">Fetch restaurants from Yelp Fusion API and add them to the database. Duplicates are automatically skipped.</div>
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">Location</label>
                    <input id="yelp_location" class="form-input" value="Toronto" />
                </div>
                <div class="form-group">
                    <label class="form-label">Max results (1–50)</label>
                    <input id="yelp_limit" class="form-input" type="number" value="20" min="1" max="50" />
                </div>
            </div>
            <div id="yelp_msg" style="font-size:13px;min-height:18px;margin-top:14px;"></div>
            <div class="modal-actions">
                <button type="button" id="yelp_import_btn" class="btn-primary">Import</button>
                <button type="button" id="yelp_cancel_btn" class="btn-secondary">Cancel</button>
            </div>
        </div>
    </div>

    <!-- Add Restaurant modal -->
    <div class="modal-backdrop" id="admin-add-backdrop">
        <div class="modal-box">
            <div class="modal-title">+ Add Restaurant</div>
            <div class="modal-subtitle">Enter the restaurant details below.</div>
            <div class="modal-section-label">Basic Info</div>
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">Name</label>
                    <input id="admin_name" class="form-input" placeholder="Restaurant name" />
                </div>
                <div class="form-group">
                    <label class="form-label">Cuisine</label>
                    <input id="admin_cuisine" class="form-input" placeholder="e.g. Italian" />
                </div>
                <div class="form-group">
                    <label class="form-label">Location</label>
                    <input id="admin_location" class="form-input" placeholder="City, Province" />
                </div>
                <div class="form-group">
                    <label class="form-label">Dietary Tags</label>
                    <input id="admin_dietary" class="form-input" placeholder="comma-separated" />
                </div>
                <div class="form-group form-full">
                    <label class="form-label">Description</label>
                    <textarea id="admin_description" class="form-textarea"></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">Latitude <span style="color:#9a8b80;font-weight:400;">(optional)</span></label>
                    <input id="admin_latitude" class="form-input" type="number" step="any" placeholder="e.g. 43.9414" />
                </div>
                <div class="form-group">
                    <label class="form-label">Longitude <span style="color:#9a8b80;font-weight:400;">(optional)</span></label>
                    <input id="admin_longitude" class="form-input" type="number" step="any" placeholder="e.g. -78.8964" />
                </div>
            </div>
            <div class="modal-actions">
                <button type="button" id="admin_add_save" class="btn-primary">Save Restaurant</button>
                <button type="button" id="admin_add_cancel" class="btn-secondary">Cancel</button>
            </div>
        </div>
    </div>

    <!-- Edit Restaurant modal -->
    <div class="modal-backdrop" id="admin-edit-backdrop">
        <div class="modal-box">
            <div class="modal-title">✏️ Edit Restaurant</div>
            <div class="modal-subtitle">Update restaurant details and image below.</div>

            <div class="modal-section-label">Restaurant Image</div>
            <div class="modal-image-box">
                <img id="admin_edit_image_preview" style="display:none;width:100%;max-height:160px;object-fit:cover;border-radius:8px;margin-bottom:12px;" src="#" alt="Current image" />
                <div id="admin_edit_no_image" style="display:none;width:100%;height:100px;background:#fff;border:1px dashed #d5cfc9;border-radius:8px;align-items:center;justify-content:center;color:#bbb;font-size:13px;margin-bottom:12px;">No image uploaded</div>
                <div id="admin_edit_drop_zone" class="drop-zone">
                    <input type="file" id="admin_edit_image_file" accept="image/jpeg,image/png,image/gif,image/webp" style="position:absolute;opacity:0;width:0;height:0;" />
                    <div class="dz-icon">📷</div>
                    <div class="dz-title"><strong>Click or drag image</strong> to upload</div>
                    <div class="dz-hint">JPG, PNG, GIF or WebP · Max 5 MB</div>
                </div>
                <div id="admin_edit_image_msg" style="font-size:12px;margin-top:8px;min-height:16px;"></div>
            </div>

            <div class="modal-section-label">Details</div>
            <div class="form-grid">
                <div class="form-group">
                    <label class="form-label">Name</label>
                    <input id="admin_edit_name" class="form-input" />
                </div>
                <div class="form-group">
                    <label class="form-label">Cuisine</label>
                    <input id="admin_edit_cuisine" class="form-input" />
                </div>
                <div class="form-group">
                    <label class="form-label">Location</label>
                    <input id="admin_edit_location" class="form-input" />
                </div>
                <div class="form-group">
                    <label class="form-label">Dietary Tags</label>
                    <input id="admin_edit_dietary" class="form-input" placeholder="comma-separated" />
                </div>
                <div class="form-group form-full">
                    <label class="form-label">Description</label>
                    <textarea id="admin_edit_description" class="form-textarea"></textarea>
                </div>
                <div class="form-group">
                    <label class="form-label">Latitude <span style="color:#9a8b80;font-weight:400;">(optional)</span></label>
                    <input id="admin_edit_latitude" class="form-input" type="number" step="any" placeholder="e.g. 43.9414" />
                </div>
                <div class="form-group">
                    <label class="form-label">Longitude <span style="color:#9a8b80;font-weight:400;">(optional)</span></label>
                    <input id="admin_edit_longitude" class="form-input" type="number" step="any" placeholder="e.g. -78.8964" />
                </div>
            </div>
            <div class="modal-actions">
                <button type="button" id="admin_edit_save" class="btn-primary">Save Changes</button>
                <button type="button" id="admin_edit_cancel" class="btn-secondary">Cancel</button>
            </div>
        </div>
    </div>

    <!-- Upload Image modal -->
    <div class="modal-backdrop" id="admin-upload-backdrop" style="z-index:200;">
        <div class="modal-box" style="max-width:480px;">
            <div class="modal-title">📷 Upload Restaurant Image</div>
            <p id="admin-upload-subtitle" style="font-size:13px;color:var(--text-muted);margin-bottom:16px;"></p>
            <form id="admin-upload-form" enctype="multipart/form-data">
                <img id="admin-upload-preview" style="display:none;width:100%;max-height:180px;object-fit:cover;border-radius:8px;margin-bottom:12px;" src="#" alt="Preview" />
                <div id="admin-upload-drop-zone" class="drop-zone" style="padding:32px 16px;position:relative;">
                    <input type="file" id="admin-upload-file" name="file" accept="image/jpeg,image/png,image/gif,image/webp" style="position:absolute;inset:0;opacity:0;width:100%;height:100%;cursor:pointer;" />
                    <div class="dz-icon" style="font-size:32px;">📷</div>
                    <div class="dz-title"><strong>Click or drag &amp; drop</strong> an image</div>
                    <div class="dz-hint">JPG, PNG, GIF or WebP · Max 5 MB</div>
                </div>
                <div id="admin-upload-msg" style="font-size:13px;min-height:18px;margin-top:10px;"></div>
                <div class="modal-actions">
                    <button type="button" id="admin-upload-save" disabled class="btn-primary">Upload</button>
                    <button type="button" id="admin-upload-cancel" class="btn-secondary">Cancel</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Row Details modal -->
    <div class="modal-backdrop" id="admin-detail-backdrop" style="z-index:240;">
        <div class="modal-box admin-detail-modal">
            <div class="admin-detail-header">
                <div>
                    <div id="admin-detail-title" class="modal-title">Details</div>
                    <div id="admin-detail-subtitle" class="modal-subtitle">Inspect the selected row in more detail.</div>
                </div>
                <button type="button" id="admin-detail-close" class="admin-detail-close" aria-label="Close detail view">&times;</button>
            </div>
            <div id="admin-detail-body"></div>
        </div>
    </div>

    <script>
        // 🔍 DEBUG: Script is loading
        console.log('[DEBUG] [ADMIN_DASHBOARD] Script initialized');

        // ── Show More / Show Less ──
        document.querySelectorAll('.btn-show-more').forEach(btn => {
            btn.addEventListener('click', () => {
                const section = btn.getAttribute('data-section');
                const total = parseInt(btn.getAttribute('data-total'), 10);
                const extraRows = document.querySelectorAll('tr.extra-row[data-section="' + section + '"]');
                const expanded = btn.getAttribute('data-expanded') === 'true';
                const footer = btn.closest('.section-footer');
                const label = footer ? footer.querySelector('.row-count-label') : null;

                if (expanded) {
                    extraRows.forEach(r => r.classList.remove('visible'));
                    btn.textContent = 'Show all ' + total + ' \u2192';
                    btn.setAttribute('data-expanded', 'false');
                    if (label) label.textContent = 'Showing 5 of ' + total;
                } else {
                    extraRows.forEach(r => r.classList.add('visible'));
                    btn.textContent = 'Show less \u2191';
                    btn.setAttribute('data-expanded', 'true');
                    if (label) label.textContent = 'Showing all ' + total;
                }
            });
        });

        const backendUrl = {{ backend_url | tojson }}.replace(/\\/$/, '');

        function escapeHtml(value) {
            return String(value ?? '').replace(/[&<>"']/g, (character) => ({
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#39;'
            })[character]);
        }

        function normalizeAdminImageUrl(url) {
            if (!url) return '';
            if (/^https?:\/\//i.test(url)) return url;
            return backendUrl + url;
        }

        function getDetailFieldValue(value, fallback = '-') {
            if (value === undefined || value === null || value === '') {
                return fallback;
            }
            return escapeHtml(value);
        }

        function getDetailBadgeMarkup(values) {
            if (!values || !values.length) {
                return '<span class="admin-detail-empty">None</span>';
            }
            return '<div class="admin-detail-badges">' + values.map(value => '<span class="admin-detail-badge">' + escapeHtml(value) + '</span>').join('') + '</div>';
        }

        function getGalleryMarkup(images) {
            if (!images || !images.length) {
                return '<div class="admin-detail-empty">No images attached.</div>';
            }
            return '<div class="admin-detail-gallery">' + images.map((src, index) => {
                const safeSrc = escapeHtml(src);
                return '<button type="button" class="admin-detail-gallery-item" data-src="' + safeSrc + '" aria-label="View image ' + (index + 1) + '"><img src="' + safeSrc + '" alt="Attached image ' + (index + 1) + '" /></button>';
            }).join('') + '</div>';
        }

        function closeAdminDetailModal() {
            const backdrop = document.getElementById('admin-detail-backdrop');
            if (backdrop) backdrop.style.display = 'none';
        }

        function renderDetailCards(items) {
            return items.filter(Boolean).map(item => {
                const fullClass = item.full ? ' full' : '';
                return '<div class="admin-detail-card' + fullClass + '"><div class="admin-detail-label">' + escapeHtml(item.label) + '</div><div class="admin-detail-value">' + item.value + '</div></div>';
            }).join('');
        }

        function openAdminDetailModal(rawDetail) {
            let detail = rawDetail;
            if (typeof rawDetail === 'string') {
                try {
                    detail = JSON.parse(rawDetail);
                } catch (error) {
                    console.error('Could not parse admin row detail payload', error);
                    return;
                }
            }

            const titleEl = document.getElementById('admin-detail-title');
            const subtitleEl = document.getElementById('admin-detail-subtitle');
            const bodyEl = document.getElementById('admin-detail-body');
            const backdrop = document.getElementById('admin-detail-backdrop');
            if (!titleEl || !subtitleEl || !bodyEl || !backdrop) return;

            const typeLabel = {
                user: 'User details',
                restaurant: 'Restaurant details',
                menu: 'Menu item details',
                pending: 'Pending review details',
                review: 'Review details'
            }[detail.type] || 'Row details';

            const heading = {
                user: detail.username ? detail.username : 'User #' + (detail.id || ''),
                restaurant: detail.name ? detail.name : 'Restaurant #' + (detail.id || ''),
                menu: detail.name ? detail.name : 'Menu item #' + (detail.id || ''),
                pending: detail.restaurantName ? 'Pending review for ' + detail.restaurantName : 'Pending review #' + (detail.id || ''),
                review: detail.restaurantName ? 'Review for ' + detail.restaurantName : 'Review #' + (detail.id || '')
            }[detail.type] || 'Details';

            titleEl.textContent = heading;
            subtitleEl.textContent = typeLabel;

            const images = (detail.imageUrls || []).map(normalizeAdminImageUrl).filter(Boolean);
            if (detail.imageUrl) images.unshift(normalizeAdminImageUrl(detail.imageUrl));

            const sections = [];
            if (detail.type === 'user') {
                sections.push(renderDetailCards([
                    { label: 'ID', value: getDetailFieldValue(detail.id) },
                    { label: 'Username', value: getDetailFieldValue(detail.username) },
                    { label: 'Role', value: getDetailFieldValue(detail.role) },
                ]));
            } else if (detail.type === 'restaurant') {
                sections.push(renderDetailCards([
                    { label: 'ID', value: getDetailFieldValue(detail.id) },
                    { label: 'Name', value: getDetailFieldValue(detail.name) },
                    { label: 'Cuisine', value: getDetailFieldValue(detail.cuisine) },
                    { label: 'Location', value: getDetailFieldValue(detail.location) },
                    { label: 'Image', value: getDetailFieldValue(detail.imageUrl ? 'Attached' : 'Not uploaded') },
                    { label: 'Description', value: getDetailFieldValue(detail.description), full: true },
                ]));
                sections.push('<div class="admin-detail-card full"><div class="admin-detail-label">Dietary Tags</div>' + getDetailBadgeMarkup(String(detail.dietaryTags || '').split(',').map(item => item.trim()).filter(Boolean)) + '</div>');
            } else if (detail.type === 'menu') {
                sections.push(renderDetailCards([
                    { label: 'ID', value: getDetailFieldValue(detail.id) },
                    { label: 'Restaurant', value: getDetailFieldValue(detail.restaurantName || detail.restaurantId) },
                    { label: 'Item Name', value: getDetailFieldValue(detail.name) },
                    { label: 'Price', value: getDetailFieldValue(detail.price) },
                    { label: 'Description', value: getDetailFieldValue(detail.description), full: true },
                ]));
                if (detail.imageUrl) {
                    const menuImageUrl = detail.imageUrl.startsWith('http')
                        ? detail.imageUrl
                        : (backendUrl + (detail.imageUrl.startsWith('/') ? detail.imageUrl : '/' + detail.imageUrl));
                    const imgHtml = `<div class="admin-detail-card full"><img src="${escapeHtml(menuImageUrl)}" alt="Menu Item Image" style="width: 100%; height: auto; max-height: 300px; object-fit: cover; border-radius: 10px; border: 1px solid #ede3da;" /></div>`;
                    sections.push(imgHtml);
                }
            } else {
                sections.push(renderDetailCards([
                    { label: 'ID', value: getDetailFieldValue(detail.id) },
                    { label: 'User', value: getDetailFieldValue(detail.username || detail.userId) },
                    { label: 'Restaurant', value: getDetailFieldValue(detail.restaurantName || detail.restaurantId) },
                    { label: 'Rating', value: getDetailFieldValue(detail.rating) },
                    { label: 'Status', value: getDetailFieldValue(detail.status) },
                    { label: 'Comment', value: getDetailFieldValue(detail.comment), full: true },
                ]));
            }

            if (images.length) {
                sections.push('<div class="admin-detail-card full"><div class="admin-detail-label">Images</div>' + getGalleryMarkup(images) + '</div>');
            }

            bodyEl.innerHTML = sections.join('');
            bodyEl.querySelectorAll('.admin-detail-gallery-item').forEach(btn => {
                btn.addEventListener('click', () => openAdminImagePreview(btn.getAttribute('data-src')));
            });

            backdrop.style.display = 'flex';
        }

        document.querySelectorAll('tr[data-detail]').forEach(row => {
            row.addEventListener('click', (event) => {
                if (event.target.closest('button, a, input, label, .pending-review-thumb')) {
                    return;
                }
                openAdminDetailModal(row.getAttribute('data-detail'));
            });
            row.addEventListener('keydown', (event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                    event.preventDefault();
                    openAdminDetailModal(row.getAttribute('data-detail'));
                }
            });
            row.tabIndex = 0;
            row.setAttribute('role', 'button');
        });

        function openAdminImagePreview(src) {
            const existing = document.getElementById('admin-image-preview-overlay');
            if (existing) existing.remove();

            const overlay = document.createElement('div');
            overlay.id = 'admin-image-preview-overlay';
            overlay.style.position = 'fixed';
            overlay.style.inset = '0';
            overlay.style.background = 'rgba(10, 8, 6, 0.72)';
            overlay.style.backdropFilter = 'blur(4px)';
            overlay.style.display = 'flex';
            overlay.style.alignItems = 'center';
            overlay.style.justifyContent = 'center';
            overlay.style.padding = '20px';
            overlay.style.zIndex = '250';
            overlay.innerHTML = `
                <div style="position:relative;width:min(92vw, 1280px);max-height:92vh;display:flex;align-items:center;justify-content:center;">
                    <button type="button" id="admin-image-preview-close" style="position:absolute;top:-52px;right:0;width:42px;height:42px;border:none;border-radius:50%;background:rgba(255,255,255,0.22);color:#fff;font-size:22px;cursor:pointer;">&times;</button>
                    <img src="${src}" alt="Review image preview" style="width:100%;max-height:92vh;display:block;object-fit:contain;border-radius:16px;box-shadow:0 20px 48px rgba(0,0,0,0.42);background:#111;" />
                </div>
            `;
            document.body.appendChild(overlay);

            const closePreview = () => overlay.remove();
            overlay.addEventListener('click', (evt) => {
                if (evt.target === overlay) closePreview();
            });
            overlay.querySelector('#admin-image-preview-close').addEventListener('click', closePreview);
        }

        document.querySelectorAll('.pending-review-thumb').forEach((img) => {
            img.addEventListener('click', (event) => {
                event.stopPropagation();
                openAdminImagePreview(img.src);
            });
        });

        const adminDetailBackdrop = document.getElementById('admin-detail-backdrop');
        const adminDetailClose = document.getElementById('admin-detail-close');
        if (adminDetailBackdrop) {
            adminDetailBackdrop.addEventListener('click', (event) => {
                if (event.target === adminDetailBackdrop) {
                    closeAdminDetailModal();
                }
            });
        }
        if (adminDetailClose) {
            adminDetailClose.addEventListener('click', closeAdminDetailModal);
        }
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                closeAdminDetailModal();
            }
        });

        // ── Pending Reviews: Approve / Reject ──
        function showModerationFeedback(message, isSuccess) {
            const fb = document.getElementById('pending-reviews-feedback');
            if (!fb) return;
            fb.textContent = message;
            fb.style.background = isSuccess ? '#e8f5e9' : '#fdecea';
            fb.style.color = isSuccess ? '#1b5e20' : '#b71c1c';
            fb.style.display = 'block';
            setTimeout(() => { fb.style.display = 'none'; }, 4000);
        }

        function updatePendingReviewCount(delta) {
            const countEl = document.getElementById('pending-reviews-count');
            if (!countEl) return;

            const current = parseInt(countEl.textContent || '0', 10);
            const next = Math.max(0, (Number.isNaN(current) ? 0 : current) + delta);
            countEl.textContent = String(next);

            const section = document.getElementById('section-pending-reviews');
            if (!section) return;

            const footer = section.querySelector('.section-footer');
            if (!footer) return;

            const label = footer.querySelector('.row-count-label');
            const btn = footer.querySelector('.btn-show-more[data-section="pending-reviews"]');

            if (btn) {
                btn.setAttribute('data-total', String(next));
                const expanded = btn.getAttribute('data-expanded') === 'true';

                if (next <= 5) {
                    btn.style.display = 'none';
                    if (label) label.textContent = 'Showing ' + next + ' of ' + next;
                } else {
                    btn.style.display = '';
                    btn.textContent = expanded ? 'Show less \u2191' : 'Show all ' + next + ' \u2192';
                    if (label) label.textContent = expanded ? 'Showing all ' + next : 'Showing 5 of ' + next;
                }
            }
        }

        function removeReviewRowAndCheckEmpty(id) {
            const row = document.getElementById('pending-row-' + id);
            if (row) {
                row.remove();
                updatePendingReviewCount(-1);
            }
            const tbody = document.getElementById('pending-reviews-tbody');
            if (tbody && tbody.querySelectorAll('tr:not(.empty-row)').length === 0) {
                if (!document.getElementById('pending-reviews-empty')) {
                    const tr = document.createElement('tr');
                    tr.className = 'empty-row';
                    tr.id = 'pending-reviews-empty';
                    tr.innerHTML = '<td colspan="7">No pending reviews</td>';
                    tbody.appendChild(tr);
                }
            }
        }

        document.querySelectorAll('.approve-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.getAttribute('data-id');
                btn.disabled = true;
                try {
                    const resp = await fetch('/admin/reviews/' + id + '/approve', { method: 'PUT' });
                    if (resp.ok) {
                        removeReviewRowAndCheckEmpty(id);
                        showModerationFeedback('Review #' + id + ' approved and published.', true);
                    } else {
                        const body = await resp.json().catch(() => ({}));
                        showModerationFeedback('Error: ' + (body.error || 'Could not approve review.'), false);
                        btn.disabled = false;
                    }
                } catch (e) {
                    showModerationFeedback('Network error approving review.', false);
                    btn.disabled = false;
                }
            });
        });

        document.querySelectorAll('.reject-btn').forEach(btn => {
            btn.addEventListener('click', async () => {
                const id = btn.getAttribute('data-id');
                btn.disabled = true;
                try {
                    const resp = await fetch('/admin/reviews/' + id + '/reject', { method: 'PUT' });
                    if (resp.ok) {
                        removeReviewRowAndCheckEmpty(id);
                        showModerationFeedback('Review #' + id + ' rejected.', true);
                    } else {
                        const body = await resp.json().catch(() => ({}));
                        showModerationFeedback('Error: ' + (body.error || 'Could not reject review.'), false);
                        btn.disabled = false;
                    }
                } catch (e) {
                    showModerationFeedback('Network error rejecting review.', false);
                    btn.disabled = false;
                }
            });
        });

        // ── Yelp Import modal ──
        const yelpBackdrop = document.getElementById('yelp-import-backdrop');
        const openYelpModalBtn = document.getElementById('open-yelp-modal');
        const yelpCancelBtn = document.getElementById('yelp_cancel_btn');
        const yelpImportBtn = document.getElementById('yelp_import_btn');
        console.log('[DEBUG] Yelp modal elements:', { openYelpModalBtn, yelpCancelBtn, yelpImportBtn, yelpBackdrop });
        if (openYelpModalBtn) {
            openYelpModalBtn.addEventListener('click', () => {
                console.log('[DEBUG] Open Yelp modal clicked');
                document.getElementById('yelp_msg').textContent = '';
                document.getElementById('yelp_msg').style.color = '';
                yelpBackdrop.style.display = 'flex';
            });
        }
        if (yelpCancelBtn) {
            yelpCancelBtn.addEventListener('click', () => { yelpBackdrop.style.display = 'none'; });
        }

        if (yelpImportBtn) {
            yelpImportBtn.addEventListener('click', async () => {
            const location = document.getElementById('yelp_location').value.trim() || 'Toronto';
            const limit = parseInt(document.getElementById('yelp_limit').value, 10) || 20;
            const msgEl = document.getElementById('yelp_msg');
            const btn = yelpImportBtn;

            btn.disabled = true;
            btn.textContent = 'Importing…';
            msgEl.textContent = '';

            try {
                const res = await fetch('/admin/import-yelp-restaurants', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ location, limit })
                });
                const data = await res.json().catch(() => ({}));
                if (res.ok) {
                    msgEl.textContent = '✓ ' + (data.message || data.imported + ' restaurants imported');
                    msgEl.style.color = '#2e7d32';
                    setTimeout(() => { yelpBackdrop.style.display = 'none'; window.location.reload(); }, 1500);
                } else {
                    msgEl.textContent = '✗ ' + (data.error || data.message || 'Import failed');
                    msgEl.style.color = '#b71c1c';
                }
            } catch (e) {
                msgEl.textContent = '✗ Network error: ' + e;
                msgEl.style.color = '#b71c1c';
            } finally {
                btn.disabled = false;
                btn.textContent = 'Import';
            }
            });
        }

        const adminBackdrop = document.getElementById('admin-add-backdrop');
        const openAddModalBtn = document.getElementById('open-add-modal');
        const adminAddCancelBtn = document.getElementById('admin_add_cancel');
        const adminAddSaveBtn = document.getElementById('admin_add_save');
        console.log('[DEBUG] Add restaurant modal elements:', { openAddModalBtn, adminAddCancelBtn, adminAddSaveBtn, adminBackdrop });
        if (openAddModalBtn) openAddModalBtn.addEventListener('click', () => { console.log('[DEBUG] Open Add modal clicked'); adminBackdrop.style.display = 'flex'; });
        if (adminAddCancelBtn) adminAddCancelBtn.addEventListener('click', () => { console.log('[DEBUG] Cancel Add modal'); adminBackdrop.style.display = 'none'; });

        if (adminAddSaveBtn) adminAddSaveBtn.addEventListener('click', async () => {
            console.log('[DEBUG] Save restaurant clicked');
            const payload = {
                name: document.getElementById('admin_name').value.trim(),
                cuisine: document.getElementById('admin_cuisine').value.trim(),
                dietaryTags: document.getElementById('admin_dietary').value.trim(),
                location: document.getElementById('admin_location').value.trim(),
                description: document.getElementById('admin_description').value.trim()
            };
            const latVal = document.getElementById('admin_latitude').value.trim();
            const lngVal = document.getElementById('admin_longitude').value.trim();
            if (latVal !== '') payload.latitude = parseFloat(latVal);
            if (lngVal !== '') payload.longitude = parseFloat(lngVal);
            if (!payload.name || !payload.cuisine || !payload.location) {
                alert('Please provide name, cuisine and location');
                return;
            }

            try {
                console.log('[DEBUG] Sending POST request to /admin/restaurants with payload:', payload);
                const res = await fetch('/admin/restaurants', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await res.json().catch(() => ({}));
                console.log('[DEBUG] Response status:', res.status, 'data:', data);

                if (res.ok) {
                    // Success - refresh dashboard to show new restaurant
                    adminBackdrop.style.display = 'none';
                    window.location.reload();
                    return;
                }

                alert('Failed to add restaurant: ' + (data.error || data.message || JSON.stringify(data)));
            } catch (e) {
                alert('Request failed: ' + e);
            }
        });

        // Attach delete handlers to per-row delete buttons
        console.log('[DEBUG] Attaching delete handlers to', document.querySelectorAll('.admin-delete').length, 'buttons');
        document.querySelectorAll('.admin-delete').forEach(btn => {
            btn.addEventListener('click', async (ev) => {
                console.log('[DEBUG] Delete button clicked:', btn.getAttribute('data-id'));
                const id = btn.getAttribute('data-id');
                if (!id) return;
                if (!confirm('Delete restaurant #' + id + '? This action cannot be undone.')) return;
                try {
                    console.log('[DEBUG] Sending DELETE request for restaurant:', id);
                    const resp = await fetch('/admin/restaurants/' + encodeURIComponent(id), { method: 'DELETE' });
                    const body = await resp.json().catch(() => ({}));
                    console.log('[DEBUG] Delete response:', resp.status, body);
                    if (resp.ok) {
                        window.location.reload();
                        return;
                    }
                    alert('Failed to delete: ' + (body.error || body.message || JSON.stringify(body)));
                } catch (e) {
                    alert('Request failed: ' + e);
                }
            });
        });

        // Edit button handlers - open modal and populate fields
        console.log('[DEBUG] Attaching edit handlers to', document.querySelectorAll('.admin-edit').length, 'buttons');
        document.querySelectorAll('.admin-edit').forEach(btn => {
            btn.addEventListener('click', (ev) => {
                console.log('[DEBUG] Edit button clicked:', btn.getAttribute('data-id'));
                const id = btn.getAttribute('data-id');
                if (!id) return;
                document.getElementById('admin_edit_name').value = btn.getAttribute('data-name') || '';
                document.getElementById('admin_edit_cuisine').value = btn.getAttribute('data-cuisine') || '';
                document.getElementById('admin_edit_location').value = btn.getAttribute('data-location') || '';
                document.getElementById('admin_edit_dietary').value = btn.getAttribute('data-dietary') || '';
                document.getElementById('admin_edit_description').value = btn.getAttribute('data-description') || '';
                document.getElementById('admin_edit_latitude').value = btn.getAttribute('data-latitude') || '';
                document.getElementById('admin_edit_longitude').value = btn.getAttribute('data-longitude') || '';

                // Handle image preview
                const imageUrl = btn.getAttribute('data-image') || '';
                const imagePreview = document.getElementById('admin_edit_image_preview');
                const noImageMsg = document.getElementById('admin_edit_no_image');
                if (imageUrl) {
                    imagePreview.src = imageUrl;
                    imagePreview.style.display = 'block';
                    noImageMsg.style.display = 'none';
                } else {
                    imagePreview.style.display = 'none';
                    noImageMsg.style.display = 'flex';
                }

                // Reset image file input
                document.getElementById('admin_edit_image_file').value = '';
                document.getElementById('admin_edit_image_msg').textContent = '';

                // Store id on save button for later
                document.getElementById('admin_edit_save').setAttribute('data-id', id);
                document.getElementById('admin-edit-backdrop').style.display = 'flex';
            });
        });

        const adminEditCancelBtn = document.getElementById('admin_edit_cancel');
        if (adminEditCancelBtn) {
            adminEditCancelBtn.addEventListener('click', () => {
                document.getElementById('admin-edit-backdrop').style.display = 'none';
                document.getElementById('admin_edit_image_file').value = '';
            });
        }

        // Image file handling in edit modal
        const editImageFile = document.getElementById('admin_edit_image_file');
        const editDropZone = document.getElementById('admin_edit_drop_zone');
        const editImageMsg = document.getElementById('admin_edit_image_msg');
        const editImagePreview = document.getElementById('admin_edit_image_preview');

        if (editDropZone && editImageFile) {
            editDropZone.addEventListener('click', () => editImageFile.click());

            editImageFile.addEventListener('change', handleEditImageFileSelect);

            editDropZone.addEventListener('dragover', e => {
                e.preventDefault();
                editDropZone.style.borderColor = '#b85c38';
                editDropZone.style.background = '#faf6f3';
            });

            editDropZone.addEventListener('dragleave', () => {
                editDropZone.style.borderColor = '#d5cfc9';
                editDropZone.style.background = '';
            });

            editDropZone.addEventListener('drop', e => {
                e.preventDefault();
                editDropZone.style.borderColor = '#d5cfc9';
                editDropZone.style.background = '';
                if (e.dataTransfer.files.length) {
                    editImageFile.files = e.dataTransfer.files;
                    handleEditImageFileSelect();
                }
            });
        }

        function handleEditImageFileSelect() {
            const file = editImageFile.files[0];
            if (!file) return;
            const allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
            if (!allowed.includes(file.type)) {
                editImageMsg.textContent = '✗ Invalid file type. Use JPG, PNG, GIF or WebP.';
                editImageMsg.style.color = '#b71c1c';
                editImageFile.value = '';
                return;
            }
            if (file.size > 5 * 1024 * 1024) {
                editImageMsg.textContent = '✗ File too large. Max 5 MB.';
                editImageMsg.style.color = '#b71c1c';
                editImageFile.value = '';
                return;
            }
            editImageMsg.textContent = '✓ Image ready to upload';
            editImageMsg.style.color = '#2e7d32';
            const reader = new FileReader();
            reader.onload = e => {
                editImagePreview.src = e.target.result;
                editImagePreview.style.display = 'block';
                document.getElementById('admin_edit_no_image').style.display = 'none';
            };
            reader.readAsDataURL(file);
        }

        const adminEditSaveBtn = document.getElementById('admin_edit_save');
        console.log('[DEBUG] Edit save button:', adminEditSaveBtn);
        if (adminEditSaveBtn) adminEditSaveBtn.addEventListener('click', async () => {
            console.log('[DEBUG] Edit save button clicked');
            const id = document.getElementById('admin_edit_save').getAttribute('data-id');
            if (!id) return alert('No restaurant selected');

            const payload = {
                name: document.getElementById('admin_edit_name').value.trim(),
                cuisine: document.getElementById('admin_edit_cuisine').value.trim(),
                dietaryTags: document.getElementById('admin_edit_dietary').value.trim(),
                location: document.getElementById('admin_edit_location').value.trim(),
                description: document.getElementById('admin_edit_description').value.trim()
            };
            const editLatVal = document.getElementById('admin_edit_latitude').value.trim();
            const editLngVal = document.getElementById('admin_edit_longitude').value.trim();
            if (editLatVal !== '') payload.latitude = parseFloat(editLatVal);
            if (editLngVal !== '') payload.longitude = parseFloat(editLngVal);

            if (!payload.name || !payload.cuisine || !payload.location) {
                alert('Please provide name, cuisine and location');
                return;
            }

            const saveBtn = document.getElementById('admin_edit_save');
            saveBtn.disabled = true;
            saveBtn.textContent = 'Saving…';

            try {
                // First, update restaurant details via PUT
                const res = await fetch('/admin/restaurants/' + encodeURIComponent(id), {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await res.json().catch(() => ({}));

                if (!res.ok) {
                    alert('Failed to update restaurant: ' + (data.error || data.message || JSON.stringify(data)));
                    saveBtn.disabled = false;
                    saveBtn.textContent = 'Save Changes';
                    return;
                }

                // Then, if a new image was selected, upload it
                const imageFile = document.getElementById('admin_edit_image_file').files[0];
                if (imageFile) {
                    saveBtn.textContent = 'Uploading image…';
                    const formData = new FormData();
                    formData.append('file', imageFile);

                    const uploadRes = await fetch('/admin/restaurants/' + encodeURIComponent(id) + '/upload-image', {
                        method: 'POST',
                        body: formData
                    });

                    if (!uploadRes.ok) {
                        const uploadData = await uploadRes.json().catch(() => ({}));
                        const errorMsg = uploadData.error || uploadData.message || 'Unknown error';
                        console.error('Image upload failed:', { status: uploadRes.status, response: uploadData });
                        alert('Image upload failed (HTTP ' + uploadRes.status + '): ' + errorMsg);
                    }
                }

                // Close modal and reload
                document.getElementById('admin-edit-backdrop').style.display = 'none';
                window.location.reload();
            } catch (e) {
                alert('Request failed: ' + e);
                saveBtn.disabled = false;
                saveBtn.textContent = 'Save Changes';
            }
        });

        // ── Upload Image modal ──
        const uploadBackdrop = document.getElementById('admin-upload-backdrop');
        const adminUploadFile = document.getElementById('admin-upload-file');
        const adminUploadPreview = document.getElementById('admin-upload-preview');
        const adminUploadSave = document.getElementById('admin-upload-save');
        const adminUploadMsg = document.getElementById('admin-upload-msg');
        const adminUploadDropZone = document.getElementById('admin-upload-drop-zone');

        document.querySelectorAll('.admin-upload-img').forEach(btn => {
            btn.addEventListener('click', () => {
                console.log('[DEBUG] Upload image button clicked:', btn.getAttribute('data-id'));
                const id = btn.getAttribute('data-id');
                const name = btn.getAttribute('data-name') || ('Restaurant #' + id);
                document.getElementById('admin-upload-subtitle').textContent = 'Uploading image for: ' + name;
                adminUploadSave.setAttribute('data-id', id);
                adminUploadSave.disabled = true;
                adminUploadMsg.textContent = '';
                adminUploadPreview.style.display = 'none';
                adminUploadFile.value = '';
                uploadBackdrop.style.display = 'flex';
            });
        });

        const adminUploadCancelBtn = document.getElementById('admin-upload-cancel');
        if (adminUploadCancelBtn) adminUploadCancelBtn.addEventListener('click', () => { uploadBackdrop.style.display = 'none'; });

        if (adminUploadFile) adminUploadFile.addEventListener('change', handleAdminFileSelect);

        if (adminUploadDropZone && adminUploadFile) {
            adminUploadDropZone.addEventListener('dragover', e => {
                e.preventDefault();
                adminUploadDropZone.style.borderColor = '#b85c38';
                adminUploadDropZone.style.background = '#faf6f3';
            });
            adminUploadDropZone.addEventListener('dragleave', () => {
                adminUploadDropZone.style.borderColor = '#d5cfc9';
                adminUploadDropZone.style.background = '';
            });
            adminUploadDropZone.addEventListener('drop', e => {
                e.preventDefault();
                adminUploadDropZone.style.borderColor = '#d5cfc9';
                adminUploadDropZone.style.background = '';
                if (e.dataTransfer.files.length) {
                    adminUploadFile.files = e.dataTransfer.files;
                    handleAdminFileSelect();
                }
            });
        }

        function handleAdminFileSelect() {
            const file = adminUploadFile.files[0];
            if (!file) return;
            const allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
            if (!allowed.includes(file.type)) {
                adminUploadMsg.textContent = '✗ Invalid file type. Use JPG, PNG, GIF or WebP.';
                adminUploadMsg.style.color = '#b71c1c';
                adminUploadFile.value = '';
                return;
            }
            if (file.size > 5 * 1024 * 1024) {
                adminUploadMsg.textContent = '✗ File too large. Max 5 MB.';
                adminUploadMsg.style.color = '#b71c1c';
                adminUploadFile.value = '';
                return;
            }
            adminUploadMsg.textContent = '';
            const reader = new FileReader();
            reader.onload = e => {
                adminUploadPreview.src = e.target.result;
                adminUploadPreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
            adminUploadSave.disabled = false;
        }

        adminUploadSave.addEventListener('click', async () => {
            const id = adminUploadSave.getAttribute('data-id');
            if (!id || !adminUploadFile.files[0]) return;

            const formData = new FormData();
            formData.append('file', adminUploadFile.files[0]);

            adminUploadSave.disabled = true;
            adminUploadMsg.textContent = 'Uploading…';
            adminUploadMsg.style.color = '#666';

            try {
                const res = await fetch('/admin/restaurants/' + encodeURIComponent(id) + '/upload-image', {
                    method: 'POST',
                    body: formData
                });
                const data = await res.json().catch(() => ({}));
                if (res.ok) {
                    adminUploadMsg.textContent = '✓ Image uploaded successfully!';
                    adminUploadMsg.style.color = '#2e7d32';
                    setTimeout(() => { uploadBackdrop.style.display = 'none'; window.location.reload(); }, 1200);
                } else {
                    adminUploadMsg.textContent = '✗ ' + (data.error || data.message || 'Upload failed');
                    adminUploadMsg.style.color = '#b71c1c';
                    adminUploadSave.disabled = false;
                }
            } catch (e) {
                adminUploadMsg.textContent = '✗ Network error: ' + e;
                adminUploadMsg.style.color = '#b71c1c';
                adminUploadSave.disabled = false;
            }
        });

        console.log('[DEBUG] [ADMIN_DASHBOARD] Script fully loaded and all event listeners attached!');
    </script>
</body>
</html>
"""


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
    """Public homepage - show dashboard layout without requiring login."""
    restaurants: list[Any] = []
    try:
        resp = requests.get(restaurants_url(), timeout=5)
        if resp.ok:
            data = resp.json()
            restaurants = data if isinstance(data, list) else data.get("data", [])
    except (requests.RequestException, ValueError):
        pass

    return render_template(
        "user_dashboard.html",
        username=session.get("user_username", "Guest"),
        restaurants=restaurants,
        backend_url=BACKEND_BASE_URL,
        is_guest=not bool(session.get("user_token")),
        admin_view_as_user=bool(session.get("admin_view_as_user")),
        admin_username=session.get("admin_username", ""),
    )

@app.get("/login")
def login_selector():
    """Login selection page (User / Owner / Admin)."""
    return render_template("landing.html")

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


@app.put("/api/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>")
def update_menu_item_proxy(restaurant_id: int, menu_item_id: int) -> tuple[dict[str, Any], int]:
    payload = request.get_json(silent=True) or {}
    token = session.get("owner_token") or session.get("admin_token") or request.headers.get("Authorization")
    headers = {"Authorization": token, "Content-Type": "application/json"} if token else {"Content-Type": "application/json"}
    try:
        response = requests.put(
            f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants/{restaurant_id}/menu/{menu_item_id}",
            json=payload,
            headers=headers,
            timeout=8,
        )
        try:
            body = response.json() if response.content else {}
        except ValueError:
            body = {"error": response.text}
        return body, response.status_code
    except requests.RequestException as exc:
        return _error_payload("Couldn't reach backend to update menu item", str(exc)), 502


@app.delete("/api/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>")
def delete_menu_item_proxy(restaurant_id: int, menu_item_id: int) -> tuple[dict[str, Any], int]:
    token = session.get("owner_token") or session.get("admin_token") or request.headers.get("Authorization")
    headers = {"Authorization": token} if token else {}
    try:
        response = requests.delete(
            f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants/{restaurant_id}/menu/{menu_item_id}",
            headers=headers,
            timeout=8,
        )
        try:
            body = response.json() if response.content else {}
        except ValueError:
            body = {"error": response.text}
        return body, response.status_code
    except requests.RequestException as exc:
        return _error_payload("Couldn't reach backend to delete menu item", str(exc)), 502


@app.post("/api/restaurants/<int:restaurant_id>/menu/<int:menu_item_id>/upload-image")
def upload_menu_item_image_proxy(restaurant_id: int, menu_item_id: int) -> tuple[dict[str, Any], int]:
    token = session.get("owner_token") or session.get("admin_token") or request.headers.get("Authorization")
    uploaded_file = request.files.get("file")
    if not uploaded_file or not uploaded_file.filename:
        return {"error": "No image file selected."}, 400

    headers = {"Authorization": token} if token else {}
    try:
        response = requests.post(
            f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants/{restaurant_id}/menu/{menu_item_id}/upload-image",
            headers=headers,
            files={"file": (uploaded_file.filename, uploaded_file.stream, uploaded_file.content_type)},
            timeout=12,
        )
        try:
            body = response.json() if response.content else {}
        except ValueError:
            body = {"error": response.text}
        return body, response.status_code
    except requests.RequestException as exc:
        return _error_payload("Couldn't reach backend to upload menu item image", str(exc)), 502


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


def reviews_url() -> str:
    return f"{BACKEND_BASE_URL.rstrip('/')}/api/reviews"


def yelp_reviews_url() -> str:
    return f"{BACKEND_BASE_URL.rstrip('/')}/api/yelp/reviews"


def admin_user_view_reviews_url() -> str:
    return f"{BACKEND_BASE_URL.rstrip('/')}/api/reviews/admin/user-view"


def admin_reviews_url() -> str:
    return f"{BACKEND_BASE_URL.rstrip('/')}/api/admin/reviews"


@app.put("/admin/reviews/<int:review_id>/approve")
def admin_approve_review(review_id: int):
    """Approve a pending review (admin only)."""
    if not session.get("admin_token"):
        return {"error": "Not authenticated"}, 401
    token = session["admin_token"]
    headers = {"Authorization": token}
    try:
        resp = requests.put(
            f"{admin_reviews_url()}/{review_id}/approve", headers=headers, timeout=5
        )
        try:
            body = resp.json() if resp.content else {}
        except ValueError:
            body = {"message": resp.text}
        return jsonify(body), resp.status_code
    except requests.RequestException:
        return jsonify({"error": "Could not reach backend to approve review."}), 502


@app.put("/admin/reviews/<int:review_id>/reject")
def admin_reject_review(review_id: int):
    """Reject a pending review (admin only)."""
    if not session.get("admin_token"):
        return {"error": "Not authenticated"}, 401
    token = session["admin_token"]
    headers = {"Authorization": token}
    try:
        resp = requests.put(
            f"{admin_reviews_url()}/{review_id}/reject", headers=headers, timeout=5
        )
        try:
            body = resp.json() if resp.content else {}
        except ValueError:
            body = {"message": resp.text}
        return jsonify(body), resp.status_code
    except requests.RequestException:
        return jsonify({"error": "Could not reach backend to reject review."}), 502


@app.get("/api/reviews/restaurant/<int:restaurant_id>")
def get_reviews_for_restaurant(restaurant_id: int) -> tuple[dict[str, Any], int]:
    headers: dict[str, str] = {}
    token = session.get("user_token") or request.headers.get("Authorization")
    if token:
        headers["Authorization"] = token
    try:
        response = requests.get(
            f"{reviews_url()}/restaurant/{restaurant_id}",
            headers=headers,
            timeout=5,
        )
        body = response.json() if response.content else []
        if response.ok:
            return {"ok": True, "data": body}, 200
        return {
            "ok": False,
            "message": body.get("error") if isinstance(body, dict) else "Failed to load reviews",
        }, response.status_code
    except requests.RequestException as exc:
        return _error_payload("Couldn't reach backend to load reviews", str(exc)), 502


@app.get("/api/yelp/reviews/restaurant/<int:restaurant_id>")
def get_yelp_reviews_for_restaurant(restaurant_id: int) -> tuple[dict[str, Any], int]:
    try:
        response = requests.get(
            f"{yelp_reviews_url()}/restaurant/{restaurant_id}",
            timeout=8,
        )
        body = response.json() if response.content else []
        if response.ok:
            return {"ok": True, "data": body}, 200
        # Yelp review-text can be unavailable for some business references.
        # Return an empty list so the UI can fall back to Yelp summary metadata.
        return {"ok": True, "data": [], "yelpUnavailable": True}, 200
    except requests.RequestException as exc:
        # Degrade gracefully to keep restaurant detail panel usable.
        return {"ok": True, "data": [], "yelpUnavailable": True}, 200


@app.post("/api/reviews")
def create_review() -> tuple[dict[str, Any], int]:
    payload = request.get_json(silent=True) or {}
    headers: dict[str, str] = {}

    in_admin_user_view_mode = bool(session.get("admin_view_as_user"))
    target_url = reviews_url()

    # In admin "view as user" mode, use a dedicated backend endpoint that
    # verifies admin privileges and safely impersonates a regular user account.
    if in_admin_user_view_mode:
        token = session.get("admin_token")
        target_url = admin_user_view_reviews_url()
    else:
        # Prefer the server-side session token so the client never needs to
        # handle the raw token value.
        token = session.get("user_token") or request.headers.get("Authorization")

    if token:
        headers["Authorization"] = token

    try:
        uploaded_images = request.files.getlist("images")

        has_form_payload = bool(request.form.get("restaurantId") or request.form.get("rating") or request.form.get("comment"))

        if uploaded_images or has_form_payload:
            form_data = {
                "restaurantId": request.form.get("restaurantId", ""),
                "rating": request.form.get("rating", ""),
                "comment": request.form.get("comment", ""),
            }
            files = [
                (
                    "images",
                    (
                        image.filename,
                        image.stream,
                        image.content_type or "application/octet-stream",
                    ),
                )
                for image in uploaded_images
                if image and image.filename
            ]
            response = requests.post(
                target_url,
                data=form_data,
                files=files,
                headers=headers,
                timeout=15,
            )
        else:
            headers["Content-Type"] = "application/json"
            response = requests.post(target_url, json=payload, headers=headers, timeout=5)
        body = response.json() if response.content else {}
        return {"ok": response.ok, "data": body}, response.status_code
    except requests.RequestException as exc:
        return _error_payload("Couldn't reach backend to create review", str(exc)), 502


# ---------------------------------------------------------------------------
# User routes
# ---------------------------------------------------------------------------

@app.get("/user")
def user_view():
    """User view landing - choose Register or Login."""
    return render_template("user_view.html")


@app.route("/user/register", methods=["GET", "POST"])
def user_register():
    """User registration page and handler."""
    if request.method == "GET":
        return render_template("register.html", error=None, success=None)

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        return render_template(
            "register.html", error="Username and password are required.", success=None
        )

    try:
        response = requests.post(
            f"{BACKEND_BASE_URL.rstrip('/')}/api/users/register",
            json={"username": username, "password": password, "role": "USER"},
            timeout=5,
        )

        if response.status_code == 201:
            # Attempt automatic login after successful registration
            try:
                login_resp = requests.post(
                    auth_url("/login"),
                    json={"username": username, "password": password},
                    timeout=5,
                )
                if login_resp.ok:
                    body = login_resp.json()
                    token = (
                        body.get("token")
                        or body.get("accessToken")
                        or body.get("jwt")
                        or ""
                    )
                    session["user_token"] = token
                    session["user_username"] = username
                    session["user_role"] = "USER"
                    return redirect(url_for("user_dashboard"))
            except requests.RequestException:
                pass
            # Auto-login failed; send user to login page
            return render_template(
                "register.html",
                error=None,
                success="Account created! Please sign in.",
            )

        elif response.status_code == 400:
            try:
                error_message = response.json().get("error", "Failed to create account.")
            except ValueError:
                error_message = "Failed to create account."
            return render_template("register.html", error=error_message, success=None)

        else:
            return render_template(
                "register.html",
                error="Failed to create account. Please try again.",
                success=None,
            )

    except requests.RequestException:
        return render_template(
            "register.html",
            error="Could not connect to the server. Please try again.",
            success=None,
        )


@app.route("/user/login", methods=["GET", "POST"])
def user_login():
    """User login page and handler."""
    if request.method == "GET":
        return render_template("user_login.html", error=None)

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        return render_template(
            "user_login.html", error="Please enter username and password."
        )

    try:
        resp = requests.post(
            auth_url("/login"),
            json={"username": username, "password": password},
            timeout=5,
        )

        if not resp.ok:
            try:
                msg = resp.json().get("message") or resp.json().get("error", "Invalid credentials.")
            except ValueError:
                msg = "Invalid credentials."
            return render_template("user_login.html", error=msg)

        body = resp.json()
        token = (
            body.get("token")
            or body.get("accessToken")
            or body.get("jwt")
            or ""
        )
        session["user_token"] = token
        session["user_username"] = username
        session["user_role"] = (
            body.get("role")
            or body.get("userRole")
            or (body.get("user", {}) or {}).get("role")
            or "USER"
        )
        return redirect(url_for("user_dashboard"))

    except requests.RequestException:
        return render_template(
            "user_login.html",
            error="Could not reach authentication service. Please try again.",
        )


@app.get("/user/logout")
def user_logout():
    """Clear user session and redirect to user view."""
    token = session.get("user_token")
    if token:
        try:
            requests.post(
                auth_url("/logout"),
                headers={"Authorization": token},
                timeout=5,
            )
        except requests.RequestException:
            pass
    session.pop("user_token", None)
    session.pop("user_username", None)
    session.pop("user_role", None)
    return redirect(url_for("user_view"))


@app.get("/user/dashboard")
def user_dashboard():
    """User dashboard - restaurant list + review submission."""
    in_admin_user_view_mode = bool(session.get("admin_view_as_user"))
    if not session.get("user_token") and not in_admin_user_view_mode:
        return redirect(url_for("user_login"))

    restaurants: list[Any] = []
    try:
        resp = requests.get(restaurants_url(), timeout=5)
        if resp.ok:
            data = resp.json()
            restaurants = data if isinstance(data, list) else data.get("data", [])
    except (requests.RequestException, ValueError):
        pass

    return render_template(
        "user_dashboard.html",
        username=(
            session.get("user_username")
            or (session.get("admin_username") if in_admin_user_view_mode else None)
            or "User"
        ),
        restaurants=restaurants,
        backend_url=BACKEND_BASE_URL,
        is_guest=False,
        admin_view_as_user=in_admin_user_view_mode,
        admin_username=session.get("admin_username", ""),
    )

# ---------------------------------------------------------------------------
# Admin routes
# ---------------------------------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    """Admin login page and handler."""
    if request.method == "GET":
        # If already logged in as admin, go straight to dashboard
        if session.get("admin_token"):
            return redirect(url_for("admin_dashboard"))
        return render_template_string(ADMIN_LOGIN_TEMPLATE, error=None)

    # POST – attempt login via backend
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        return render_template_string(
            ADMIN_LOGIN_TEMPLATE, error="Please enter both username and password."
        )

    try:
        resp = requests.post(
            auth_url("/login"),
            json={"username": username, "password": password},
            timeout=5,
        )

        if not resp.ok:
            try:
                msg = resp.json().get("message") or resp.json().get("error", "Invalid credentials.")
            except ValueError:
                msg = "Invalid credentials."
            return render_template_string(ADMIN_LOGIN_TEMPLATE, error=msg)

        body = resp.json()

        # Check admin role – backend may return role in different fields
        role = (
            body.get("role")
            or body.get("userRole")
            or (body.get("user", {}) or {}).get("role")
            or ""
        )
        if role.upper() != "ADMIN":
            return render_template_string(
                ADMIN_LOGIN_TEMPLATE, error="Access denied. Admin privileges required."
            )

        # Extract token from backend response
        token = (
            body.get("token")
            or body.get("accessToken")
            or body.get("jwt")
            or ""
        )

        # Store admin session data
        session["admin_token"] = token
        session["admin_username"] = username
        session["admin_role"] = "ADMIN"

        return redirect(url_for("admin_dashboard"))

    except requests.RequestException:
        return render_template_string(
            ADMIN_LOGIN_TEMPLATE, error="Could not reach authentication service. Please try again."
        )


@app.get("/admin/dashboard")
def admin_dashboard():
    """Admin dashboard showing database tables."""
    if not session.get("admin_token"):
        return redirect(url_for("admin_login"))

    token = session["admin_token"]
    # Backend expects the raw token string (not a 'Bearer ' prefix)
    headers = {"Authorization": token}

    # Fetch data for dashboard tables – gracefully handle failures
    users = []
    restaurants = []
    reviews = []
    pending_reviews = []
    menu_items = []

    try:
        resp = requests.get(
            f"{BACKEND_BASE_URL.rstrip('/')}/api/users", headers=headers, timeout=5
        )
        if resp.ok:
            data = resp.json()
            users = data if isinstance(data, list) else data.get("data", [])
    except (requests.RequestException, ValueError):
        pass

    try:
        resp = requests.get(restaurants_url(), headers=headers, timeout=5)
        if resp.ok:
            data = resp.json()
            restaurants = data if isinstance(data, list) else data.get("data", [])
    except (requests.RequestException, ValueError):
        pass

    try:
        resp = requests.get(
            f"{BACKEND_BASE_URL.rstrip('/')}/api/reviews", headers=headers, timeout=5
        )
        if resp.ok:
            data = resp.json()
            reviews = data if isinstance(data, list) else data.get("data", [])
    except (requests.RequestException, ValueError):
        pass

    try:
        resp = requests.get(
            f"{admin_reviews_url()}/pending", headers=headers, timeout=5
        )
        if resp.ok:
            data = resp.json()
            pending_reviews = data if isinstance(data, list) else data.get("data", [])
    except (requests.RequestException, ValueError):
        pass

    for restaurant in restaurants:
        if not isinstance(restaurant, dict):
            continue

        restaurant_name = restaurant.get("name") or f"Restaurant #{restaurant.get('id', 'Unknown')}"
        raw_menu_items = restaurant.get("menuItems") or restaurant.get("menu_items") or []

        if isinstance(raw_menu_items, list) and raw_menu_items:
            for item in raw_menu_items:
                if not isinstance(item, dict):
                    continue

                raw_price = item.get("price")
                if raw_price in (None, ""):
                    price_text = "-"
                else:
                    try:
                        price_text = f"${float(raw_price):.2f}"
                    except (TypeError, ValueError):
                        price_text = str(raw_price)

                menu_items.append(
                    {
                        "id": item.get("id") or "",
                        "restaurant_id": restaurant.get("id") or "",
                        "restaurant_name": restaurant_name,
                        "name": item.get("itemName") or item.get("name") or "Unnamed item",
                        "price": price_text,
                        "description": item.get("description") or "",
                        "imageUrl": item.get("imageUrl") or "",
                    }
                )
            continue

        menu_names = restaurant.get("menuItemNames") or restaurant.get("menu_item_names") or []
        if isinstance(menu_names, list):
            for name in menu_names:
                if not name:
                    continue
                menu_items.append(
                    {
                        "restaurant_name": restaurant_name,
                        "name": str(name),
                        "price": "-",
                        "description": "",
                    }
                )

    return render_template_string(
        ADMIN_DASHBOARD_TEMPLATE,
        admin_username=session.get("admin_username", "Admin"),
        users=users,
        restaurants=restaurants,
        menu_items=menu_items,
        reviews=reviews,
        pending_reviews=pending_reviews,
        backend_url=BACKEND_BASE_URL,
        admin_user_view_active=bool(session.get("admin_view_as_user")),
        admin_owner_view_active=bool(session.get("admin_view_as_owner")),
    )


def _clear_admin_owner_view_state() -> None:
    """Clear temporary admin owner-view mode state."""
    session.pop("admin_view_as_owner", None)
    session.pop("admin_owner_view_restaurant_id", None)


def _restore_admin_user_view_state() -> None:
    """Restore session state after admin user-view mode ends."""
    was_user_view = bool(session.pop("admin_view_as_user", False))
    had_user_session = bool(session.pop("admin_had_user_session", False))

    if was_user_view and had_user_session:
        previous_token = session.pop("admin_prev_user_token", "")
        previous_username = session.pop("admin_prev_user_username", "")
        previous_role = session.pop("admin_prev_user_role", "USER")

        if previous_token:
            session["user_token"] = previous_token
        else:
            session.pop("user_token", None)

        if previous_username:
            session["user_username"] = previous_username
        else:
            session.pop("user_username", None)

        if previous_role:
            session["user_role"] = previous_role
        else:
            session.pop("user_role", None)
    else:
        session.pop("admin_prev_user_token", None)
        session.pop("admin_prev_user_username", None)
        session.pop("admin_prev_user_role", None)
        session.pop("user_token", None)
        session.pop("user_username", None)
        session.pop("user_role", None)


@app.get("/admin/view-as-user")
def admin_view_as_user():
    """Temporarily switch an admin into user-view mode for review testing."""
    if not session.get("admin_token"):
        return redirect(url_for("admin_login"))

    _clear_admin_owner_view_state()

    if not session.get("admin_view_as_user"):
        had_user_session = bool(session.get("user_token"))
        session["admin_had_user_session"] = had_user_session
        if had_user_session:
            session["admin_prev_user_token"] = session.get("user_token", "")
            session["admin_prev_user_username"] = session.get("user_username", "")
            session["admin_prev_user_role"] = session.get("user_role", "USER")

    session["admin_view_as_user"] = True

    return redirect(url_for("user_dashboard"))


@app.get("/admin/exit-user-view")
def admin_exit_user_view():
    """Exit admin user-view mode and return to the admin dashboard."""
    if not session.get("admin_token"):
        return redirect(url_for("admin_login"))

    _restore_admin_user_view_state()

    return redirect(url_for("admin_dashboard"))


@app.get("/admin/view-as-owner")
def admin_view_as_owner():
    """Temporarily switch an admin into owner-view mode for management testing."""
    if not session.get("admin_token"):
        return redirect(url_for("admin_login"))

    _restore_admin_user_view_state()
    session["admin_view_as_owner"] = True

    return redirect(url_for("owner_dashboard"))


@app.get("/admin/exit-owner-view")
def admin_exit_owner_view():
    """Exit admin owner-view mode and return to the admin dashboard."""
    if not session.get("admin_token"):
        return redirect(url_for("admin_login"))

    _clear_admin_owner_view_state()

    return redirect(url_for("admin_dashboard"))


@app.post("/admin/restaurants")
def admin_add_restaurant():
    """Handle admin create-restaurant requests from the dashboard UI."""
    if not session.get("admin_token"):
        return redirect(url_for("admin_login"))

    payload = request.get_json(silent=True) or {}
    token = session.get("admin_token")
    headers = {"Authorization": token} if token else {}

    try:
        resp = requests.post(
            f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants",
            json=payload,
            headers=headers,
            timeout=5,
        )

        # Forward backend response as JSON to the AJAX caller so the
        # frontend can react without receiving full HTML pages.
        try:
            body = resp.json() if resp.content else {}
        except ValueError:
            body = {"message": resp.text}

        if resp.ok:
            return jsonify(body), resp.status_code

        # Non-OK from backend -> return error JSON with status code
        msg = body.get("error") or body.get("message") or str(body)
        return jsonify({"error": msg}), resp.status_code

    except requests.RequestException:
        msg = "Could not reach backend to create restaurant."

    # On error, re-fetch dashboard data and render with an error message.
    users = []
    restaurants = []
    reviews = []
    try:
        r = requests.get(f"{BACKEND_BASE_URL.rstrip('/')}/api/users", headers=headers, timeout=5)
        if r.ok:
            data = r.json()
            users = data if isinstance(data, list) else data.get("data", [])
    except Exception:
        pass

    try:
        r = requests.get(restaurants_url(), headers=headers, timeout=5)
        if r.ok:
            data = r.json()
            restaurants = data if isinstance(data, list) else data.get("data", [])
    except Exception:
        pass

    try:
        r = requests.get(f"{BACKEND_BASE_URL.rstrip('/')}/api/reviews", headers=headers, timeout=5)
        if r.ok:
            data = r.json()
            reviews = data if isinstance(data, list) else data.get("data", [])
    except Exception:
        pass

    return render_template_string(
        ADMIN_DASHBOARD_TEMPLATE,
        admin_username=session.get("admin_username", "Admin"),
        users=users,
        restaurants=restaurants,
        reviews=reviews,
        pending_reviews=[],
        error=msg,
        backend_url=BACKEND_BASE_URL,
        admin_user_view_active=bool(session.get("admin_view_as_user")),
        admin_owner_view_active=bool(session.get("admin_view_as_owner")),
    )


@app.delete("/admin/restaurants/<int:rid>")
def admin_delete_restaurant(rid: int) -> tuple[dict[str, Any], int]:
    """Proxy DELETE /admin/restaurants/<id> to backend, using stored admin session token."""
    if not session.get("admin_token"):
        return {"error": "Not authenticated"}, 401

    token = session.get("admin_token")
    headers = {"Authorization": token} if token else {}
    try:
        resp = requests.delete(f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants/{rid}", headers=headers, timeout=5)
        try:
            body = resp.json() if resp.content else {}
        except ValueError:
            body = {"message": resp.text}

        if resp.ok:
            return body, resp.status_code
        return {"error": body.get("error") or body.get("message") or str(body)}, resp.status_code
    except requests.RequestException as exc:
        return _error_payload("Couldn't reach backend to delete restaurant", str(exc)), 502


@app.put("/admin/restaurants/<int:rid>")
def admin_update_restaurant(rid: int) -> tuple[dict[str, Any], int]:
    """Proxy PUT /admin/restaurants/<id> to backend, using stored admin session token."""
    if not session.get("admin_token"):
        return {"error": "Not authenticated"}, 401

    payload = request.get_json(silent=True) or {}
    token = session.get("admin_token")
    headers = {"Authorization": token, "Content-Type": "application/json"} if token else {"Content-Type": "application/json"}
    try:
        resp = requests.put(f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants/{rid}", json=payload, headers=headers, timeout=5)
        try:
            body = resp.json() if resp.content else {}
        except ValueError:
            body = {"message": resp.text}

        if resp.ok:
            return body, resp.status_code
        return {"error": body.get("error") or body.get("message") or str(body)}, resp.status_code
    except requests.RequestException as exc:
        return _error_payload("Couldn't reach backend to update restaurant", str(exc)), 502


@app.post("/admin/import-yelp-restaurants")
def admin_import_yelp() -> tuple[dict[str, Any], int]:
    """Proxy POST /admin/import-yelp-restaurants to backend Yelp import endpoint."""
    if not session.get("admin_token"):
        return {"error": "Not authenticated"}, 401

    data = request.get_json(silent=True) or {}
    location = data.get("location", "Toronto")
    limit = int(data.get("limit", 20))

    token = session.get("admin_token")
    headers = {"Authorization": token} if token else {}
    try:
        url = (f"{BACKEND_BASE_URL.rstrip('/')}/api/admin/import-yelp-restaurants"
               f"?location={requests.utils.quote(location)}&limit={limit}")
        resp = requests.post(url, headers=headers, timeout=15)
        try:
            body = resp.json() if resp.content else {}
        except ValueError:
            body = {"message": resp.text}
        if resp.ok:
            return body, resp.status_code
        return {"error": body.get("error") or body.get("message") or str(body)}, resp.status_code
    except requests.RequestException as exc:
        return _error_payload("Couldn't reach backend for Yelp import", str(exc)), 502


@app.post("/admin/restaurants/<int:rid>/upload-image")
def admin_upload_restaurant_image(rid: int) -> tuple[dict[str, Any], int]:
    """Proxy image upload for a restaurant from admin dashboard."""
    print(f"DEBUG: Upload handler called for restaurant {rid}")
    print(f"DEBUG: Content-Length: {request.content_length}")
    print(f"DEBUG: Files in request: {list(request.files.keys())}")

    if not session.get("admin_token"):
        return {"error": "Not authenticated"}, 401

    token = session.get("admin_token")
    uploaded_file = request.files.get("file")
    if not uploaded_file or not uploaded_file.filename:
        return {"error": "No image file provided"}, 400

    try:
        resp = requests.post(
            f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants/{rid}/upload-image",
            headers={"Authorization": token},
            files={"file": (uploaded_file.filename, uploaded_file.stream, uploaded_file.content_type)},
            timeout=10,
        )
        try:
            body = resp.json() if resp.content else {}
        except ValueError:
            body = {"message": resp.text}
        if resp.ok:
            return body, resp.status_code
        return {"error": body.get("error") or body.get("message") or str(body)}, resp.status_code
    except requests.RequestException as exc:
        return _error_payload("Couldn't reach backend to upload image", str(exc)), 502


@app.get("/admin/logout")
def admin_logout():
    """Clear admin session and redirect to login page."""
    token = session.get("admin_token")
    if token:
        try:
            requests.post(
                auth_url("/logout"),
                headers={"Authorization": token},
                timeout=5,
            )
        except requests.RequestException:
            pass

    session.pop("admin_token", None)
    session.pop("admin_username", None)
    session.pop("admin_role", None)
    session.pop("admin_view_as_user", None)
    session.pop("admin_view_as_owner", None)
    session.pop("admin_owner_view_restaurant_id", None)
    session.pop("admin_had_user_session", None)
    session.pop("admin_prev_user_token", None)
    session.pop("admin_prev_user_username", None)
    session.pop("admin_prev_user_role", None)
    return redirect(url_for("admin_login"))


def _resolve_owner_auth_token() -> str | None:
    """Resolve which token should be used for owner-area actions."""
    owner_token = session.get("owner_token")
    if owner_token:
        return owner_token

    if session.get("admin_view_as_owner") and session.get("admin_token"):
        return session.get("admin_token")

    return None


def _render_owner_dashboard(*, restaurant: Any, reviews: list[Any], error: str | None = None, success: str | None = None):
    """Render owner dashboard with consistent mode context."""
    in_admin_owner_view_mode = bool(session.get("admin_view_as_owner") and session.get("admin_token"))
    owner_name = (
        session.get("admin_username") if in_admin_owner_view_mode else session.get("owner_username")
    ) or ("Admin" if in_admin_owner_view_mode else "Owner")

    return render_template(
        "owner_dashboard.html",
        owner_username=owner_name,
        restaurant=restaurant,
        reviews=reviews,
        error=error,
        success=success,
        backend_url=BACKEND_BASE_URL,
        admin_view_as_owner=in_admin_owner_view_mode,
    )


# ---------------------------------------------------------------------------
# Owner routes
# ---------------------------------------------------------------------------

@app.get("/owner")
def owner_view():
    """Owner view landing - choose Register or Login."""
    if session.get("owner_token"):
        return redirect(url_for("owner_dashboard"))
    return render_template("owner_view.html")


@app.route("/owner/register", methods=["GET", "POST"])
def owner_register():
    """Owner registration page and handler."""
    if request.method == "GET":
        if session.get("owner_token"):
            return redirect(url_for("owner_dashboard"))
        return render_template("owner_register.html", error=None, success=None)

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        return render_template(
            "owner_register.html", error="Username and password are required.", success=None
        )

    try:
        response = requests.post(
            f"{BACKEND_BASE_URL.rstrip('/')}/api/users/register",
            json={"username": username, "password": password, "role": "OWNER"},
            timeout=5,
        )

        if response.status_code == 201:
            # Attempt automatic login after successful registration
            try:
                login_resp = requests.post(
                    auth_url("/login"),
                    json={"username": username, "password": password},
                    timeout=5,
                )
                if login_resp.ok:
                    body = login_resp.json()
                    role = (
                        body.get("role")
                        or body.get("userRole")
                        or (body.get("user", {}) or {}).get("role")
                        or ""
                    )
                    if role.upper() != "OWNER":
                        return render_template(
                            "owner_register.html",
                            error="Account created but owner sign-in failed. Please use Owner Sign In.",
                            success=None,
                        )
                    token = (
                        body.get("token")
                        or body.get("accessToken")
                        or body.get("jwt")
                        or ""
                    )
                    session["owner_token"] = token
                    session["owner_username"] = username
                    session["owner_role"] = "OWNER"
                    return redirect(url_for("owner_dashboard"))
            except requests.RequestException:
                pass
            return render_template(
                "owner_register.html",
                error=None,
                success="Account created! Please sign in.",
            )

        elif response.status_code == 400:
            try:
                error_message = response.json().get("error", "Failed to create account.")
            except ValueError:
                error_message = "Failed to create account."
            return render_template("owner_register.html", error=error_message, success=None)

        else:
            return render_template(
                "owner_register.html",
                error="Failed to create account. Please try again.",
                success=None,
            )

    except requests.RequestException:
        return render_template(
            "owner_register.html",
            error="Could not connect to the server. Please try again.",
            success=None,
        )


@app.route("/owner/login", methods=["GET", "POST"])
def owner_login():
    """Owner login page and handler."""
    if request.method == "GET":
        if session.get("owner_token"):
            return redirect(url_for("owner_dashboard"))
        return render_template("owner_login.html", error=None)

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        return render_template("owner_login.html", error="Please enter username and password.")

    try:
        resp = requests.post(
            auth_url("/login"),
            json={"username": username, "password": password},
            timeout=5,
        )

        if not resp.ok:
            try:
                msg = resp.json().get("message") or resp.json().get("error", "Invalid credentials.")
            except ValueError:
                msg = "Invalid credentials."
            return render_template("owner_login.html", error=msg)

        body = resp.json()
        role = (
            body.get("role")
            or body.get("userRole")
            or (body.get("user", {}) or {}).get("role")
            or ""
        )
        if role.upper() != "OWNER":
            return render_template(
                "owner_login.html", error="Access denied. Owner account required."
            )

        token = (
            body.get("token")
            or body.get("accessToken")
            or body.get("jwt")
            or ""
        )
        session["owner_token"] = token
        session["owner_username"] = username
        session["owner_role"] = role.upper() or "OWNER"
        return redirect(url_for("owner_dashboard"))

    except requests.RequestException:
        return render_template(
            "owner_login.html",
            error="Could not reach authentication service. Please try again.",
        )


@app.get("/owner/logout")
def owner_logout():
    """Clear owner session and redirect to owner view."""
    if session.get("admin_view_as_owner") and session.get("admin_token"):
        _clear_admin_owner_view_state()
        return redirect(url_for("admin_dashboard"))

    token = session.get("owner_token")
    if token:
        try:
            requests.post(
                auth_url("/logout"),
                headers={"Authorization": token},
                timeout=5,
            )
        except requests.RequestException:
            pass
    session.pop("owner_token", None)
    session.pop("owner_username", None)
    session.pop("owner_role", None)
    return redirect(url_for("owner_view"))


@app.get("/owner/dashboard")
def owner_dashboard():
    """Owner dashboard - show their restaurant and its reviews."""
    token = _resolve_owner_auth_token()
    if not token:
        return redirect(url_for("owner_login"))

    restaurant, reviews = _fetch_owner_restaurant_and_reviews(token)

    return _render_owner_dashboard(restaurant=restaurant, reviews=reviews)


@app.post("/owner/restaurant/create")
def owner_create_restaurant():
    """Handle owner restaurant creation from dashboard form."""
    token = _resolve_owner_auth_token()
    if not token:
        return redirect(url_for("owner_login"))

    headers = {"Authorization": token, "Content-Type": "application/json"}

    name = request.form.get("name", "").strip()
    cuisine = request.form.get("cuisine", "").strip()
    location = request.form.get("location", "").strip()
    dietary_tags = request.form.get("dietary_tags", "").strip()
    description = request.form.get("description", "").strip()
    latitude_raw = request.form.get("latitude", "").strip()
    longitude_raw = request.form.get("longitude", "").strip()

    if not name or not cuisine or not location:
        return _render_owner_dashboard(
            restaurant=None,
            reviews=[],
            error="Name, cuisine, and location are required.",
        )

    payload = {
        "name": name,
        "cuisine": cuisine,
        "location": location,
        "dietaryTags": dietary_tags or None,
        "description": description or None,
    }
    if latitude_raw:
        try:
            payload["latitude"] = float(latitude_raw)
        except ValueError:
            pass  # Input type="number" prevents non-numeric values; skip silently if bypassed
    if longitude_raw:
        try:
            payload["longitude"] = float(longitude_raw)
        except ValueError:
            pass  # Input type="number" prevents non-numeric values; skip silently if bypassed

    try:
        resp = requests.post(
            f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants",
            json=payload,
            headers=headers,
            timeout=5,
        )
        if resp.ok:
            if session.get("admin_view_as_owner"):
                try:
                    created = resp.json() if resp.content else {}
                except ValueError:
                    created = {}
                created_id = created.get("id") if isinstance(created, dict) else None
                if created_id is not None:
                    try:
                        session["admin_owner_view_restaurant_id"] = int(created_id)
                    except (TypeError, ValueError):
                        pass
            return redirect(url_for("owner_dashboard"))
        try:
            msg = resp.json().get("error") or resp.json().get("message") or "Failed to create restaurant."
        except ValueError:
            msg = "Failed to create restaurant."
        return _render_owner_dashboard(restaurant=None, reviews=[], error=msg)
    except requests.RequestException:
        return _render_owner_dashboard(
            restaurant=None,
            reviews=[],
            error="Could not connect to the server. Please try again.",
        )
    
@app.post("/owner/restaurant/update")
def owner_update_restaurant():
    """Handle owner restaurant detail updates from dashboard form."""
    token = _resolve_owner_auth_token()
    if not token:
        return redirect(url_for("owner_login"))

    headers = {"Authorization": token, "Content-Type": "application/json"}

    restaurant_id = request.form.get("restaurant_id", "").strip()
    name = request.form.get("name", "").strip()
    cuisine = request.form.get("cuisine", "").strip()
    location = request.form.get("location", "").strip()
    dietary_tags = request.form.get("dietary_tags", "").strip()
    description = request.form.get("description", "").strip()
    latitude_raw = request.form.get("latitude", "").strip()
    longitude_raw = request.form.get("longitude", "").strip()

    if not restaurant_id or not name or not cuisine or not location:
        return redirect(url_for("owner_dashboard", edit="true"))

    payload = {
        "name": name,
        "cuisine": cuisine,
        "location": location,
        "dietaryTags": dietary_tags or None,
        "description": description or None,
    }
    if latitude_raw:
        try:
            payload["latitude"] = float(latitude_raw)
        except ValueError:
            pass  # Input type="number" prevents non-numeric values; skip silently if bypassed
    if longitude_raw:
        try:
            payload["longitude"] = float(longitude_raw)
        except ValueError:
            pass  # Input type="number" prevents non-numeric values; skip silently if bypassed

    try:
        resp = requests.put(
            f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants/{restaurant_id}",
            json=payload,
            headers=headers,
            timeout=5,
        )

        if resp.ok:
            return redirect(url_for("owner_dashboard"))

        try:
            msg = resp.json().get("error") or resp.json().get("message") or "Failed to update restaurant."
        except ValueError:
            msg = "Failed to update restaurant."

        # re-fetch dashboard data so the page still renders nicely with the error
        restaurant = None
        reviews: list[Any] = []

        try:
            my_resp = requests.get(
                f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants/my",
                headers={"Authorization": token},
                timeout=5,
            )
            if my_resp.ok:
                data = my_resp.json()
                restaurant = data.get("restaurant") if isinstance(data, dict) else None
        except (requests.RequestException, ValueError):
            pass

        if restaurant and restaurant.get("id"):
            rid = restaurant["id"]
            try:
                review_resp = requests.get(
                    f"{BACKEND_BASE_URL.rstrip('/')}/api/reviews/restaurant/{rid}",
                    headers={"Authorization": token},
                    timeout=5,
                )
                if review_resp.ok:
                    data = review_resp.json()
                    reviews = data if isinstance(data, list) else []
            except (requests.RequestException, ValueError):
                pass

        return _render_owner_dashboard(restaurant=restaurant, reviews=reviews, error=msg)

    except requests.RequestException:
        return redirect(url_for("owner_dashboard", edit="true"))


@app.post("/owner/menu/add")
def owner_add_menu_item():
    """Handle owner adding a menu item to their restaurant."""
    token = _resolve_owner_auth_token()
    if not token:
        return redirect(url_for("owner_login"))

    headers = {"Authorization": token, "Content-Type": "application/json"}

    restaurant_id = request.form.get("restaurant_id", "").strip()
    item_name = request.form.get("item_name", "").strip()
    price = request.form.get("price", "").strip()
    description = request.form.get("description", "").strip()
    dietary_tags = request.form.get("dietary_tags", "").strip()

    if not restaurant_id or not item_name or not price:
        # Re-fetch restaurant and reviews to re-render the dashboard
        restaurant, reviews = _fetch_owner_restaurant_and_reviews(token)
        return _render_owner_dashboard(
            restaurant=restaurant,
            reviews=reviews,
            error="Item name and price are required.",
        )

    payload = {
        "itemName": item_name,
        "price": price,
        "description": description or None,
        "dietaryTags": dietary_tags or None,
    }

    try:
        resp = requests.post(
            f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants/{restaurant_id}/menu",
            json=payload,
            headers=headers,
            timeout=5,
        )
        if resp.ok:
            uploaded_file = request.files.get("file")
            if uploaded_file and uploaded_file.filename:
                try:
                    created_item = resp.json() if resp.content else {}
                except ValueError:
                    created_item = {}
                menu_item_id = created_item.get("id") if isinstance(created_item, dict) else None
                if menu_item_id:
                    try:
                        requests.post(
                            f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants/{restaurant_id}/menu/{menu_item_id}/upload-image",
                            headers={"Authorization": token},
                            files={"file": (uploaded_file.filename, uploaded_file.stream, uploaded_file.content_type)},
                            timeout=10,
                        )
                    except requests.RequestException:
                        pass
            return redirect(url_for("owner_dashboard"))
        try:
            msg = resp.json().get("error") or resp.json().get("message") or "Failed to add menu item."
        except ValueError:
            msg = "Failed to add menu item."
        restaurant, reviews = _fetch_owner_restaurant_and_reviews(token)
        return _render_owner_dashboard(restaurant=restaurant, reviews=reviews, error=msg)
    except requests.RequestException:
        restaurant, reviews = _fetch_owner_restaurant_and_reviews(token)
        return _render_owner_dashboard(
            restaurant=restaurant,
            reviews=reviews,
            error="Could not connect to the server. Please try again.",
        )


@app.post("/owner/restaurant/upload-image")
def owner_upload_image():
    """Handle owner uploading an image for their restaurant."""
    token = _resolve_owner_auth_token()
    if not token:
        return redirect(url_for("owner_login"))

    restaurant_id = request.form.get("restaurant_id", "").strip()

    if not restaurant_id:
        restaurant, reviews = _fetch_owner_restaurant_and_reviews(token)
        return _render_owner_dashboard(
            restaurant=restaurant,
            reviews=reviews,
            error="Restaurant ID is missing.",
        )

    uploaded_file = request.files.get("file")
    if not uploaded_file or not uploaded_file.filename:
        restaurant, reviews = _fetch_owner_restaurant_and_reviews(token)
        return _render_owner_dashboard(
            restaurant=restaurant,
            reviews=reviews,
            error="No image file selected.",
        )

    try:
        resp = requests.post(
            f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants/{restaurant_id}/upload-image",
            headers={"Authorization": token},
            files={"file": (uploaded_file.filename, uploaded_file.stream, uploaded_file.content_type)},
            timeout=10,
        )
        if resp.ok:
            return redirect(url_for("owner_dashboard"))
        try:
            resp_json = resp.json()
            msg = resp_json.get("error") or resp_json.get("message") or "Failed to upload image."
        except ValueError:
            msg = "Failed to upload image."
        restaurant, reviews = _fetch_owner_restaurant_and_reviews(token)
        return _render_owner_dashboard(restaurant=restaurant, reviews=reviews, error=msg)
    except requests.RequestException:
        restaurant, reviews = _fetch_owner_restaurant_and_reviews(token)
        return _render_owner_dashboard(
            restaurant=restaurant,
            reviews=reviews,
            error="Could not connect to the server. Please try again.",
        )


def _fetch_owner_restaurant_and_reviews(token: str):
    """Helper to fetch the owner's restaurant and its reviews."""
    headers = {"Authorization": token}
    restaurant = None
    reviews: list[Any] = []
    in_admin_owner_view_mode = bool(session.get("admin_view_as_owner") and session.get("admin_token"))

    if in_admin_owner_view_mode:
        selected_id = session.get("admin_owner_view_restaurant_id")
        if selected_id is not None:
            try:
                rid = int(selected_id)
                resp = requests.get(
                    f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants/{rid}",
                    headers=headers,
                    timeout=5,
                )
                if resp.ok:
                    data = resp.json()
                    restaurant = data if isinstance(data, dict) else None
                elif resp.status_code == 404:
                    # Selected restaurant was removed; clear stale simulation state.
                    session.pop("admin_owner_view_restaurant_id", None)
            except (requests.RequestException, ValueError, TypeError):
                pass

    if restaurant is None:
        try:
            resp = requests.get(
                f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants/my",
                headers=headers,
                timeout=5,
            )
            if resp.ok:
                data = resp.json()
                restaurant = data.get("restaurant") if isinstance(data, dict) else None
                if in_admin_owner_view_mode and restaurant and restaurant.get("id") is not None:
                    try:
                        session["admin_owner_view_restaurant_id"] = int(restaurant.get("id"))
                    except (TypeError, ValueError):
                        pass
        except (requests.RequestException, ValueError):
            pass

    if restaurant and restaurant.get("id"):
        rid = restaurant["id"]
        try:
            resp = requests.get(
                f"{BACKEND_BASE_URL.rstrip('/')}/api/reviews/restaurant/{rid}",
                headers=headers,
                timeout=5,
            )
            if resp.ok:
                data = resp.json()
                reviews = data if isinstance(data, list) else []
        except (requests.RequestException, ValueError):
            pass

    return restaurant, reviews


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
