FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc g++ make pkg-config \
    ffmpeg libsndfile1 git curl wget ca-certificates \
    libavdevice-dev libavfilter-dev libavformat-dev libavcodec-dev \
    libswscale-dev libavutil-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip setuptools wheel


RUN pip install av==14.0.1 --only-binary=:all: --no-cache-dir


RUN pip install faster-whisper==1.0.1 --no-deps --no-cache-dir


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Copy project ----------
COPY . .

# ---------- Environment ----------
ENV DJANGO_SETTINGS_MODULE=AfrikAI.settings
ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# ---------- Run ----------
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "AfrikAI.asgi:application"]
