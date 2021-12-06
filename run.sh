#!/usr/bin/env bash

set -eo pipefail

DC="${DC:-exec}"

# If we're running in CI we need to disable TTY allocation for docker-compose
# commands that enable it by default, such as exec and run.
TTY=""
if [[ ! -t 1 ]]; then
    TTY="-T"
fi

# -----------------------------------------------------------------------------
# Helper functions start with _ and aren't listed in this script's help menu.
# -----------------------------------------------------------------------------

function _dc {
    export DOCKER_BUILDKIT=1
    docker-compose ${TTY} "${@}"
}

function _use_local_env {
    sort -u environment/local.env | grep -v '^$\|^\s*\#' > './environment/local.env.tempfile'
    export "$(< environment/local.env.tempfile xargs)"
    rm environment/local.env.tempfile
}

# ----------------------------------------------------------------------------
# * General functions.

function up {
    cd backend
    rm main.db
    uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level info
}

function erd {
    cd backend
    eralchemy -i sqlite:///./main.db -o erd_from_sqlite.pdf
}

function front {
    cd frontend && pnpm dev
}

# -----------------------------------------------------------------------------

function help {
    printf "%s <task> [args]\n\nTasks:\n" "${0}"

    compgen -A function | grep -v "^_" | cat -n
}

TIMEFORMAT=$'\nTask completed in %3lR'
time "${@:-help}"
