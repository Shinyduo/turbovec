FROM python:3.12-slim

WORKDIR /app

# turbovec ships prebuilt wheels (x86-64-v3 / Haswell 2013+), so no Rust toolchain
# is needed at build time.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Persisted index lives here; mount a Railway volume at /data.
RUN mkdir -p /data
ENV DATA_DIR=/data

# Railway injects PORT at runtime; default to 8080 for local runs.
ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
