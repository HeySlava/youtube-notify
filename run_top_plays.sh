#!/usr/bin/env bash

WORK_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ENV_FILE=$WORK_DIR/.env
IMAGE=top_plays:latest
STORAGE_FOLDER=$WORK_DIR/storage

DOCKER_EXEC=$(which docker)
GIT_EXEC=$(which git)

if docker image inspect $IMAGE >/dev/null 2>&1; then
    docker image rm $IMAGE
fi

cd $WORK_DIR
mkdir -p $STORAGE_FOLDER
"$GIT_EXEC" -C "$WORK_DIR" pull --prune
"$DOCKER_EXEC" build -t "$IMAGE" "$WORK_DIR"
"$DOCKER_EXEC" run --rm -v "$STORAGE_FOLDER:/app/storage" --env-file "$ENV_FILE" "$IMAGE"
