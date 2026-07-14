# BugBountyMart — Bug Bounty Practice Lab

> **⚠️ WARNING: This application is intentionally vulnerable. DO NOT deploy it on any public-facing server or production environment. Use it only in isolated local environments for educational purposes.**

A realistic e-commerce web application designed for practicing bug bounty hunting techniques. It contains **16+ vulnerability classes** mapped to real-world bug bounty scenarios.

## Features

- Realistic e-commerce UI (products, cart, checkout, orders)
- User authentication & profiles
- Admin dashboard
- REST API endpoints
- File uploads, search, contact form
- XML import/export

## Vulnerabilities Included

| # | Vulnerability | Location | How to Find |
|---|-------------|----------|-------------|
| 1 | **Reflected XSS** | `/search`, `/contact`, login error | Input reflects in response without encoding |
| 2 | **Stored XSS** | Product reviews, contact messages | Input saved to DB and rendered later |
| 3 | **DOM XSS** | `/product/<id>` (hash-based) | `location.hash` used in innerHTML |
| 4 | **SQL Injection** | `/login`, `/search`, `/api/search` | Concatenated SQL queries |
| 5 | **NoSQL Injection** | `/api/login` | JSON-based auth bypass |
| 6 | **SSRF** | `/contact` (webhook), `/admin/fetch` | URL parameter fetches remote resource |
| 7 | **IDOR** | `/order/<id>`, `/profile/<id>`, `/api/user` | Sequential numeric IDs, no authorization check |
| 8 | **Open Redirect** | `/login`, `/redirect` | `return_to` parameter |
| 9 | **LFI / Path Traversal** | `/download`, `/admin/view` | File parameter loads server files |
| 10 | **OS Command Injection** | `/admin/ping` | User input passed to os.system |
| 11 | **SSTI** | `/admin/greeting` | render_template_string with user input |
| 12 | **XXE** | `/import` | XML parsed with external entities enabled |
| 13 | **CSRF** | `/profile/update`, `/cart/add` | No CSRF tokens on state-changing actions |
| 14 | **JWT Attacks** | `/api/*` | `none` algorithm, weak secret, no expiry |
| 15 | **File Upload** | `/profile/upload` | No extension/type validation |
| 16 | **CORS Misconfig** | `/api/*` | `Access-Control-Allow-Origin: *` + credentials |
| 17 | **Business Logic** | `/checkout` | Price/quantity manipulation, negative values |
| 18 | **Race Condition** | `/checkout/apply-coupon` | No atomic coupon validation |
| 19 | **Information Disclosure** | `/.git/HEAD`, `/actuator/env`, `/backup.sql`, stack traces | Sensitive endpoints exposed |
| 20 | **GraphQL Introspection** | `/graphql` | Schema exposed |
| 21 | **Host Header Injection** | `/forgot-password` | Password reset link uses Host header |
| 22 | **Mass Assignment** | `/api/register` | Extra fields accepted (role, is_admin) |

## Quick Start

### Option 1: Local Python
```bash
cd bugbounty_lab
pip install -r requirements.txt
python app.py
# Open http://127.0.0.1:5000
```

### Option 2: Docker
```bash
cd bugbounty_lab
docker build -t bugbounty-lab .
docker run -p 5000:5000 bugbounty-lab
```

## Default Accounts

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |
| alice | password | Customer |
| bob | 123456 | Customer |
| charlie | qwerty | Customer |

## Practice Workflow

1. **Recon**: Browse the site, check `/.git/HEAD`, `/robots.txt`, `/actuator/env`, `/swagger`
2. **Auth**: Try SQLi on login, JWT manipulation on API, register with `role=admin`
3. **XSS**: Test search box, contact form, product reviews
4. **IDOR**: Change order IDs, profile IDs in URLs
5. **Business Logic**: Modify price/quantity in checkout request
6. **File Upload**: Upload PHP shell to `/profile/upload`
7. **Admin**: Access `/admin`, test ping command, SSTI in greeting
8. **SSRF**: Use contact webhook or admin fetch to hit internal IPs
9. **XXE**: Import XML file with external entities
10. **Race**: Apply single-use coupon multiple times rapidly

## Tips

- Use **Burp Suite** or **OWASP ZAP** to intercept and modify requests
- Check browser DevTools for JS source code hints
- Try both `GET` and `POST` for API endpoints
- Look at response headers for CORS and JWT clues

## License

MIT — Educational use only. The authors are not responsible for misuse.
