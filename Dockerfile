# ---------- Stage 1: Build React App ----------
ARG FRONTEND_IMAGE
ARG BACKEND_IMAGE

FROM ${FRONTEND_IMAGE} AS frontend-build

# following args should be inside the frontend-build stage, else they will be picked
ARG FRONTEND_ENV
ARG BACKEND_URL

ENV FRONTEND_ENV=REACT_APP_BACKEND_URL=${BACKEND_URL}

WORKDIR /app
RUN echo "[BUILD_LOG] Copying frontend files..."
RUN echo "[BUILD_LOG] BACKEND_URL=${BACKEND_URL}"
COPY frontend/ /app/

RUN echo "[BUILD_LOG] Setting up frontend environment..."
RUN sed -i "s|https://[^/]*preview[^/]*\.emergentagent\.com|${BACKEND_URL}|g" /app/.env
RUN cat /app/.env

RUN echo "[BUILD_LOG] Installing and building frontend dependencies..."
RUN yarn install --check-files && yarn build

# ---------- Final Image ----------
FROM ${BACKEND_IMAGE}

# Optional post-install commands
ARG POST_INSTALL_COMMANDS=""

RUN echo "[BUILD_LOG] Setting up backend environment..."
RUN echo "[BUILD_LOG] Copying backend files..."
COPY . /app

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Install Nginx and other dependencies
ENV DEBIAN_FRONTEND=noninteractive

# Copy nginx config after installation
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built frontend AFTER Nginx is installed
COPY --from=frontend-build /app/build /usr/share/nginx/html

# Install Python dependencies for backend
RUN echo "[BUILD_LOG] Installing Python dependencies..."
# Emergent Integrations is a private package that is hosted on a cloudfront CDN
RUN pip config set global.extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
# --no-dependencies to avoid conflicts, as we are installing pip freeze output, all the dependencies are already listed
RUN pip install --no-cache-dir --no-dependencies -r /app/backend/requirements.txt

# Run optional post-install commands if provided
RUN if [ -n "$POST_INSTALL_COMMANDS" ]; then \
        echo "[BUILD_LOG] Running post-install commands: $POST_INSTALL_COMMANDS"; \
        eval "$POST_INSTALL_COMMANDS"; \
    fi

# Add env variables if needed
ENV PYTHONUNBUFFERED=1

# Start both services: Uvicorn and Nginx
CMD ["bash", "/entrypoint.sh"]