# Base image: small Python 3.11 image (Debian Bookworm)
FROM python:3.11-slim-bookworm

# Avoid creating .pyc files and ensure logs print immediately (useful in containers)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# Copy Docker-only environment file into the container as ".env"
# IMPORTANT: Keep .env.docker OUT of GitHub (in .gitignore), but it WILL be inside the image.
COPY .env.docker /app/.env

# Install system dependencies required for:
# - Microsoft ODBC Driver 17 (msodbcsql17)
# - Building pyodbc if needed (gcc/g++)
# - unixODBC runtime + headers
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg2 \
    ca-certificates \
    unixodbc \
    unixodbc-dev \
    gcc \
    g++ \
  && mkdir -p /etc/apt/keyrings \
  # Add Microsoft package signing key (modern approach using keyrings)
  && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
     | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg \
  # Add Microsoft repo for Debian 12 (Bookworm)
  && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
     > /etc/apt/sources.list.d/mssql-release.list \
  && apt-get update \
  # Install Microsoft ODBC driver (accept EULA)
  && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17 \
  # Cleanup to keep image small
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements first so Docker can cache dependency installation
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of your application files (app.py, db.py, swagger.yml, controllers/, etc.)
COPY . /app

# Expose the port your Flask/Connexion app runs on
EXPOSE 5000

# Start the API
CMD ["python", "app.py"]
