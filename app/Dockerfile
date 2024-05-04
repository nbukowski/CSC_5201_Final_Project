FROM python:3

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Use ENTRYPOINT to run a startup script
COPY startup.sh /app/startup.sh

RUN chmod +x /app/startup.sh

ENTRYPOINT ["/bin/bash", "/app/startup.sh"]

EXPOSE 5000