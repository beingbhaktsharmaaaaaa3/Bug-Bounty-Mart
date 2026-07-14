# BugBountyMart v2.0 — Ultimate Bug Bounty Practice Lab

> **WARNING**: This application is intentionally vulnerable. DO NOT deploy in production. For educational purposes only.

## What's New in v2.0

- **34 Vulnerability Categories** with multiple variants each
- **CTF Mode** at `/ctf` with 50+ challenges
- **3 Difficulty Levels**: Easy (100 pts), Medium (200 pts), Hard (300 pts)
- **Flag Verification System** with progress tracking
- **Hint System** for each challenge
- **Reset Progress** option for repeated practice

## Quick Start

```bash
#clone repo
cd Bug-Bounty-Mart
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# 3. Set difficulty (edit config.py first)
nano config.py  # Change DIFFICULTY = 'easy, medium, hard'

# Run the application
python app.py

# Access the lab
Main site: http://127.0.0.1:5000
CTF mode:  http://127.0.0.1:5000/ctf
Difficulty info: http://127.0.0.1:5000/difficulty
```

## Default Credentials

| Username | Password | Role | 2FA |
|----------|----------|------|-----|
| admin | admin123 | admin | Enabled |
| alice | password | user | Disabled |
| bob | 123456 | user | Disabled |
| charlie | qwerty | user | Disabled |
| support | support2024 | support | Disabled |

## Vulnerability Map

### Injection Bugs (13)
1. **SQL Injection - Error Based** — `/login` (verbose errors)
2. **SQL Injection - Boolean Blind** — `/login/blind` (true/false only)
3. **SQL Injection - Time Based** — `/login/time` (SLEEP delays)
4. **SQL Injection - Union Based** — `/login/union` (data extraction)
5. **Command Injection** — `/admin/ping` (OS command execution)
6. **SSTI (Server-Side Template Injection)** — `/admin/greeting` (Jinja2)
7. **XXE (XML External Entity)** — `/order/<id>/export` (file read)
8. **XXE - Out of Band** — `/order/<id>/export-oob` (blind exfiltration)
9. **CRLF Injection** — `/crlf-test` (header injection)
10. **NoSQL Injection** — `/api/nosql/login` (JSON operators)
11. **Deserialization** — `/api/deserialize` (pickle)
12. **YAML Deserialization** — `/api/yaml/load` (unsafe yaml)
13. **XPath Injection** — `/api/xpath/search` (XML query injection)
14. **LDAP Injection** — `/api/ldap/search` (filter bypass)

### Server Side Logic Bugs (11)
15. **SSRF** — `/admin/fetch`, `/contact` (server-side requests)
16. **SSRF - DNS Rebinding** — Simulated via `/admin/fetch`
17. **File Upload** — `/profile/upload` (unrestricted upload)
18. **Path Traversal** — `/download` (directory escape)
19. **LFI (Local File Inclusion)** — `/admin/view` (local file read)
20. **RFI (Remote File Inclusion)** — `/admin/view` (remote file fetch)
21. **Cache Poisoning** — `/cache-poison` (header-based poisoning)
22. **Cache Deception** — `/profile/<id>.css` (extension trick)
23. **HTTP Request Smuggling** — `/smuggle-test` (CL.TE / TE.CL)
24. **Secondary Context** — `/api/user-data` (JSON to HTML context)
25. **Race Condition** — `/race-coupon`, `/checkout` (timing attacks)

### Client Side Bugs (9)
26. **XSS - Reflected** — `/search`, `/login` (immediate reflection)
27. **XSS - Stored** — `/review`, `/contact`, `/profile` (persistent)
28. **XSS - DOM** — `/product/<id>` (hash-based innerHTML)
29. **CSRF** — `/profile/update`, `/cart/add` (no token)
30. **Open Redirect** — `/redirect`, `/login` (arbitrary URLs)
31. **CSTI** — `/csti-demo` (client-side template injection)
32. **PostMessage** — `/postmessage-demo` (no origin validation)
33. **Prototype Pollution** — `/api/config` (Object.prototype pollution)
34. **Clickjacking** — `/clickjacking-demo` (missing X-Frame-Options)

### Authentication Bugs (8)
35. **JWT - Weak Secret** — `/api/jwt/weak` (brute-forceable)
36. **JWT - None Algorithm** — `/api/jwt/none` (signature bypass)
37. **JWT - Key Confusion** — `/api/jwt/key-confusion` (RS256→HS256)
38. **2FA Bypass** — `/2fa-verify` (weak backup codes)
39. **Brute Force** — `/login/brute` (no rate limiting)
40. **Password Reset** — `/forgot-password` (predictable tokens)
41. **OAuth Misconfiguration** — `/oauth/authorize` (missing state)
42. **SAML Vulnerability** — `/saml/acs` (no signature validation)

### Authorization Bugs (4)
43. **IDOR** — `/profile/<id>`, `/order/<id>` (missing auth checks)
44. **Access Control** — `/admin` (role check only)
45. **Mass Assignment** — `/register`, `/api/register` (extra fields)
46. **Information Disclosure** — Multiple endpoints (verbose errors, git, env)

### Infrastructure (2)
47. **Cloud Storage Misconfiguration** — `/s3-bucket/<path>` (public bucket)
48. **Subdomain Takeover** — `/subdomain-check` (CNAME to dead service)

### Web Enumeration (4)
49. **Files & Directories** — `/.git/HEAD`, `/.env`, `/backup.sql`
50. **Virtual Hosts** — `/vhost-check` (Host header enumeration)
51. **Fuzzing & Parameters** — `/api/debug` (hidden debug params)
52. **DNS Zone Transfer** — `/dns/zone-transfer` (AXFR simulation)

## CTF Mode

Navigate to `/ctf` to access the CTF dashboard.

### Features
- **Challenge Cards**: Organized by category with Easy/Medium/Hard tabs
- **Flag Verification**: Submit flags to mark challenges as solved
- **Progress Tracking**: Visual progress bar, points, and solved count
- **Hint System**: Click the lightbulb icon for hints
- **Reset**: Start fresh anytime with the reset button

### Flag Format
All flags follow the format: `ctf{category_name_difficulty_random}`

Example: `ctf{sqli_error_based_easy_a1b2c3}`

## Practice Tips

1. **Start with Easy mode** to understand the vulnerability
2. **Read the hints** if you're stuck (no penalty!)
3. **Use Burp Suite** or similar tools for intercepting requests
4. **Check the source code** — it's open for learning
5. **Try all difficulty levels** — they have different exploitation paths

## Tools Recommended

- Burp Suite / OWASP ZAP
- sqlmap (for SQLi practice)
- jwt_tool (for JWT attacks)
- ffuf / gobuster (for enumeration)
- Postman (for API testing)

## License

Educational Use Only. The authors are not responsible for misuse.
