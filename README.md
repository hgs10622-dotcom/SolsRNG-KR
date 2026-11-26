# AETHER RNG v0.2.0

Roblox가 아닌 웹브라우저용 무료 오라 수집 시뮬레이터입니다.

## 기능
- 1,000종 오라 데이터 / 8단계 희귀도
- 1,000종 전용 GLB 3D 모델 생성 및 전시
- 이름·설명·색상·희귀도 기반의 개별 조형 디자인
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

The Pages build generates one locally hosted GLB model for every catalog entry (1,000 total). Each model is built deterministically from its own aura ID, Korean name, description, palette, and rarity tier. Name-led sculptural families (for example crystal, cosmos, flora, geode, vortex, wings, frost, spiral, sanctum, crown, comet, and blade) provide distinct primary silhouettes; per-aura geometry, asymmetry, orbit layout, accents, and tier details make each asset individual rather than reusing a small set of meshes with recolored materials.

Models are loaded on demand through Three.js GLTFLoader. The build also validates all 1,000 GLB files and publishes `assets/aura/manifest.json`, containing each model's catalog identity, file size, mesh count, bounds, and SHA-256 digest. The manifest validation fails the deployment if a model is missing, malformed, empty, or byte-identical to another model.

- Source geometry is generated locally by `tools/generate_aura_models.py`.
- Validation and manifest generation: `tools/validate_aura_models.py`.
- No external model downloads are required during deployment.
