# scholia-packs

Offline dictionary packs for the [Scholia](https://github.com/DevAyo-Technologies/scholia_app)
reading app — the static host chosen by the app's packaging decision D3:
a plain catalog manifest + zip artifacts on GitHub Releases. No backend
surface; the app treats these URLs as static data.

## Layout

- **Releases** hold the artifacts. One release per catalog version
  (tag `v1`, `v2`, …). Each release asset set:
  - `catalog.json` — the manifest the app fetches (`DICTIONARY_CATALOG_URL`)
  - one zip per pack (`<id>-v<version>.zip`)
- `main` carries this README + the generator for `catalog.json`.

Stable catalog URL (v1):
`https://github.com/DevAyo-Technologies/scholia-packs/releases/download/v1/catalog.json`

## Pack format (the app contract)

Each zip contains `manifest.json` + `pack.sqlite` (`entries` table,
senses-only). The authoritative schema lives in the app repo:
`tool/dictionary/README.md` there documents the sqlite layout, the
manifest fields, and the double verification the app performs (zip
sha256 against the catalog entry, then inner `pack.sqlite` sha256
against the embedded manifest). A corrupt artifact is rejected and
deleted, never partially installed.

## Wave-1 packs (2026-10-29)

Monolingual packs (glosses in the pack language), built from the
**non-English Wiktionary editions** via
[wiktextract / kaikki.org](https://kaikki.org) raw JSONL extracts,
filtered to the edition's own language. Licensed **CC BY-SA 4.0 + GFDL**
(the share-alike binds the pack artifact, never app code or private user
records); the full license text is embedded in every pack's manifest and
shown in the app under Settings → Dictionaries.

| Pack | Entries | Zip | Source edition |
|---|---|---|---|
| `es-es-v1.zip` | 846,729 | 39.0 MB | Spanish Wiktionary (eswiktionary) |
| `pt-pt-v1.zip` | 399,101 | 18.2 MB | Portuguese Wiktionary (ptwiktionary) |
| `de-de-v1.zip` | 978,089 | 94.3 MB | German Wiktionary (dewiktionary) |
| `fr-fr-v1.zip` | 2,092,631 | 157.8 MB | French Wiktionary (frwiktionary) |
| `ja-ja-v1.zip` | 131,061 | 9.8 MB | Japanese Wiktionary (jawiktionary) |
| `ko-ko-v1.zip` | 69,974 | 4.2 MB | Korean Wiktionary (kowiktionary) |

Extracted 2026-10-29 from wiktextract dumps dated 2026-10-01; sizes and
checksums are recorded in `catalog.json` (the app verifies both layers).

Pack ids use bare ISO 639-1 codes because that is what the app's
`LanguageCatalog.normalize` folds language values to before resolving a
pack (`pt-BR` → `pt`). The bundled English lite pack (`en-en`, Open
English Wordnet) ships inside the app itself, not here.

## Rebuilding a pack

The ETL lives in the app repo (`tool/dictionary/build_pack.dart`):

```bash
curl -sSL -o ko.jsonl.gz https://kaikki.org/kowiktionary/raw-wiktextract-data.jsonl.gz
gunzip ko.jsonl.gz
dart run tool/dictionary/build_pack.dart \
  --adapter wiktextract \
  --input ko.jsonl \
  --out . \
  --language ko --definition-language ko \
  --version 1 \
  --source-tag wiktionary-ko \
  --attribution "Korean Wiktionary via wiktextract (CC BY-SA 4.0 + GFDL)" \
  --license-name "CC BY-SA 4.0 + GFDL" \
  --license-url "https://creativecommons.org/licenses/by-sa/4.0/" \
  --license-file CC-BY-SA-4.0.txt \
  --lang-code ko
```

Dataset swaps bump the pack `version` and ship as a new catalog release;
the app picks the highest installed/catalog version per language pair.
