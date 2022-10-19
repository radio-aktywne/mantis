#!/bin/bash --login

set +euo pipefail
conda activate emischeduler
set -euo pipefail

exec "$@"
