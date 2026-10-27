# Adding data without losing the audit trail

1. Keep original TrackMan TM and available PP exports in the appropriate season folder in ColonelsProject. Preserve filenames and recording IDs. A second copy of an export is not another game.
2. Refresh the authoritative source pipeline first: historical master/PBP for historical seasons; the reviewed Studio release for Fall 2026. New raw fall files are **not** silently appended by Atlas. Add the session to Studio, review identity/count/scoring continuity, and adjudicate pitch-type candidates in the pitcher's own arsenal. Keep original tags and a decision record. Confirm any ambiguous scoring with the scorer.
3. Check that Studio `site/data/fall.json`, `audit/pitches_clean.csv` and `audit/plate_appearances.csv` describe the same release. Atlas deliberately does not import the older `Fall26/cleaned` or old app branches.
4. Rebuild Atlas:

   ```sh
   python3 pipeline/build.py --source /path/to/ColonelsProject
   node --test tests/*.test.mjs
   python3 pipeline/package.py
   python3 -m http.server 4390 --directory site
   ```

5. Coverage assertions are a release lock for the October 24 snapshot. When intentionally adding games, update expected source counts and the date cutoff in the builder and tests **after independent reconciliation**, not merely to make a test green. Preserve the Graham Johnson, duplicate, confidence-gate and outcome-pooling regression checks.
6. If historical data changes, regenerate the candidate screen with `pipeline/screen_reference.py --source /path/to/ColonelsProject`. Inspect candidates before accepting new analytical corrections. The strict build rule is transparent and preserves source labels; borderline cases stay retained. Screens are not calibrated probabilities of correctness.
7. Review each affected player, competition filter and replay. Check missing PP coverage, unresolved scoring, throw targets, and low-confidence launches. Repeat/restarted sessions should remain visible and sensitivity-filterable, not silently removed.
8. Commit source code, documentation, tests, and `site/data/*.json.gz`. The workflow expands JSON, verifies the release and publishes to Pages. Do not commit the full ColonelsProject folder or private personal/roster-health files.

For an entirely new season, extend the season registry, source ingestion and tests deliberately; the existing seven-season list is explicit. No background upload or cloud service automatically reads your computer.

To add or replace a headshot without changing statistics, follow [PHOTOS.md](PHOTOS.md). Photo identity mappings and framing are maintained separately from the analytics pipeline.
