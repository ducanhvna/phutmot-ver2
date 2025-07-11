FROM python:3.11-slim-bullseye

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Cài các thư viện hệ thống cần thiết cho pyodbc + SQL Server
RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd curl gnupg2 unixodbc-dev gcc g++
#     curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
#     curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list && \
#     apt-get update && \
#     (dpkg --print-architecture | grep -q amd64 && ACCEPT_EULA=Y apt-get install -y msodbcsql17 || echo "Skipping msodbcsql17 install: not amd64 architecture; ODBC Driver 17 for SQL Server will not be available.")

COPY . .

COPY entrypoint.sh .
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
