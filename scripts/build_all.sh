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

build master mas-0.13.x-or-newer
build py2 mas-0.12.x-or-older

rm -rf build
mv _build build