#!/usr/bin/env python3
"""Deploy stephanie-richard-wedding to Netlify via REST API (CLI-hang fallback)."""
import json, hashlib, time, urllib.request, urllib.error, os, sys

TOKEN = json.load(open(os.path.expanduser("~/.netlify/config.json")))["accessTokens"]["default"]
API = "https://api.netlify.com"
SITE_NAME = "stephanierichard"
SITE_ID = sys.argv[1] if len(sys.argv) > 1 else None

def api(method, path, data=None, ctype=None, raw=False):
    headers = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "Mozilla/5.0"}
    body = None
    if data is not None:
        if isinstance(data, bytes):
            body = data
            if ctype: headers["Content-Type"] = ctype
        else:
            body = json.dumps(data).encode()
            headers["Content-Type"] = ctype or "application/json"
    req = urllib.request.Request(f"{API}{path}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            content = r.read().decode()
            return r.status, (content if raw or not content else json.loads(content))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]

def sha1(p):
    return hashlib.sha1(open(p, "rb").read()).hexdigest()

# 1. create or reuse the site
if SITE_ID:
    code, site = api("GET", f"/api/v1/sites/{SITE_ID}")
else:
    code, site = api("POST", "/api/v1/sites", {"name": SITE_NAME})
print("site:", code, site.get("id") if isinstance(site, dict) else site)
if code not in (200, 201):
    sys.exit(1)
site_id = site["id"]

# 2. make it public (API-created sites default to edge-access SSO)
code, site = api("PUT", f"/api/v1/sites/{site_id}", {"sso_login": False})
print("sso_login off:", code)

# 3. create deploy
code, dep = api("POST", f"/api/v1/sites/{site_id}/deploys", b"")
print("deploy created:", code, dep.get("id") if isinstance(dep, dict) else dep)
if code not in (200, 201):
    # site already has a deploy in progress? create draft-style with async
    code, dep = api("POST", f"/api/v1/sites/{site_id}/deploys", {"async": False})
    print("deploy retry:", code, dep)
    sys.exit(1) if code not in (200, 201) else None
dep_id = dep["id"]

# files to publish — index.html + everything under photos/ (skip docs/scripts)
SKIP = {"README.md", "webhook.gs", "deploy_netlify.py", ".DS_Store"}
files_map = {}
for root, dirs, names in os.walk("."):
    dirs[:] = [d for d in dirs if d not in (".git", "node_modules", ".netlify")]
    for n in names:
        if n.startswith(".") or n in SKIP:
            continue
        p = os.path.join(root, n)
        url = "/" + os.path.relpath(p, ".").replace(os.sep, "/")
        files_map[url] = sha1(p)
print("files to publish:", list(files_map))
code, dep2 = api("PUT", f"/api/v1/sites/{site_id}/deploys/{dep_id}",
                 {"files": files_map, "functions": {}, "async": False})
print("announce:", code, dep2.get("required") if isinstance(dep2, dict) else dep2)
required = dep2.get("required", [])

# 4. upload files (iterate files_map paths — `required` may contain hashes, not paths)
for path in files_map:
    with open(path.lstrip("/"), "rb") as f:
        data = f.read()
    code, _ = api("PUT", f"/api/v1/deploys/{dep_id}/files/{path.lstrip('/')}", data, "application/octet-stream", raw=True)
    print(f"upload {path}: {code}")

# 5. poll until ready
for i in range(30):
    code, dep3 = api("GET", f"/api/v1/deploys/{dep_id}")
    state = dep3.get("state") if isinstance(dep3, dict) else dep3
    if state == "ready":
        print("DEPLOY READY:", dep3.get("deploy_ssl_url") or dep3.get("ssl_url"))
        break
    if state in ("error", "failed"):
        print("DEPLOY FAILED:", dep3)
        break
    time.sleep(2)
else:
    print("TIMEOUT waiting for deploy")
