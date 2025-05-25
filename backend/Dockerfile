FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY entrypoint.sh .
RUN chmod +x ./entrypoint.sh

RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd

ENTRYPOINT ["./entrypoint.sh"]
