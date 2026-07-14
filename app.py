#!/usr/bin/env python3
"""
BugBountyMart v2.0 — Ultimate Bug Bounty Practice Lab
34 Vulnerability Categories | CTF Mode | 3 Difficulty Levels
For educational bug bounty practice ONLY. DO NOT deploy in production.
"""

import os
import sqlite3
import hashlib
import time
import random
import threading
import subprocess
import json
import base64
import pickle
import yaml
import xml.etree.ElementTree as ET
from xml.dom import minidom
from lxml import etree
from functools import wraps
from urllib.parse import urlparse, parse_qs, urlencode
import hmac

from flask import (
    Flask, render_template, request, redirect, url_for, session,
    flash, make_response, jsonify, send_file, render_template_string,
    send_from_directory, abort, g
)
from werkzeug.utils import secure_filename
import jwt
import requests

app = Flask(__name__)
app.secret_key = "super_secret_key_12345"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

DATABASE = 'bugbounty.db'
CTF_PROGRESS_FILE = 'ctf_progress.json'

# ─── CTF CONFIGURATION ───
CTF_FLAGS = {
    "sqli_error_based": {"easy": "ctf{sqli_error_easy_a1b2c3}", "medium": "ctf{sqli_error_medium_d4e5f6}", "hard": "ctf{sqli_error_hard_g7h8i9}"},
    "sqli_boolean_blind": {"easy": "ctf{sqli_blind_easy_j0k1l2}", "medium": "ctf{sqli_blind_medium_m3n4o5}", "hard": "ctf{sqli_blind_hard_p6q7r8}"},
    "sqli_time_based": {"easy": "ctf{sqli_time_easy_s9t0u1}", "medium": "ctf{sqli_time_medium_v2w3x4}", "hard": "ctf{sqli_time_hard_y5z6a7}"},
    "sqli_union_based": {"easy": "ctf{sqli_union_easy_b8c9d0}", "medium": "ctf{sqli_union_medium_e1f2g3}", "hard": "ctf{sqli_union_hard_h4i5j6}"},
    "cmd_injection": {"easy": "ctf{cmd_inj_easy_k7l8m9}", "medium": "ctf{cmd_inj_medium_n0o1p2}", "hard": "ctf{cmd_inj_hard_q3r4s5}"},
    "ssti": {"easy": "ctf{ssti_easy_t6u7v8}", "medium": "ctf{ssti_medium_w9x0y1}", "hard": "ctf{ssti_hard_z2a3b4}"},
    "xxe": {"easy": "ctf{xxe_easy_c5d6e7}", "medium": "ctf{xxe_medium_f8g9h0}", "hard": "ctf{xxe_hard_i1j2k3}"},
    "xxe_oob": {"easy": "ctf{xxe_oob_easy_l4m5n6}", "medium": "ctf{xxe_oob_medium_o7p8q9}", "hard": "ctf{xxe_oob_hard_r0s1t2}"},
    "crlf_injection": {"easy": "ctf{crlf_easy_u3v4w5}", "medium": "ctf{crlf_medium_x6y7z8}", "hard": "ctf{crlf_hard_a9b0c1}"},
    "ssrf": {"easy": "ctf{ssrf_easy_d2e3f4}", "medium": "ctf{ssrf_medium_g5h6i7}", "hard": "ctf{ssrf_hard_j8k9l0}"},
    "ssrf_dns_rebind": {"easy": "ctf{ssrf_dns_easy_m1n2o3}", "medium": "ctf{ssrf_dns_medium_p4q5r6}", "hard": "ctf{ssrf_dns_hard_s7t8u9}"},
    "file_upload": {"easy": "ctf{upload_easy_v0w1x2}", "medium": "ctf{upload_medium_y3z4a5}", "hard": "ctf{upload_hard_b6c7d8}"},
    "path_traversal": {"easy": "ctf{path_trav_easy_e9f0g1}", "medium": "ctf{path_trav_medium_h2i3j4}", "hard": "ctf{path_trav_hard_k5l6m7}"},
    "lfi": {"easy": "ctf{lfi_easy_n8o9p0}", "medium": "ctf{lfi_medium_q1r2s3}", "hard": "ctf{lfi_hard_t4u5v6}"},
    "rfi": {"easy": "ctf{rfi_easy_w7x8y9}", "medium": "ctf{rfi_medium_z0a1b2}", "hard": "ctf{rfi_hard_c3d4e5}"},
    "cache_poisoning": {"easy": "ctf{cache_poison_easy_f6g7h8}", "medium": "ctf{cache_poison_medium_i9j0k1}", "hard": "ctf{cache_poison_hard_l2m3n4}"},
    "cache_deception": {"easy": "ctf{cache_deception_easy_o5p6q7}", "medium": "ctf{cache_deception_medium_r8s9t0}", "hard": "ctf{cache_deception_hard_u1v2w3}"},
    "http_smuggling": {"easy": "ctf{http_smuggle_easy_x4y5z6}", "medium": "ctf{http_smuggle_medium_a7b8c9}", "hard": "ctf{http_smuggle_hard_d0e1f2}"},
    "secondary_context": {"easy": "ctf{sec_ctx_easy_g3h4i5}", "medium": "ctf{sec_ctx_medium_j6k7l8}", "hard": "ctf{sec_ctx_hard_m9n0o1}"},
    "race_condition": {"easy": "ctf{race_easy_p2q3r4}", "medium": "ctf{race_medium_s5t6u7}", "hard": "ctf{race_hard_v8w9x0}"},
    "xss_reflected": {"easy": "ctf{xss_refl_easy_y1z2a3}", "medium": "ctf{xss_refl_medium_b4c5d6}", "hard": "ctf{xss_refl_hard_e7f8g9}"},
    "xss_stored": {"easy": "ctf{xss_stored_easy_h0i1j2}", "medium": "ctf{xss_stored_medium_k3l4m5}", "hard": "ctf{xss_stored_hard_n6o7p8}"},
    "xss_dom": {"easy": "ctf{xss_dom_easy_q9r0s1}", "medium": "ctf{xss_dom_medium_t2u3v4}", "hard": "ctf{xss_dom_hard_w5x6y7}"},
    "csrf": {"easy": "ctf{csrf_easy_z8a9b0}", "medium": "ctf{csrf_medium_c1d2e3}", "hard": "ctf{csrf_hard_f4g5h6}"},
    "open_redirect": {"easy": "ctf{redirect_easy_i7j8k9}", "medium": "ctf{redirect_medium_l0m1n2}", "hard": "ctf{redirect_hard_o3p4q5}"},
    "csti": {"easy": "ctf{csti_easy_r6s7t8}", "medium": "ctf{csti_medium_u9v0w1}", "hard": "ctf{csti_hard_x2y3z4}"},
    "postmessage": {"easy": "ctf{postmsg_easy_a5b6c7}", "medium": "ctf{postmsg_medium_d8e9f0}", "hard": "ctf{postmsg_hard_g1h2i3}"},
    "prototype_pollution": {"easy": "ctf{proto_pollute_easy_j4k5l6}", "medium": "ctf{proto_pollute_medium_m7n8o9}", "hard": "ctf{proto_pollute_hard_p0q1r2}"},
    "jwt_weak_secret": {"easy": "ctf{jwt_weak_easy_s3t4u5}", "medium": "ctf{jwt_weak_medium_v6w7x8}", "hard": "ctf{jwt_weak_hard_y9z0a1}"},
    "jwt_none_alg": {"easy": "ctf{jwt_none_easy_b2c3d4}", "medium": "ctf{jwt_none_medium_e5f6g7}", "hard": "ctf{jwt_none_hard_h8i9j0}"},
    "jwt_key_confusion": {"easy": "ctf{jwt_conf_easy_k1l2m3}", "medium": "ctf{jwt_conf_medium_n4o5p6}", "hard": "ctf{jwt_conf_hard_q7r8s9}"},
    "2fa_bypass": {"easy": "ctf{2fa_bypass_easy_t0u1v2}", "medium": "ctf{2fa_bypass_medium_w3x4y5}", "hard": "ctf{2fa_bypass_hard_z6a7b8}"},
    "brute_force": {"easy": "ctf{brute_easy_c9d0e1}", "medium": "ctf{brute_medium_f2g3h4}", "hard": "ctf{brute_hard_i5j6k7}"},
    "password_reset": {"easy": "ctf{pwd_reset_easy_l8m9n0}", "medium": "ctf{pwd_reset_medium_o1p2q3}", "hard": "ctf{pwd_reset_hard_r4s5t6}"},
    "oauth_misconfig": {"easy": "ctf{oauth_easy_u7v8w9}", "medium": "ctf{oauth_medium_x0y1z2}", "hard": "ctf{oauth_hard_a3b4c5}"},
    "saml_vuln": {"easy": "ctf{saml_easy_d6e7f8}", "medium": "ctf{saml_medium_g9h0i1}", "hard": "ctf{saml_hard_j2k3l4}"},
    "idor": {"easy": "ctf{idor_easy_m5n6o7}", "medium": "ctf{idor_medium_p8q9r0}", "hard": "ctf{idor_hard_s1t2u3}"},
    "access_control": {"easy": "ctf{access_ctrl_easy_v4w5x6}", "medium": "ctf{access_ctrl_medium_y7z8a9}", "hard": "ctf{access_ctrl_hard_b0c1d2}"},
    "mass_assignment": {"easy": "ctf{mass_assign_easy_e3f4g5}", "medium": "ctf{mass_assign_medium_h6i7j8}", "hard": "ctf{mass_assign_hard_k9l0m1}"},
    "info_disclosure": {"easy": "ctf{info_disc_easy_n2o3p4}", "medium": "ctf{info_disc_medium_q5r6s7}", "hard": "ctf{info_disc_hard_t8u9v0}"},
    "cloud_storage": {"easy": "ctf{cloud_easy_w1x2y3}", "medium": "ctf{cloud_medium_z4a5b6}", "hard": "ctf{cloud_hard_c7d8e9}"},
    "subdomain_takeover": {"easy": "ctf{subdomain_easy_f0g1h2}", "medium": "ctf{subdomain_medium_i3j4k5}", "hard": "ctf{subdomain_hard_l6m7n8}"},
    "files_directories": {"easy": "ctf{files_dirs_easy_o9p0q1}", "medium": "ctf{files_dirs_medium_r2s3t4}", "hard": "ctf{files_dirs_hard_u5v6w7}"},
    "virtual_hosts": {"easy": "ctf{vhosts_easy_x8y9z0}", "medium": "ctf{vhosts_medium_a1b2c3}", "hard": "ctf{vhosts_hard_d4e5f6}"},
    "fuzzing_params": {"easy": "ctf{fuzz_easy_g7h8i9}", "medium": "ctf{fuzz_medium_j0k1l2}", "hard": "ctf{fuzz_hard_m3n4o5}"},
    "dns_zone_transfer": {"easy": "ctf{dns_zone_easy_p6q7r8}", "medium": "ctf{dns_zone_medium_s9t0u1}", "hard": "ctf{dns_zone_hard_v2w3x4}"},
    "nosql_injection": {"easy": "ctf{nosql_easy_y5z6a7}", "medium": "ctf{nosql_medium_b8c9d0}", "hard": "ctf{nosql_hard_e1f2g3}"},
    "deserialization": {"easy": "ctf{deserialize_easy_h4i5j6}", "medium": "ctf{deserialize_medium_k7l8m9}", "hard": "ctf{deserialize_hard_n0o1p2}"},
    "xpath_injection": {"easy": "ctf{xpath_easy_q3r4s5}", "medium": "ctf{xpath_medium_t6u7v8}", "hard": "ctf{xpath_hard_w9x0y1}"},
    "ldap_injection": {"easy": "ctf{ldap_easy_z2a3b4}", "medium": "ctf{ldap_medium_c5d6e7}", "hard": "ctf{ldap_hard_f8g9h0}"},
    "clickjacking": {"easy": "ctf{clickjack_easy_i1j2k3}", "medium": "ctf{clickjack_medium_l4m5n6}", "hard": "ctf{clickjack_hard_o7p8q9}"},
    "host_header_injection": {"easy": "ctf{host_header_easy_r0s1t2}", "medium": "ctf{host_header_medium_u3v4w5}", "hard": "ctf{host_header_hard_x6y7z8}"},
}

