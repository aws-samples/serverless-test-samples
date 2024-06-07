# app/Dockerfile

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

# COPY . .
ADD demo-app/urs-ui.py ./ui.py
ADD demo-app/requirements.txt .
ADD demo-app/_img ./_img
RUN pip3 install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
