# Use a minimal Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install the Python dependencies first (better use of the Docker layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the API code and the serialized model into the container
COPY . .

# The Flask API listens on port 7860
EXPOSE 7860

# Start the app with gunicorn: 4 workers, bound to all interfaces on port 7860
# "app:superkart_api" -> the superkart_api object inside app.py
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
