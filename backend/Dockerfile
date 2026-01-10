# 1. Base Python image
FROM python:3.10-slim

# 2. Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    unzip \
    libopus0 \
    libasound2 \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# 3. Download & install Rhubarb Lip Sync (Linux version)
RUN wget https://github.com/DanielSWolf/rhubarb-lip-sync/releases/download/v1.14.0/Rhubarb-Lip-Sync-1.14.0-Linux.zip -O /tmp/rhubarb.zip && \
    unzip /tmp/rhubarb.zip -d /opt/rhubarb && \
    chmod +x /opt/rhubarb/Rhubarb-Lip-Sync-1.14.0-Linux/rhubarb && \
    ln -s /opt/rhubarb/Rhubarb-Lip-Sync-1.14.0-Linux/rhubarb /usr/local/bin/rhubarb && \
    rm /tmp/rhubarb.zip

# 4. Set working directory
WORKDIR /app

# 5. Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy project files
COPY . .

# 7. Expose API port (Render uses 10000 by default)
EXPOSE 10000

# 8. Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000", "--workers", "1"]
