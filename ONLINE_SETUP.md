# AETHER RNG 온라인 서비스

## 구성 완료
- Supabase 프로젝트: `AETHER-RNG`
- 프로젝트 리전: Seoul (`ap-northeast-2`)
- 데이터베이스: `player_profiles`, `player_inventory`, `roll_history`
- RLS 정책 및 서버 측 `roll_aura()` RPC
- 전체 플레이어 랭킹 뷰
- 브라우저용 Supabase 설정 파일
- GitHub Pages 자동 배포 워크플로

## 온라인 기능
1. 웹사이트에서 이메일과 비밀번호로 회원가입합니다.
2. 이메일 인증이 요구되면 인증 메일을 확인합니다.
3. 로그인한 뒤 뽑기를 실행하면 서버에서 결과를 결정하고 DB에 기록합니다.
4. 같은 계정으로 다른 기기에서 로그인하면 저장된 오라와 기록을 불러옵니다.
5. 랭킹 탭에서 공개 플레이어 순위를 확인할 수 있습니다.

## GitHub Pages
기본 주소: https://hgs10622-dotcom.github.io/SolsRNG-KR/

저장소 Settings → Pages에서 Source가 **GitHub Actions**인지 확인해야 합니다. 워크플로는 main 브랜치 변경 시 자동 실행됩니다.

## 보안
- 브라우저에는 공개용 publishable key만 포함됩니다.
- service_role 키는 절대 프론트엔드에 넣지 않습니다.
- 플레이어 인벤토리와 기록은 RLS로 계정별 접근을 제한합니다.
- 공개 랭킹은 플레이어 이름, 총 뽑기 수, 최고 희귀도만 표시합니다.

## 도메인과 가동 시간
사용자 소유의 도메인을 별도로 등록해야 사용자 지정 주소를 연결할 수 있습니다. GitHub Pages는 정적 웹사이트 호스팅이며 계약상 24/7 가동 보장은 아닙니다. Supabase 무료 요금제에도 사용량 제한 및 일시 중지 조건이 있을 수 있습니다.
