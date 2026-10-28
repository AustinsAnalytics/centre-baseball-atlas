# Adding data without losing the audit trail

1. Keep original TrackMan TM and available PP exports in the appropriate season folder in ColonelsProject. Preserve filenames and recording IDs. A second copy of an export is not another game.
2. Refresh the authoritative source pipeline first: historical master/PBP for historical seasons; the reviewed Studio release for Fall 2026. New raw fall files are **not** silently appended by Atlas. Add the session to Studio, review identity/count/scoring continuity, and adjudicate pitch-type candidates in the pitcher's own arsenal. Keep original tags and a decision record. Confirm any ambiguous scoring with the scorer.
3. Check that Studio `site/data/fall.json`, `audit/pitches_clean.csv` and `audit/plate_appearances.csv` describe the same release. Atlas deliberately does not import the older `Fall26/cleaned` or old app branches.
4. Preserve `pipeline/pitch_review_overlay.json`, `pitch_review_events.json`, `pitch_review_cases.json`, `pitch_review_summary.json` and `player_registry.json`. The exact-UID overlay asserts expected prior identities/types before applying reviewed changes. If a new upstream export already contains a correction, reconcile that assertion and its audit record deliberately; do not bypass it. Preserve published player IDs and append new identities. See [PITCH_AUDIT.md](PITCH_AUDIT.md).

   Rebuild Atlas:

   ```sh
   python3 pipeline/build.py --source /path/to/ColonelsProject
   node --test tests/*.test.mjs
   python3 pipeline/package.py
   python3 -m http.server 4390 --directory site
   ```

5. Coverage assertions are a release lock for the October 24 snapshot. When intentionally adding games, update expected source counts and the date cutoff in the builder and tests **after independent reconciliation**, not merely to make a test green. Preserve the Graham Johnson, duplicate, confidence-gate and outcome-pooling regression checks.
6. If historical data changes, regenerate the candidate screen with `pipeline/screen_reference.py --source /path/to/ColonelsProject`. Inspect candidates before accepting new analytical corrections. The strict build rule is transparent and preserves source labels; borderline cases stay retained. Screens are not calibrated probabilities of correctness.
7. Review each affected player, competition filter and replay. Check missing PP coverage, unresolved scoring, throw targets, and low-confidence launches. Repeat/restarted sessions should remain visible and sensitivity-filterable, not silently removed.
8. Commit source code, documentation, tests, and `site/data/*.json.gz`. The workflow expands JSON, verifies the release and publishes to Pages. Do not commit the full ColonelsProject folder, private personal/roster-health files, or `audit_2026_10_27/` working data. The package excludes that local baseline/cache folder. Audit investigation scripts require the original source archive and frozen pre-audit baseline; ordinary builds use the versioned reviewed overlays and never automatically approve model candidates.

For an entirely new season, extend the season registry, source ingestion and tests deliberately; the existing seven-season list is explicit. No background upload or cloud service automatically reads your computer.

To add or replace a headshot without changing statistics, follow [PHOTOS.md](PHOTOS.md). Photo identity mappings and framing are maintained separately from the analytics pipeline.

The top-right timestamp comes from `site/release.json`. Packaging stamps local builds; GitHub Actions refreshes it immediately before uploading the site. It displays Eastern time (EDT/EST), independent of the visitor’s timezone. It describes the site release, not the date of the newest baseball recording.
