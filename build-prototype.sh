#!/usr/bin/env bash
# Offline build and image checks only. No flash target is invoked.
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
export PATH="$ROOT/venv/bin:$ROOT/toolchain/usr/bin:$ROOT/toolchain/bin:$PATH"
if [[ ! -f "$ROOT/smk/build-rk61/build.ninja" ]]; then
    meson setup "$ROOT/smk/build-rk61" "$ROOT/smk" \
        --buildtype=release -Disp=enabled -Dsleep=disabled
fi
meson compile -C "$ROOT/smk/build-rk61" royalkludge-rk61_default_smk.hex
python3 "$ROOT/test_prototype.py"
