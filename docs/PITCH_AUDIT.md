# Seven-season pitch identity and type audit

Reviewed October 27, 2026. Scope: all 40,126 source records across seven seasons; 40,123 eligible pitches in Atlas. Original exports are unchanged. This is a reproducible analytical review, not a claim that every remaining tag is perfect.

## Results

- **801 pitches reassigned to a named pitcher:** 606 supported by official appearance/substitution records plus pitch context; 195 inferred from release, movement, velocity and recording continuity.
- **15 additional pitches removed from Cowdrey and marked unidentified:** September 22, 2024, top of inning 2. Team and contact records remain available. No named substitute is asserted.
- **321 additional pitch-type decisions**, after identity correction. These supplement the prior 27 historical and 82 eligible Fall 2026 type changes. Analytical labels describe likely families, not independently verified grip or intent.
- **Cowdrey: zero remaining Slider labels; three Unclassified pitches.** 110 pitches previously attributed to him were removed. One pitch previously tagged Carr was restored to Cowdrey after a separate boundary review.
- All existing eligible pitches, batting outcomes, contact/location measurements and replays remain. Player IDs and headshot links are stable.

## Cowdrey, specifically

The prior Atlas view contained 150 Slider labels under Cowdrey (including one earlier analytical relabel). Of these, 42 move with corrected pitcher identities; the remaining 108 receive 87 Curveball, 14 Changeup, 6 Cutter and 1 Unclassified labels. Two other undefined pitches are also Unclassified.

| Session | Decision | Evidence |
|---|---|---|
| February 1, 2025, innings 3–4 | 40 pitches → Zach Heavern | Two-inning cluster with Heavern-like fastball run, breaking-ball shape and release; distinctly different from Cowdrey innings 1–2. Strong inference. |
| February 1, 2025, innings 5–6 | 43 pitches → Aidan Christmas | Low release around 4.7 ft, wide release side, running fastball and sweeping breaker match Christmas references. Strong inference. |
| March 28, 2026 at Millsaps, inning 4 | 11 pitches → Tommy Severson | Official substitution plus lower release and lower-velocity shape continuing into named Severson pitches. |
| April 18, 2025 vs Sewanee, pitch 194 | 1 pitch → Zach Heavern | Official substitution and first-pitch continuity. |
| September 22, 2024, inning 2 | 15 pitches → Unidentified | Entire outing differs from Cowdrey; candidate identity remains unconfirmed. |
| October 12, 2025, pitch 28 | 1 pitch from Carr → Cowdrey | Early name change; same fastball shape and uninterrupted timing as Cowdrey preceding pitches. |

## Coverage by season

| Season | Source records | Eligible | Identity decisions applied | Additional type decisions |
|---|---:|---:|---:|---:|
| Spring 2026 | 11498 | 11498 | 228 | 43 |
| Fall 2024 | 3732 | 3732 | 45 | 37 |
| Spring 2025 | 9025 | 9025 | 265 | 66 |
| Spring 2024 | 9329 | 9329 | 237 | 94 |
| Fall 2023 | 2012 | 2012 | 39 | 71 |
| Fall 2025 | 3006 | 3006 | 2 | 10 |
| Fall 2026 | 1524 | 1521 | 0 | 0 |

## How the audit works

1. Unique PitchUID is the join key. Original TM/PP exports are cross-checked against the historical master and reviewed Fall source. The full ledger includes excluded records and every retained pitch, not just flagged rows.
2. Pitcher identity is evaluated before pitch type. Other-recording reference profiles use velocity, IVB, raw horizontal break, spin, release height/side and extension. Multiple pitch-specific release profiles prevent treating a naturally lower breaking-ball slot as a different pitcher. Scores are standardized distances, never calibrated identity probabilities.
3. All 94 tracked spring games were reconciled with official box scores. Starter and explicit substitution records are reconstructed from both teams' pitching lists. The exported p-home/p-away cells are not trusted: they can lose a pitcher/DH starter or put an offensive-half substitution on the wrong team.
4. Official PA-ending pitcher is only a candidate for individual pitches. Physical release changes, count sequence, recording pauses, prior/following pitches and pitching lines determine actual boundaries. Official pitch totals are useful corroboration but may include inherited-count attribution or scoring errors.
5. Practice changes require more than nearest-player distance. A same-game named continuation, a distinctive multi-pitch release/movement cluster, or a sustained combination of signals supports inference. Ambiguous profiles stay retained or unidentified. Late inning/half tags are not silently rewritten; those source contexts may still lag a pitcher change.
6. Type screening uses high/medium release confidence, finite measurements and plausible velocity. Velocity/IVB/raw horizontal break/spin are scaled by 2 mph/4 in/4 in/200 rpm. Trimmed median references require eight examples; nine-neighbor votes exclude the target pitch. Other recordings are used when at least 35 reference pitches are available. Otherwise a leave-one-pitch-out season reference is used.
7. General type changes require a different broad family, alternative distance ≤1.1, current distance ≥2.6, advantage ≥1.8, support ≥12 and at least 8/9 nearby-reference agreement. Cowdrey also uses the reported no-slider arsenal, separated fastball/curve/cutter/changeup shape anchors and manual review of sparse early-season labels. Borderline curve/cutter shapes are retained. Exact anchor bounds and all per-pitch reasons are versioned in the scripts and ledger.
8. Exact-UID overlays assert the expected previous values at build time. Raw measurements and original identities/tags are preserved. The source-label option changes types only; reviewed pitcher attribution remains active. Changing the pipeline does not edit the original exports.

