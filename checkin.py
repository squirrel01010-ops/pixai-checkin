"""PixAI 일일 출석(무료 크레딧 수령) - GraphQL API 직접 호출.

PIXAI_TOKEN 환경 변수에 PixAI API 키 또는 로그인 토큰을 넣습니다.
여러 계정은 줄바꿈 또는 쉼표로 구분합니다.
"""
import base64
import datetime
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://api.pixai.art/graphql"
CLAIM = "mutation dailyClaimQuota { dailyClaimQuota }"
ME = "query me { me { id username quotaAmount } }"
ALREADY = ("already", "claimed", "today", "once")


def gql(token, query, retries=3):
    body = json.dumps({"query": query}).encode()
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
        "user-agent": "pixai-checkin/1.0",
        "origin": "https://pixai.art",
        "referer": "https://pixai.art/",
    })
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                return json.load(res)
        except urllib.error.HTTPError as e:
            text = e.read().decode(errors="replace")
            if e.code in (401, 403):
                raise RuntimeError(f"인증 실패 (HTTP {e.code}): {text[:200]}") from None
            if attempt == retries:
                raise RuntimeError(f"HTTP {e.code}: {text[:200]}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == retries:
                raise RuntimeError(f"네트워크 오류: {e}") from None
        time.sleep(2 ** attempt)


def errors_of(resp):
    return [e.get("message", "") for e in resp.get("errors") or []]


def me(token):
    resp = gql(token, ME)
    errs = errors_of(resp)
    if errs:
        raise RuntimeError("계정 조회 실패: " + "; ".join(errs))
    return resp["data"]["me"]


def token_expiry(token):
    """로그인 토큰(JWT)이면 만료 시각을 돌려준다. API 키면 None."""
    parts = token.split(".")
    if len(parts) != 3:
        return None
    try:
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))
        return datetime.datetime.fromtimestamp(int(payload["exp"]), datetime.timezone(datetime.timedelta(hours=9)))
    except Exception:
        return None


def checkin(token, label):
    exp = token_expiry(token)
    if exp:
        left = (exp - datetime.datetime.now(exp.tzinfo)).days
        print(f"[{label}] 토큰 만료: {exp:%Y-%m-%d %H:%M} KST (약 {left}일 남음)")
        if left < 3:
            print(f"[{label}] 토큰이 곧 만료됩니다. 다시 복사해서 Secret을 교체하세요.", file=sys.stderr)
    user = me(token)
    name = user.get("username") or user.get("id")
    before = user.get("quotaAmount")
    errs = errors_of(gql(token, CLAIM))
    after = me(token).get("quotaAmount")
    gained = (int(after) - int(before)) if str(before).lstrip("-").isdigit() and str(after).lstrip("-").isdigit() else None

    if errs:
        msg = "; ".join(errs)
        if any(k in msg.lower() for k in ALREADY):
            print(f"[{label}] {name}: 오늘 이미 출석함 ({msg}) / 크레딧 {after}")
            return True
        print(f"[{label}] {name}: 출석 실패 - {msg}", file=sys.stderr)
        return False

    if gained:
        print(f"[{label}] {name}: 출석 완료! +{gained} 크레딧 (현재 {after})")
    else:
        print(f"[{label}] {name}: 출석 요청 완료 (오늘 이미 받았거나 반영 지연) / 크레딧 {after}")
    return True


def main():
    raw = os.environ.get("PIXAI_TOKEN", "")
    tokens = [t.strip().removeprefix("Bearer ").strip()
              for t in raw.replace(",", "\n").splitlines() if t.strip()]
    if not tokens:
        print("PIXAI_TOKEN이 비어 있습니다. README.md를 참고해 Secret을 등록하세요.", file=sys.stderr)
        return 1
    ok = True
    for i, token in enumerate(tokens, 1):
        try:
            ok &= checkin(token, f"계정{i}")
        except Exception as exc:
            print(f"[계정{i}] 오류: {exc}", file=sys.stderr)
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
