import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import httpx

CONFIG_PATH = Path(__file__).parent / "config.json"


def load_config(path=CONFIG_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@dataclass
class ChatResult:
    text: str
    tokens_in: int
    tokens_out: int
    seconds: float
    model: str
    estimated: bool = False


class LLMError(Exception):
    pass


def _headers(cfg, auth_style):
    key = os.environ.get(cfg["backend"]["api_key_env"])
    if not key:
        raise LLMError("environment variable %s is not set" % cfg["backend"]["api_key_env"])
    h = {
        "anthropic-version": cfg["backend"]["anthropic_version"],
        "content-type": "application/json",
    }
    if auth_style == "x-api-key":
        h["x-api-key"] = key
    else:
        h["authorization"] = "Bearer " + key
    return h


def chat(model, system, user, cfg=None, max_tokens=None):
    cfg = cfg or load_config()
    url = cfg["backend"]["base_url"].rstrip("/") + "/v1/messages"
    body = {
        "model": model,
        "max_tokens": max_tokens or cfg["limits"]["max_output_tokens"],
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    styles = [cfg["backend"].get("auth_style", "x-api-key"), "bearer"]
    last_err = None
    for attempt in range(cfg["backend"]["max_retries"] + 1):
        for style in dict.fromkeys(styles):
            t0 = time.time()
            try:
                r = httpx.post(url, headers=_headers(cfg, style), json=body,
                               timeout=cfg["backend"]["timeout_s"])
            except httpx.HTTPError as e:
                last_err = "network error: %s" % type(e).__name__
                continue
            if r.status_code in (401, 403) and style != styles[-1]:
                last_err = "auth rejected (%d) with %s" % (r.status_code, style)
                continue
            if r.status_code == 200:
                data = r.json()
                text = "".join(b.get("text", "") for b in data.get("content", []))
                usage = data.get("usage", {})
                tin, tout = usage.get("input_tokens"), usage.get("output_tokens")
                est = tin is None or tout is None
                if est:
                    tin, tout = len(system + user) // 4, len(text) // 4
                return ChatResult(text, tin, tout, time.time() - t0, model, est)
            last_err = "http %d: %s" % (r.status_code, r.text[:300])
            if r.status_code < 500 and r.status_code != 429:
                raise LLMError(last_err)
    raise LLMError(last_err or "unknown error")


def ping():
    cfg = load_config()
    for role in ("worker", "synthesizer", "planner"):
        model = cfg["models"][role]
        try:
            res = chat(model, "Reply with the single word: pong", "ping", cfg, max_tokens=20)
            print("%-12s %-28s ok  in=%s out=%s %.1fs reply=%r%s" % (
                role, model, res.tokens_in, res.tokens_out, res.seconds,
                res.text.strip()[:30], " (estimated)" if res.estimated else ""))
        except LLMError as e:
            print("%-12s %-28s FAIL %s" % (role, model, e))


if __name__ == "__main__":
    if "--ping" in sys.argv:
        ping()
    else:
        print("usage: python llm.py --ping")
