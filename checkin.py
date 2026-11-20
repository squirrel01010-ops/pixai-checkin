"""PixAI 일일 출석(무료 크레딧 수령) + 로그인 토큰 자동 갱신.

웹사이트의 "일일 크레딧 받기" 버튼과 같은 요청(dailyClaimQuota)을 보낸다.

환경 변수
  PIXAI_TOKEN       로그인 토큰(또는 API 키). 여러 계정은 줄바꿈/쉼표로 구분.
  PIXAI_MODE        claim(기본): 출석 + 필요 시 토큰 갱신 / refresh: 토큰 갱신만
  PIXAI_STATE_FILE  갱신된 토큰을 보관할 파일 (기본 .pixai_tokens.json)
  PIXAI_WAIT_REFRESH  1이면 만료 4시간 이내일 때 작업 안에서 기다렸다가 갱신
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
REFRESH = "mutation refreshToken { refreshToken }"
ALREADY = ("already", "claimed")
WAIT_WINDOW = 4 * 3600  # 만료 4시간 이내에 실행되면 작업 안에서 기다렸다가 갱신
WAIT_UNTIL = 50 * 60     # 만료 50분 전부터 갱신 재시도 (웹사이트는 1시간 전부터 갱신)
RETRY_EVERY = 5 * 60
KST = datetime.timezone(datetime.timedelta(hours=9))


def gql(token, query, retries=3):
    body = json.dumps({"query": query}).encode()
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "content-type": "application/json",
        "authorization": f"Bearer {token}",
        "user-agent": "Mozilla/5.0",
        "origin": "https://pixai.art",
        "referer": "https://pixai.art/",
    })
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=30) as res:
                return json.load(res), res.headers
        except urllib.error.HTTPError as e:
            text = e.read().decode(errors="replace")
            if e.code in (401, 403):
                raise RuntimeError(f"인증 실패 (HTTP {e.code}): {text[:200]} -> 토큰을 다시 복사해 Secret을 교체하세요") from None
            if attempt == retries:
                raise RuntimeError(f"HTTP {e.code}: {text[:200]}") from None
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt == retries:
                raise RuntimeError(f"네트워크 오류: {e}") from None
        time.sleep(2 ** attempt)


def errors_of(resp):
    return [e.get("message", "") for e in resp.get("errors") or []]


def jwt_payload(token):
    parts = token.split(".")
    if len(parts) != 3:
        return None
    try:
        return json.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))
    except Exception:
        return None


def exp_of(token):
    p = jwt_payload(token)
    return int(p["exp"]) if p and "exp" in p else None


def sub_of(token):
    p = jwt_payload(token)
    return str(p.get("sub") or p.get("user_id")) if p else None


def mask(token):
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::add-mask::{token}")


def me(token):
    resp, _ = gql(token, ME)
    errs = errors_of(resp)
    if errs:
        raise RuntimeError("계정 조회 실패: " + "; ".join(errs))
    return resp["data"]["me"]


def try_refresh(token):
    """refreshToken을 호출해 새 토큰이 나오면 돌려준다. 아직이면 None."""
    resp, headers = gql(token, REFRESH)
    errs = errors_of(resp)
    if errs:
        print(f"  토큰 갱신 응답 오류: {'; '.join(errs)}", file=sys.stderr)
        return None
    new = (headers.get("token") or "").strip()
    if new and new != token and (exp_of(new) or 0) > (exp_of(token) or 0):
        mask(new)
        return new
    return None


def fmt(ts):
    return datetime.datetime.fromtimestamp(ts, KST).strftime("%Y-%m-%d %H:%M")


def maybe_refresh(token, label):
    """매 실행마다 갱신을 시도한다. 서버가 새 토큰을 주면 그걸 돌려준다."""
    exp = exp_of(token)
    if exp is None:
        return token  # API 키 등 JWT가 아닌 토큰
    left = exp - time.time()
    if left <= 0:
        raise RuntimeError(f"토큰 만료됨 ({fmt(exp)} KST) -> 다시 복사해서 Secret을 교체하세요")
    print(f"[{label}] 토큰 만료: {fmt(exp)} KST ({left / 3600:.1f}시간 남음)")
    new = try_refresh(token)
    if new:
        print(f"[{label}] 토큰 자동 갱신 완료 -> 새 만료 {fmt(exp_of(new))} KST")
        return new
    return token


def wait_and_refresh(token, label):
    """만료가 WAIT_WINDOW 안이면 만료 직전까지 기다리며 갱신을 재시도한다.

    GitHub 예약 실행은 몇 시간씩 빠지기 때문에, 만료 직전 갱신 시간대에
    실행이 걸린다는 보장이 없다. 그래서 가까운 실행이 대신 기다린다.
    """
    exp = exp_of(token)
    if exp is None or not os.environ.get("PIXAI_WAIT_REFRESH"):
        return token
    left = exp - time.time()
    if left <= 0 or left > WAIT_WINDOW:
        return token
    start = exp - WAIT_UNTIL
    if start > time.time():
        print(f"[{label}] 만료가 가까워 {fmt(start)} KST까지 기다렸다가 갱신합니다", flush=True)
        time.sleep(start - time.time())
    while time.time() < exp - 60:
        try:
            new = try_refresh(token)
        except Exception as exc:
            print(f"[{label}] 갱신 시도 오류: {exc}", file=sys.stderr)
            new = None
        if new:
            print(f"[{label}] 토큰 자동 갱신 완료 -> 새 만료 {fmt(exp_of(new))} KST", flush=True)
            return new
        time.sleep(min(RETRY_EVERY, max(1, exp - 60 - time.time())))
    print(f"[{label}] 만료 전까지 새 토큰이 발급되지 않았습니다. 토큰을 다시 복사해 Secret을 교체하세요.",
          file=sys.stderr)
    return token


def claim(token, label):
    user = me(token)
    before = user.get("quotaAmount")
    resp, _ = gql(token, CLAIM)
    errs = errors_of(resp)
    after = me(token).get("quotaAmount")
    if errs:
        msg = "; ".join(errs)
        if any(k in msg.lower() for k in ALREADY):
            print(f"[{label}] 오늘 이미 출석함 / 크레딧 {after}")
            return True
        print(f"[{label}] 출석 실패 - {msg}", file=sys.stderr)
        return False
    try:
        gained = int(after) - int(before)
    except (TypeError, ValueError):
        gained = None
    if gained:
        print(f"[{label}] 출석 완료! +{gained} 크레딧 (현재 {after})")
    else:
        print(f"[{label}] 출석 요청 완료 / 크레딧 {after}")
    return True


def load_state(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def main():
    mode = os.environ.get("PIXAI_MODE", "claim").strip() or "claim"
    state_file = os.environ.get("PIXAI_STATE_FILE", ".pixai_tokens.json")
    raw = os.environ.get("PIXAI_TOKEN", "")
    tokens = [t.strip().removeprefix("Bearer ").strip()
              for t in raw.replace(",", "\n").splitlines() if t.strip()]
    if not tokens:
        print("PIXAI_TOKEN이 비어 있습니다. README.md를 참고해 Secret을 등록하세요.", file=sys.stderr)
        return 1

    state = load_state(state_file)
    new_state = {}
    subs = [sub_of(t) for t in tokens]
    ok = True
    for i, token in enumerate(tokens, 1):
        label = f"계정{i}"
        sub = sub_of(token)
        cached = state.get(sub) if sub else None
        # Secret보다 캐시에 저장된(자동 갱신된) 토큰이 더 오래 유효하면 그걸 쓴다.
        if cached and (exp_of(cached) or 0) > (exp_of(token) or 0):
            token = cached
        mask(token)
        try:
            token = maybe_refresh(token, label)
            if mode == "claim":
                ok &= claim(token, label)
        except Exception as exc:
            print(f"[{label}] 오류: {exc}", file=sys.stderr)
            ok = False
        if sub:
            new_state[sub] = token

    # 출석은 끝났으니, 만료가 가까운 토큰은 여기서 기다렸다가 갱신한다 (만료 순서대로).
    for sub, token in sorted(new_state.items(), key=lambda kv: exp_of(kv[1]) or 0):
        label = f"계정{subs.index(sub) + 1}" if sub in subs else sub
        new_state[sub] = wait_and_refresh(token, label)

    save_state(state_file, state, new_state)
    return 0 if ok else 1


def save_state(state_file, old, new_state):
    if new_state == old:
        return False
    fd = os.open(state_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(new_state, f)
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write("changed=true\n")
    return True


if __name__ == "__main__":
    sys.exit(main())
