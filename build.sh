#!/bin/bash

set -e

for f in programs/*; do
    name=$(basename "$f")
    echo -e "\033[32mAssembling $name...\033[0m"
    vasm -Fbin -dotdir -o "roms/${name%.*}.bin" "$f" -L "apis/${name%.*}.txt" -esc
    echo
done

