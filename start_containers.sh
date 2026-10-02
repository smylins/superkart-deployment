#!/bin/bash
# Builds and starts the SuperKart backend (Flask) and frontend (Streamlit) containers
# on a shared Docker network. Run inside the Codespace with:  bash start_containers.sh
set -e

# 1. Create a Docker network so the two containers can talk to each other by name
docker network create superkart-app-network 2>/dev/null || true

# 2. Remove old containers (if any) so the script can be re-run safely
docker rm -f backend frontend 2>/dev/null || true

# 3. Build and run the backend (Flask API on port 7860), container name "backend"
docker build -t superkart-backend ./backend_files
docker run -d --name backend --network superkart-app-network -p 7860:7860 superkart-backend

# 4. Build and run the frontend (Streamlit on port 8501), container name "frontend"
docker build -t superkart-frontend ./frontend_files
docker run -d --name frontend --network superkart-app-network -p 8501:8501 superkart-frontend

echo "Containers running:"
docker ps
echo "Backend  -> port 7860   |   Frontend -> port 8501"
