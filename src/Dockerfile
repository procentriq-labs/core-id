# ========================
# Base stage: Shared between dev and prod
# ========================
FROM python:3.11-slim AS base

# Set the working directory in the container
WORKDIR /usr/src

# Install deb dependencies
COPY packages.txt ./
RUN apt-get update
RUN xargs apt-get install -y < packages.txt

# Install any needed packages specified in requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Expose port for the API
EXPOSE 8000/tcp

# ========================
# Development Stage
# ========================
FROM base AS development

# Install additional dev dependencies
COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# DO NOT copy source code; mounted via compose

# Use uvicorn to run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ========================
# Production Stage
# ========================
FROM base AS production

# Copy only the application source code (no tests)
COPY ./app ./app
COPY ./alembic ./alembic
COPY alembic.ini ./

# Use uvicorn to run the FastAPI application in production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]