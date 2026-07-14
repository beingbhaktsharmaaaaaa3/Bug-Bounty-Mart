"""
BugBountyMart v2.1 — Global Difficulty Configuration

Before running the app, set your desired difficulty level here.
Options: 'easy', 'medium', 'hard'

After changing, restart the Flask app for changes to take effect.
"""

# ═══════════════════════════════════════════════════════════════
# GLOBAL DIFFICULTY SETTING
# Change this value before running python app.py
# ═══════════════════════════════════════════════════════════════

DIFFICULTY = 'easy'  # Options: 'easy', 'medium', 'hard'

# ═══════════════════════════════════════════════════════════════
# DIFFICULTY-SPECIFIC SETTINGS (Auto-applied based on DIFFICULTY)
# Do NOT modify below unless you know what you're doing
# ═══════════════════════════════════════════════════════════════

DIFFICULTY_CONFIG = {
    'easy': {
        'name': 'Easy',
        'points_multiplier': 1,
        # SQL Injection
        'sqli_verbose_errors': True,
        'sqli_show_query': True,
        'sqli_delay_seconds': 5,
        'sqli_blind_hints': True,
        # XSS
        'xss_filter_level': 'none',       # No filtering
        'xss_csp_enabled': False,
        'xss_encoding_required': False,
        # Command Injection
        'cmdi_filter_chars': [],          # No filtering
        'cmdi_blind_mode': False,
        # File Upload
        'upload_check_extension': False,
        'upload_check_mime': False,
        'upload_check_magic': False,
        # SSTI
        'ssti_filter_keywords': [],       # No filtering
        'ssti_sandboxed': False,
        # SSRF
        'ssrf_block_private_ips': False,
        'ssrf_dns_rebind_required': False,
        # JWT
        'jwt_weak_secret_in_source': True,
        'jwt_none_alg_accepted': True,
        'jwt_key_confusion_possible': True,
        # Auth
        'auth_rate_limit': False,
        'auth_2fa_backup_predictable': True,
        'auth_password_reset_token_predictable': True,
        # Info Disclosure
        'error_show_stacktrace': True,
        'error_show_query': True,
        'git_exposed': True,
        'env_exposed': True,
        # IDOR
        'idor_strict_check': False,
        # CSRF
        'csrf_token_required': False,
        # Path Traversal
        'path_traversal_filter': False,
        'path_traversal_encoding_check': False,
        # Cache
        'cache_headers_present': False,
        # Clickjacking
        'x_frame_options_set': False,
        # PostMessage
        'postmessage_origin_check': False,
        # Prototype Pollution
        'prototype_pollution_protection': False,
        # Hints
        'show_vulnerability_hints': True,
        'show_flag_locations': True,
    },
    'medium': {
        'name': 'Medium',
        'points_multiplier': 2,
        # SQL Injection
        'sqli_verbose_errors': True,
        'sqli_show_query': False,
        'sqli_delay_seconds': 2,
        'sqli_blind_hints': False,
        # XSS
        'xss_filter_level': 'basic',      # Filters <script> tags
        'xss_csp_enabled': False,
        'xss_encoding_required': False,
        # Command Injection
        'cmdi_filter_chars': [';', '&', '|'],  # Blocks common separators
        'cmdi_blind_mode': False,
        # File Upload
        'upload_check_extension': True,
        'upload_check_mime': False,
        'upload_check_magic': False,
        # SSTI
        'ssti_filter_keywords': ['config', 'os', 'subprocess'],  # Basic filtering
        'ssti_sandboxed': False,
        # SSRF
        'ssrf_block_private_ips': True,
        'ssrf_dns_rebind_required': False,
        # JWT
        'jwt_weak_secret_in_source': False,
        'jwt_none_alg_accepted': True,
        'jwt_key_confusion_possible': True,
        # Auth
        'auth_rate_limit': False,
        'auth_2fa_backup_predictable': False,
        'auth_password_reset_token_predictable': False,
        # Info Disclosure
        'error_show_stacktrace': False,
        'error_show_query': False,
        'git_exposed': True,
        'env_exposed': True,
        # IDOR
        'idor_strict_check': False,
        # CSRF
        'csrf_token_required': False,
        # Path Traversal
        'path_traversal_filter': True,
        'path_traversal_encoding_check': False,
        # Cache
        'cache_headers_present': False,
        # Clickjacking
        'x_frame_options_set': False,
        # PostMessage
        'postmessage_origin_check': False,
        # Prototype Pollution
        'prototype_pollution_protection': False,
        # Hints
        'show_vulnerability_hints': True,
        'show_flag_locations': False,
    },
    'hard': {
        'name': 'Hard',
        'points_multiplier': 3,
        # SQL Injection
        'sqli_verbose_errors': False,
        'sqli_show_query': False,
        'sqli_delay_seconds': 1,
        'sqli_blind_hints': False,
        # XSS
        'xss_filter_level': 'strict',     # Multiple filters + encoding
        'xss_csp_enabled': True,
        'xss_encoding_required': True,
        # Command Injection
        'cmdi_filter_chars': [';', '&', '|', '$', '`', '$(', '${'],
        'cmdi_blind_mode': True,
        # File Upload
        'upload_check_extension': True,
        'upload_check_mime': True,
        'upload_check_magic': True,
        # SSTI
        'ssti_filter_keywords': ['config', 'os', 'subprocess', 'import', '__', 'class', 'mro'],
        'ssti_sandboxed': True,
        # SSRF
        'ssrf_block_private_ips': True,
        'ssrf_dns_rebind_required': True,
        # JWT
        'jwt_weak_secret_in_source': False,
        'jwt_none_alg_accepted': False,
        'jwt_key_confusion_possible': True,
        # Auth
        'auth_rate_limit': True,
        'auth_2fa_backup_predictable': False,
        'auth_password_reset_token_predictable': False,
        # Info Disclosure
        'error_show_stacktrace': False,
        'error_show_query': False,
        'git_exposed': False,
        'env_exposed': False,
        # IDOR
        'idor_strict_check': True,
        # CSRF
        'csrf_token_required': True,
        # Path Traversal
        'path_traversal_filter': True,
        'path_traversal_encoding_check': True,
        # Cache
        'cache_headers_present': True,
        # Clickjacking
        'x_frame_options_set': True,
        # PostMessage
        'postmessage_origin_check': True,
        # Prototype Pollution
        'prototype_pollution_protection': True,
        # Hints
        'show_vulnerability_hints': False,
        'show_flag_locations': False,
    }
}

# Validate difficulty
if DIFFICULTY not in DIFFICULTY_CONFIG:
    raise ValueError(f"Invalid DIFFICULTY: {DIFFICULTY}. Must be 'easy', 'medium', or 'hard'.")

# Export current config
CURRENT_CONFIG = DIFFICULTY_CONFIG[DIFFICULTY]

# Helper function to check current difficulty settings
def is_easy():
    return DIFFICULTY == 'easy'

def is_medium():
    return DIFFICULTY == 'medium'

def is_hard():
    return DIFFICULTY == 'hard'

def get_config(key, default=None):
    return CURRENT_CONFIG.get(key, default)
