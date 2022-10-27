#!/bin/sh

dir="$(dirname "$(CDPATH="" cd -- "$(dirname -- "$0")" && pwd)")"
cd "$dir" || exit 1

rm -rf build
mkdir -p _build

build() {
    git switch "$1" >/dev/null 2>&1
    ./scripts/build.sh
    file="$(find build -type f)"
    mv "$file" "_build/$(basename "${file%.zip}-$2.zip")"
    git switch - >/dev/null 2>&1
}

build master r8-py39
build py2 r6-py27

rm -rf build
mv _build build