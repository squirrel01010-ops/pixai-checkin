"""Interactive setup inside the user's private Codespace. No secrets printed."""
import json
import os
import subprocess
from pathlib import Path
from urllib.parse import urlparse


def main():
    if not Path("state.json").is_file():
        raise SystemExit("먼저 python login.py로 로그인하세요.")
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo:
        raise SystemExit("이 스크립트는 본인 저장소의 Codespaces에서 실행하세요.")
    url = input("실제 출석 화면 주소 (https://pixai.art/...): ").strip()
    if urlparse(url).scheme != "https" or urlparse(url).hostname != "pixai.art":
        raise SystemExit("https://pixai.art 주소만 허용됩니다.")
    claim = input("확인한 출석 버튼의 Playwright 선택자: ").strip()
    done = input("확인한 오늘 수령 완료 표시의 Playwright 선택자: ").strip()
    if not claim or not done:
        raise SystemExit("실제 화면에서 두 선택자를 확인해야 합니다.")
    state = Path("state.json").read_text()
    json.loads(state)
    env = dict(os.environ, PIXAI_CHECKIN_URL=url, PIXAI_CLAIM_SELECTOR=claim,
               PIXAI_DONE_SELECTOR=done, PIXAI_STORAGE_STATE=state)
    print("먼저 실제 출석/완료 표시를 검증합니다. 성공해야 예약 설정을 저장합니다.")
    subprocess.run(["python", "checkin.py"], check=True, env=env)
    subprocess.run(["gh", "secret", "set", "PIXAI_STORAGE_STATE", "--repo", repo],
                   input=state, text=True, check=True)
    for name, value in (("PIXAI_CHECKIN_URL", url), ("PIXAI_CLAIM_SELECTOR", claim),
                        ("PIXAI_DONE_SELECTOR", done)):
        subprocess.run(["gh", "variable", "set", name, "--repo", repo, "--body", value], check=True)
    print("검증 및 저장 완료. GitHub Actions에서 수동 실행 결과도 확인하세요.")
    subprocess.run(["gh", "variable", "set", "PIXAI_READY", "--repo", repo,
                    "--body", "true"], check=True)


if __name__ == "__main__":
    main()
