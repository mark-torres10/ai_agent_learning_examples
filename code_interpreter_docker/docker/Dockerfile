FROM python:3.10

RUN apt-get update && \
    apt-get install -y build-essential && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd -m sandboxuser
USER sandboxuser
WORKDIR /home/sandboxuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "--version"]
