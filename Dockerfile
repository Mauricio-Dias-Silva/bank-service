
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Expose port
EXPOSE 8080

# Command to run (using gunicorn)
CMD sh -c "python manage.py migrate && gunicorn --bind 0.0.0.0:8080 config.wsgi:application"
