# AETHER RNG v0.2.0

Roblox가 아닌 웹브라우저용 무료 오라 수집 시뮬레이터입니다.

## 기능
- 1,000종 오라 데이터 / 8단계 희귀도 (1차 전용 GLB 모델 50종)
- 서버에서 처리하는 확률 뽑기
- 아이디 + 비밀번호만으로 회원가입 및 로그인 (이메일 입력 불필요)
- Supabase 클라우드 저장: 인벤토리, 뽑기 횟수, 최고 희귀도, 장착 오라, 최근 기록
- 전체 플레이어 랭킹
- 오라 도감, 자동 뽑기, 연출 및 효과음 설정
- 로그인 전 로컬 저장 모드
- 모바일 반응형 UI

## 접속
GitHub Pages: https://hgs10622-dotcom.github.io/SolsRNG-KR/

## 기술 구성
- 정적 웹 호스팅: GitHub Pages + GitHub Actions
- 데이터베이스 및 인증: Supabase
- 데이터베이스 스키마: `supabase/schema.sql` 및 `supabase/migrations/`
- 아이디 인증: `supabase/functions/username-auth/index.ts` (서버 내부 별칭을 사용하며 이메일은 수집하지 않음)
- 브라우저 설정: `supabase-config.js` (브라우저 공개용 publishable key만 포함)

## 안전
모든 뽑기는 무료이며 현금 결제, 현금성 재화, 유료 확률 상품은 없습니다. Supabase service_role 키는 브라우저나 저장소에 넣지 않습니다.

## 3D Aura Models

Aura showcase models load on demand as GLB assets through Three.js GLTFLoader. The deployment pipeline generates 50 dedicated, locally hosted GLB models for the first 50 catalog entries. Each GLB is built from its own aura ID, rarity, palette, sculptural geometry, orbital structures, signature motif, and material setup; the remaining catalog entries retain the procedural fallback until their dedicated model batch is produced.

- Asset source and CC0 license: https://grab3d.com/developers/
- Model files are loaded from the documented static download route: `https://grab3d.com/dl/{slug}/{file}`
- Models are requested only when their aura is selected, rather than downloading the full collection at startup.
