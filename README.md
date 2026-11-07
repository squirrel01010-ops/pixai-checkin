# PixAI 자동 출석체크

GitHub Actions가 매일 PixAI GraphQL API의 `dailyClaimQuota`를 호출해 일일 무료 크레딧을 받습니다.
브라우저/서버 필요 없고, `checkin.py`는 파이썬 표준 라이브러리만 씁니다.

- 실행 시각: 매일 한국 시간 09:17, 21:17 (두 번째는 재시도용. 이미 받았으면 그냥 넘어감)
- 출석 전후 크레딧을 조회해 몇 크레딧 받았는지 로그에 찍습니다.
- 여러 계정 지원 (토큰을 줄바꿈으로 구분)

## 설정 (폰으로도 가능)

### 1. PixAI 토큰 얻기

**방법 A — API 키 (추천, 만료 없음)**
pixai.art 로그인 → 프로필 → 설정(Edit profile) → **API Keys** 메뉴에서 키를 생성하고 복사합니다.

**방법 B — 로그인 토큰**
PC 크롬에서 pixai.art 로그인 → F12 → Network 탭 → `graphql` 요청 클릭 →
Request Headers의 `authorization: Bearer xxxxx`에서 `xxxxx` 부분을 복사합니다.
또는 `pip install -r requirements.txt && python -m playwright install chromium && python get_token.py`
로 로그인하면 `token.txt`에 자동 저장됩니다. (로그인 토큰은 만료될 수 있음)

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
