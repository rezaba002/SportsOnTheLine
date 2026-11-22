"""Small bo3.gg client: curl with retries, polite pacing, on-disk cache."""
import hashlib, json, os, subprocess, threading, time

API = "https://api.bo3.gg/api/v1/"
CACHE = os.path.join(os.path.dirname(__file__), "..", "research", "bo3_cache")
os.makedirs(CACHE, exist_ok=True)
PAUSE = 0.07  # min seconds between request starts, across all threads
_last = [0.0]
_lock = threading.Lock()


def _curl(args, timeout=30):
    for attempt in range(6):
        with _lock:
            wait = PAUSE - (time.time() - _last[0])
            if wait > 0:
                time.sleep(wait)
            _last[0] = time.time()
        r = subprocess.run(["curl", "-s", "-m", str(timeout), "-A", "Mozilla/5.0", *args], capture_output=True)
        if r.returncode == 0 and r.stdout:
            return r.stdout
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"curl failed: {args[-1]}")


def api(path, cache=True):
    """GET api.bo3.gg/api/v1/<path> as JSON (cached by path)."""
    key = os.path.join(CACHE, hashlib.md5(path.encode()).hexdigest() + ".json")
    if cache and os.path.exists(key):
        with open(key, encoding="utf-8") as f:
            return json.load(f)
    for attempt in range(4):
        body = _curl([API + path])
        try:
            data = json.loads(body)
            break
        except json.JSONDecodeError:
            time.sleep(3 * (attempt + 1))
    else:
        raise RuntimeError(f"bad JSON: {path}: {body[:200]!r}")
    if cache:
        with open(key, "w", encoding="utf-8") as f:
            json.dump(data, f)
    return data


def get_range(url, a, b):
    """Byte range a..b of url -> (body, total_size)."""
    import re
    out = _curl(["-r", f"{a}-{b}", "-D", "-", url])
    hdr, _, body = out.partition(b"\r\n\r\n")
    while body.startswith(b"HTTP/"):  # proxy CONNECT header block comes first
        hdr, _, body = body.partition(b"\r\n\r\n")
    m = re.search(rb"content-range: bytes \d+-\d+/(\d+)", hdr, re.I)
    if not m:
        raise RuntimeError(f"no content-range: {url} {hdr[:200]!r}")
    return body, int(m.group(1))
