#!/usr/bin/env python3
"""Generate catalog.json from built pack zips.

Reads every *.zip in the input directory, extracts the embedded
manifest.json, computes the zip sha256 + size, and emits the catalog
manifest the app fetches (formatVersion 1). The URL template points at
this repo's GitHub Release assets.

Usage:
    python3 generate_catalog.py --zips-dir out/ --release-tag v1 > catalog.json
"""

import argparse
import hashlib
import json
import sys
import zipfile
from pathlib import Path

RELEASE_URL_TEMPLATE = (
    "https://github.com/DevAyo-Technologies/scholia-packs/releases/"
    "download/{tag}/{filename}"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zips-dir", required=True)
    parser.add_argument("--release-tag", required=True)
    args = parser.parse_args()

    packs = []
    for zip_path in sorted(Path(args.zips_dir).glob("*.zip")):
        data = zip_path.read_bytes()
        with zipfile.ZipFile(zip_path) as z:
            manifest = json.loads(z.read("manifest.json"))
        packs.append(
            {
                "id": manifest["id"],
                "language": manifest["language"],
                "definitionLanguage": manifest["definitionLanguage"],
                "version": manifest["version"],
                "sourceTag": manifest["sourceTag"],
                "attribution": manifest["attribution"],
                "sizeBytes": len(data),
                "url": RELEASE_URL_TEMPLATE.format(
                    tag=args.release_tag, filename=zip_path.name
                ),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )

    if not packs:
        print("no pack zips found", file=sys.stderr)
        return 1

    json.dump({"formatVersion": 1, "packs": packs}, sys.stdout, indent=2)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
