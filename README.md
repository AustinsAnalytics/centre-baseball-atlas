# Centre Atlas

Seven seasons of Centre baseball, connected. [Open the app](https://austinsanalytics.github.io/centre-baseball-atlas/).

A static, searchable field guide built from the supplied ColonelsProject baseball archive and the reviewed Fall 2026 Studio release. It covers 40,123 unique eligible pitches, 160 tracked sessions, 138 spring PBP games (44 without tracking), and 5,354 supported ball-flight reconstructions through October 24, 2026.

- Warm ivory / forest / gold palette and persistent top-right dark mode.
- Player notebooks with season histories and session logs; side-by-side comparisons.
- Headshots across player notebooks, cards, search, comparisons and leaderboards, with source credits and individual head-and-shoulder framing. See [photo sources and maintenance](docs/PHOTOS.md).
- Pitch lab with selectable measurement axes, location maps, arsenal details and pitch inspection.
- Game Room with exact-count, inning, outs, runner/score and outcome filters; searchable pitch ledger, complete recorded PA sequences and direct pitch links.
- [Analysis Studio](docs/ANALYSIS_STUDIO.md) with count-to-location drilldowns, valid consecutive-pitch matrices, measured contact neighborhoods, and matched-player development comparisons.
- Baseball-query search with visible filter interpretation, shareable studies, selected-sample exports, and evidence-based questions in player notebooks.
- Hitting outcomes, decision splits, confidence-gated contact and spray maps.
- Starting-position evidence, reconstructed fielding credits and target-specific catcher throws.
- Replay room with observed starts and bounded ball-flight fits, including clearly inferred catches.
- Recalculating discovery notes, uncertainty intervals, searchable review ledger, CSV exports and shareable views.

## Run locally

No front-end installation or build system is required. Use Node 20+ for verification and Python 3 for the local server:

```sh
python3 - <<'PY'
import gzip
from pathlib import Path
for p in Path('site/data').glob('*.json.gz'):
    p.with_suffix('').write_bytes(gzip.decompress(p.read_bytes()))
PY
node --test tests/*.test.mjs
python3 -m http.server 4390 --directory site
```

Open `http://127.0.0.1:4390/`. GitHub Actions performs these data checks and publishes `site/` to GitHub Pages on every push to `main`. The repository stores deterministic gzip versions of the data; Pages expands them to ordinary JSON before deployment. It requires no API keys, runtime server, external analytics or paid hosting.

## Data standards

Full-game PBP and tracked plate appearances are separate pools. The app never appends both versions of a matched PA. Spring-game outcomes default to full PBP; practice/scrimmage outcomes remain tracked and identifiable. Metrics are derived from numerator/denominator counts. EV, location and landings use explicit confidence gates. Original records are never overwritten.

All 1,521 eligible Fall 2026 pitches retain the final Studio decisions, including 82 tag corrections, reviewed exclusions and the confirmed Graham Johnson single. Historical review applies 27 extreme cross-family same-outing inferences and retains 588 other candidates for review. These are analytical judgments, not verified pitch intent. Source-normalized labels remain selectable.

Historical replay outcomes follow reconciled PA scoring where available, with original operator results preserved in the inspector. Fielder positions are observations at release, including unnamed position slots; they are not movement routes. An inferred airborne catch has no assigned catch time, point or catching fielder. Fielding credits are reconstructed PBP and retain known residual discrepancies.

No private roster-health documents, draft adjustment notes, credentials or personal documents are published. Model-based bat speed, MLB Stuff+ claims, invented official innings/ERA and unsupported fielding rankings are excluded. See the app’s **Data & methods** page and [data contract](docs/DATA_CONTRACT.md).

## Refreshing the data

See [UPDATE_DATA.md](docs/UPDATE_DATA.md). Source exports are kept outside this repository. `pipeline/build.py --source /path/to/ColonelsProject` rebuilds the normalized data with Python, pandas and numpy. `pipeline/package.py` compresses the verified data and produces a portable website ZIP.
