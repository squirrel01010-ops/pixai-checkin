# PixAI 자동 출석체크

웹사이트/앱에서 매일 "일일 크레딧 받기"를 누르는 것과 똑같은 요청을 GitHub Actions가 대신 보냅니다.
(PixAI 웹사이트의 받기 버튼도 내부적으로 `api.pixai.art/graphql`의 `dailyClaimQuota`를 호출합니다.
유료 개발자 API를 쓰는 게 아니라 본인 로그인 상태로 버튼 누르는 것과 같습니다.)
브라우저/서버 필요 없고, `checkin.py`는 파이썬 표준 라이브러리만 씁니다.

아이디/비밀번호 자동 로그인은 PixAI 로그인에 reCAPTCHA가 걸려 있어 하지 않습니다.
처음에 한 번 직접 로그인해서 로그인 토큰을 복사해 두면, 그 다음부터는 매일 자동입니다.

- 실행 시각: 매일 한국 시간 09:17, 21:17 (두 번째는 재시도용. 이미 받았으면 그냥 넘어감)
- 출석 전후 크레딧을 조회해 몇 크레딧 받았는지 로그에 찍습니다.
- 여러 계정 지원 (토큰을 줄바꿈으로 구분)

## 설정 (폰으로도 가능)

### 1. PixAI 토큰 얻기

**방법 A — 웹사이트 로그인 토큰 (PC 크롬)**
pixai.art 로그인 → F12 → Network 탭 → 페이지 새로고침 → `graphql` 요청 클릭 →
Request Headers의 `authorization: Bearer xxxxx`에서 `xxxxx` 부분을 복사합니다.
또는 `pip install -r requirements.txt && python -m playwright install chromium && python get_token.py`
를 실행해 뜨는 창에서 로그인하면 `token.txt`에 자동 저장됩니다.
로그아웃하거나 토큰이 만료되면 다시 복사해서 Secret을 교체하세요.

**방법 B — 폰만 있는 경우**
pixai.art 로그인 → 프로필 설정의 **API Keys** 메뉴에서 키를 만들어 복사합니다.
이것도 본인 계정으로 로그인한 것과 같게 동작하고 만료되지 않습니다.

### 2. GitHub Secret 등록

저장소 **Settings → Secrets and variables → Actions → New repository secret**

- Name: `PIXAI_TOKEN`
- Secret: 1번에서 복사한 토큰 (계정 여러 개면 한 줄에 하나씩)

### 3. 테스트 실행

**Actions → PixAI daily check-in → Run workflow** 를 눌러 실행하고 로그에
`출석 완료! +N 크레딧` 또는 `오늘 이미 출석함`이 나오면 끝입니다. 이후 매일 자동으로 돕니다.

## 로컬 실행

```sh
PIXAI_TOKEN=여기에토큰 python checkin.py
```

## 문제 해결

- `인증 실패 (HTTP 401)`: 토큰이 틀렸거나 만료됨 → 새로 발급해서 Secret 교체
- 실행 안 됨: Actions 탭에서 워크플로가 Disable 상태인지 확인 (기본 브랜치에 workflow 파일이 있어야 예약 실행됨)
- 중지: Actions → PixAI daily check-in → `...` → Disable workflow
