# Use slim Python 3.11 base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt ./

# Install system dependencies for Tkinter and image handling
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libfreetype6-dev \
        libjpeg-dev \
        zlib1g-dev \
        tk-dev \
        tcl-dev \
        x11-apps \
        xvfb \
        && pip install --no-cache-dir -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Make Python output unbuffered
ENV PYTHONUNBUFFERED=1

# Set matplotlib backend for headless plotting (can be overridden if GUI works)
ENV MPLBACKEND=Agg

# Set the DISPLAY environment variable (equivalent to -e DISPLAY=host.docker.internal:0.0)
ENV DISPLAY=host.docker.internal:0.0

# Start X virtual framebuffer if needed and run dashboard
CMD ["python", "dashboard.py"]