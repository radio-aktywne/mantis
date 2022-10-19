ARG MINICONDA_IMAGE_TAG=4.10.3-alpine

FROM continuumio/miniconda3:$MINICONDA_IMAGE_TAG AS base

# add bash, because it's not available by default on alpine
# and ffmpeg because we need it for streaming
# and git to get pystreams
RUN apk add --no-cache bash ffmpeg git

WORKDIR /app/

# install poetry
COPY ./requirements.txt ./requirements.txt
RUN --mount=type=cache,target=/root/.cache \
    python3 -m pip install -r ./requirements.txt

# create new environment
# warning: for some reason conda can hang on "Executing transaction" for a couple of minutes
COPY environment.yaml ./environment.yaml
RUN --mount=type=cache,target=/opt/conda/pkgs \
    conda env create -f ./environment.yaml

# "activate" environment for all commands (note: ENTRYPOINT is separate from SHELL)
SHELL ["conda", "run", "--no-capture-output", "-n", "emischeduler", "/bin/bash", "-c"]

WORKDIR /app/emischeduler/

# add poetry files
COPY ./emischeduler/pyproject.toml ./emischeduler/poetry.lock ./

FROM base AS test

# install dependencies only (notice that no source code is present yet)
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --only main,test

# add source, tests and necessary files
COPY ./emischeduler/src/ ./src/
COPY ./emischeduler/tests/ ./tests/
COPY ./emischeduler/LICENSE ./emischeduler/README.md ./

# build wheel by poetry and install by pip (to force non-editable mode)
RUN poetry build -f wheel && \
    python -m pip install --no-deps --no-index --no-cache-dir --find-links=dist emischeduler

# add entrypoint
COPY ./entrypoint.sh ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh", "pytest"]
CMD []

FROM base AS production

# install dependencies only (notice that no source code is present yet)
RUN --mount=type=cache,target=/root/.cache \
    poetry install --no-root --only main

# add source and necessary files
COPY ./emischeduler/src/ ./src/
COPY ./emischeduler/LICENSE ./emischeduler/README.md ./

# build wheel by poetry and install by pip (to force non-editable mode)
RUN poetry build -f wheel && \
    python -m pip install --no-deps --no-index --no-cache-dir --find-links=dist emischeduler

# add entrypoint
COPY ./entrypoint.sh ./entrypoint.sh

ENV EMISCHEDULER_DB_HOST=localhost \
    EMISCHEDULER_DB_PORT=32000 \
    EMISCHEDULER_DB_PASSWORD=password \
    EMISCHEDULER_ADMIN_PORT=33000 \
    EMISCHEDULER_ADMIN_USERNAME=admin \
    EMISCHEDULER_ADMIN_PASSWORD=password \
    EMISCHEDULER_EMISTREAM_HOST=localhost \
    EMISCHEDULER_EMISTREAM_PORT=10000 \
    EMISCHEDULER_EMIARCHIVE_HOST=localhost \
    EMISCHEDULER_EMIARCHIVE_PORT=30000 \
    EMISCHEDULER_EMIARCHIVE_USERNAME=readonly \
    EMISCHEDULER_EMIARCHIVE_PASSWORD=password \
    EMISCHEDULER_EMISHOWS_HOST=localhost \
    EMISCHEDULER_EMISHOWS_PORT=35000

EXPOSE 33000

ENTRYPOINT ["./entrypoint.sh", "emischeduler"]
CMD []
