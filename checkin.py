"""Click only explicitly configured daily-credit controls and verify the result."""
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


def required(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"{name} 설정이 필요합니다. README.md를 참고하세요.")
    return value


def run():
    target = required("PIXAI_CHECKIN_URL")
    if urlparse(target).scheme != "https" or urlparse(target).hostname != "pixai.art":
        raise ValueError("출석 URL은 https://pixai.art 내의 주소여야 합니다.")
    claim_selector = required("PIXAI_CLAIM_SELECTOR")
    done_selector = required("PIXAI_DONE_SELECTOR")
    raw = os.environ.get("PIXAI_STORAGE_STATE")
    state = json.loads(raw) if raw else json.loads(Path("state.json").read_text())
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context(storage_state=state)
            page = context.new_page()
            page.set_default_timeout(20_000)
            page.goto(target, wait_until="domcontentloaded", timeout=60_000)
            # Wait for the actual claim/done controls; do not assume page load means login succeeded.
            done = page.locator(done_selector)
            claim = page.locator(claim_selector)
            done.or_(claim).first.wait_for(state="visible", timeout=45_000)
            if done.first.is_visible():
                print("이미 출석 완료 상태입니다.")
                return
            if claim.count() != 1:
                raise RuntimeError("출석 버튼이 하나로 특정되지 않습니다. 선택자를 확인하세요.")
            claim.click()
            done.first.wait_for(state="visible", timeout=30_000)
            print("출석 완료 표시를 확인했습니다.")
        finally:
            browser.close()


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:
        # Playwright errors can contain private page content; do not upload browser traces.
        print(f"출석 실패 ({type(exc).__name__}). 세션 만료, 추가 인증, URL/선택자를 확인하세요.", file=sys.stderr)
        sys.exit(1)
