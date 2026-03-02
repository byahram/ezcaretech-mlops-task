# 빌드 환경 (경량화를 위해 파이썬 슬림 이미지 사용)
FROM python:3.10-slim AS builder

WORKDIR /app

# 빌드에 필요한 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

# 의존성 설치
COPY api/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 2단계: 실행 환경
FROM python:3.10-slim

WORKDIR /app

# 보안을 위해 권한이 제한된 사용자 생성 및 전환
RUN useradd -m mluser
USER mluser

# 빌드 단계에서 설치된 패키지 복사
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 소스 코드 및 모델 로드 로직 복사
COPY api/ ./api/

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV APP_ENV=production

# API 포트 노출
EXPOSE 8000

# 실행 명령 (Gunicorn/Uvicorn 활용)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]