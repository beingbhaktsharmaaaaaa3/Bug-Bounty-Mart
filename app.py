#!/usr/bin/env python3
"""
BugBountyMart — Intentionally Vulnerable Web Application
For educational bug bounty practice ONLY.
DO NOT deploy in production.
"""

import os
import sqlite3
import hashlib
import time
import random
import threading
import subprocess
import xml.etree.ElementTree as ET
from xml.dom import minidom
from lxml import etree
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for, session,
    flash, make_response, jsonify, send_file, render_template_string,
    send_from_directory, abort
)
from werkzeug.utils import secure_filename
import jwt
import requests

app = Flask(__name__)
app.secret_key = "super_secret_key_12345"  # Weak secret for JWT practice
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

DATABASE = 'bugbounty.db'

# ─── DB Setup ───
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    db = get_db()
    db.executescript("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            email TEXT,
            role TEXT DEFAULT 'user',
            is_admin INTEGER DEFAULT 0,
            avatar TEXT,
            bio TEXT
        );
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            price REAL,
            image TEXT,
            category TEXT
        );
        CREATE TABLE reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            user_id INTEGER,
            username TEXT,
            content TEXT,
            rating INTEGER
        );
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            items TEXT,
            total REAL,
            status TEXT,
            coupon TEXT
        );
        CREATE TABLE coupons (
            code TEXT PRIMARY KEY,
            discount INTEGER,
            used INTEGER DEFAULT 0
        );
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            subject TEXT,
            body TEXT,
            webhook_url TEXT
        );
        INSERT INTO users (username, password, email, role, is_admin) VALUES
            ('admin', 'admin123', 'admin@bugbountymart.local', 'admin', 1),
            ('alice', 'password', 'alice@example.com', 'user', 0),
            ('bob', '123456', 'bob@example.com', 'user', 0),
            ('charlie', 'qwerty', 'charlie@example.com', 'user', 0);
        INSERT INTO products (name, description, price, image, category) VALUES
            ('Laptop Pro X1', 'High-performance laptop for professionals', 1299.99, 'laptop.jpg', 'Electronics'),
            ('Wireless Headphones', 'Noise cancelling over-ear headphones', 249.99, 'headphones.jpg', 'Electronics'),
            ('Smart Watch Gen 4', 'Fitness tracking smartwatch', 199.99, 'watch.jpg', 'Electronics'),
            ('USB-C Hub', '7-in-1 USB-C adapter', 59.99, 'hub.jpg', 'Accessories'),
            ('Mechanical Keyboard', 'RGB backlit mechanical keyboard', 149.99, 'keyboard.jpg', 'Accessories'),
            ('Webcam 4K', 'Ultra HD webcam for streaming', 89.99, 'webcam.jpg', 'Electronics');
        INSERT INTO coupons (code, discount, used) VALUES
            ('WELCOME10', 10, 0),
            ('FLASH50', 50, 0),
            ('SINGLEUSE', 100, 0);
        INSERT INTO reviews (product_id, user_id, username, content, rating) VALUES
            (1, 2, 'alice', 'Great laptop, very fast!', 5),
            (1, 3, 'bob', 'Battery could be better <script>alert("xss")</script>', 4),
            (2, 4, 'charlie', 'Sound quality is amazing', 5);
    """)
    db.commit()
    db.close()

# ─── Helpers ───
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', return_to=request.url))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

def generate_jwt(user_id, username, role):
    """VULNERABLE: weak secret, no expiry, supports 'none' algorithm"""
    payload = {'user_id': user_id, 'username': username, 'role': role, 'iat': int(time.time())}
    return jwt.encode(payload, app.secret_key, algorithm='HS256')

def decode_jwt(token):
    """VULNERABLE: accepts 'none' algorithm if specified in header"""
    try:
        # Unsafely allow none algorithm for educational purposes
        return jwt.decode(token, app.secret_key, algorithms=['HS256', 'none'], options={"verify_signature": False})
    except Exception as e:
        return None

# ─── Routes ───

@app.route('/')
def index():
    db = get_db()
    products = db.execute('SELECT * FROM products').fetchall()
    db.close()
    return render_template('index.html', products=products)

# ─── Auth (SQLi + XSS + Open Redirect + Mass Assignment) ───

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        # VULNERABLE: SQL Injection via string concatenation
        db = get_db()
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        try:
            user = db.execute(query).fetchone()
        except Exception as e:
            # VULNERABLE: Verbose error disclosure
            error = f"SQL Error: {str(e)}"
            user = None
        db.close()
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return_to = request.args.get('return_to', '') or request.form.get('return_to', '')
            # VULNERABLE: Open Redirect
            if return_to:
                return redirect(return_to)
            return redirect(url_for('index'))
        else:
            # VULNERABLE: XSS in error message (reflects username)
            error = f"Invalid credentials for user: {username}"
    return_to = request.args.get('return_to', '')
    return render_template('login.html', error=error, return_to=return_to)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        # VULNERABLE: Mass Assignment — extra fields accepted
        role = request.form.get('role', 'user')
        is_admin = request.form.get('is_admin', 0)
        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password, email, role, is_admin) VALUES (?, ?, ?, ?, ?)",
                (username, password, email, role, is_admin)
            )
            db.commit()
            flash('Registration successful!')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error: {e}')
        finally:
            db.close()
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """VULNERABLE: Host Header Injection — reset link uses request.host"""
    message = ''
    if request.method == 'POST':
        email = request.form.get('email')
        # VULNERABLE: Uses Host header to build reset link
        reset_link = f"http://{request.host}/reset-password?token=abc123&email={email}"
        message = f"If your email exists, a reset link has been sent to: {reset_link}"
    return render_template('forgot_password.html', message=message)

# ─── Product & Search (XSS + SQLi) ───

@app.route('/product/<int:product_id>')
def product(product_id):
    db = get_db()
    # VULNERABLE: SQL Injection possible if product_id is string, but here it's int
    # Still demonstrating via search
    prod = db.execute('SELECT * FROM products WHERE id=?', (product_id,)).fetchone()
    reviews = db.execute('SELECT * FROM reviews WHERE product_id=?', (product_id,)).fetchall()
    db.close()
    return render_template('product.html', product=prod, reviews=reviews)

@app.route('/search')
def search():
    q = request.args.get('q', '')
    db = get_db()
    # VULNERABLE: SQL Injection
    query = f"SELECT * FROM products WHERE name LIKE '%{q}%' OR description LIKE '%{q}%'"
    try:
        results = db.execute(query).fetchall()
    except Exception as e:
        results = []
        flash(f"Search error: {e}")
    db.close()
    # VULNERABLE: Reflected XSS — q rendered without escaping in template
    return render_template('search.html', q=q, results=results)

@app.route('/review/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    content = request.form.get('content', '')
    rating = request.form.get('rating', 5)
    db = get_db()
    # VULNERABLE: Stored XSS — content not sanitized
    db.execute(
        "INSERT INTO reviews (product_id, user_id, username, content, rating) VALUES (?, ?, ?, ?, ?)",
        (product_id, session['user_id'], session['username'], content, rating)
    )
    db.commit()
    db.close()
    flash('Review added!')
    return redirect(url_for('product', product_id=product_id))

# ─── Profile (IDOR + File Upload + CSRF + XSS) ───

@app.route('/profile')
@login_required
def profile():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
    db.close()
    return render_template('profile.html', user=user)

@app.route('/profile/<int:user_id>')
def profile_by_id(user_id):
    """VULNERABLE: IDOR — no authorization check"""
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()
    db.close()
    if not user:
        abort(404)
    return render_template('profile.html', user=user)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """VULNERABLE: CSRF — no token validation"""
    bio = request.form.get('bio', '')
    email = request.form.get('email', '')
    db = get_db()
    # VULNERABLE: Stored XSS in bio
    db.execute("UPDATE users SET bio=?, email=? WHERE id=?", (bio, email, session['user_id']))
    db.commit()
    db.close()
    flash('Profile updated')
    return redirect(url_for('profile'))

@app.route('/profile/upload', methods=['POST'])
@login_required
def upload_avatar():
    """VULNERABLE: Unrestricted File Upload"""
    if 'avatar' not in request.files:
        flash('No file')
        return redirect(url_for('profile'))
    file = request.files['avatar']
    if file.filename == '':
        flash('No filename')
        return redirect(url_for('profile'))
    # VULNERABLE: No extension validation, no content-type check
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    db = get_db()
    db.execute("UPDATE users SET avatar=? WHERE id=?", (filename, session['user_id']))
    db.commit()
    db.close()
    flash(f'Uploaded {filename}')
    return redirect(url_for('profile'))

# ─── Cart & Checkout (Business Logic + Race Condition + IDOR) ───

@app.route('/cart')
@login_required
def cart():
    cart_items = session.get('cart', [])
    db = get_db()
    products = []
    total = 0
    for item in cart_items:
        p = db.execute('SELECT * FROM products WHERE id=?', (item['id'],)).fetchone()
        if p:
            products.append({'product': p, 'qty': item.get('qty', 1), 'price': item.get('price', p['price'])})
            total += item.get('price', p['price']) * item.get('qty', 1)
    db.close()
    return render_template('cart.html', products=products, total=total)

@app.route('/cart/add', methods=['POST'])
@login_required
def add_to_cart():
    """VULNERABLE: CSRF + Business Logic (price manipulation)"""
    product_id = int(request.form.get('product_id'))
    qty = int(request.form.get('qty', 1))
    # VULNERABLE: Client-controlled price
    price = float(request.form.get('price', 0))
    if 'cart' not in session:
        session['cart'] = []
    cart = session['cart']
    cart.append({'id': product_id, 'qty': qty, 'price': price})
    session['cart'] = cart
    flash('Added to cart')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        cart_items = session.get('cart', [])
        # VULNERABLE: Business Logic — client sends total, server trusts it
        total = float(request.form.get('total', 0))
        coupon = request.form.get('coupon', '')
        db = get_db()
        # VULNERABLE: Race Condition — no atomic check
        c = db.execute('SELECT * FROM coupons WHERE code=?', (coupon,)).fetchone()
        if c:
            total = total * (1 - c['discount']/100)
            db.execute('UPDATE coupons SET used=used+1 WHERE code=?', (coupon,))
        items_str = ','.join([str(i['id']) for i in cart_items])
        db.execute(
            "INSERT INTO orders (user_id, items, total, status, coupon) VALUES (?, ?, ?, ?, ?)",
            (session['user_id'], items_str, total, 'pending', coupon)
        )
        db.commit()
        order_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        db.close()
        session.pop('cart', None)
        return redirect(url_for('order', order_id=order_id))
    cart_items = session.get('cart', [])
    db = get_db()
    products = []
    total = 0
    for item in cart_items:
        p = db.execute('SELECT * FROM products WHERE id=?', (item['id'],)).fetchone()
        if p:
            # VULNERABLE: Uses client-provided price if available
            price = item.get('price', p['price'])
            products.append({'product': p, 'qty': item['qty'], 'price': price})
            total += price * item['qty']
    db.close()
    return render_template('checkout.html', products=products, total=total)

@app.route('/order/<int:order_id>')
def order(order_id):
    """VULNERABLE: IDOR — no authorization check"""
    db = get_db()
    order = db.execute('SELECT * FROM orders WHERE id=?', (order_id,)).fetchone()
    db.close()
    if not order:
        abort(404)
    return render_template('order.html', order=order)

@app.route('/order/<int:order_id>/export', methods=['POST'])
def export_order(order_id):
    """VULNERABLE: XXE — processes XML with external entities enabled"""
    xml_data = request.data
    if not xml_data:
        return jsonify({'error': 'No XML data'}), 400
    try:
        # VULNERABLE: lxml with resolve_entities=True (default in older versions, explicit here)
        parser = etree.XMLParser(resolve_entities=True, no_network=False)
        root = etree.fromstring(xml_data, parser=parser)
        result = etree.tostring(root, pretty_print=True).decode()
        return jsonify({'parsed': result})
    except Exception as e:
        # VULNERABLE: Verbose error
        return jsonify({'error': str(e)}), 500

# ─── Contact (XSS + SSRF) ───

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        subject = request.form.get('subject', '')
        body = request.form.get('body', '')
        webhook_url = request.form.get('webhook_url', '')
        db = get_db()
        # VULNERABLE: Stored XSS in all fields
        db.execute(
            "INSERT INTO messages (name, email, subject, body, webhook_url) VALUES (?, ?, ?, ?, ?)",
            (name, email, subject, body, webhook_url)
        )
        db.commit()
        msg_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        db.close()
        # VULNERABLE: SSRF — fetches webhook URL without validation
        if webhook_url:
            try:
                requests.get(webhook_url, timeout=5)
            except Exception:
                pass
        flash('Message sent!')
        return redirect(url_for('contact'))
    db = get_db()
    messages = db.execute('SELECT * FROM messages ORDER BY id DESC LIMIT 10').fetchall()
    db.close()
    return render_template('contact.html', messages=messages)

# ─── Admin (Command Injection + SSTI + LFI + Info Disclosure) ───

@app.route('/admin')
@admin_required
def admin_panel():
    db = get_db()
    users = db.execute('SELECT id, username, email, role, is_admin FROM users').fetchall()
    orders = db.execute('SELECT * FROM orders').fetchall()
    messages = db.execute('SELECT * FROM messages').fetchall()
    db.close()
    return render_template('admin.html', users=users, orders=orders, messages=messages)

@app.route('/admin/ping', methods=['POST'])
@admin_required
def admin_ping():
    """VULNERABLE: OS Command Injection"""
    host = request.form.get('host', '127.0.0.1')
    # VULNERABLE: Direct shell command execution
    cmd = f"ping -c 3 {host}"
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=10).decode()
    except subprocess.CalledProcessError as e:
        output = e.output.decode()
    except Exception as e:
        output = str(e)
    return render_template('admin_result.html', title='Ping Result', output=output)

@app.route('/admin/greeting', methods=['GET', 'POST'])
@admin_required
def admin_greeting():
    """VULNERABLE: SSTI via render_template_string"""
    template = request.form.get('template', 'Hello, {{name}}!') if request.method == 'POST' else 'Hello, {{name}}!'
    name = request.form.get('name', 'Admin') if request.method == 'POST' else 'Admin'
    # VULNERABLE: render_template_string with user-controlled template
    try:
        rendered = render_template_string(template, name=name)
    except Exception as e:
        rendered = f"Template Error: {e}"
    return render_template('admin_result.html', title='Greeting', output=rendered)

@app.route('/admin/fetch', methods=['POST'])
@admin_required
def admin_fetch():
    """VULNERABLE: SSRF — fetches arbitrary URL"""
    url = request.form.get('url', '')
    try:
        resp = requests.get(url, timeout=10)
        output = f"Status: {resp.status_code}\n\n{resp.text[:2000]}"
    except Exception as e:
        output = str(e)
    return render_template('admin_result.html', title='Fetch Result', output=output)

@app.route('/admin/view', methods=['GET'])
@admin_required
def admin_view_file():
    """VULNERABLE: LFI / Path Traversal"""
    filename = request.args.get('file', 'app.py')
    # VULNERABLE: No path sanitization
    try:
        with open(filename, 'r') as f:
            content = f.read()
        return render_template('admin_result.html', title=f'View: {filename}', output=content)
    except Exception as e:
        return render_template('admin_result.html', title='Error', output=str(e))

# ─── Download (LFI) ───

@app.route('/download')
def download():
    """VULNERABLE: Path Traversal"""
    filename = request.args.get('file', 'laptop.jpg')
    # VULNERABLE: No path validation
    return send_from_directory('static/images', filename)

# ─── Redirect (Open Redirect) ───

@app.route('/redirect')
def redirect_page():
    """VULNERABLE: Open Redirect"""
    url = request.args.get('url', '/')
    return redirect(url)

# ─── API (JWT + CORS + IDOR + SQLi + NoSQL) ───

@app.route('/api/login', methods=['POST'])
def api_login():
    """VULNERABLE: NoSQL Injection via JSON, weak JWT"""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    db = get_db()
    # VULNERABLE: If username is dict, this becomes NoSQL injection
    if isinstance(username, dict):
        # Simulating NoSQL injection for educational demo
        # In real MongoDB: db.users.find({"username": {"$ne": null}})
        # Here we simulate with a raw SQL approach that bypasses auth
        cond = ' OR '.join([f"{k}='{v}'" for k, v in username.items()])
        query = f"SELECT * FROM users WHERE {cond}"
        user = db.execute(query).fetchone()
    else:
        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?", (username, password)
        ).fetchone()
    db.close()
    if user:
        token = generate_jwt(user['id'], user['username'], user['role'])
        return jsonify({'token': token, 'user': {'id': user['id'], 'username': user['username'], 'role': user['role']}})
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/user/<int:user_id>', methods=['GET'])
def api_user(user_id):
    """VULNERABLE: IDOR + CORS misconfiguration"""
    # VULNERABLE: CORS — allows any origin with credentials
    origin = request.headers.get('Origin', '*')
    resp = make_response()
    resp.headers['Access-Control-Allow-Origin'] = origin
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

    if request.method == 'OPTIONS':
        return resp

    auth = request.headers.get('Authorization', '')
    token = auth.replace('Bearer ', '') if auth.startswith('Bearer ') else None
    # VULNERABLE: JWT accepts 'none' algorithm
    if token:
        payload = decode_jwt(token)
    else:
        payload = None

    db = get_db()
    # VULNERABLE: IDOR — no authorization check against user_id
    user = db.execute('SELECT id, username, email, role, bio, avatar FROM users WHERE id=?', (user_id,)).fetchone()
    db.close()
    if user:
        resp.set_data(jsonify(dict(user)).data)
        resp.mimetype = 'application/json'
        return resp
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/search', methods=['GET'])
def api_search():
    """VULNERABLE: SQL Injection in JSON API"""
    q = request.args.get('q', '')
    db = get_db()
    # VULNERABLE: SQLi
    query = f"SELECT * FROM products WHERE name LIKE '%{q}%'"
    results = db.execute(query).fetchall()
    db.close()
    return jsonify([dict(r) for r in results])

@app.route('/api/register', methods=['POST'])
def api_register():
    """VULNERABLE: Mass Assignment — accepts any fields"""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    # VULNERABLE: Mass assignment
    role = data.get('role', 'user')
    is_admin = data.get('is_admin', 0)
    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, password, email, role, is_admin) VALUES (?, ?, ?, ?, ?)",
            (username, password, email, role, is_admin)
        )
        db.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# ─── GraphQL (Simulated) ───

@app.route('/graphql', methods=['GET', 'POST'])
def graphql():
    """VULNERABLE: GraphQL introspection enabled"""
    schema = {
        "data": {
            "__schema": {
                "types": [
                    {"name": "User", "fields": ["id", "username", "email", "password", "role", "is_admin"]},
                    {"name": "Product", "fields": ["id", "name", "description", "price"]},
                    {"name": "Order", "fields": ["id", "user_id", "items", "total", "status"]},
                    {"name": "Review", "fields": ["id", "product_id", "user_id", "content"]},
                    {"name": "Message", "fields": ["id", "name", "email", "body", "webhook_url"]}
                ]
            }
        }
    }
    if request.method == 'POST':
        data = request.get_json() or {}
        query = data.get('query', '')
        # VULNERABLE: No auth check, introspection always enabled
        if 'introspection' in query.lower() or '__schema' in query.lower() or request.method == 'GET':
            return jsonify(schema)
        # Simple query simulation
        if 'users' in query.lower():
            db = get_db()
            users = db.execute('SELECT id, username, email, role FROM users').fetchall()
            db.close()
            return jsonify({'data': {'users': [dict(u) for u in users]}})
    return jsonify(schema)

# ─── Information Disclosure ───

@app.route('/.git/HEAD')
def git_head():
    """VULNERABLE: Exposed git repository"""
    return "ref: refs/heads/main\n"

@app.route('/.git/config')
def git_config():
    return """[core]
    repositoryformatversion = 0
    filemode = true
    bare = false
    logallrefupdates = true
