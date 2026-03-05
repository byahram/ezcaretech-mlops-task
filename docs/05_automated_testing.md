# 5. 자동화된 테스트 (실제 구현 + 실행 결과)

## 1. 테스트 왜 넣었나? (목적과 범위)

모델이 매달 업데이트되는데, 제가 일일이 "이거 긍정 나오나? 서버 안 죽나?" 수동으로 포스트맨 돌려볼 시간이 없습니다. 그래서 CI/CD 파이프라인 안에서 모델 버그나 API 결함을 자동으로 잡아내려고 `pytest`를 붙였습니다.

- **범위**: 
  - K8s가 주기적으로 찌를 `/health` 엔드포인트가 잘 살아있는지 확인
  - `/predict`에 텍스트 넣었을 때 에러 안 뱉고 `result`, `latency_ms` 같은 필수 값을 잘 뱉어내는지 검증

## 2. 테스트 작성 내용 (`tests/test_api.py`)

FastAPI의 `TestClient`를 써서 서버를 직접 안 띄워도 코드로 API를 테스트하게 만들었습니다.

1. **`test_read_health`**: 상태 코드가 200이 뜨는지, JSON에 `{"status": "up"}`이 제대로 들어가는지 체크합니다.
2. **`test_predict_endpoint`**: "테스트 문장입니다."를 넣어서 실제 추론을 돌려보고 리턴값 스키마가 맞는지 봅니다. (Mocking 안 하고 진짜 모델 추론을 태워서 검증합니다.)

## 3. 실행 결과 인증

로컬 환경에서 직접 돌려본 `pytest` 결과입니다. (에러 났던 컴패터빌리티 이슈도 `httpx<0.28.0`으로 핀(pin) 꽂아서 해결했습니다.)

```text
============================= test session starts ==============================
platform darwin -- Python 3.14.3, pytest-9.0.2, pluggy-1.6.0
rootdir: /Users/ahramkim/Documents/GitHub/ezcaretech-mlops-task
plugins: anyio-4.12.1
collected 2 items

tests/test_api.py ..                                                     [100%]

============================== 2 passed in 5.23s ===============================
```

## 4. 앞으로의 계획

지금은 런타임 에러가 안 나는지, 스키마가 맞는지 위주로 보는데, 나중에 시간 되면 "미리 정해둔 정답 셋(Test Set) 100개 넣고 Accuracy 80% 밑으로 떨어지면 배포 중단" 같은 성능 검증 테스트도 추가해보고 싶습니다.