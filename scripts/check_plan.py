#!/usr/bin/env python3
"""Usage: check_plan.py <plan.md> <repo-path>. Needs CONFLUENCE_AUTH and CONFLUENCE_SERVER for Confluence links."""
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

PATH_RE = re.compile(r"^([^\s:`]+?)(?::(\d+)(?:-(\d+))?)?$")
EXT_RE = re.compile(r"\.[A-Za-z][A-Za-z0-9]{0,7}$")
SKIP_CHARS = set("*?{}[]<>$")
LINK_RE = re.compile(r"(https?://[^\s)>\]]+/wiki/[^\s)>\]]*?/pages/(\d+))")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    # Never forward the token to another URL: a 3xx raises HTTPError.
    def redirect_request(self, *args, **kwargs):
        return None


_opener = urllib.request.build_opener(_NoRedirect)
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
HASH_RE = re.compile(r"`([0-9a-f]{7,40})`")


def check_path(token, repo):
    m = PATH_RE.match(token)
    # ponytail: no "/" and no extension means not a path (class names, hashes, words)
    if not m or "://" in token or SKIP_CHARS & set(token) or not ("/" in m[1] or EXT_RE.search(m[1])):
        return None
    path, start, end = m[1], m[2], m[3]
    full = os.path.realpath(os.path.join(repo, path))
    root = os.path.realpath(repo)
    if not full.startswith(root + os.sep):
        return f"{token}: outside the repo"
    if not os.path.exists(full):
        return f"{token}: not found"
    if start:
        if not os.path.isfile(full):
            return f"{token}: line given for a folder"
        with open(full, "rb") as f:
            count = sum(1 for _ in f)
        last = int(end or start)
        if not 1 <= int(start) <= last <= count:
            return f"{token}: line out of range (file has {count} lines)"
    return None


def check_link(url, page_id, env):
    server = env["CONFLUENCE_SERVER"].rstrip("/")
    if urllib.parse.urlsplit(url).netloc != urllib.parse.urlsplit(server).netloc:
        return f"page {page_id}: link host is not the Confluence server"
    req = urllib.request.Request(
        f"{server}/wiki/api/v2/pages/{page_id}",
        headers={"Authorization": f"Basic {env['CONFLUENCE_AUTH']}"},
    )
    try:
        with _opener.open(req, timeout=20) as r:
            return None if r.status == 200 else f"page {page_id}: HTTP {r.status}"
    except urllib.error.HTTPError as e:
        return f"page {page_id}: HTTP {e.code}"
    except OSError as e:
        return f"page {page_id}: {type(e).__name__}"


def check_docs_header(text, repo):
    m = re.search(r"^## Docs to update\s*\n+(.*)", text, re.M)
    if not m:
        return None
    header = m[1]
    h = HASH_RE.search(header)
    if not DATE_RE.search(header) or not h:
        return "Docs to update: header needs a date and a `commit hash`"
    r = subprocess.run(["git", "-C", repo, "cat-file", "-e", h[1] + "^{commit}"], capture_output=True)
    return None if r.returncode == 0 else f"Docs to update: commit {h[1]} not found"


def check(text, repo, env):
    failures = []
    prose = re.sub(r"^(```|~~~).*?^\1", "", text, flags=re.M | re.S)
    for token in dict.fromkeys(re.findall(r"`([^`\n]+)`", prose)):
        failures.append(check_path(token, repo))
    links = list(dict.fromkeys(LINK_RE.findall(prose)))
    if links:
        server = env.get("CONFLUENCE_SERVER", "")
        if not env.get("CONFLUENCE_AUTH") or not server:
            failures.append("Confluence links found but CONFLUENCE_AUTH or CONFLUENCE_SERVER is not set")
        elif not server.startswith("https://"):
            failures.append("CONFLUENCE_SERVER must start with https://")
        else:
            failures += [check_link(u, i, env) for u, i in links]
    failures.append(check_docs_header(prose, repo))
    return [f for f in failures if f]


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    if not os.path.isdir(sys.argv[2]):
        sys.exit(f"repo path is not a folder: {sys.argv[2]}")
    with open(sys.argv[1], encoding="utf-8") as f:
        text = f.read()
    failures = check(text, sys.argv[2], os.environ)
    for f in failures:
        print(f)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
