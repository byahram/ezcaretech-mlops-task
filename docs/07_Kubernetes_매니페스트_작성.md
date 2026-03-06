# 7. Kubernetes 매니페스트 (설정 파일 + 설명)

## 1. 개요 및 매니페스트 구성
운영 전담자 없이 가용성 99.5% 이상을 달성하기 위해 Kubernetes에 어플리케이션을 배포하는 구조로 짰습니다. `deployments/` 폴더 내에 3개의 주요 YAML 파일을 작성했습니다.

- `01-deployment.yaml`: FastAPI 앱 파드를 정의 (Replicas, 리소스 제한, 프로브 등 설정)
- `02-service.yaml`: 생성된 파드들을 묶어주고 외부 트래픽을 분배하는 설정 (LoadBalancer/ClusterIP)
- `03-hpa.yaml`: 트래픽(CPU/Memory 부하)에 따라 파드를 늘리거나 줄이는 수평 확장(Auto-scaling) 설정

## 2. 핵심 설계 의사결정 (2년차 관점)

### 2.1 고가용성과 무중단 배포 (Deployment)
- **Replicas=2**: 파드 하나가 죽어도 다른 하나가 트래픽을 처리할 수 있게 기본 2개로 띄웠습니다.
- **Liveness & Readiness Probes**: 앱이 죽었는지(Liveness) 아니면 아직 트래픽 받을 준비가 안 됐는지(Readiness) K8s가 주기적으로 `/health` API를 찔러보고 알아서 파드를 재시작하거나 트래픽을 차단하게 했습니다. 이렇게 해야 저희 팀(개발자들)이 새벽에 직접 서버 재부팅하러 안 들어와도 됩니다.
- **Rolling Update**: 새로운 모델(버전)이 배포될 때, 구버전 파드를 한 번에 안 내리고 새 파드가 정상적으로 뜬 걸 확인(Readiness)한 다음 롤아웃되도록 `strategy`를 설정했습니다. (무중단 배포 구현 완성)

### 2.2 리소스 관리 (Resource Requests/Limits)
- ML 모델이 메모리나 CPU를 독식하다 서버 전체가 뻗는(OOM Killed 등) 대참사를 막기 위해 `requests`와 `limits`를 명확히 걸어뒀습니다. 
  - *Requests*: 컨테이너가 뜰 때 최소한 보장받는 리소스
  - *Limits*: 컨테이너가 쓸 수 있는 최대 리소스 (이걸 넘어가면 K8s가 파드를 죽임)

### 2.3 오토스케일링 (HPA)
- 월 1~2회 새 모델 배포될 때나 이벤트로 트래픽이 몰릴 때, CPU 평균 사용률이 70%를 넘으면 알아서 파드를 4개까지 늘리도록 HPA(Horizontal Pod Autoscaler)를 붙였습니다. 트래픽 빠지면 다시 2개로 줄어들어서 인프라 비용 낭비도 막았습니다.