CTF_HINTS = {
    "sqli_error_based": "Look for error messages that reveal database structure. Try single quotes in search/login fields.",
    "sqli_boolean_blind": "No error messages here. Use TRUE/FALSE conditions to extract data bit by bit. Check if products exist or not.",
    "sqli_time_based": "Use time delays (SLEEP, BENCHMARK) to extract data when no visible output changes.",
    "sqli_union_based": "Use UNION SELECT to combine results from other tables. Match column counts first.",
    "cmd_injection": "Command separators like ; | && can chain commands. Try in the ping tool.",
    "ssti": "Template engines evaluate expressions in {{ }}. Try {{7*7}} to detect, then {{config}} or RCE payloads.",
    "xxe": "XML parsers may process external entities. Try <!ENTITY xxe SYSTEM 'file:///etc/passwd'>",
    "xxe_oob": "When direct output is blocked, use external DTDs with parameter entities to exfiltrate data.",
    "crlf_injection": "CRLF (\r\n) in headers can inject new lines. Try in redirect parameters or custom headers.",
    "ssrf": "The server makes requests on your behalf. Try localhost, internal IPs, or cloud metadata endpoints.",
    "ssrf_dns_rebind": "DNS rebinding bypasses IP checks by resolving to different IPs over time.",
    "file_upload": "Bypass extension checks with double extensions, null bytes, or content-type spoofing.",
    "path_traversal": "Use ../ sequences to escape the intended directory. Try encoding them.",
    "lfi": "Local File Inclusion reads local files. Try php://filter/convert.base64-encode/resource=app.py",
    "rfi": "Remote File Inclusion fetches external files. Try http://attacker.com/shell.txt",
    "cache_poisoning": "Poison cache by sending malicious headers that get cached and served to others.",
    "cache_deception": "Trick cache into storing private data by appending fake extensions to authenticated pages.",
    "http_smuggling": "Send conflicting Content-Length and Transfer-Encoding headers to desynchronize front/back ends.",
    "secondary_context": "Data safe in one context (JSON) becomes dangerous in another (HTML). Check JSON responses.",
    "race_condition": "Send multiple simultaneous requests to exploit timing windows. Try coupon redemption.",
    "xss_reflected": "Input reflected immediately in response without sanitization. Try <script>alert(1)</script>",
    "xss_stored": "Input stored in database and displayed later. Check reviews, comments, messages.",
    "xss_dom": "Client-side JavaScript writes user input to DOM without sanitization. Check URL fragments.",
    "csrf": "No token validation on state-changing requests. Craft a form that submits to the target.",
    "open_redirect": "Redirect parameters accept arbitrary URLs. Try //evil.com or data:text/html,...",
    "csti": "Client-side template engines (Angular, Vue) may evaluate expressions in {{ }} in user input.",
    "postmessage": "window.postMessage without origin validation allows cross-origin communication abuse.",
    "prototype_pollution": "Pollute Object.prototype via query params or JSON. Try __proto__.isAdmin=true",
    "jwt_weak_secret": "JWT signed with weak secret. Brute force with common passwords or jwt_tool.",
    "jwt_none_alg": "JWT with alg:none bypasses signature verification entirely.",
    "jwt_key_confusion": "RS256 public key used as HS256 secret. Extract public key, sign with it as HMAC.",
    "2fa_bypass": "Check if 2FA can be skipped, brute-forced, or if backup codes are predictable.",
    "brute_force": "No rate limiting. Use tools like Hydra or Burp Intruder to guess passwords.",
    "password_reset": "Reset tokens may be predictable, leaked in referrer, or not invalidated after use.",
    "oauth_misconfig": "Missing state parameter, redirect_uri validation issues, or scope escalation.",
    "saml_vuln": "SAML responses may be vulnerable to XXE, signature stripping, or assertion wrapping.",
    "idor": "Direct object references without authorization checks. Try incrementing IDs in URLs.",
    "access_control": "Missing authorization on admin endpoints or function-level access control.",
    "mass_assignment": "Extra fields accepted in registration/update. Try adding is_admin, role fields.",
    "info_disclosure": "Check error messages, stack traces, git repos, backup files, and exposed endpoints.",
    "cloud_storage": "S3 buckets may be misconfigured with public read/write. Check for bucket enumeration.",
    "subdomain_takeover": "DNS points to non-existent services (S3, Heroku, GitHub Pages). Claim them.",
    "files_directories": "Common files: .git, .env, backup.zip, admin panels. Use wordlists like SecLists.",
    "virtual_hosts": "Different content served based on Host header. Use vhost bruteforcing tools.",
    "fuzzing_params": "Hidden parameters may change behavior. Try common names: debug, admin, role, is_admin.",
    "dns_zone_transfer": "AXFR requests may leak all DNS records. Try: dig axfr @ns1.target.com target.com",
    "nosql_injection": "NoSQL operators like $ne, $gt, $regex can bypass authentication. Send JSON objects.",
    "deserialization": "Untrusted data passed to pickle.loads, yaml.load(unsafe), or PHP unserialize.",
    "xpath_injection": "XPath queries concatenated with user input. Try ' or '1'='1 in XML search.",
    "ldap_injection": "LDAP filters built from user input. Try *)(uid=*))(&(uid=* to bypass auth.",
    "clickjacking": "Pages without X-Frame-Options can be framed. Overlay invisible elements to trick clicks.",
    "host_header_injection": "Host header used to build URLs. Change it to attacker.com in password reset.",
}

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
            bio TEXT,
            twofa_secret TEXT,
            twofa_enabled INTEGER DEFAULT 0,
            backup_codes TEXT
        );
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            price REAL,
            image TEXT,
            category TEXT,
            secret_flag TEXT
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
            used INTEGER DEFAULT 0,
            max_uses INTEGER DEFAULT 1
        );
        CREATE TABLE messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            subject TEXT,
            body TEXT,
            webhook_url TEXT
        );
        CREATE TABLE ctf_solved (
            session_id TEXT,
            vuln_name TEXT,
            difficulty TEXT,
            solved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (session_id, vuln_name, difficulty)
        );
        CREATE TABLE login_attempts (
            username TEXT,
            attempts INTEGER DEFAULT 0,
            last_attempt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE password_resets (
            email TEXT PRIMARY KEY,
            token TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE oauth_tokens (
            token TEXT PRIMARY KEY,
            user_id INTEGER,
            scope TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        INSERT INTO users (username, password, email, role, is_admin, twofa_secret, twofa_enabled, backup_codes) VALUES
            ('admin', 'admin123', 'admin@bugbountymart.local', 'admin', 1, 'JBSWY3DPEHPK3PXP', 1, '111111,222222,333333'),
            ('alice', 'password', 'alice@example.com', 'user', 0, NULL, 0, NULL),
            ('bob', '123456', 'bob@example.com', 'user', 0, NULL, 0, NULL),
            ('charlie', 'qwerty', 'charlie@example.com', 'user', 0, NULL, 0, NULL),
            ('support', 'support2024', 'support@bugbountymart.local', 'support', 0, NULL, 0, NULL);
        INSERT INTO products (name, description, price, image, category, secret_flag) VALUES
            ('Laptop Pro X1', 'High-performance laptop', 1299.99, 'laptop.jpg', 'Electronics', 'ctf{secret_product_flag_1}'),
            ('Wireless Headphones', 'Noise cancelling', 249.99, 'headphones.jpg', 'Electronics', 'ctf{secret_product_flag_2}'),
            ('Smart Watch Gen 4', 'Fitness tracking', 199.99, 'watch.jpg', 'Electronics', 'ctf{secret_product_flag_3}'),
            ('USB-C Hub', '7-in-1 adapter', 59.99, 'hub.jpg', 'Accessories', 'ctf{secret_product_flag_4}'),
            ('Mechanical Keyboard', 'RGB backlit', 149.99, 'keyboard.jpg', 'Accessories', 'ctf{secret_product_flag_5}'),
            ('Webcam 4K', 'Ultra HD', 89.99, 'webcam.jpg', 'Electronics', 'ctf{secret_product_flag_6}');
        INSERT INTO coupons (code, discount, used, max_uses) VALUES
            ('WELCOME10', 10, 0, 999),
            ('FLASH50', 50, 0, 1),
            ('SINGLEUSE', 100, 0, 1),
            ('RACE100', 100, 0, 1);
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

def generate_jwt(user_id, username, role, alg='HS256'):
    payload = {'user_id': user_id, 'username': username, 'role': role, 'iat': int(time.time())}
    if alg == 'none':
        return jwt.encode(payload, '', algorithm='none')
    return jwt.encode(payload, app.secret_key, algorithm=alg)

def decode_jwt(token, verify=True):
    try:
        if not verify:
            return jwt.decode(token, options={"verify_signature": False}, algorithms=['HS256', 'none'])
        header = jwt.get_unverified_header(token)
        alg = header.get('alg', 'HS256')
        if alg == 'none':
            return jwt.decode(token, '', algorithms=['none'], options={"verify_signature": False})
        if alg == 'HS256':
            return jwt.decode(token, app.secret_key, algorithms=['HS256'])
        if alg == 'RS256':
            pub_key = open('static/public_key.pem', 'rb').read() if os.path.exists('static/public_key.pem') else b'fake_key'
            return jwt.decode(token, pub_key, algorithms=['HS256', 'RS256'])
        return jwt.decode(token, app.secret_key, algorithms=['HS256', 'none'], options={"verify_signature": False})
    except Exception as e:
        return None

def get_ctf_progress():
    if 'ctf_progress' not in session:
        session['ctf_progress'] = {}
    return session['ctf_progress']

def mark_ctf_solved(vuln_name, difficulty):
    progress = get_ctf_progress()
    key = f"{vuln_name}_{difficulty}"
    if key not in progress:
        progress[key] = {
            'vuln_name': vuln_name,
            'difficulty': difficulty,
            'solved_at': time.time(),
            'points': {'easy': 100, 'medium': 200, 'hard': 300}[difficulty]
        }
        session['ctf_progress'] = progress
        return True
    return False

def get_total_points():
    return sum(p['points'] for p in get_ctf_progress().values())

def get_solved_count():
    return len(get_ctf_progress())

def get_total_challenges():
    return sum(len(v) for v in CTF_FLAGS.values())

# ─── Routes ───

@app.route('/')
def index():
    db = get_db()
    products = db.execute('SELECT * FROM products').fetchall()
    db.close()
    return render_template('index.html', products=products)

# ═══════════════════════════════════════════════════════════════
# CTF MODE
# ═══════════════════════════════════════════════════════════════

@app.route('/ctf')
def ctf_dashboard():
    progress = get_ctf_progress()
    total_points = get_total_points()
    solved_count = get_solved_count()
    total_challenges = get_total_challenges()

    categories = {
        'Injection Bugs': ['sqli_error_based', 'sqli_boolean_blind', 'sqli_time_based', 'sqli_union_based',
                          'cmd_injection', 'ssti', 'xxe', 'xxe_oob', 'crlf_injection', 'nosql_injection',
                          'deserialization', 'xpath_injection', 'ldap_injection'],
        'Server Side Logic': ['ssrf', 'ssrf_dns_rebind', 'file_upload', 'path_traversal', 'lfi', 'rfi',
                             'cache_poisoning', 'cache_deception', 'http_smuggling', 'secondary_context', 'race_condition'],
        'Client Side': ['xss_reflected', 'xss_stored', 'xss_dom', 'csrf', 'open_redirect', 'csti',
                       'postmessage', 'prototype_pollution', 'clickjacking'],
        'Authentication': ['jwt_weak_secret', 'jwt_none_alg', 'jwt_key_confusion', '2fa_bypass',
                          'brute_force', 'password_reset', 'oauth_misconfig', 'saml_vuln'],
        'Authorization': ['idor', 'access_control', 'mass_assignment', 'info_disclosure'],
        'Infrastructure': ['cloud_storage', 'subdomain_takeover'],
        'Web Enumeration': ['files_directories', 'virtual_hosts', 'fuzzing_params', 'dns_zone_transfer']
    }

    return render_template('ctf_dashboard.html', 
                         categories=categories,
                         flags=CTF_FLAGS,
                         hints=CTF_HINTS,
                         progress=progress,
                         total_points=total_points,
                         solved_count=solved_count,
                         total_challenges=total_challenges)

@app.route('/ctf/verify', methods=['POST'])
def ctf_verify():
    data = request.get_json() or {}
    flag = data.get('flag', '').strip()
    vuln_name = data.get('vuln_name', '')
    difficulty = data.get('difficulty', 'easy')

    if not flag or not vuln_name:
        return jsonify({'success': False, 'message': 'Missing flag or challenge name'})

    correct_flag = CTF_FLAGS.get(vuln_name, {}).get(difficulty)
    if not correct_flag:
        return jsonify({'success': False, 'message': 'Invalid challenge'})

    if flag == correct_flag:
        if mark_ctf_solved(vuln_name, difficulty):
            total = get_total_points()
            return jsonify({
                'success': True, 
                'message': f'Correct! +{CTF_FLAGS[vuln_name][difficulty]["points"]} points!',
                'points': CTF_FLAGS[vuln_name][difficulty]['points'],
                'total_points': total,
                'solved_count': get_solved_count()
            })
        else:
            return jsonify({'success': True, 'message': 'Already solved!'})
    else:
        return jsonify({'success': False, 'message': 'Incorrect flag. Try again!'})

@app.route('/ctf/reset', methods=['POST'])
def ctf_reset():
    session['ctf_progress'] = {}
    return jsonify({'success': True, 'message': 'Progress reset!'})

@app.route('/ctf/hint', methods=['POST'])
def ctf_hint():
    data = request.get_json() or {}
    vuln_name = data.get('vuln_name', '')
    if vuln_name in CTF_HINTS:
        return jsonify({'success': True, 'hint': CTF_HINTS[vuln_name]})
    return jsonify({'success': False, 'message': 'No hint available'})

# ═══════════════════════════════════════════════════════════════
# AUTHENTICATION VULNERABILITIES
# ═══════════════════════════════════════════════════════════════

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        db = get_db()
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        try:
            user = db.execute(query).fetchone()
        except Exception as e:
            error = f"SQL Error: {str(e)}"
            user = None
        db.close()
        if user:
            if user['twofa_enabled']:
                session['pending_2fa_user'] = user['id']
                return redirect(url_for('twofa_verify'))
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return_to = request.args.get('return_to', '') or request.form.get('return_to', '')
            if return_to:
                return redirect(return_to)
            return redirect(url_for('index'))
        else:
            error = f"Invalid credentials for user: {username}"
    return_to = request.args.get('return_to', '')
    return render_template('login.html', error=error, return_to=return_to)

@app.route('/login/blind', methods=['GET', 'POST'])
def login_blind():
    message = ''
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        db = get_db()
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        try:
            user = db.execute(query).fetchone()
        except:
            user = None
        db.close()
        if user:
            message = "Login successful!"
        else:
            message = "Login failed."
    return render_template('login_blind.html', message=message)

@app.route('/login/time', methods=['GET', 'POST'])
def login_time():
    message = ''
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        db = get_db()
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        try:
            start = time.time()
            user = db.execute(query).fetchone()
            elapsed = time.time() - start
        except Exception as e:
            user = None
            elapsed = 0
        db.close()
        if user:
            message = "Welcome back!"
        else:
            message = "Invalid credentials"
    return render_template('login_time.html', message=message)

@app.route('/login/union', methods=['GET', 'POST'])
def login_union():
    error = ''
    users_list = []
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        db = get_db()
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        try:
            users_list = db.execute(query).fetchall()
        except Exception as e:
            error = str(e)
        db.close()
    return render_template('login_union.html', users=users_list, error=error)

@app.route('/2fa-verify', methods=['GET', 'POST'])
def twofa_verify():
    message = ''
    user_id = session.get('pending_2fa_user')
    if not user_id:
        return redirect(url_for('login'))
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()
    if request.method == 'POST':
        code = request.form.get('code', '')
        backup = request.form.get('backup_code', '')
        if backup and backup in (user['backup_codes'] or '').split(','):
            session.pop('pending_2fa_user', None)
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('index'))
        if len(code) == 6 and code.isdigit():
            try:
                import pyotp
                totp = pyotp.TOTP(user['twofa_secret'])
                if totp.verify(code) or code == '000000':
                    session.pop('pending_2fa_user', None)
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['role'] = user['role']
                    return redirect(url_for('index'))
                else:
                    message = "Invalid code"
            except:
                message = "Invalid code"
        else:
            message = "Code must be 6 digits"
    db.close()
    return render_template('twofa_verify.html', message=message, user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
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
    message = ''
    if request.method == 'POST':
        email = request.form.get('email')
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
        if user:
            token = hashlib.md5(f"{email}{int(time.time()/3600)}".encode()).hexdigest()[:8]
            db.execute('INSERT OR REPLACE INTO password_resets (email, token) VALUES (?, ?)', (email, token))
            db.commit()
            reset_link = f"http://{request.host}/reset-password?token={token}&email={email}"
            message = f"Reset link: {reset_link}"
        else:
            message = "If your email exists, a reset link has been sent."
        db.close()
    return render_template('forgot_password.html', message=message)

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token', '') or request.form.get('token', '')
    email = request.args.get('email', '') or request.form.get('email', '')
    message = ''
    db = get_db()
    reset = db.execute('SELECT * FROM password_resets WHERE email=? AND token=?', (email, token)).fetchone()
    if request.method == 'POST' and reset:
        new_password = request.form.get('password', '')
        db.execute('UPDATE users SET password=? WHERE email=?', (new_password, email))
        db.commit()
        message = "Password updated successfully!"
    db.close()
    return render_template('reset_password.html', token=token, email=email, message=message, valid=bool(reset))

# ═══════════════════════════════════════════════════════════════
# PRODUCT & SEARCH (XSS + SQLi)
# ═══════════════════════════════════════════════════════════════

@app.route('/product/<int:product_id>')
def product(product_id):
    db = get_db()
    prod = db.execute('SELECT * FROM products WHERE id=?', (product_id,)).fetchone()
    reviews = db.execute('SELECT * FROM reviews WHERE product_id=?', (product_id,)).fetchall()
    db.close()
    return render_template('product.html', product=prod, reviews=reviews)

@app.route('/search')
def search():
    q = request.args.get('q', '')
    db = get_db()
    query = f"SELECT * FROM products WHERE name LIKE '%{q}%' OR description LIKE '%{q}%'"
    try:
        results = db.execute(query).fetchall()
    except Exception as e:
        results = []
        flash(f"Search error: {e}")
    db.close()
    return render_template('search.html', q=q, results=results)

@app.route('/review/<int:product_id>', methods=['POST'])
@login_required
def add_review(product_id):
    content = request.form.get('content', '')
    rating = request.form.get('rating', 5)
    db = get_db()
    db.execute(
        "INSERT INTO reviews (product_id, user_id, username, content, rating) VALUES (?, ?, ?, ?, ?)",
        (product_id, session['user_id'], session['username'], content, rating)
    )
    db.commit()
    db.close()
    flash('Review added!')
    return redirect(url_for('product', product_id=product_id))

# ═══════════════════════════════════════════════════════════════
# PROFILE (IDOR + File Upload + CSRF + XSS)
# ═══════════════════════════════════════════════════════════════

@app.route('/profile')
@login_required
def profile():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
    db.close()
    return render_template('profile.html', user=user)

@app.route('/profile/<int:user_id>')
def profile_by_id(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()
    db.close()
    if not user:
        abort(404)
    return render_template('profile.html', user=user)

@app.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    bio = request.form.get('bio', '')
    email = request.form.get('email', '')
    db = get_db()
    db.execute("UPDATE users SET bio=?, email=? WHERE id=?", (bio, email, session['user_id']))
    db.commit()
    db.close()
    flash('Profile updated')
    return redirect(url_for('profile'))

@app.route('/profile/upload', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        flash('No file')
        return redirect(url_for('profile'))
    file = request.files['avatar']
    if file.filename == '':
        flash('No filename')
        return redirect(url_for('profile'))
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    db = get_db()
    db.execute("UPDATE users SET avatar=? WHERE id=?", (filename, session['user_id']))
    db.commit()
    db.close()
    flash(f'Uploaded {filename}')
    return redirect(url_for('profile'))

# ═══════════════════════════════════════════════════════════════
# CART & CHECKOUT (Business Logic + Race Condition + IDOR)
# ═══════════════════════════════════════════════════════════════

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
    product_id = int(request.form.get('product_id'))
    qty = int(request.form.get('qty', 1))
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
        total = float(request.form.get('total', 0))
        coupon = request.form.get('coupon', '')
        db = get_db()
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
            price = item.get('price', p['price'])
            products.append({'product': p, 'qty': item['qty'], 'price': price})
            total += price * item['qty']
    db.close()
    return render_template('checkout.html', products=products, total=total)

@app.route('/order/<int:order_id>')
def order(order_id):
    db = get_db()
    order = db.execute('SELECT * FROM orders WHERE id=?', (order_id,)).fetchone()
    db.close()
    if not order:
        abort(404)
    return render_template('order.html', order=order)

@app.route('/order/<int:order_id>/export', methods=['POST'])
def export_order(order_id):
    xml_data = request.data
    if not xml_data:
        return jsonify({'error': 'No XML data'}), 400
    try:
        parser = etree.XMLParser(resolve_entities=True, no_network=False)
        root = etree.fromstring(xml_data, parser=parser)
        result = etree.tostring(root, pretty_print=True).decode()
        return jsonify({'parsed': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/order/<int:order_id>/export-oob', methods=['POST'])
def export_order_oob():
    xml_data = request.data
    if not xml_data:
        return jsonify({'error': 'No XML data'}), 400
    try:
        parser = etree.XMLParser(resolve_entities=True, no_network=False)
        root = etree.fromstring(xml_data, parser=parser)
        return jsonify({'status': 'XML processed successfully'})
    except Exception as e:
        return jsonify({'status': 'Processed', 'debug': str(e)})

# ═══════════════════════════════════════════════════════════════
# CONTACT (XSS + SSRF)
# ═══════════════════════════════════════════════════════════════

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        subject = request.form.get('subject', '')
        body = request.form.get('body', '')
        webhook_url = request.form.get('webhook_url', '')
        db = get_db()
        db.execute(
            "INSERT INTO messages (name, email, subject, body, webhook_url) VALUES (?, ?, ?, ?, ?)",
            (name, email, subject, body, webhook_url)
        )
        db.commit()
        msg_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
        db.close()
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

# ═══════════════════════════════════════════════════════════════
# ADMIN (Command Injection + SSTI + LFI + Info Disclosure)
# ═══════════════════════════════════════════════════════════════

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
    host = request.form.get('host', '127.0.0.1')
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
    template = request.form.get('template', 'Hello, {{name}}!') if request.method == 'POST' else 'Hello, {{name}}!'
    name = request.form.get('name', 'Admin') if request.method == 'POST' else 'Admin'
    try:
        rendered = render_template_string(template, name=name)
    except Exception as e:
        rendered = f"Template Error: {e}"
    return render_template('admin_result.html', title='Greeting', output=rendered)

@app.route('/admin/fetch', methods=['POST'])
@admin_required
def admin_fetch():
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
    filename = request.args.get('file', 'app.py')
    try:
        with open(filename, 'r') as f:
            content = f.read()
        return render_template('admin_result.html', title=f'View: {filename}', output=content)
    except Exception as e:
        return render_template('admin_result.html', title='Error', output=str(e))

# ═══════════════════════════════════════════════════════════════
# ADDITIONAL VULNERABILITY ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route('/download')
def download():
    filename = request.args.get('file', 'laptop.jpg')
    return send_from_directory('static/images', filename)

@app.route('/redirect')
def redirect_page():
    url = request.args.get('url', '/')
    return redirect(url)

@app.route('/redirect/filtered')
def redirect_filtered():
    url = request.args.get('url', '/')
    if url.startswith('http://') and 'evil' not in url.lower():
        return redirect(url)
    return redirect(url)

# ─── CRLF Injection ───
@app.route('/crlf-test')
def crlf_test():
    next_page = request.args.get('next', '/')
    resp = make_response(redirect(next_page))
    resp.headers['X-Next-Page'] = next_page
    return resp

# ─── Cache Poisoning ───
@app.route('/cache-poison')
def cache_poison():
    custom_header = request.headers.get('X-Custom-Header', '')
    resp = make_response(render_template_string(f"<h1>Welcome</h1><p>Custom: {custom_header}</p>"))
    resp.headers['X-Cache-Key'] = f"page_{custom_header}"
    resp.headers['Cache-Control'] = 'public, max-age=3600'
    return resp

# ─── Cache Deception ───
@app.route('/profile/<int:user_id>.css')
def profile_css(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()
    db.close()
    resp = make_response(f"/* User profile data */\n/* ID: {user_id} */\n/* Name: {user['username']} */\n/* Email: {user['email']} */\n/* Role: {user['role']} */")
    resp.headers['Content-Type'] = 'text/css'
    resp.headers['Cache-Control'] = 'public, max-age=86400'
    return resp

# ─── HTTP Request Smuggling ───
@app.route('/smuggle-test', methods=['POST'])
def smuggle_test():
    data = request.get_data(as_text=True)
    cl = request.headers.get('Content-Length', '')
    te = request.headers.get('Transfer-Encoding', '')
    return jsonify({
        'received': data,
        'content_length': cl,
        'transfer_encoding': te,
        'parsed_body': request.form.to_dict()
    })

# ─── Secondary Context ───
@app.route('/api/user-data')
def api_user_data():
    user_id = request.args.get('id', '1')
    db = get_db()
    user = db.execute('SELECT id, username, email, bio FROM users WHERE id=?', (user_id,)).fetchone()
    db.close()
    if user:
        return jsonify({
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'bio': user['bio'] or '',
            'html_preview': f"<div class='bio'>{user['bio'] or 'No bio'}</div>"
        })
    return jsonify({'error': 'Not found'}), 404

# ─── Race Condition ───
@app.route('/race-coupon', methods=['POST'])
@login_required
def race_coupon():
    coupon = request.form.get('coupon', '')
    db = get_db()
    c = db.execute('SELECT * FROM coupons WHERE code=?', (coupon,)).fetchone()
    if c and c['used'] < c['max_uses']:
        time.sleep(0.1)
        db.execute('UPDATE coupons SET used=used+1 WHERE code=?', (coupon,))
        db.commit()
        flash(f'Coupon {coupon} applied! Discount: {c["discount"]}%')
    else:
        flash('Invalid or expired coupon')
    db.close()
    return redirect(url_for('checkout'))

# ═══════════════════════════════════════════════════════════════
# API VULNERABILITIES
# ═══════════════════════════════════════════════════════════════

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    db = get_db()
    if isinstance(username, dict):
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
    origin = request.headers.get('Origin', '*')
    resp = make_response()
    resp.headers['Access-Control-Allow-Origin'] = origin
    resp.headers['Access-Control-Allow-Credentials'] = 'true'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    if request.method == 'OPTIONS':
        return resp
    auth = request.headers.get('Authorization', '')
    token = auth.replace('Bearer ', '') if auth.startswith('Bearer ') else None
    if token:
        payload = decode_jwt(token, verify=False)
    else:
        payload = None
    db = get_db()
    user = db.execute('SELECT id, username, email, role, bio, avatar FROM users WHERE id=?', (user_id,)).fetchone()
    db.close()
    if user:
        resp.set_data(jsonify(dict(user)).data)
        resp.mimetype = 'application/json'
        return resp
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/search', methods=['GET'])
def api_search():
    q = request.args.get('q', '')
    db = get_db()
    query = f"SELECT * FROM products WHERE name LIKE '%{q}%'"
    results = db.execute(query).fetchall()
    db.close()
    return jsonify([dict(r) for r in results])

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
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

# ─── JWT Vulnerabilities ───
@app.route('/api/jwt/weak', methods=['POST'])
def jwt_weak():
    data = request.get_json() or {}
    username = data.get('username', 'guest')
    token = generate_jwt(0, username, 'user', alg='HS256')
    return jsonify({'token': token, 'note': 'Signed with weak secret'})

@app.route('/api/jwt/none', methods=['POST'])
def jwt_none():
    data = request.get_json() or {}
    username = data.get('username', 'guest')
    token = generate_jwt(0, username, 'user', alg='none')
    return jsonify({'token': token, 'note': 'alg:none - no signature!'})

@app.route('/api/jwt/verify', methods=['POST'])
def jwt_verify():
    data = request.get_json() or {}
    token = data.get('token', '')
    payload = decode_jwt(token, verify=False)
    if payload:
        return jsonify({'valid': True, 'payload': payload})
    return jsonify({'valid': False}), 401

@app.route('/api/jwt/key-confusion', methods=['POST'])
def jwt_key_confusion():
    data = request.get_json() or {}
    token = data.get('token', '')
    try:
        pub_key = open('static/public_key.pem', 'rb').read() if os.path.exists('static/public_key.pem') else b'fake'
        payload = jwt.decode(token, pub_key, algorithms=['HS256'])
        return jsonify({'valid': True, 'payload': payload})
    except Exception as e:
        return jsonify({'valid': False, 'error': str(e)}), 401

# ─── OAuth Misconfiguration ───
@app.route('/oauth/authorize')
def oauth_authorize():
    client_id = request.args.get('client_id', '')
    redirect_uri = request.args.get('redirect_uri', '')
    scope = request.args.get('scope', 'read')
    if 'bugbountymart' in redirect_uri or not redirect_uri:
        code = hashlib.sha256(f"{client_id}{time.time()}".encode()).hexdigest()[:16]
        db = get_db()
        db.execute('INSERT INTO oauth_tokens (token, user_id, scope) VALUES (?, ?, ?)', (code, 1, scope))
        db.commit()
        db.close()
        if redirect_uri:
            return redirect(f"{redirect_uri}?code={code}")
        return jsonify({'code': code})
    return jsonify({'error': 'Invalid redirect_uri'}), 400

@app.route('/oauth/token', methods=['POST'])
def oauth_token():
    code = request.form.get('code', '')
    db = get_db()
    token = db.execute('SELECT * FROM oauth_tokens WHERE token=?', (code,)).fetchone()
    db.close()
    if token:
        access_token = generate_jwt(token['user_id'], 'oauth_user', 'user')
        return jsonify({'access_token': access_token, 'token_type': 'Bearer'})
    return jsonify({'error': 'Invalid code'}), 400

# ─── SAML Vulnerability ───
@app.route('/saml/acs', methods=['POST'])
def saml_acs():
    saml_response = request.form.get('SAMLResponse', '')
    try:
        decoded = base64.b64decode(saml_response).decode()
        if '<NameID>' in decoded:
            import re
            nameid = re.search(r'<NameID>(.*?)</NameID>', decoded)
            if nameid:
                username = nameid.group(1)
                db = get_db()
                user = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
                db.close()
                if user:
                    session['user_id'] = user['id']
                    session['username'] = user['username']
                    session['role'] = user['role']
                    return redirect(url_for('index'))
        return jsonify({'error': 'Invalid SAML'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ─── Brute Force ───
@app.route('/login/brute', methods=['GET', 'POST'])
def login_brute():
    error = ''
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        db.close()
        if user:
            if user['password'] == password:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                return redirect(url_for('index'))
            else:
                error = "Password incorrect"
        else:
            error = "Username not found"
    return render_template('login_brute.html', error=error)

# ─── GraphQL (Simulated) ───
@app.route('/graphql', methods=['GET', 'POST'])
def graphql():
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
        if 'introspection' in query.lower() or '__schema' in query.lower() or request.method == 'GET':
            return jsonify(schema)
        if 'users' in query.lower():
            db = get_db()
            users = db.execute('SELECT id, username, email, role FROM users').fetchall()
            db.close()
            return jsonify({'data': {'users': [dict(u) for u in users]}})
    return jsonify(schema)

# ─── NoSQL Injection ───
@app.route('/api/nosql/login', methods=['POST'])
def nosql_login():
    """VULNERABLE: NoSQL Injection via JSON operators"""
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    db = get_db()
    if isinstance(username, dict):
        # Simulating NoSQL injection - any dict bypasses auth
        user = db.execute("SELECT * FROM users WHERE username='admin'").fetchone()
    else:
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
    db.close()
    if user:
        return jsonify({'success': True, 'user': dict(user)})
    return jsonify({'success': False}), 401

# ─── Deserialization ───
@app.route('/api/deserialize', methods=['POST'])
def deserialize():
    """VULNERABLE: Insecure Deserialization with pickle"""
    data = request.data
    try:
        # VULNERABLE: pickle.loads on untrusted data
        obj = pickle.loads(data)
        return jsonify({'result': str(obj)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/yaml/load', methods=['POST'])
def yaml_load():
    """VULNERABLE: Unsafe YAML loading"""
    data = request.data.decode()
    try:
        # VULNERABLE: yaml.load without SafeLoader
        obj = yaml.load(data, Loader=yaml.FullLoader)
        return jsonify({'result': str(obj)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ─── XPath Injection ───
@app.route('/api/xpath/search', methods=['GET'])
def xpath_search():
    """VULNERABLE: XPath Injection"""
    q = request.args.get('q', '')
    # Simulated XML data
    xml_data = """<?xml version="1.0"?>
    <users>
        <user><username>admin</username><password>admin123</password></user>
        <user><username>alice</username><password>password</password></user>
        <user><username>bob</username><password>123456</password></user>
    </users>"""
    try:
        root = ET.fromstring(xml_data)
        # VULNERABLE: XPath query built from user input
        xpath_query = f".//user[username='{q}']"
        results = root.findall(xpath_query)
        output = []
        for r in results:
            output.append({
                'username': r.find('username').text,
                'password': r.find('password').text
            })
        return jsonify({'results': output, 'query': xpath_query})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ─── LDAP Injection ───
@app.route('/api/ldap/search', methods=['GET'])
def ldap_search():
    """VULNERABLE: LDAP Injection"""
    uid = request.args.get('uid', '')
    # VULNERABLE: LDAP filter built from user input
    ldap_filter = f"(uid={uid})"
    # Simulated LDAP search
    users = [
        {'uid': 'admin', 'cn': 'Administrator', 'mail': 'admin@bugbountymart.local'},
        {'uid': 'alice', 'cn': 'Alice Smith', 'mail': 'alice@example.com'},
        {'uid': 'bob', 'cn': 'Bob Jones', 'mail': 'bob@example.com'}
    ]
    # Simulated vulnerable filter evaluation
    if '*)(uid=*' in uid or '(&' in uid:
        return jsonify({'results': users, 'filter': ldap_filter})
    result = [u for u in users if u['uid'] == uid]
    return jsonify({'results': result, 'filter': ldap_filter})

# ─── Clickjacking ───
@app.route('/clickjacking-demo')
def clickjacking_demo():
    """VULNERABLE: Page without X-Frame-Options"""
    resp = make_response(render_template('clickjacking.html'))
    # Intentionally missing X-Frame-Options
    return resp

# ─── PostMessage ───
@app.route('/postmessage-demo')
def postmessage_demo():
    """VULNERABLE: PostMessage without origin validation"""
    return render_template('postmessage.html')

# ─── Client-Side Template Injection ───
@app.route('/csti-demo')
def csti_demo():
    """VULNERABLE: Client-side template injection with Vue.js"""
    return render_template('csti.html')

# ─── Prototype Pollution ───
@app.route('/api/config', methods=['GET'])
def api_config():
    """VULNERABLE: Prototype Pollution via query params"""
    # Merge query params into config object (simulated)
    config = {'theme': 'light', 'admin': False}
    for key, value in request.args.items():
        # VULNERABLE: Direct property assignment without validation
        if key.startswith('__proto__') or key.startswith('constructor'):
            # In a real app, this would pollute the prototype
            pass
        config[key] = value
    return jsonify(config)

# ─── Cloud Storage Misconfiguration ───
@app.route('/s3-bucket/<path:bucket_path>')
def s3_bucket(bucket_path):
    """VULNERABLE: Simulated S3 bucket with public access"""
    # Simulating public S3 bucket listing
    return jsonify({
        'bucket': bucket_path,
        'contents': ['config.json', 'backup.zip', 'credentials.csv', 'private_keys/'],
        'permissions': 'public-read-write',
        'message': 'This bucket is publicly accessible'
    })

# ─── Subdomain Takeover ───
@app.route('/subdomain-check')
def subdomain_check():
    """VULNERABLE: Simulated subdomain takeover detection"""
    subdomain = request.args.get('subdomain', '')
    # Simulated CNAME check
    cname_records = {
        'blog.bugbountymart.local': 'nonexistent.github.io',
        'shop.bugbountymart.local': 'bugbountymart.herokuapp.com',
        'cdn.bugbountymart.local': 'd111111abcdef8.cloudfront.net'
    }
    if subdomain in cname_records:
        return jsonify({
            'subdomain': subdomain,
            'cname': cname_records[subdomain],
            'status': 'vulnerable',
            'message': 'CNAME points to non-existent service - subdomain takeover possible'
        })
    return jsonify({'subdomain': subdomain, 'status': 'not_found'})

# ─── DNS Zone Transfer ───
@app.route('/dns/zone-transfer')
def dns_zone_transfer():
    """VULNERABLE: Simulated DNS zone transfer"""
    domain = request.args.get('domain', 'bugbountymart.local')
    # VULNERABLE: No auth check for zone transfer
    zones = {
        'bugbountymart.local': {
            'A': {'www': '192.168.1.10', 'admin': '192.168.1.11', 'api': '192.168.1.12'},
            'CNAME': {'blog': 'nonexistent.github.io', 'shop': 'bugbountymart.herokuapp.com'},
            'MX': {'mail': 'mail.bugbountymart.local'},
            'TXT': {'verification': 'v=spf1 include:_spf.google.com ~all'},
            'NS': {'ns1': 'ns1.bugbountymart.local', 'ns2': 'ns2.bugbountymart.local'}
        }
    }
    if domain in zones:
        return jsonify({'domain': domain, 'zone': zones[domain], 'transfer_allowed': True})
    return jsonify({'error': 'Zone not found'}), 404

# ─── Virtual Host Enumeration ───
@app.route('/vhost-check')
def vhost_check():
    """VULNERABLE: Virtual host discovery"""
    host = request.headers.get('Host', '')
    vhosts = {
        'admin.bugbountymart.local': {'status': 'active', 'note': 'Admin panel accessible'},
        'api.bugbountymart.local': {'status': 'active', 'note': 'API documentation exposed'},
        'staging.bugbountymart.local': {'status': 'active', 'note': 'Debug mode enabled'},
        'dev.bugbountymart.local': {'status': 'active', 'note': 'Source code exposed'},
        'internal.bugbountymart.local': {'status': 'active', 'note': 'Internal tools'}
    }
    if host in vhosts:
        return jsonify({'vhost': host, **vhosts[host]})
    return jsonify({'vhost': host, 'status': 'default', 'available_vhosts': list(vhosts.keys())})

# ─── Fuzzing & Hidden Parameters ───
@app.route('/api/debug')
def api_debug():
    """VULNERABLE: Hidden debug endpoint"""
    debug = request.args.get('debug', '')
    admin = request.args.get('admin', '')
    if debug == 'true':
        return jsonify({
            'debug': True,
            'env': dict(os.environ),
            'config': {'secret_key': app.secret_key, 'database': DATABASE},
            'routes': [str(rule) for rule in app.url_map.iter_rules()]
        })
    if admin == 'true':
        db = get_db()
        users = db.execute('SELECT * FROM users').fetchall()
        db.close()
        return jsonify({'admin_mode': True, 'users': [dict(u) for u in users]})
    return jsonify({'message': 'API is working'})

# ═══════════════════════════════════════════════════════════════
# INFORMATION DISCLOSURE
# ═══════════════════════════════════════════════════════════════

@app.route('/.git/HEAD')
def git_head():
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
    if os.path.exists(DATABASE):
        return send_file(DATABASE, mimetype='application/octet-stream')
    return 'Not found', 404

@app.route('/phpinfo.php')
def phpinfo():
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
Disallow: /ctf
Disallow: /api/debug
"""

@app.route('/sitemap.xml')
def sitemap():
    return """<?xml version="1.0" encoding="UTF-8"?>
<urlset>
  <url><loc>https://bugbountymart.local/</loc></url>
  <url><loc>https://bugbountymart.local/admin</loc></url>
  <url><loc>https://bugbountymart.local/api/search</loc></url>
  <url><loc>https://bugbountymart.local/ctf</loc></url>
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
    return f"""
    <h1>404 Not Found</h1>
    <p>The requested URL {request.path} was not found on this server.</p>
    <p>Server: Werkzeug/3.0.3 Python/{os.sys.version_info.major}.{os.sys.version_info.minor}</p>
    <p>Trace: {e}</p>
    """, 404

@app.errorhandler(500)
def server_error(e):
    import traceback
    return f"""
    <h1>500 Internal Server Error</h1>
    <pre>{traceback.format_exc()}</pre>
    """, 500

# ─── Main ───
if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('static/images', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    init_db()
    print("=" * 60)
    print("BugBountyMart v2.0 — Ultimate Bug Bounty Practice Lab")
    print("=" * 60)
    print("URL: http://127.0.0.1:5000")
    print("Admin: admin / admin123")
    print("CTF Mode: http://127.0.0.1:5000/ctf")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
