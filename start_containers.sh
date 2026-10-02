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

# 5. Check that the frontend can reach the backend over the Docker network.
#    Some Codespaces block container-to-container traffic; in that case the frontend
#    is restarted to call the backend through its public Codespace URL instead.
sleep 10
if docker exec frontend python -c "import requests; requests.get('http://backend:7860/', timeout=5)" 2>/dev/null; then
    echo "Frontend reaches the backend over the Docker network (http://backend:7860)."
elif [ -n "$CODESPACE_NAME" ]; then
    PUBLIC_BACKEND_URL="https://${CODESPACE_NAME}-7860.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
    echo "Docker network blocked - frontend will use the public backend URL: $PUBLIC_BACKEND_URL"
    docker rm -f frontend
    docker run -d --name frontend --network superkart-app-network -p 8501:8501 \
        -e BACKEND_URL="$PUBLIC_BACKEND_URL" superkart-frontend
    echo "IMPORTANT: set port 7860 (and 8501) to Public in the PORTS tab."
fi

# 6. Try to make both ports public automatically (otherwise do it in the PORTS tab)
if [ -n "$CODESPACE_NAME" ] && command -v gh >/dev/null; then
    gh codespace ports visibility 7860:public 8501:public -c "$CODESPACE_NAME" 2>/dev/null \
        && echo "Ports 7860 and 8501 set to Public." \
        || echo "Could not change port visibility automatically - set 7860 and 8501 to Public in the PORTS tab."
fi

echo "Containers running:"
docker ps
echo "Backend  -> port 7860   |   Frontend -> port 8501"