[remote "origin"]
    url = https://github.com/bugbountymart/internal-api.git
    fetch = +refs/heads/*:refs/remotes/origin/*
"""

@app.route('/actuator/env')
def actuator_env():
    """VULNERABLE: Exposed environment variables"""
    return jsonify({
        'DATABASE_URL': 'sqlite:///bugbounty.db',
        'SECRET_KEY': app.secret_key,
        'AWS_ACCESS_KEY': 'AKIAIOSFODNN7EXAMPLE',
        'AWS_SECRET_KEY': 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY',
        'STRIPE_API_KEY': 'sk_live_51Hxxxxxxxxxxxxxxxxxxxxxx',
        'INTERNAL_API_TOKEN': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
    })

@app.route('/backup.sql')
def backup_sql():
    """VULNERABLE: Exposed database backup"""
    if os.path.exists(DATABASE):
        return send_file(DATABASE, mimetype='application/octet-stream')
    return 'Not found', 404

@app.route('/phpinfo.php')
def phpinfo():
    """VULNERABLE: Technology info disclosure"""
    return f"""
    <html><body>
    <h1>System Info</h1>
    <p>Python Version: {os.sys.version}</p>
    <p>Flask Version: 3.0.3</p>
    <p>Server: Werkzeug</p>
    <p>Database: SQLite 3</p>
    <p>Working Directory: {os.getcwd()}</p>
    </body></html>
    """

@app.route('/swagger')
def swagger():
    """VULNERABLE: API documentation exposes internals"""
    return jsonify({
        "swagger": "2.0",
        "info": {"title": "BugBountyMart API", "version": "1.0"},
        "paths": {
            "/api/login": {"post": {"summary": "Login", "parameters": [
                {"name": "username", "in": "formData"},
                {"name": "password", "in": "formData"}
            ]}},
            "/api/user/{id}": {"get": {"summary": "Get user by ID (no auth check)"}},
            "/api/search": {"get": {"summary": "Search products (SQLi possible)"}},
            "/admin/ping": {"post": {"summary": "Ping host (RCE)"}},
            "/admin/fetch": {"post": {"summary": "Fetch URL (SSRF)"}}
        }
    })

@app.route('/robots.txt')
def robots():
    return """User-agent: *
Disallow: /admin
Disallow: /actuator
Disallow: /.git
Disallow: /backup.sql
Disallow: /swagger
"""

@app.route('/sitemap.xml')
def sitemap():
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url><loc>https://bugbountymart.local/</loc></url>
  <url><loc>https://bugbountymart.local/admin</loc></url>
  <url><loc>https://bugbountymart.local/api/search</loc></url>
</urlset>
"""

@app.route('/.env')
def env_file():
    return """SECRET_KEY=super_secret_key_12345
DATABASE_URL=sqlite:///bugbounty.db
AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
STRIPE_API_KEY=sk_live_51Hxxxxxxxxxxxxxxxxxxxxxx
DEBUG=True
"""

@app.route('/crossdomain.xml')
def crossdomain():
    return """<?xml version="1.0"?>
<cross-domain-policy>
  <allow-access-from domain="*"/>
</cross-domain-policy>
"""

# ─── Error Handlers (Info Disclosure) ───

@app.errorhandler(404)
def not_found(e):
    # VULNERABLE: Verbose error
    return f"""
    <h1>404 Not Found</h1>
    <p>The requested URL {request.path} was not found on this server.</p>
    <p>Server: Werkzeug/3.0.3 Python/{os.sys.version_info.major}.{os.sys.version_info.minor}</p>
    <p>Trace: {e}</p>
    """, 404

@app.errorhandler(500)
def server_error(e):
    # VULNERABLE: Stack trace disclosure
    import traceback
    return f"""
    <h1>500 Internal Server Error</h1>
    <pre>{traceback.format_exc()}</pre>
    """, 500

# ─── Main ───
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    init_db()
    print("=" * 60)
    print("BugBountyMart — Vulnerable Practice Lab")
    print("=" * 60)
    print("URL: http://127.0.0.1:5000")
    print("Admin: admin / admin123")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
