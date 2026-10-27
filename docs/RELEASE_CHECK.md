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
