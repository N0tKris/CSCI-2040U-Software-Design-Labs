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

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", secrets.token_hex(32))

BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8080")


# ---------------------------------------------------------------------------
# Admin login page template (inline)
# ---------------------------------------------------------------------------
ADMIN_LOGIN_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Admin Login — PlateRate</title>
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
    <title>Admin Dashboard — PlateRate</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            background: #f5f0eb;
            color: #333;
        }
        .topbar {
            background: #fff;
            border-bottom: 1px solid #e0d8d0;
            padding: 14px 28px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .topbar .brand {
            font-size: 20px;
            font-weight: 700;
            color: #b85c38;
        }
        .topbar .user-info {
            display: flex;
            align-items: center;
            gap: 16px;
            font-size: 14px;
            color: #555;
        }
        .topbar .user-info span { font-weight: 600; color: #333; }
        .btn-logout {
            padding: 6px 16px;
            background: transparent;
            border: 1px solid #ccc;
            border-radius: 6px;
            font-size: 13px;
            color: #666;
            cursor: pointer;
            text-decoration: none;
            transition: border-color 0.2s, color 0.2s;
        }
        .btn-logout:hover { border-color: #b85c38; color: #b85c38; }
        .dashboard {
            max-width: 1100px;
            margin: 28px auto;
            padding: 0 20px;
        }
        .dashboard h2 {
            font-size: 22px;
            font-weight: 700;
            margin-bottom: 20px;
            color: #333;
        }
        .section {
            background: #fff;
            border-radius: 10px;
            box-shadow: 0 2px 12px rgba(0,0,0,0.05);
            margin-bottom: 24px;
            overflow: hidden;
        }
        .section-header {
            padding: 14px 22px;
            background: #faf8f6;
            border-bottom: 1px solid #ece5de;
            font-size: 16px;
            font-weight: 600;
            color: #b85c38;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            text-align: left;
            padding: 10px 22px;
            font-size: 12px;
            text-transform: uppercase;
            color: #999;
            font-weight: 600;
            border-bottom: 1px solid #ece5de;
        }
        td {
            padding: 12px 22px;
            font-size: 14px;
            border-bottom: 1px solid #f2eeea;
            color: #444;
        }
        tr:last-child td { border-bottom: none; }
        .empty-row td {
            text-align: center;
            color: #aaa;
            padding: 24px;
            font-style: italic;
        }
        .badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-admin { background: #fce4ec; color: #c62828; }
        .badge-user  { background: #e8f5e9; color: #2e7d32; }
        .badge-owner { background: #fff3e0; color: #e65100; }
        .stars { color: #f5a623; letter-spacing: 1px; }
    </style>
</head>
<body>
    <div class="topbar">
        <div class="brand">PlateRate — Admin Dashboard</div>
        <div class="user-info">
            Logged in as <span>{{ admin_username }}</span>
            <a href="{{ url_for('admin_logout') }}" class="btn-logout">Logout</a>
        </div>
    </div>

    <div class="dashboard">
        <h2>Database Management</h2>

        <!-- Users Table -->
        <div class="section">
            <div class="section-header">Users</div>
            <table>
                <thead>
                    <tr><th>ID</th><th>Username</th><th>Role</th></tr>
                </thead>
                <tbody>
                {% if users %}
                    {% for u in users %}
                    <tr>
                        <td>{{ u.id }}</td>
                        <td>{{ u.username }}</td>
                        <td>
                            {% set role_class = {'ADMIN': 'badge-admin', 'OWNER': 'badge-owner'}.get(u.role, 'badge-user') %}
                            <span class="badge {{ role_class }}">
                                {{ u.role }}
                            </span>
                        </td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr class="empty-row"><td colspan="3">No users found</td></tr>
                {% endif %}
                </tbody>
            </table>
        </div>

        <!-- Restaurants Table -->
        <div class="section">
            <div class="section-header">Restaurants
                <span style="float:right;display:flex;gap:8px;">
                    <button id="open-yelp-modal" style="padding:6px 10px;border-radius:6px;border:1px solid #d6c2b7;background:#fff;color:#b85c38;cursor:pointer;">🔍 Import from Yelp</button>
                    <button id="open-add-modal" style="padding:6px 10px;border-radius:6px;border:1px solid #d6c2b7;background:#fff;color:#b85c38;cursor:pointer;">+ Add restaurant</button>
                </span>
            </div>
            <table>
                <thead>
                    <tr><th>ID</th><th>Name</th><th>Cuisine</th><th>Location</th><th>Dietary Tags</th><th>Actions</th></tr>
                </thead>
                <tbody>
                {% if restaurants %}
                    {% for r in restaurants %}
                    <tr>
                        <td>{{ r.id }}</td>
                        <td>{{ r.name }}</td>
                        <td>{{ r.cuisine }}</td>
                        <td>{{ r.location }}</td>
                        <td>{{ r.dietaryTags or r.dietary_tags or '—' }}</td>
                        <td>
                            <button class="admin-edit" 
                                data-id="{{ r.id }}" 
                                data-name="{{ r.name|e }}" 
                                data-cuisine="{{ r.cuisine|e }}" 
                                data-location="{{ r.location|e }}" 
                                data-dietary="{{ (r.dietaryTags or r.dietary_tags)|default('')|e }}"
                                data-description="{{ (r.description or '')|e }}"
                                style="padding:6px 10px;border-radius:6px;border:1px solid #d6c2b7;background:#fff;color:#4a4a4a;cursor:pointer;margin-right:6px;">Edit</button>
                            <button class="admin-delete" data-id="{{ r.id }}" style="padding:6px 10px;border-radius:6px;border:1px solid #e2bdb0;background:#fff;color:#b85c38;cursor:pointer;">Delete</button>
                        </td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr class="empty-row"><td colspan="6">No restaurants found</td></tr>
                {% endif %}
                </tbody>
            </table>
        </div>

        <!-- Reviews Table -->
        <div class="section">
            <div class="section-header">Reviews</div>
            <table>
                <thead>
                    <tr><th>ID</th><th>User</th><th>Restaurant</th><th>Rating</th><th>Comment</th></tr>
                </thead>
                <tbody>
                {% if reviews %}
                    {% for rv in reviews %}
                    <tr>
                        <td>{{ rv.id }}</td>
                        <td>{{ rv.username or rv.userId or rv.user_id or '—' }}</td>
                        <td>{{ rv.restaurantId or rv.restaurant_id or '—' }}</td>
                        <td class="stars">{{ '★' * rv.rating }}{{ '☆' * (5 - rv.rating) }}</td>
                        <td>{{ rv.comment or '—' }}</td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr class="empty-row"><td colspan="5">No reviews found</td></tr>
                {% endif %}
                </tbody>
            </table>
        </div>
    </div>
    
    {% if error %}
    <div style="max-width:1100px;margin:12px auto 0;padding:0 20px;color:#b71c1c">{{ error }}</div>
    {% endif %}

    <!-- Yelp Import modal -->
    <div id="yelp-import-backdrop" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.25);align-items:center;justify-content:center;padding:20px;z-index:200;">
        <div style="width:100%;max-width:420px;background:#fff;border:1px solid #e6ddd6;padding:24px;border-radius:8px;">
            <h3 style="margin:0 0 6px 0;color:#b85c38;">Import from Yelp</h3>
            <p style="margin:0 0 16px;color:#666;font-size:13px;">Fetch restaurants from Yelp Fusion API and add them to the database. Duplicates are automatically skipped.</p>
            <div style="display:grid;gap:12px;margin-bottom:16px;">
                <div>
                    <label style="font-weight:600;font-size:13px;display:block;margin-bottom:4px;">Location</label>
                    <input id="yelp_location" value="Toronto" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:6px;font-size:14px;" />
                </div>
                <div>
                    <label style="font-weight:600;font-size:13px;display:block;margin-bottom:4px;">Max results (1-50)</label>
                    <input id="yelp_limit" type="number" value="20" min="1" max="50" style="width:100%;padding:8px;border:1px solid #ccc;border-radius:6px;font-size:14px;" />
                </div>
            </div>
            <div id="yelp_msg" style="font-size:13px;min-height:18px;margin-bottom:12px;"></div>
            <div style="display:flex;gap:8px;justify-content:flex-end;">
                <button id="yelp_import_btn" style="padding:8px 16px;background:#b85c38;color:#fff;border:none;border-radius:6px;font-weight:600;cursor:pointer;">Import</button>
                <button id="yelp_cancel_btn" style="padding:8px 12px;background:#fff;border:1px solid #ccc;border-radius:6px;cursor:pointer;">Cancel</button>
            </div>
        </div>
    </div>

    <!-- Add Restaurant modal (admin dashboard) -->
    <div class="modal-backdrop" id="admin-add-backdrop" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.25);align-items:center;justify-content:center;padding:20px;">
        <div style="width:100%;max-width:600px;background:#fff;border:1px solid #e6ddd6;padding:20px;border-radius:8px;">
            <h3 style="margin:0 0 8px 0;color:#b85c38;">Add Restaurant</h3>
            <p style="margin:0 0 12px;color:#666">Enter the restaurant details below.</p>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                <div>
                    <label style="font-weight:600;font-size:13px;">Name</label>
                    <input id="admin_name" style="width:100%;padding:8px;margin-top:6px;border:1px solid #ccc" />
                </div>
                <div>
                    <label style="font-weight:600;font-size:13px;">Cuisine</label>
                    <input id="admin_cuisine" style="width:100%;padding:8px;margin-top:6px;border:1px solid #ccc" />
                </div>
                <div>
                    <label style="font-weight:600;font-size:13px;">Dietary Tags</label>
                    <input id="admin_dietary" placeholder="comma-separated" style="width:100%;padding:8px;margin-top:6px;border:1px solid #ccc" />
                </div>
                <div>
                    <label style="font-weight:600;font-size:13px;">Location</label>
                    <input id="admin_location" style="width:100%;padding:8px;margin-top:6px;border:1px solid #ccc" />
                </div>
                <div style="grid-column:1/ -1;">
                    <label style="font-weight:600;font-size:13px;">Description</label>
                    <textarea id="admin_description" style="width:100%;padding:8px;margin-top:6px;border:1px solid #ccc;min-height:80px"></textarea>
                </div>
            </div>

            <div style="margin-top:12px;display:flex;gap:8px;justify-content:flex-end;">
                <button id="admin_add_save" style="padding:8px 12px;background:#b85c38;color:#fff;border:none;border-radius:6px;">Save</button>
                <button id="admin_add_cancel" style="padding:8px 12px;background:#fff;border:1px solid #ccc;border-radius:6px;">Cancel</button>
            </div>
        </div>
    </div>

    <!-- Edit Restaurant modal (admin dashboard) -->
    <div class="modal-backdrop" id="admin-edit-backdrop" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,0.25);align-items:center;justify-content:center;padding:20px;">
        <div style="width:100%;max-width:600px;background:#fff;border:1px solid #e6ddd6;padding:20px;border-radius:8px;">
            <h3 style="margin:0 0 8px 0;color:#b85c38;">Edit Restaurant</h3>
            <p style="margin:0 0 12px;color:#666">Update the restaurant details below.</p>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                <div>
                    <label style="font-weight:600;font-size:13px;">Name</label>
                    <input id="admin_edit_name" style="width:100%;padding:8px;margin-top:6px;border:1px solid #ccc" />
                </div>
                <div>
                    <label style="font-weight:600;font-size:13px;">Cuisine</label>
                    <input id="admin_edit_cuisine" style="width:100%;padding:8px;margin-top:6px;border:1px solid #ccc" />
                </div>
                <div>
                    <label style="font-weight:600;font-size:13px;">Dietary Tags</label>
                    <input id="admin_edit_dietary" placeholder="comma-separated" style="width:100%;padding:8px;margin-top:6px;border:1px solid #ccc" />
                </div>
                <div>
                    <label style="font-weight:600;font-size:13px;">Location</label>
                    <input id="admin_edit_location" style="width:100%;padding:8px;margin-top:6px;border:1px solid #ccc" />
                </div>
                <div style="grid-column:1/ -1;">
                    <label style="font-weight:600;font-size:13px;">Description</label>
                    <textarea id="admin_edit_description" style="width:100%;padding:8px;margin-top:6px;border:1px solid #ccc;min-height:80px"></textarea>
                </div>
            </div>

            <div style="margin-top:12px;display:flex;gap:8px;justify-content:flex-end;">
                <button id="admin_edit_save" style="padding:8px 12px;background:#b85c38;color:#fff;border:none;border-radius:6px;">Save</button>
                <button id="admin_edit_cancel" style="padding:8px 12px;background:#fff;border:1px solid #ccc;border-radius:6px;">Cancel</button>
            </div>
        </div>
    </div>

    <script>
        // ── Yelp Import modal ──
        const yelpBackdrop = document.getElementById('yelp-import-backdrop');
        document.getElementById('open-yelp-modal').addEventListener('click', () => {
            document.getElementById('yelp_msg').textContent = '';
            document.getElementById('yelp_msg').style.color = '';
            yelpBackdrop.style.display = 'flex';
        });
        document.getElementById('yelp_cancel_btn').addEventListener('click', () => { yelpBackdrop.style.display = 'none'; });

        document.getElementById('yelp_import_btn').addEventListener('click', async () => {
            const location = document.getElementById('yelp_location').value.trim() || 'Toronto';
            const limit = parseInt(document.getElementById('yelp_limit').value, 10) || 20;
            const msgEl = document.getElementById('yelp_msg');
            const btn = document.getElementById('yelp_import_btn');

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

        const adminBackdrop = document.getElementById('admin-add-backdrop');
        document.getElementById('open-add-modal').addEventListener('click', () => { adminBackdrop.style.display = 'flex'; });
        document.getElementById('admin_add_cancel').addEventListener('click', () => { adminBackdrop.style.display = 'none'; });

        document.getElementById('admin_add_save').addEventListener('click', async () => {
            const payload = {
                name: document.getElementById('admin_name').value.trim(),
                cuisine: document.getElementById('admin_cuisine').value.trim(),
                dietaryTags: document.getElementById('admin_dietary').value.trim(),
                location: document.getElementById('admin_location').value.trim(),
                description: document.getElementById('admin_description').value.trim()
            };
            if (!payload.name || !payload.cuisine || !payload.location) {
                alert('Please provide name, cuisine and location');
                return;
            }

            try {
                const res = await fetch('/admin/restaurants', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await res.json().catch(() => ({}));

                if (res.ok) {
                    // Success — refresh dashboard to show new restaurant
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
        document.querySelectorAll('.admin-delete').forEach(btn => {
            btn.addEventListener('click', async (ev) => {
                const id = btn.getAttribute('data-id');
                if (!id) return;
                if (!confirm('Delete restaurant #' + id + '? This action cannot be undone.')) return;
                try {
                    const resp = await fetch('/admin/restaurants/' + encodeURIComponent(id), { method: 'DELETE' });
                    const body = await resp.json().catch(() => ({}));
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

        // Edit button handlers — open modal and populate fields
        document.querySelectorAll('.admin-edit').forEach(btn => {
            btn.addEventListener('click', (ev) => {
                const id = btn.getAttribute('data-id');
                if (!id) return;
                document.getElementById('admin_edit_name').value = btn.getAttribute('data-name') || '';
                document.getElementById('admin_edit_cuisine').value = btn.getAttribute('data-cuisine') || '';
                document.getElementById('admin_edit_location').value = btn.getAttribute('data-location') || '';
                document.getElementById('admin_edit_dietary').value = btn.getAttribute('data-dietary') || '';
                document.getElementById('admin_edit_description').value = btn.getAttribute('data-description') || '';
                // store id on save button for later
                document.getElementById('admin_edit_save').setAttribute('data-id', id);
                document.getElementById('admin-edit-backdrop').style.display = 'flex';
            });
        });

        document.getElementById('admin_edit_cancel').addEventListener('click', () => { document.getElementById('admin-edit-backdrop').style.display = 'none'; });

        document.getElementById('admin_edit_save').addEventListener('click', async () => {
            const id = document.getElementById('admin_edit_save').getAttribute('data-id');
            if (!id) return alert('No restaurant selected');
            const payload = {
                name: document.getElementById('admin_edit_name').value.trim(),
                cuisine: document.getElementById('admin_edit_cuisine').value.trim(),
                dietaryTags: document.getElementById('admin_edit_dietary').value.trim(),
                location: document.getElementById('admin_edit_location').value.trim(),
                description: document.getElementById('admin_edit_description').value.trim()
            };
            if (!payload.name || !payload.cuisine || !payload.location) {
                alert('Please provide name, cuisine and location');
                return;
            }

            try {
                const res = await fetch('/admin/restaurants/' + encodeURIComponent(id), {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                const data = await res.json().catch(() => ({}));

                if (res.ok) {
                    document.getElementById('admin-edit-backdrop').style.display = 'none';
                    window.location.reload();
                    return;
                }

                alert('Failed to update restaurant: ' + (data.error || data.message || JSON.stringify(data)));
            } catch (e) {
                alert('Request failed: ' + e);
            }
        });
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
    """Public homepage — show dashboard layout without requiring login."""
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


@app.post("/api/reviews")
def create_review() -> tuple[dict[str, Any], int]:
    payload = request.get_json(silent=True) or {}
    headers: dict[str, str] = {"Content-Type": "application/json"}
    # Prefer the server-side session token so the client never needs to
    # handle the raw token value.
    token = session.get("user_token") or request.headers.get("Authorization")
    if token:
        headers["Authorization"] = token
    try:
        response = requests.post(reviews_url(), json=payload, headers=headers, timeout=5)
        body = response.json() if response.content else {}
        return {"ok": response.ok, "data": body}, response.status_code
    except requests.RequestException as exc:
        return _error_payload("Couldn't reach backend to create review", str(exc)), 502


# ---------------------------------------------------------------------------
# User routes
# ---------------------------------------------------------------------------

@app.get("/user")
def user_view():
    """User view landing — choose Register or Login."""
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
    """User dashboard — restaurant list + review submission."""
    if not session.get("user_token"):
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
        username=session.get("user_username", "User"),
        restaurants=restaurants,
        backend_url=BACKEND_BASE_URL,
        is_guest=False,
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

    return render_template_string(
        ADMIN_DASHBOARD_TEMPLATE,
        admin_username=session.get("admin_username", "Admin"),
        users=users,
        restaurants=restaurants,
        reviews=reviews,
    )


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
        error=msg,
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
    return redirect(url_for("admin_login"))


# ---------------------------------------------------------------------------
# Owner routes
# ---------------------------------------------------------------------------

@app.get("/owner")
def owner_view():
    """Owner view landing — choose Register or Login."""
    return render_template("owner_view.html")


@app.route("/owner/register", methods=["GET", "POST"])
def owner_register():
    """Owner registration page and handler."""
    if request.method == "GET":
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
        session["owner_role"] = "OWNER"
        return redirect(url_for("owner_dashboard"))

    except requests.RequestException:
        return render_template(
            "owner_login.html",
            error="Could not reach authentication service. Please try again.",
        )


@app.get("/owner/logout")
def owner_logout():
    """Clear owner session and redirect to owner view."""
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
    """Owner dashboard — show their restaurant and its reviews."""
    if not session.get("owner_token"):
        return redirect(url_for("owner_login"))

    token = session["owner_token"]
    headers = {"Authorization": token}

    restaurant = None
    reviews: list[Any] = []

    # Fetch owner's restaurant
    try:
        resp = requests.get(
            f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants/my",
            headers=headers,
            timeout=5,
        )
        if resp.ok:
            data = resp.json()
            restaurant = data.get("restaurant") if isinstance(data, dict) else None
    except (requests.RequestException, ValueError):
        pass

    # Fetch reviews for owner's restaurant
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

    return render_template(
        "owner_dashboard.html",
        owner_username=session.get("owner_username", "Owner"),
        restaurant=restaurant,
        reviews=reviews,
    )


@app.post("/owner/restaurant/create")
def owner_create_restaurant():
    """Handle owner restaurant creation from dashboard form."""
    if not session.get("owner_token"):
        return redirect(url_for("owner_login"))

    token = session["owner_token"]
    headers = {"Authorization": token, "Content-Type": "application/json"}

    name = request.form.get("name", "").strip()
    cuisine = request.form.get("cuisine", "").strip()
    location = request.form.get("location", "").strip()
    dietary_tags = request.form.get("dietary_tags", "").strip()
    description = request.form.get("description", "").strip()

    if not name or not cuisine or not location:
        return render_template(
            "owner_dashboard.html",
            owner_username=session.get("owner_username", "Owner"),
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

    try:
        resp = requests.post(
            f"{BACKEND_BASE_URL.rstrip('/')}/api/restaurants",
            json=payload,
            headers=headers,
            timeout=5,
        )
        if resp.ok:
            return redirect(url_for("owner_dashboard"))
        try:
            msg = resp.json().get("error") or resp.json().get("message") or "Failed to create restaurant."
        except ValueError:
            msg = "Failed to create restaurant."
        return render_template(
            "owner_dashboard.html",
            owner_username=session.get("owner_username", "Owner"),
            restaurant=None,
            reviews=[],
            error=msg,
        )
    except requests.RequestException:
        return render_template(
            "owner_dashboard.html",
            owner_username=session.get("owner_username", "Owner"),
            restaurant=None,
            reviews=[],
            error="Could not connect to the server. Please try again.",
        )


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
