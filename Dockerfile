ARG MINICONDA_IMAGE_TAG=4.10.3-alpine

FROM continuumio/miniconda3:$MINICONDA_IMAGE_TAG

# add bash, because it's not available by default on alpine
# and ffmpeg because we need it for streaming
# and git to get pystreams
RUN apk add --no-cache bash ffmpeg git

# install poetry
COPY ./requirements.txt /tmp/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /tmp/requirements.txt

# create new environment
# see: https://jcristharif.com/conda-docker-tips.html
# warning: for some reason conda can hang on "Executing transaction" for a couple of minutes
COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml && \
    conda clean -afy && \
    find /opt/conda/ -follow -type f -name '*.a' -delete && \
    find /opt/conda/ -follow -type f -name '*.pyc' -delete && \
    find /opt/conda/ -follow -type f -name '*.js.map' -delete

# "activate" environment for all commands (note: ENTRYPOINT is separate from SHELL)
SHELL ["conda", "run", "--no-capture-output", "-n", "emischeduler", "/bin/bash", "-c"]

# add poetry files
COPY ./emischeduler/pyproject.toml ./emischeduler/poetry.lock /tmp/emischeduler/
WORKDIR /tmp/emischeduler

# install dependencies only (notice that no source code is present yet) and delete cache
RUN poetry install --no-root && \
    rm -rf ~/.cache/pypoetry

# add source and necessary files
COPY ./emischeduler/src/ /tmp/emischeduler/src/
COPY ./emischeduler/LICENSE ./emischeduler/README.md /tmp/emischeduler/

# build wheel by poetry and install by pip (to force non-editable mode)
RUN poetry build -f wheel && \
    python -m pip install --no-deps --no-index --no-cache-dir --find-links=dist emischeduler

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
    EMISCHEDULER_EMIARCHIVE_PASSWORD=password

EXPOSE 33000

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "emischeduler", "emischeduler"]
