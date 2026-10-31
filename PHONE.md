# 폰에서 무료 사용량 안으로 설정하기

아직 본인 계정으로 검증되지 않은 구성입니다. PixAI가 Codespaces/Actions 접속을 차단하거나
로그인 세션을 다른 환경에서 허용하지 않으면 이 방법은 작동하지 않습니다.
무료 사용량과 서비스 제공 조건은 GitHub 계정의 현재 설정을 확인해야 합니다.

## 1. GitHub에 올리기

폰에서 ZIP을 다운로드하고 파일 앱에서 압축을 풉니다.
GitHub 웹에서 새 **비공개 저장소**를 만든 뒤 Add file → Upload files로 폴더 내용을 업로드하세요.
모바일 화면에서 메뉴가 보이지 않으면 브라우저의 데스크톱 사이트 보기를 켭니다.
최상위에 `requirements.txt`, `.github/workflows/checkin.yml`,
`.devcontainer/devcontainer.json`이 있어야 합니다. ZIP 자체만 업로드하면 실행되지 않습니다.
파일 선택기에서 숨김 폴더를 업로드할 수 없다면 GitHub의 Add file → Create new file에서
위 두 경로를 각각 만들고 다운로드한 파일 내용을 복사합니다.

## 2. 비용 제한과 원격 화면

GitHub Settings → Billing and licensing에서 Codespaces와 Actions의 무료 잔여량과 예산을 확인하세요.
초과 사용이 중단되도록 설정하고 유료 사용을 허용하지 마세요. 무료 한도가 없으면 시작하지 마세요.

저장소 Code → Codespaces → Create codespace on main을 선택합니다. 작은 기본 머신이면 충분합니다.
설치 완료 후 터미널에서 `python login.py`를 실행합니다.
Ports 탭에서 6080을 찾아 **Private**인지 확인하고 브라우저에서 엽니다.
VNC 연결 화면이 나오면 Connect를 누릅니다. desktop-lite의 기본 암호는 `vscode`입니다.
암호만으로 보호하지 말고 포트 공개 범위를 반드시 Private으로 유지하세요.
현재 데스크톱 화면에서 브라우저가 뜨지 않으면 터미널의 설치 오류를 확인하세요.

원격 Chromium에서 직접 PixAI 로그인합니다. CAPTCHA가 있으면 직접 처리하고 우회하지 마세요.
로그인이 끝나면 Codespaces 터미널로 돌아와 Enter를 누릅니다.
쿠키나 세션 파일 내용은 채팅에 보내지 마세요.

## 3. 출석 버튼 확인 및 설정

아래 명령으로 같은 원격 화면에서 선택 도구를 열 수 있습니다.

```sh
python -m playwright codegen --load-storage=state.json https://pixai.art
```

일일 크레딧 화면의 주소와 수령 버튼, 오늘 이미 수령했다는 표시의 선택자를 확인하세요.
선택자 표기법은 README.md를 참고하세요. 실제 화면 문구/구조를 확인하지 않고 추측하면 안 됩니다.
메뉴를 먼저 열어야 하는 화면은 `checkin.py`에 해당 조작을 추가해야 합니다.

터미널에서 다음을 실행하고 확인한 값을 입력합니다.

```sh
python phone_setup.py
```

실제 출석 상태 확인에 성공한 뒤에만 GitHub Secret과 Variables를 저장합니다.
GitHub CLI 권한 오류가 나면 저장소 Settings → Secrets and variables → Actions에서
README.md의 항목들을 직접 등록할 수 있습니다. 이때 세션은 오직 본인 저장소 Secret에만 저장하세요.

Actions 탭에서 PixAI daily check-in을 수동 실행하고 성공 여부를 확인하세요.
기본 브랜치에 workflow가 있으면 매일 한국 시간 12:17 전후로 실행됩니다.
설정 전에는 예약 실행을 건너뜁니다. `phone_setup.py`가 검증 후 `PIXAI_READY=true`를 저장하면 활성화됩니다.
Secret과 Variables를 직접 등록하는 경우 수동 검증을 마친 뒤 `PIXAI_READY` 변수도 `true`로 설정하세요.

## 4. 설정 후 Codespaces 정리

Codespaces는 매일 실행하는 서버가 아닙니다. 설정 완료 후 **Stop codespace**로 중지하세요.
더 이상 필요 없으면 Delete로 삭제하여 저장 공간 사용량도 줄일 수 있습니다.
Actions의 Secret은 Codespace 삭제 후에도 남습니다. 세션 만료 시 새 Codespace에서 다시 로그인하고 교체합니다.
출석 자동화를 중지하려면 Actions에서 Disable workflow를 누릅니다.
