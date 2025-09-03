#syntax=docker/dockerfile:1 

FROM python:3.11-slim

RUN apt-get update && apt-get install -y postgresql-client && apt-get clean

# Set working directory
WORKDIR /backend

# Copy only requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app code
COPY . .


