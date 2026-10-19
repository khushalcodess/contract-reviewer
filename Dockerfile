FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
COPY requirements-app.txt .
RUN pip install --no-cache-dir -r requirements-app.txt
COPY src ./src
COPY app ./app
COPY eval ./eval
ENV HF_HOME=/hf_cache
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]