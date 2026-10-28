# Analysis Studio

The Analysis Studio adds four linked analytical tools over the reviewed data. The separate [October 27 pitch audit](PITCH_AUDIT.md) updates identity and type labels; scoring, raw measurements and historical coverage remain unchanged. Pair fixtures below reflect the corrected identities.

## Count and location

The 12-count map shows whiffs/swings, called plus swinging strikes/known calls, or swings/known calls. Clicking a count filters the location map and evidence ledger. A 5×5 location grid spans catcher-view x = −2.5 to +2.5 feet and height = 0 to 5 feet. Display x is **negative raw PlateLocSide**. The last cells include the outer upper boundary. Locations outside the grid are reported; missing/low-confidence locations do not enter it.

The strike-zone outline uses the existing ±0.83 ft, 1.5–3.5 ft analytic box. Spatial cells do not align exactly to its edges. Each selected sample shows its numerator, denominator and 95% Wilson interval. Dashed count cells have fewer than eight denominator opportunities; dashed location cells have fewer than five. Cells remain inspectable without becoming evidence of established player skill.

## Consecutive pitch pairs

Pairs are constructed from complete loaded season rows grouped by logical game and PA, ordered by recorded game pitch order. They require the same pitcher, batter and recording, consecutive numeric order, and a recognized count transition. Pitcher changes, missing pitches and count resets are excluded.

Exact count, selected location cell and handedness survive the count-map → pair pivot. User filters apply to the **second** pitch after constructing these pairs. This is essential: filtering to sliders before finding adjacency would invent slider–slider pairs across intervening fastballs. The matrix shows the second pitch's whiffs/swings and number of pairs. Geometry links two independent pitch measurements; the connecting segments are **not flight trajectories**.

Speed change is mean(next velocity − previous velocity), in mph. Release and plate gaps are mean pairwise Euclidean distances in their two-dimensional coordinate spaces, converted from feet to inches. Both measurements must be finite; plate gaps also require both usable-location flags. These are descriptive relationships, not a validated tunnel score or a causal measure of deception. Count, hitter, pitcher, pitch mix and location remain intertwined.

Independently reconciled fixtures: 28,990 valid pairs across all seven seasons; 18,680 with Centre pitching. Fall 2026 has 886 Centre pairs, 337 second-pitch swings and 90 misses. Fastball→Slider is 97 pairs / 37 swings / 16 misses. Cowdrey Fastball→Curveball has 10 pairs but only nine usable velocity pairs; nulls never become zero velocity.

## Contact lab

Only InPlay pitches with both confidence-gated, finite EV and LA enter the landscape and its 24 neighborhoods. EV bins are <80, [80,90), [90,95), and ≥95 mph. Angle bins are <0, [0,8), [8,20), [20,32], (32,50), and ≥50°. Every usable contact belongs to exactly one bin.

The highlighted custom hard-air window is **EV ≥95 mph and LA 8–32° inclusive**. It is not the standard Barrel definition, xBA or xwOBA. Contact percentages use the paired-measurement denominator; full-game PBP totals are never attached to the selected contact pool. An InPlay/Strikeout source conflict remains inspectable as measured contact rather than silently becoming an ordinary batted-ball out.

## Development

Compare the same player across two selected seasons using the same team, competition, pitch type, batter side, pitcher arm and count filters. Single-session filters are disabled because a session cannot belong to both periods. The default tab comparison is Fall 2025 versus Fall 2026 intrasquads. Physical measurements default to Fastball if no specific pitch type is selected; this avoids interpreting an arsenal-mix shift as a velocity or movement change.

Eligible players must meet the selected minimum in **both** periods. Each rate has its own denominator: swings for whiff, usable locations for zone, known calls for CSW, usable EV for hard-hit, outside locations for chase and in-zone locations for in-zone swing. Changes in rates are percentage points. Rows are sorted by absolute change, not labeled improvement or decline. Fall conditions, opponents and locations still differ.

Only the two required season datasets load for a period comparison. Selecting all seasons prompts the user to choose an individual comparison season.

## Search, sharing and coaching questions

The homepage and global search recognize supported player names/aliases, pitch types, season phrases, batter/pitcher handedness, exact counts, two strikes, and the requested study tool. The interpretation card lists the applied filters before navigation. Unsupported language is not answered as a generated scouting claim. “Vs lefties” means left-handed batters in a pitching study and left-handed pitchers in a hitting study.

Study links preserve the tool, lens, metric, count, location cell, contact neighborhood, pairing and period filters. Selected-pitch exports use the same sample as the evidence ledger. Pair exports contain the second pitches; each has a linkable full sequence in the app.

Player notebooks add a grounded observation and a next question based on that player's selected data. These are descriptive prompts for investigation, not mechanical diagnoses or prescriptive training plans.
