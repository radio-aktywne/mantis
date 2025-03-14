# Use generic base image with Nix installed
FROM nixos/nix:2.26.2 AS env

# Configure Nix
RUN echo "extra-experimental-features = nix-command flakes" >> /etc/nix/nix.conf

# Set working directory to something other than root
WORKDIR /env/

# Copy Nix files
COPY flake.lock *.nix ./

# Copy env script
COPY scripts/env.sh scripts/env.sh

# Build runtime shell closure and activation script
RUN \
    # Mount cached store paths
    --mount=type=cache,target=/nix-store-cache/ \
    # Mount Nix evaluation cache
    --mount=type=cache,target=/root/.cache/nix/ \
    ./scripts/env.sh runtime build/ /nix-store-cache/

# Ubuntu is probably the safest choice for a runtime container right now
FROM ubuntu:24.04

# Use bash as default shell
SHELL ["/bin/bash", "-c"]

# Copy runtime shell closure and activation script
COPY --from=env /env/build/closure/ /nix/store/
COPY --from=env /env/build/activate /env/activate

# Set working directory to something other than root
WORKDIR /service/

# Create service user and data directory
RUN useradd --create-home service && \
    mkdir --parents data/

# Setup entrypoint for RUN commands
COPY scripts/shell.sh scripts/shell.sh
SHELL ["/service/scripts/shell.sh"]

# Copy Poetry files
COPY poetry.lock poetry.toml pyproject.toml ./

# Install dependencies only
# hadolint ignore=SC2239
RUN \
    # Mount Poetry cache
    --mount=type=cache,target=/root/.cache/pypoetry/ \
    poetry install --no-interaction --no-root --only main

# Copy source
COPY src/ src/

# Build wheel and install with pip to force non-editable install
# See: https://github.com/python-poetry/poetry/issues/1382
# hadolint ignore=SC2239
RUN poetry build --no-interaction --format wheel && \
    poetry run -- python -m pip install --no-deps --no-index --no-cache-dir dist/*.whl && \
    rm --recursive --force dist/ ./*.egg-info

# Copy file with environment variables for Python
COPY .env.python .env.python

# Setup main entrypoint
COPY scripts/entrypoint.sh scripts/entrypoint.sh
ENTRYPOINT ["/service/scripts/entrypoint.sh", "poetry", "run", "--", "dotenv", "--file", ".env.python", "run", "--", "mantis"]
CMD []

# Setup ownership
RUN chown --recursive service: ./
