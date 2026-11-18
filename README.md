# AETHER RNG v0.1.0

Roblox가 아닌 웹브라우저용 오라 수집 시뮬레이터입니다.

## 실행
`index.html`을 브라우저에서 열면 바로 실행됩니다.

## 기능
- 18종 오라 / 8단계 희귀도
- 확률 기반 뽑기 및 획득 연출
- 인벤토리와 오라 도감
- 오라 장착 / 자동 뽑기
- 최근 획득 기록
- 브라우저 자동 저장(localStorage)
- 저장 데이터 JSON 내보내기
- 모바일 반응형 UI

## GitHub Pages 배포
1. 저장소 Settings → Pages로 이동합니다.
2. Build and deployment의 Source를 **GitHub Actions**로 설정합니다.
3. `.github/workflows/pages.yml`이 main 브랜치 변경 시 자동 배포합니다.
4. 기본 주소: https://hgs10622-dotcom.github.io/SolsRNG-KR/

## 온라인 DB 준비
공유 계정·인벤토리·랭킹을 위한 Supabase SQL 스키마가 `supabase/schema.sql`에 있습니다. 설정 순서는 [ONLINE_SETUP.md](ONLINE_SETUP.md)를 확인하세요. 현재 브라우저 버전은 Supabase 프로젝트 연결 전까지 로컬 저장 모드입니다.

## 유의사항
모든 뽑기는 무료이며 현금 결제나 현금성 재화를 사용하지 않습니다. 브라우저 저장 데이터는 현재 기기에만 저장됩니다.
