OpenCode (oh-my-opencode) Windows 설치 및 사용 가이드

환경: Windows 10/11, Node.js (NPM)

1. 개요
이 문서는 AI 코딩 에이전트 OpenCode를 Windows 환경에서 oh-my-opencode 플러그인 매니저를 통해 설치하고 사용하는 방법을 다룹니다. (Bun 런타임은 Windows 파일 잠금 이슈로 인해 사용을 권장하지 않음)

2. 설치 방법 (Installation)
가장 안정적인 NPM(Node.js) 기반 설치 방식입니다.

노드 설치 후 

npm i -g opencode-ai

2.1 초기 설치 명령어
터미널(cmd)에서 아래 명령어를 실행하여 설치 마법사를 시작합니다.

DOS

npx oh-my-opencode install
2.2 설치 옵션 선택 (중요)
설치 도중 질문이 나오면 아래와 같이 선택하여 충돌을 방지합니다.

Do you have a Claude Pro/Max subscription?

👉 No (유료 API Key가 없으면 No 선택)

Do you have a ChatGPT Plus/Pro subscription?

👉 Yes (웹 로그인 방식 사용)

Will you integrate Google Gemini?

👉 No (설치 오류 방지를 위해 일단 No 선택, 추후 개별 인증)

3. 계정 인증 (Authentication)
설치 완료 후, 터미널에서 아래 명령어로 AI 모델들을 연결합니다.

3.1 ChatGPT Plus 연결
명령어 입력:

DOS

opencode auth login
메뉴 선택: ChatGPT Plus/Pro (Manual URL Paste)

절차:

터미널에 뜬 URL 복사 → 브라우저 접속 및 로그인

로그인 완료 후 나오는 긴 인증 코드(또는 에러 페이지 URL) 전체 복사

터미널에 붙여넣기 후 엔터

3.2 Google Gemini 연결 (선택 사항)
명령어 입력:

DOS

opencode auth login
메뉴 선택: Google → OAuth with Antigravity

절차:

Project ID는 공란으로 두고 엔터

브라우저 로그인 후 권한 허용

제공된 인증 코드를 터미널에 붙여넣기

4. 트러블슈팅 (Troubleshooting)
Failed to link, EUNKNOWN, BunInstallFailed 등의 에러가 발생하며 설치가 꼬였을 때 사용하는 초기화 명령어입니다. (순서대로 한 줄씩 실행)

DOS

:: 1. 설정 폴더 삭제 (기억 소거)
rmdir /s /q "C:\Users\사용자계정\.config\opencode"

:: 2. 캐시 폴더 삭제 (찌꺼기 제거)
rmdir /s /q "C:\Users\사용자계정\.cache\opencode"

:: 3. 재설치 시작
npx oh-my-opencode install
5. 사용 방법 (Usage Workflow)
OpenCode는 현재 폴더에 파일을 생성하므로, 반드시 프로젝트별 폴더를 만든 후 실행해야 합니다.

5.1 프로젝트 시작하기 (예시: ESP32 온습도 프로젝트)
DOS

:: 1. 프로젝트 폴더 생성
mkdir esp32-project

:: 2. 폴더로 이동
cd esp32-project

:: 3. OpenCode 실행
opencode
5.2 프롬프트 작성 팁 (The Magic Word)
입력창이 뜨면 작업 지시를 내립니다. 이때 ulw (Ultra Work) 키워드를 붙이면 에이전트 성능이 극대화됩니다.

입력 예시: "ESP32-S3를 사용하여 온습도 데이터를 1초마다 수집하고, 이를 웹 서버에 띄우는 코드를 작성해줘. 센서 라이브러리는 DHT22를 사용해. ulw"

6. 주요 단축키 및 명령어
opencode --version: 설치된 버전 확인

Ctrl + C: 작업 중인 에이전트 강제 중지 또는 프로그램 종료

opencode auth logout: 로그인 풀기 (계정 변경 시)