#syntax=docker/dockerfile:1 


FROM node:23-slim

RUN apt-get update && apt-get install -y curl && apt-get clean

# Create/Set dir
WORKDIR /frontend 
 
# Copy only package files first
COPY package.json package-lock.json ./

# Install dependencies 
RUN npm install 

ARG INSTALL_PLAYWRIGHT=false

# Conditionally install Playwright and its deps
RUN if [ "$INSTALL_PLAYWRIGHT" = "true" ]; then \
      npx playwright install --with-deps; \
    fi

# Copy source
COPY . .


# FROM node:23-slim
#
# # Create/Set dir
# WORKDIR /frontend 
#
# # Get yarn 
# RUN corepack enable && corepack prepare yarn@stable --activate
#
# # Copy only package files first
# COPY package.json package-lock.json ./
#
# # Install dependencies 
# # RUN yarn install --frozen-lockfile
# RUN npm install 
#
#
#
# # Copy source
# COPY . .
#
#


