# Name: Dockerfile
#
# Description: Development environment for ToolOps with PostgreSQL support.
#
# Last_updated: 2026-05-30
#
# Updated_by: Hedi Manai
# Github: https://github.com/hedimanai-pro
# LinkedIn: https://www.linkedin.com/in/hedimanai
#
# Note: This project is open source for knowledge sharing

FROM python:3.12-slim

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/workspace

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy dependency definitions first
COPY pyproject.toml ./
COPY README.md ./
COPY CHANGELOG.md ./
COPY requirements.txt ./

# Copy package source before editable installation
COPY toolops/ ./toolops/

# Install ToolOps with its default dependencies and development tools
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the development files
COPY tests/ ./tests/
COPY Makefile ./

# Default command runs the test suite
CMD ["make", "test"]
