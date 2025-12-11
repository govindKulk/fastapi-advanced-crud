FROM python:3.11-slim


# Set Enironment Variables

# allow logs in container logs
ENV PYTHONUNBUFFERED=1

# don't write files such as .pyc reducing the image size
ENV PYTHONDONTWRITEBYTECODE=1

# disabled pip download cache so that cached wheels and tarballs are not stored in the image
ENV PIP_NO_CACHE_DIR=1

# stops pip from checking newer version on every run
ENV PIP_DISABLE_PIP_VERSION_CHECK=1


# Set Work Directory
WORKDIR /app

# Install System Dependencies
# apt-get update -> updates package metadata so that you can install latest version of system packages
# apt-get install ... build-essential libpq-dev installs compilation tools and PostgreSQL client headers, which are typically needed to compile wheels for packages like psycopg2 or other C‑extensions.
# --no-install-recommends avoids pulling extra suggested packages, keeping the image smaller.
# rm -rf /var/lib/apt/lists/* deletes cached apt metadata to reduce image size further.
# Combining with && into one RUN layer minimizes the number of layers and ensures cleanup happens only if installs succeed.
RUN apt-get update \\
    && apt-get install -y --no-install-recommends \\
        build-essential \\
        libpq-dev \\
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN pip install poetry

# Configure Poetry Environment vars
# POETRY_NO_INTERACTION = no interaction mode is needed in automated environments like docker
# POETRY_VENV_IN_PROJECT = creates .venv in project directory , here in this case /app/.venv - which is convinient in production
# POETRY_CACHE_DIR=/tmp/poetry_cache -> moves poetry cache to temporary path, reduces bloating of the image
ENV POETRY_NO_INTERACTION=1 \\
    POETRY_VENV_IN_PROJECT=1 \\
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Copy Poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
# --only=main -> installs only non-dev dependencies which are required in prod
# removes the Poetry cache from the already defined directory
RUN poetry install --only=main && rm -rf $POETRY_CACHE_DIR

# Copy Application
# This is essential, we downloaded the dependencies first creating a seperate docker layer.
# no in future if only code changes it won't trigger the installation of the application dependencies again
COPY . .


# Create non-root user
# RUN ... app -> creates a non-root user named app
# For security reasons, run the application by a less powerfull non root user
# chown -R app:app /app -> changes ownership of the app directory so that app user can read/write in the app directory
# USER app -> switches default user for subsequnt layers
RUN useradd --create-home --shell /bin/bash app \\
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "uvicorn", "app.main:task_app", "--host", "0.0.0.0", "--port", "8000"]




