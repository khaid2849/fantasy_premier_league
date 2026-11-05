#!/usr/bin/env python3
"""Get an FPL OIDC authorization code from a logged-in browser session.

FPL refresh tokens rotate and eventually expire. Instead of pasting a new one
by hand, the Premier League SSO session (account.premierleague.com cookies) of
a browser is kept, and used to start a brand new OIDC login whenever Odoo
needs a token again: with a valid session, the login page redirects back with
an authorization code without showing anything.

Notes (verified against account.premierleague.com, PingOne DaVinci):

* ``prompt=none`` is not supported (always ``login_required``): a normal
  authorize request is used, and the sign-in form showing up means that the
  session expired.
* The SSO cookies rotate on every use: the browser state returned by each run
  must be saved, the previous one stops working.

Two modes:

``--login --out FILE`` (run once on a desktop, a window opens)
    You log in to the Premier League account; the browser state (cookies) is
    saved in FILE. See docker/fpl-login.sh.

``--silent`` (called by Odoo, headless, JSON on stdin/stdout)
    stdin:  {"storage_state": {...}}
    stdout: {"status": "ok", "code": ..., "code_verifier": ..., "redirect_uri": ...,
             "storage_state": {...}}  (the rotated cookies: to be saved)
            {"status": "login_required"}  (the SSO session expired)
            {"status": "error", "message": ..., "storage_state": {...}}

The code is exchanged for tokens by Odoo (PKCE: only the holder of
``code_verifier`` can redeem it). This starts a token chain owned by Odoo
only, separate from the one the browser tab uses, so the two never "re-use"
each other's rotated refresh tokens (which makes the server revoke them).

Must run as a separate process: gevent and Odoo's prefork workers break
Chromium's process management when Playwright runs in-process.
"""
import asyncio
import base64
import hashlib
import json
import os
import secrets
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse

AUTHORIZE_URL = "https://account.premierleague.com/as/authorize"
CLIENT_ID = "bfcbaf69-aade-4c1b-8f00-c1cb8a193030"
REDIRECT_URI = "https://fantasy.premierleague.com/"
SCOPE = "openid profile email offline_access"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
)
SILENT_TIMEOUT_S = 60
# The sign-in form must stay that long before concluding the session expired
LOGIN_FORM_GRACE_S = 6
LOGIN_TIMEOUT_S = 600

BROWSER_ARGS = [
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-gpu",
    "--disable-software-rasterizer",
]
# Inside an Odoo worker, Chromium's zygote crashes (SIGCHLD handling): one
# process is fine for a single short page.
HEADLESS_ARGS = BROWSER_ARGS + ["--single-process"]


def _full_chromium_exe():
    """The full Chromium build: chromium_headless_shell crashes (SIGTRAP) as a
    child of Odoo's prefork workers."""
    root = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH", "~/.cache/ms-playwright")).expanduser()
    candidates = sorted(
        list(root.glob("chromium-*/chrome-linux64/chrome")) + list(root.glob("chromium-*/chrome-linux/chrome")),
        reverse=True,
    )
    return str(candidates[0]) if candidates else None


def _remove_rlimit_as():
    """Odoo limits the address space of its workers; Chromium needs more."""
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
    except (ImportError, ValueError, OSError):
        pass


