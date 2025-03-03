# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

ARG PYTHON_VERSION=3.12.8
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install Poetry
RUN pip install --no-cache-dir poetry

# Set up the Poetry cache directory
ENV POETRY_CACHE_DIR=/app/.cache/pypoetry
RUN poetry config cache-dir $POETRY_CACHE_DIR

RUN poetry cache clear --all pypoetry

# Copy the Poetry configuration files (pyproject.toml, poetry.lock) into the container.
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry (without installing the current project itself).
RUN poetry install --no-root

# Switch to the non-privileged user to run the application.
RUN chown -R appuser:appuser /app
USER appuser

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8000

# Run the application.
CMD poetry run python do_it_yourself.py
