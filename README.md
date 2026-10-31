# PixAI 매일 출석

**폰만 사용하는 경우 [PHONE.md](PHONE.md)를 먼저 보세요.** PC 없이 Codespaces에서 최초 로그인하도록 구성했습니다.

별도 서버 없이 GitHub Actions에서 매일 한국 시간 12:17에 실행합니다.
GitHub 실행 대기로 실제 시각은 늦어질 수 있습니다. 비공개 저장소는 계정의 Actions 사용량/과금 설정을 확인하세요.

**현재 상태:** 실행 코드와 예약 설정을 준비했습니다. 이 환경에서 PixAI에 접속할 수 없어 실제 화면과 버튼을 확인하지 못했습니다.
본인 계정 로그인, 아래 URL/선택자 설정, 수동 실행 확인이 필요하며 아직 출석이 활성화된 상태가 아닙니다.
로그인 세션 만료, CAPTCHA 또는 추가 인증이 발생하면 실패하며 본인 PC에서 다시 로그인해야 합니다.

## 1. 본인 PC에서 로그인

Python 3.10 이상을 설치하고 이 폴더에서 실행하세요.

```sh
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell에서는 .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium
python login.py
```

열린 브라우저에서 직접 로그인한 뒤 터미널에서 Enter를 누릅니다.
생성되는 `state.json`은 비밀번호에 준하는 정보입니다. 채팅, 저장소, 공개 로그에 올리지 마세요.

## 2. 실제 출석 화면 설정

로그인한 브라우저에서 일일 크레딧 수령 화면을 엽니다. 그 화면의 전체 주소를 기록하세요.
Playwright의 선택 도구로 일일 크레딧 수령 버튼과 이미 수령했음을 나타내는 표시를 확인합니다.

```sh
python -m playwright codegen --load-storage=state.json https://pixai.art
```

생성된 Python 코드를 그대로 넣는 것이 아니라 Playwright 문자열 선택자를 넣습니다.
예를 들어 도구가 `get_by_role("button", name="실제 버튼 문구", exact=True)`를 표시하면
`role=button[name="실제 버튼 문구"]`로 설정할 수 있습니다. 실제 문구는 화면에서 확인해야 합니다.
`PIXAI_DONE_SELECTOR`는 오늘 이미 수령했다는 명확한 표시여야 하며 일반 성공 알림이나 보유 크레딧 숫자를 사용하지 마세요.
페이지에서 추가 메뉴를 열어야 한다면 현재 스크립트에 그 단계를 추가해야 합니다.

## 3. GitHub 예약 실행

1. GitHub에 **비공개 저장소**를 만들고 이 폴더의 코드를 올립니다. `.github` 폴더도 포함하고 `state.json`은 제외하세요.
2. 저장소 Settings → Secrets and variables → Actions → Secrets에 `PIXAI_STORAGE_STATE`를 만들고 `state.json` 전체 내용을 붙여 넣습니다.
3. 같은 화면 Variables에 다음을 설정합니다.
   - `PIXAI_CHECKIN_URL`: 실제 일일 크레딧 화면 주소
   - `PIXAI_CLAIM_SELECTOR`: 실제 수령 버튼 선택자
   - `PIXAI_DONE_SELECTOR`: 오늘 수령 완료 표시 선택자
4. Actions → PixAI daily check-in → Run workflow를 실행하고 성공 여부와 PixAI의 수령 상태를 확인하세요.
5. 검증 후 Actions Variables에 `PIXAI_READY`를 `true`로 설정하면 매일 예약 실행됩니다. `phone_setup.py`를 쓰면 검증 후 자동 설정합니다. 실패 알림은 GitHub의 Actions 알림 설정에서 켤 수 있습니다.

로그인 세션은 실행마다 자동 갱신하여 저장하지 않습니다. 만료 시 `login.py`를 다시 실행하고 Secret을 교체하세요.
중지하려면 Actions에서 이 워크플로를 Disable workflow로 설정합니다.
