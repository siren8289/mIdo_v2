# regression PASS

## RUN-20261102-202327

### REG-FRONT 프런트 타입체크와 빌드

- 목적: tsc --noEmit과 vite build가 모두 성공한다.
- 도구 A: tsc --noEmit / PASS
- 도구 B: vite build / PASS
- 기대: exit 0
- 실제: A:exit 0 / B:exit 0
- 근거: A[PASS] tsc --noEmit exit 0 || B[PASS] vite build exit 0 vite v8.3.4 building client environment for production... transforming... ✓ 27 modules transformed. rendering chunks... computing gzip size... dist/index.html                   0.41 kB │ gzip:  0.30 kB dist/assets/index-BnGW-5Wg.css   11.67 kB │ gzip:  3.19 kB dist/assets/index-C1yzst9-.js   188.35 kB │ gzip: 62.56 kB  ✓ built in 124ms
- 위치: front/package.json tsc --noEmit:UNKNOWN
- 시각: 2026-11-02T20:23:27+09:00 / 커밋: 62e4fd07ce31+dirty

## RUN-20261102-202520

### REG-FRONT 프런트 타입체크와 빌드

- 목적: tsc --noEmit과 vite build가 모두 성공한다.
- 도구 A: tsc --noEmit / PASS
- 도구 B: vite build / PASS
- 기대: exit 0
- 실제: A:exit 0 / B:exit 0
- 근거: A[PASS] tsc --noEmit exit 0 || B[PASS] vite build exit 0 ip size... dist/index.html 0.41 kB │ gzip: 0.30 kB dist/assets/index-BnGW-5Wg.css 11.67 kB │ gzip: 3.19 kB dist/assets/index-C1yzst9-.js 188.35 kB │ gzip: 62.56 kB ✓ built in 186ms
- 위치: front/package.json tsc --noEmit:UNKNOWN
- 시각: 2026-11-02T20:25:20+09:00 / 커밋: 62e4fd07ce31+dirty

## RUN-20261102-221831

### REG-FRONT 프런트 타입체크와 빌드

- 목적: tsc --noEmit과 vite build가 모두 성공한다.
- 도구 A: tsc --noEmit / PASS
- 도구 B: vite build / PASS
- 기대: exit 0
- 실제: A:exit 0 / B:exit 0
- 근거: A[PASS] tsc --noEmit exit 0 || B[PASS] vite build exit 0 ip size... dist/index.html 0.41 kB │ gzip: 0.30 kB dist/assets/index-BnGW-5Wg.css 11.67 kB │ gzip: 3.19 kB dist/assets/index-C1yzst9-.js 188.35 kB │ gzip: 62.56 kB ✓ built in 293ms
- 위치: front/package.json tsc --noEmit:UNKNOWN
- 시각: 2026-11-02T22:18:31+09:00 / 커밋: 85df5792fdf7

