"""Run locally with a visible browser; never share state.json publicly."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://pixai.art", wait_until="domcontentloaded")
    input("브라우저에서 로그인한 뒤, 이 터미널에서 Enter를 누르세요: ")
    context.storage_state(path="state.json", indexed_db=True)
    os.chmod(Path("state.json"), 0o600)
    browser.close()
print("state.json 저장 완료. 계정 접근 정보이므로 공개하거나 커밋하지 마세요.")
