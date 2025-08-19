#syntax=docker/dockerfile:1 

FROM python:3.11-slim

# Needed to poll database to ensure its running before starting
# Also for scripts that runs seeding
RUN apt-get update && apt-get install -y curl \
  && curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
  && apt-get install -y nodejs \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /backend

# Copy only requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Node.js package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of the app code
COPY . .


