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

**방법 B — 폰만 있는 경우 (북마크로 토큰 복사)**

1. 폰 브라우저(크롬/사파리)에서 pixai.art에 접속해 **로그인**합니다. (앱 말고 웹사이트)
2. 아무 페이지나 북마크를 추가한 뒤, 그 북마크를 **편집**해서
   - 이름: `pixai토큰`
   - 주소(URL): 저장소의 [`bookmarklet.js`](bookmarklet.js) 내용 전체(`javascript:`로 시작하는 한 줄)를 붙여넣고 저장합니다.
3. pixai.art 페이지가 열린 상태에서
   - 크롬: 주소창에 `pixai토큰`을 입력하고 목록에 뜨는 **북마크 항목**(별 아이콘)을 누릅니다.
   - 사파리: 북마크 목록에서 `pixai토큰`을 누릅니다.
4. "토큰 복사 완료" 알림이 뜨면 클립보드에 복사된 상태입니다.
   복사 창이 대신 뜨면 안의 글자를 길게 눌러 **전체 선택 → 복사**하세요.

주소창에 `javascript:...`를 직접 붙여넣으면 크롬이 앞의 `javascript:`를 지워버리니 북마크 방법을 쓰세요.

**방법 C — API 키**
pixai.art 프로필 설정에 **API Keys** 메뉴가 있으면 키를 만들어 넣어도 됩니다. (만료 없음)

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

- `인증 실패 (HTTP 401)`: 토큰이 틀렸거나 만료됨 → 위 방법으로 다시 복사해서 Secret 교체
- 로그인 토큰은 실행 로그에 만료일이 찍힙니다. 웹에서 로그아웃하면 토큰이 무효화될 수 있으니 로그아웃하지 마세요.
- 실행 안 됨: Actions 탭에서 워크플로가 Disable 상태인지 확인 (기본 브랜치에 workflow 파일이 있어야 예약 실행됨)
- 중지: Actions → PixAI daily check-in → `...` → Disable workflow