def _authorize_request(prompt=None, client_id=None):
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(24)
    params = {
        "client_id": client_id or CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    if prompt:
        params["prompt"] = prompt
    return f"{AUTHORIZE_URL}?{urlencode(params)}", state, verifier


async def _run_authorize(storage_state=None, headless=True, prompt=None, timeout_s=SILENT_TIMEOUT_S,
                         client_id=None, detect_login_form=False):
    """Open the authorize URL and wait for the redirect to REDIRECT_URI.

    :param bool detect_login_form: stop as soon as the sign-in form is shown
        (no valid session) and return ``{"login_form": True}``
    :return: (query params of the redirect or None on timeout, PKCE verifier,
        browser storage state)
    """
    from playwright.async_api import async_playwright

    url, state, verifier = _authorize_request(prompt, client_id)
    async with async_playwright() as pw:
        exe = _full_chromium_exe() if headless else None
        browser = await pw.chromium.launch(
            headless=headless,
            args=HEADLESS_ARGS if headless else BROWSER_ARGS,
            executable_path=exe,
        )
        try:
            context = await browser.new_context(user_agent=USER_AGENT, storage_state=storage_state)
            page = await context.new_page()
            done = asyncio.get_running_loop().create_future()

            def check(target_url):
                if target_url and target_url.startswith(REDIRECT_URI) and f"state={state}" in target_url \
                        and not done.done():
                    done.set_result(parse_qs(urlparse(target_url).query))

            # The redirect to REDIRECT_URI is a 302 (page.route() does not see
            # redirected requests): read it from the Location header, and from
            # the request itself as a fallback.
            page.on("response", lambda response: check(response.headers.get("location")))
            page.on("request", lambda request: check(request.url))
            try:
                await page.goto(url, wait_until="commit", timeout=timeout_s * 1000)
            except Exception:  # noqa: BLE001
                # The navigation may be cut when the redirect is reached
                if not done.done():
                    raise
            result = None
            form_since = None
            loop = asyncio.get_running_loop()
            deadline = loop.time() + timeout_s
            while loop.time() < deadline:
                try:
                    result = await asyncio.wait_for(asyncio.shield(done), timeout=1)
                    break
                except asyncio.TimeoutError:
                    pass
                if detect_login_form:
                    try:
                        has_form = await page.locator('input[type="password"]').count() > 0
                    except Exception:  # noqa: BLE001 - page navigating
                        has_form = False
                    form_since = (form_since or loop.time()) if has_form else None
                    if form_since and loop.time() - form_since >= LOGIN_FORM_GRACE_S:
                        result = {"login_form": True}
                        break
            return result, verifier, await context.storage_state()
        finally:
            await browser.close()


def silent(payload):
    params, verifier, storage_state = asyncio.run(_run_authorize(
        storage_state=payload.get("storage_state"), headless=True,
        client_id=payload.get("client_id"), detect_login_form=True,
    ))
    if params is None:
        return {"status": "error", "message": "No answer from the Premier League login page",
                "storage_state": storage_state}
    if params.get("login_form"):
        return {"status": "login_required"}
    if "code" in params:
        return {
            "status": "ok",
            "code": params["code"][0],
            "code_verifier": verifier,
            "redirect_uri": REDIRECT_URI,
            "storage_state": storage_state,
        }
    error = (params.get("error") or ["unknown"])[0]
    if error in ("login_required", "interaction_required", "consent_required"):
        return {"status": "login_required"}
    return {"status": "error", "message": f"{error}: {(params.get('error_description') or [''])[0]}",
            "storage_state": storage_state}


def login(out_file):
    print("A browser window opens: log in to your Premier League / FPL account.")
    print("It closes by itself once the login is done.")
    params, _verifier, storage_state = asyncio.run(_run_authorize(
        headless=False, timeout_s=LOGIN_TIMEOUT_S,
    ))
    if not params or "code" not in params:
        print(f"Login not completed: {params}", file=sys.stderr)
        return 1
    out = Path(out_file)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".tmp")
    tmp.write_text(json.dumps(storage_state))
    # Read by the odoo container (another uid), like the Alobo profile
    tmp.chmod(0o644)
    tmp.replace(out)
    print(f"Session saved in {out}. Odoo will use it the next time it needs an FPL token.")
    return 0


def main(argv):
    _remove_rlimit_as()
    if "--login" in argv:
        if "--out" not in argv:
            print("usage: fpl_browser_auth.py --login --out FILE", file=sys.stderr)
            return 2
        return login(argv[argv.index("--out") + 1])
    if "--silent" in argv:
        try:
            result = silent(json.loads(sys.stdin.read() or "{}"))
        except Exception as e:  # noqa: BLE001 - reported to Odoo as JSON
            result = {"status": "error", "message": f"{type(e).__name__}: {e}"}
        sys.stdout.write(json.dumps(result))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
