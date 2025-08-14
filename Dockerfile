# Use official Playwright image with Python and browsers pre-installed
FROM mcr.microsoft.com/playwright/python:v1.40.0

# Set working directory
WORKDIR /app

# Install system dependencies for better performance
RUN apt-get update && apt-get install -y \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy your entire project
COPY . .

# Create necessary directories
RUN mkdir -p /var/log/supervisor /var/log/nginx

# Create database tables
RUN python create_tables.py

# Create admin user
RUN python create_admin.py

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose port
EXPOSE 80

# Start supervisor (manages both nginx and your FastAPI app)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
