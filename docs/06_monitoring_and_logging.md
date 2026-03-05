# 6. 모니터링 및 로깅 설계 (설정 파일 + 설명)

## 1. 어떻게 모니터링 할 것인가 (목표와 전략)
우리 팀엔 서버 장애 났을 때 전용으로 봐줄 인프라 운영자가 따로 없습니다. 개발자 5명이서 다 해야 하니까, 문제가 터졌을 때 "어디서, 왜" 터졌는지 바로 알 수 있는 관측성(Observability) 셋업이 필수입니다. 외부 유료 SaaS(DataDog 같은 거)는 못 쓰게 되어 있어서, 무료이면서 가장 레퍼런스가 많은 **Prometheus + Grafana + Loki** 오픈소스 조합을 선택했습니다.

## 2. 모니터링 및 로깅 설정 파일

### 2.1 Prometheus 설정 (`monitoring/prometheus.yml`)
FastAPI에서 열어둔 `/metrics` 엔드포인트를 프로메테우스가 15초마다 알아서 긁어가도록(pull) 설정했습니다.

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ml-api-service'
    static_configs:
      - targets: ['ml-api-service:8000']
```

### 2.2 Docker Compose 스택 (`monitoring/docker-compose.yml`)
로컬이나 단일 서버에서 띄울 때 앱이랑 모니터링 도구를 한 묶음으로 올리는 설정입니다.

```yaml
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
```

## 3. 핵심 모니터링 지표 (뭘 볼 것인가)
- **추론 지연 시간(Latency)**: K8s 올려놓고 모델 응답이 8ms에서 갑자기 100ms 넘어가는 스파이크가 튀는지 감시합니다.
- **초당 처리량(RPS/TPS)**: 트래픽이 평소보다 얼마나 들어오는지 파악합니다.
- **에러율(Error Rate)**: HTTP 500 에러 떨어지면 즉시 알람 가도록 모니터링합니다.

## 4. 로깅 구조 설계
- **JSON 로깅**: 나중에 검색하기 편하게 `python-json-logger` 같은 걸 써서 모든 로그 포맷을 JSON으로 통일할 예정입니다.
- **중앙 집중형 (Loki + Promtail)**: 각 컨테이너 콘솔에 찍히는 로그를 Promtail이 수거해서 Loki로 쏴줍니다. 이렇게 하면 Grafana 화면 하나에서 메트릭 그래프랑 텍스트 로그를 동시에 볼 수 있어서 원인 파악이 진짜 빠릅니다. (에러 그래프 뛰었을 때 그 시간대 로그 바로 확인 가능!)

## 5. 설계 결정 이유
- **통합 뷰**: 이리저리 서버 들어가보고 문서 볼 필요 없이 Grafana 대시보드 하나만 보면 끝이라서 개발팀 운영 부담이 확 줍니다.
- **K8s 호환성**: 어차피 나중에 Kubernetes에 올릴 때도 Kube-Prometheus-Stack(Helm)만 쓰면 지금 짠 구조를 거의 그대로 들고 갈 수 있어서 확장성이 좋습니다.