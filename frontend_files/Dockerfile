# Use a minimal Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install the Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the Streamlit app
COPY . .

# Streamlit listens on port 8501
EXPOSE 8501

# Address of the backend container on the Docker network (can be overridden with -e BACKEND_URL=...)
ENV BACKEND_URL=http://backend:7860

# Run the Streamlit app, accessible from outside the container
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]
