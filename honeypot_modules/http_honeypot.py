#!/usr/bin/env python3
from flask import Flask, request, render_template_string
from logger import HoneypotLogger

app = Flask(__name__)
logger = HoneypotLogger(honeypot_type="HTTP")

FAKE_LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel - Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .login-container {
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            width: 300px;
        }
        h2 {
            text-align: center;
            color: #333;
        }
        input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 10px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
        .error {
            color: red;
            text-align: center;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>Admin Login</h2>
        <form method="POST" action="/login">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit">Login</button>
        </form>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""


@app.before_request
def log_request():
    client_ip = request.remote_addr

    logger.log_event(
        ip_address=client_ip,
        port=8080,
        event_type="http_request",
        event_data={
            "method": request.method,
            "path": request.path,
            "user_agent": request.headers.get('User-Agent', ''),
            "query_string": request.query_string.decode('utf-8')
        }
    )

    print(f"[HTTP] {request.method} {request.path} from {client_ip}")


@app.route('/')
def index():
    return render_template_string(FAKE_LOGIN_PAGE)


@app.route('/admin')
def admin():
    return render_template_string(FAKE_LOGIN_PAGE)


@app.route('/login', methods=['POST'])
def login():
    client_ip = request.remote_addr
    username = request.form.get('username', '')
    password = request.form.get('password', '')

    logger.log_event(
        ip_address=client_ip,
        port=8080,
        event_type="http_login_attempt",
        event_data={
            "username": username,
            "password": password,
            "form_data": dict(request.form)
        }
    )

    print(f"[HTTP] Login attempt from {client_ip} - Username: {username}, Password: {password}")

    return render_template_string(FAKE_LOGIN_PAGE, error="Invalid credentials. Please try again.")


@app.route('/<path:path>')
def catch_all(path):
    client_ip = request.remote_addr

    logger.log_event(
        ip_address=client_ip,
        port=8080,
        event_type="http_path_probe",
        event_data={
            "path": path,
            "method": request.method
        }
    )

    return render_template_string(FAKE_LOGIN_PAGE)


def main():
    print("[HTTP] Starting HTTP honeypot on 0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080, debug=False)


if __name__ == '__main__':
    main()
