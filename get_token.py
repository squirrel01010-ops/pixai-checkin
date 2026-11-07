"""(선택) API 키 대신 브라우저 로그인 토큰을 뽑는 도구.

pip install playwright && python -m playwright install chromium
python get_token.py  -> 열린 브라우저에서 로그인하면 토큰이 token.txt에 저장됩니다.
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

found = {}


def on_request(req):
    auth = req.headers.get("authorization", "")
    if "api.pixai.art" in req.url and auth.lower().startswith("bearer ") and len(auth) > 20:
        found["token"] = auth[7:].strip()


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.on("request", on_request)
    page.goto("https://pixai.art/login")
    print("브라우저에서 로그인하세요. 토큰이 잡히면 자동 종료됩니다...")
    while "token" not in found:
        page.wait_for_timeout(1000)
    browser.close()

Path("token.txt").write_text(found["token"])
print("token.txt 저장 완료. 내용을 GitHub Secret PIXAI_TOKEN에 붙여 넣으세요.")
