FROM python:3.12-slim

# Install espeak-ng
RUN apt-get update && apt-get install -y espeak-ng && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . .

# Expose port
EXPOSE 10000  # Render assigns $PORT

# Run Flask dev server
CMD ["python", "app.py"]