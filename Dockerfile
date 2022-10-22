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

ENV EMISCHEDULER_API__HOST=0.0.0.0 \
    EMISCHEDULER_API__PORT=33000 \
    EMISCHEDULER_EMISTREAM__HOST=localhost \
    EMISCHEDULER_EMISTREAM__PORT=10000 \
    EMISCHEDULER_EMIARCHIVE__HOST=localhost \
    EMISCHEDULER_EMIARCHIVE__PORT=30000 \
    EMISCHEDULER_EMIARCHIVE__USERNAME=readonly \
    EMISCHEDULER_EMIARCHIVE__PASSWORD=password \
    EMISCHEDULER_EMIARCHIVE__SECURE=0 \
    EMISCHEDULER_EMISHOWS__HOST=localhost \
    EMISCHEDULER_EMISHOWS__PORT=35000 \
    EMISCHEDULER_LOG_FILE=/etc/emischeduler/log.csv \
    EMISCHEDULER_LIVE_RECORDINGS_BUCKET=live-recordings \
    EMISCHEDULER_PRE_RECORDED_BUCKET=pre-recorded

EXPOSE 33000

ENTRYPOINT ["./entrypoint.sh", "emischeduler"]
CMD []