## Important unresolved evidence

- September 22, 2024: 15 pitches clearly form a different Cowdrey-tagged outing, but the replacement pitcher is not reliably established. A coach pitching chart or video can resolve it.
- February 21, 2026 vs Trine: ten pitches tagged Reid Courtwright have a left-handed release; the official feed continues Brody Bond with a right-handed profile. TrackMan identity is retained with a source-conflict flag, rather than forcing Bond.
- March 21, 2026 at Rhodes: the official feed omits John Kosobud although the recorded late outing has his distinct release/arsenal. The 13 matched conflicts are retained and flagged; three additional unaligned pitches stay under their original Kosobud identity.
- Cowdrey unclassified: May 4, 2024 pitch 189 lacks usable tracking; February 28, 2025 pitch 196 has low-quality/incomplete tracking; October 4, 2025 pitch 53 overlaps plausible families. None is forced into a named type.
- Same-family naming (especially slider/curve and fastball/sinker), measurement outliers, missing video and incomplete practice charts limit certainty. A screen cannot establish every grip, intent or player identity. Retained candidates remain available for coach review.

### September 22 official-site follow-up

Centre’s [2024 schedule](https://centrecolonels.com/sports/baseball/schedule/2024), [2025 schedule](https://centrecolonels.com/sports/baseball/schedule/2025), [2024 baseball news archive](https://centrecolonels.com/sports/baseball/archives?season=2024&path=baseball) and all-season searches for “intrasquad” and “fall” did not yield a game report or play-by-play for the September 22, 2024 intrasquad. This is a search limitation, not proof that no private chart exists.

An additional comparison of fastball and curveball measurements against individual Centre outings favors **Isaac Rone’s September 29, 2024 outing** as an exploratory lead. Rone’s low-spin fastball is closer; some Zach Heavern references overlap the curveball and release profile. The combined standardized distances (0.625 for that Rone outing and 0.729 for Heavern’s February 10, 2024 outing) are close and are **not probabilities**. No named attribution was applied. `pipeline/investigate_unidentified.py` preserves the comparison; a contemporaneous pitching chart or video is still needed to resolve it.

## Source-name resolution

Spelling/abbreviation matches were separated from pitcher substitutions: Sheperd/Shepherd, Hatrick/Hartrick, JD Van Hook/J. Hook, Jake Hartman/J. jr, John Parker Rambo and Drew/Andrew Harbison. Existing canonical IDs are preserved. Dominican's Grayson Downing and Austin Doty entries were different stale identities; the March 1, 2026 box and official roster identify Langdon Downing and Austin Long. New names that lack a verified full-name match retain the official abbreviation.

Primary sources include [Centre official game records](https://centrecolonels.com/sports/baseball/stats), [Dominican 2026 pitching statistics](https://dustars.com/sports/baseball/stats/2026), [Langdon Downing](https://dustars.com/sports/baseball/roster/langdon-downing/4955), [Jake Thometz's DePauw roster](https://depauwtigers.com/sports/baseball/roster/2024), and [Andrew Harbison's Spalding bio](https://spaldingathletics.com/sports/baseball/roster/andrew-harbison/3666). Every official-supported identity decision links to its specific game.

## Files and reproduction

- `pipeline/pitch_review_overlay.json`: exact-UID applied changes with expected prior values, status, reason and source.
- `pipeline/pitch_review_events.json`: applied and retained identity/type evidence.
- `pipeline/player_registry.json`: stable published player identities; append new players, never renumber existing IDs.
- `site/review/all-pitch-decisions.csv.gz`: complete 40,126-record ledger, including eligibility and original-file/previous/reviewed identity.
- `site/review/pitcher-decisions.csv` and `pitch-type-decisions.csv`: searchable review queues.
- `audit_2026_10_27/`: local-only working data, cached public boxscore HTML, baseline copies and detailed packets. This folder is excluded from repository packaging.

The build consumes the approved versioned overlay; it does not automatically approve new model suggestions. To reproduce the investigation locally, run identity_audit.py, raw_identity_crosscheck.py, fetch_pitching_boxes.py, reconcile_pitcher_events.py, review_identity_cases.py, adjudicate_identity.py, audit_pitch_types.py, finalize_pitch_review.py, export_pitch_audit.py, write_audit_report.py, then build.py. Review any new candidate before changing adjudication rules. Source files remain outside the public repository.
