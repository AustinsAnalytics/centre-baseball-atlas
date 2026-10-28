# Release verification — October 26, 2026

Data cutoff: October 24, 2026. This is a reproducible analytical release, not a certification of every source scoring decision or pitch intent.

## Data checks

- Rebuilt all seven seasons from the historical master/PBP exports and reviewed Fall Studio release.
- 40,123 unique eligible pitches; 160 tracked logical sessions; 138 PBP games, including 44 without tracking; 10,618 completed tracked PA and 5,570 Centre full-game PBP PA.
- 1,521 eligible Fall pitches retain all final Studio decisions, including 82 pitch-label changes, three exclusions, and Graham Johnson's confirmed single. Its original Sacrifice tag remains available.
- 27 conservative historical cross-family changes retain source tags and review evidence; 588 other candidates remain unchanged and available for review.
- Confidence gates, batting denominators, overlapping PA pools, opponent profiles, aliases, position observations, target-specific throws and all 5,354 supported replay paths pass regression checks.
- Runner/score snapshots: 27,029 matched historical pitches and 214 estimated pitches. Fall runner/score values remain null. Estimated PBP requires explicit opt-in for these filters.
- Sequence tests cover suspended-game pitch-number resets, pitcher changes, count discontinuities, catcher-view orientation, exact matchups, and exports.

## Browser checks

All nine sections loaded without JavaScript errors. Checked normal/dark modes, 390 px phone layout, roster/player search, game/opponent search, player notebook, comparison, source/reviewed labels, PA sensitivity, pitch lab axes, replay playback, pitch inspector, sequence inspector, CSV export, direct pitch links, and shared filter links.

Independent selected-sample checks matched the UI:

- Fall 2026 Centre pitching, 1–2 count and two outs: 30 pitches, 13 swings, four whiffs, eight CSW, two usable EV.
- Spring 2026 Centre pitching, 0–2 count, RISP at PA start, within two runs: 72 pitches, 42 swings, 12 whiffs, 15 CSW, 13 usable EV.
- Graham Johnson versus Levi Wade: three recorded pitches in one PA, two swings, one usable EV of 98.8 mph; confirmed single.

The verification command is `node --test tests/*.test.mjs` (16 passing tests). GitHub Actions repeats these checks before deploying the same release. No credentials, personal documents or private roster-health notes are part of the publication package.

## Player photo update — October 27, 2026

34 photos cover 24 Centre returners, Davis Peterson from Sewanee, Nate Wiles from Mount St. Mary’s and eight user-supplied players. Every image decoded in the browser; all crops were visually reviewed. Player notebooks, roster cards, search results, comparisons and leaderboard links were checked. Desktop normal/dark modes and a 390 px phone profile were reviewed. Source names are searchable without altering statistical identities. The new asset check verifies identity keys, asset hashes, file signatures, crop bounds and missing-photo coverage. All 17 tests pass. Statistical data remains byte-for-byte identical to the October 26 release.

## Analysis Studio update — October 27, 2026

Four new modes connect count and location cells, consecutive pitch pairs, EV/LA neighborhoods and matched-player season changes to the underlying records. Nine added analytical tests verify independent season-level pair totals, rejected count/order/pitcher boundaries, missing measurement handling, catcher-view orientation, contact partitions and inclusive thresholds, measurement-specific comparison denominators, and query interpretation. All 26 checks pass. No statistical data or photo assets changed. Browser QA covers the new modes, count/cell/pair/bin filters, sequence inspector, both themes, shared views, query-to-filter navigation, and phone-width layouts.

## Seven-season identity and pitch-type audit — October 27, 2026

All 40,126 source records received a screening disposition; all 40,123 eligible pitches remain in the app. The review applies 801 named-pitcher reassignments (606 official-supported and 195 inferred), marks 15 pitches unidentified, and adds 321 type decisions. Historical type changes total 348; the 82 eligible Fall corrections remain intact. Cowdrey has no reviewed Slider labels and three Unclassified pitches. See [PITCH_AUDIT.md](PITCH_AUDIT.md) for evidence and unresolved cases.

All 33 automated tests pass. Seven new audit checks cover Cowdrey's distinct outings, unknown identity retention, real mid-PA substitutions, physical evidence that rejects the nearest model candidate, source conflicts, stable player IDs, and complete overlay coverage. Pair counts were independently recomputed: 28,990 overall and 18,680 with Centre pitching.

Independent before/after checks confirm unchanged source hashes; unchanged eligibility, pitch order, batting/scoring/context and measured contact/location values; byte-identical PBP pools, replay and defense data; and stable original player IDs/names and all 34 photos. Only reviewed pitcher/type fields and identity-derived handedness, player aggregates and sequence pairs change.

Browser QA: searchable audit records, combined identity/type evidence in the inspector, official-source links, the full searchable report, normal/dark themes, desktop and 390 px layouts. No JavaScript warnings or errors were observed. The portable website includes the compressed complete-pitch ledger; private investigation caches and baseline files are excluded from packaging.

## Confirmed Rone outing and release timestamp — October 27, 2026

The user confirmed September 22, 2024 pitches #32–46 (top 2nd) as Isaac Rone. All 15 pitch identities and five completed tracked PA now point to his existing player ID. After rerunning the type screen, pitch #38 changes from Slider to Changeup; the outing contains nine fastballs, four curveballs and two changeups. Rone’s November 2 pitch #140 retains its prior reviewed Slider label after direct release/movement review.

All 40,126 source records were screened again using reviewed pitcher identities and handedness. The remaining shape/release flags were examined without forcing assignments from nearest-profile similarity alone. Birmingham-Southern’s Ben Hoover has 14 missing throwing-hand values resolved as Right using his official roster. Other previously adjudicated pitcher and type decisions remain in place. Current totals: 816 named-pitcher corrections (606 official-supported, 195 inferred, 15 user-confirmed), 322 additional type decisions, and 349 historical type changes overall.

All 36 automated tests pass. Independent exact-record comparisons against the preceding public release confirm only 15 pitcher/status changes, one pitch-type/review change, and 14 missing-hand repairs; the five PA pitcher changes follow the confirmed outing. All other pitch values, raw input hashes, batting/scoring fields, PBP pools, replay and defense data, published player IDs and headshots are unchanged.

Browser QA verified the corrected pitch inspector, searchable identity/type evidence, Rone’s 15-pitch/five-BF notebook selection, 9/4/2 arsenal, report search, normal/dark themes, and 390 px layout without horizontal page overflow. No JavaScript warnings or errors were observed. The top-right timestamp displays Eastern time, and GitHub Actions stamps the actual publication time on each deployment. Release assets are versioned and data requests revalidate their cached responses so returning visitors receive corrections.
