# Unified Centre app: independently checked data contract

Read-only inspection, October 26, 2026. No project data or pipelines were modified or executed. Counts below were recomputed from complete saved CSVs with pandas. All paths below are relative to `ColonelsProject`.

## Authoritative inputs and keys

- Historical measurements and reconciled tracked PA results: `Colonels_Analytics/data/centre_pitch_by_pitch_master.csv` (38,602 rows × 289 columns). Unique `PitchUID`. `GameSeq` identifies the logical game/session; `GameUID` identifies a recording, and one suspended Sewanee game spans two recordings. Historical PA key is `(GameSeq, PAofGame)`; `IsPAFinalPitch` marks the record carrying PA outcome flags.
- Full spring play-by-play: `Colonels_Analytics/data/pbp_events_all_games.csv` (11,712 rows, 10,844 PA, 138 games). Unique key `(PBP_GameID, EventIdx)`. Centre batting is `(BattingSide == 'home') == CentreHome`. Do not append these PAs to matched TrackMan PAs: they overlap. Use a separate full-game outcome pool or replace matched tracked-game PA totals with PBP when constructing season results.
- Fall 2026: `Fall26/Fall26_Studio/audit/pitches_clean.csv` (1,524 records, exclude `Excluded == true` for 1,521 eligible pitches). Use `CleanPitchType`, not `TaggedPitchType` or `CandidateType`. Preserve original tag, evidence, decision reason and exclusion. PA source is sibling `plate_appearances.csv` (390 sequences; 385 completed; five incomplete). `(SessionId, PitchNo)` is only a display key; `PitchUID` is identity. `PA` joins numeric `id` in PA table. Reviewed Studio JSON `Fall26/Fall26_Studio/site/data/fall.json` supplies exact position joins, replay fits and richer PA `rows` arrays.
- DO NOT take fall outcomes/types from `Fall26/cleaned` or old `Fall26_App/site`: those branches differ in 26 pitch types and Graham Johnson's user-confirmed single; old saved app also stops after four sessions.
- Safe joins for existing derived history: `Colonels_Analytics/app/data/pitches.csv.gz` shares exact 38,602 PitchUIDs; fielding data under `Colonels_Analytics/fielding_app/data_build` use PitchUID/GameSeq/PBP_GameID depending on table. Existing site JSON indices reference its own `meta.json` dictionary and must never be treated as independent player IDs.

## Exact coverage

| Season | Eligible pitches | Recording IDs | Logical sessions | Centre pitching pitches | Centre batting pitches | Completed tracked PA (both teams) | Centre batting PA |
|---|---:|---:|---:|---:|---:|---:|---:|
| Fall 2023 | 2,012 | 9 | 9 | 2,012 | 2,012 | 543 | 543 |
| Spring 2024 | 9,329 | 33 | 33 | 5,409 | 5,080 | 2,511 | 1,391 |
| Fall 2024 | 3,732 | 25 | 25 | 3,732 | 3,732 | 944 | 944 |
| Spring 2025 | 9,025 | 32 | 32 | 5,088 | 5,386 | 2,367 | 1,397 |
| Fall 2025 | 3,006 | 15 | 15 | 2,746 | 2,773 | 752 | 694 |
| Spring 2026 | 11,498 | 41 | 40 | 5,588 | 5,910 | 3,116 | 1,609 |
| Fall 2026 | 1,521 | 6 | 6 | 1,192 | 1,183 | 385 | 302 |
| Total | 40,123 | 161 | 160 | 25,767 | 26,076 | 10,618 | 6,880 |

Historical and Fall 2026 PitchUID sets have zero overlap. Centre-vs-Centre rows count toward both Centre pitching and Centre batting, so these totals must not be added to obtain unique pitches.

There are 94 tracked spring games (28/26/40 in 2024/25/26); 27,243 spring-game pitches. Spring 2024 includes five practice sessions/1,160 pitches; spring 2025 includes six practice sessions/1,449 pitches. Fall 2025 has 13 intrasquads/2,513 pitches plus two John A. Logan scrimmages/493 pitches. Other historical fall sessions are intrasquads. Do not label all 160 sessions 'games'.

Full PBP: Spring 2024 has 49 games/3,834 both-team PA/1,952 Centre PA; 2025 has 43/3,361/1,714; 2026 has 46/3,649/1,904. Total Centre PBP PA = 5,570. Forty-four PBP games lack TrackMan. Unified games/session registry including PBP-only games should contain 204 entries (160 tracked sessions + 44 PBP-only games), while PBP games remains 138.

Fall sessions: Oct 8 = 184 records/183 eligible; Oct 9 = 189; Oct 17 = 239; Oct 18 = 243; Oct 24 Lindsey Wilson game 1 = 338 records/337 eligible; game 2 = 331/330. First four total 854 eligible; LW total 667. LW Centre pitching 338, Centre batting 329. All-fall rosters include 18 Centre pitchers and 23 Centre hitters (27/32 both teams). 33 tracked team codes including Centre exist across both collections; a team code is not a distinct-game count.

## Metric definitions to implement once and reuse

- Pitch counts include eligible source rows, but Undefined pitch calls should not silently count as balls/strikes/swings. History has 23 Undefined calls. Explicit `knownOutcome` denominator is preferable for strike/swing/CSW rates; display denominators when useful.
- Swing = `StrikeSwinging`, any `FoulBall*`, or `InPlay`; whiff = `StrikeSwinging`; called strike = `StrikeCalled`; strike = called strike OR swing; CSW = called strike OR whiff. Whiff% = whiffs/swings. CSW% = CSW/known pitch outcomes. Do not call CSW strikeout rate.
- Zone box is a fixed analytic box: |raw PlateLocSide| <= 0.83 ft and 1.5 <= PlateLocHeight <= 3.5 ft. It is not the batter-specific rulebook zone. Location metrics require High/Medium `PitchLocationConfidence` plus both coordinates. Zone% denominator is usable locations. Chase% = swings at usable out-of-zone locations / usable out-of-zone pitches; missing locations must never become chase opportunities. Contact% = 1 - whiff/swings.
- Historical usable locations under Studio's consistent confidence gate: 38,210; fall: 1,520. Historical confidence missing on 370 rows, including Clean-export coverage: 'unavailable' is not evidence of a bad measurement, but do not silently treat it as High. Offer measured/ungraded coverage separately if included.
- EV: InPlay AND High/Medium HitLaunchConfidence AND finite ExitSpeed. Historical 6,629 BIP / 5,199 usable EV; fall 214 / 162. Hard-hit% = EV >=95 / usable EV. Launch angle/sweet spot require their own finite-angle denominator; 8–32 degrees inclusive. Do not use EV count as LA denominator when missing. Never call a simple EV/LA rectangle 'Barrel%' unless explicitly 'custom hard-air contact'; it is not the standard barrel definition.
- Landing/spray-distance requires launch usability AND High/Medium HitLandingConfidence AND finite Distance/Bearing. Historical 4,632; fall 138. Fitted trajectory can exist without reliable eventual landing.
- Historical completed tracked PA: `IsPA == true` on final pitch only (10,233); historical incomplete sequences 170. Fall completed: exclude event `Incomplete` or `Unscored` (385; Unscored currently zero). Keep incomplete pitches for shape and discipline.
- Hits = 1B+2B+3B+HR; TB = 1B+2*2B+3*3B+4*HR. AB excludes BB/IBB, HBP, SH/SacBunt, SF/SacFly, catcher interference and incomplete/unknown. Errors/FC are AB, not hits. AVG = H/AB; SLG=TB/AB; OBP=(H+BB+IBB+HBP)/(AB+BB+IBB+HBP+SF). Sacrifice bunts and catcher interference are excluded from OBP denominator. OPS=OBP+SLG; BABIP=(H-HR)/(AB-K-HR+SF). K%/BB% denominator is completed PA/BF, never pitches. Preserve IBB separately but total BB includes them. Do not count IBB twice if importing historical `IsWalk` (it already includes IBB).
- Six historical generic `Sacrifice` results cannot simply be excluded from both SF and SH logic: two are FlyBall (can explicitly classify as SF with audit), one Spring2024 GroundBall, one Fall2024 GroundBall, two LineDrive. Retain a generic/uncertain sacrifice marker rather than fabricate official scoring. This affects a handful of fall/practice OBP denominators. Full PBP uses explicit SF/SH, avoiding this issue in full-game spring totals.
- Historical PBP has one `ReachedOther`: W. Wilson, game 5967, 'reached first on a muffed throw by 1b, assist by c.' This is an error-like AB with no hit; safe to preserve source plus explicit display mapping, not count as hit or walk.
- Fall totals: 385 completed PA, 300 AB, 93 H, 64 BB, 20 HBP, 87 K, 1 SF. Centre-only: 302 PA, 236 AB, 78 H, 115 TB, 49 BB, 16 HBP, 65 K, 1 SF. Graham Johnson: 23 PA,18 AB,9 H,15 TB,4 BB,1 SF => .500/.565/.833. This is an excellent regression assertion.
- Fall has five completed sequences beginning mid-count, two flagged repeated terminal sequences (distinct UIDs), and 22 count discontinuities. Default keeps reviewed source events; provide sensitivity filters rather than silently deleting them. History also has partial/missing recorded sequences. First recorded pitch and true 0-0 pitch are not identical concepts.
- Avoid presenting official ERA or charged pitcher runs from `PA_RunsScored`/`RunsOnPA`: run scoring may include inherited runners; runner-only events and responsible-pitcher attribution require additional work. Outs/IP from tracked terminal records do not equal official season IP. If shown, label 'tracked outs' and use outs/3 mathematically, baseball `.1/.2` only for display.

## Identity correction: previous review note is wrong

The previous `the initial review notes` says historical Tristan Vallone and fall Tristen Vallone are distinct. Current source evidence directly contradicts that conclusion:

- `Fall26/Fall26_Analytics/clean_fall26.py` line 36 has `NAME_FIXES = {"Vallone, Tristen": ("Vallone, Tristan", "Spelled Tristan in every earlier Centre season; same player (confirmed by the coaches).")}`.
- Historical master and current Studio records both use BatterId 10089874 for these spellings.
- Historical `pipeline/build_master.py` maps Tristen → Tristan.

**Therefore merge those two spellings into canonical Tristan Vallone and retain source name. Michael Vallone is a distinct opponent pitcher.** Do not perpetuate the earlier review error.

Taylor, Wesley → Taylor, Wes is explicit `SAME` mapping in `Fall26/Fall26_Draft/draft_results.py` line 61. Historical ID 10104851 vs fall ID 10011087 demonstrates why numeric ID alone cannot establish identity. Preserve the documented alias. Other historical typo mappings already applied: Tayor, Wesley → Taylor, Wesley; C. Austin → Austin, Chase. Canonical key should include team plus documented name alias, not fuzzy surname matching. Two historical Centre batter names are missing (both spring 2025 GameSeq88); preserve as unknown, do not string-cast NaN into a player.

Existing historical site metadata has 848 combined names, not 848 Centre players. Its PBP export already maps canonical names and contains 5,570 Centre PAs, and can be used as a verified name-resolution bridge to the raw event table, but keep its 198-game registry indices distinct from new indices.

## Fielding and replay: safe facts and limitations

- Starting-position observations: X = forward distance from home; Z = lateral toward first base; use display lateral=Z, depth=X. Seven position slots (1B,2B,3B,SS,LF,CF,RF), exact join by PitchUID. They are at release, not actual routes/catch locations. Missing fielder names or positions must remain missing. Historical `positioning.csv`: 33,772 rows. Historical master PP matches 34,784 PitchUIDs before position plausibility filters.
- Fix the known Berry game 2 PP header issue in a *new build overlay* if desired: `Trackman Folders/Spring25/Games/Berry 2 PP.csv` uses X1B_/X2B_/X3B_ column prefixes, lost by historical PP loader. 273 IDs; 272/261/247 available X measurements for 1B/2B/3B respectively. Join exact UID and normalize leading X only for these position names. Do not overwrite populated master fields with blanks.
- Fall Studio JSON includes 854 PP-joined eligible pitches, but only 853 have at least one finite marker (one source record has no finite slot). All LW records lack PP source exports; show 'positions unavailable', not default markers presented as observed. There are 162 valid fall animations, 79 air-out events labeled caught-inferred across 214 BIP. Event results do not prove catcher, catch time or catch coordinate.
- Reuse reviewed fall replay metadata/points. For history, adopt the same conservative polynomial validation from `Fall26_Studio/pipeline/replay_data.py`: High/Medium launch, complete per-axis coefficients, valid contact point, positive reported LastTrackedDistance, bounded physically finite path. Stop at earliest radial tracking extent, first ground crossing, or reliable reported hang; never extrapolate a roll/bounce. Source axes X forward/Y height/Z lateral(+1B); polynomial t starts at contact. Catch indicator is inferred only for air-ball out/SF and must be visually distinct from fit endpoint.
- Pitch break/location native horizontal convention differs from ball-flight lateral convention: reviewed location/movement charts flip raw PlateLocSide/HorzBreak for catcher-view x. For arm-side-normalized HB, multiply raw HorzBreak by -1 only for left-hand pitchers. Keep every chart's orientation label explicit.
- Historical reconstructed official-ish credits: `fielder_lines.csv` 141 season/player/position rows; `def_credits.csv`9,734 event credits; `team_defense.csv`6 team/season rows; `def_events.csv`11,712 events. Fields PO/A/E/TC/FPct/DP and observed position innings are useful, but counts are parser-reconstructed with known residual mismatches; label reconstructed PBP. Don't aggregate FPct as unweighted average: (sumPO+sumA)/(sumPO+sumA+sumE). Don't double-count duplicate credits indiscriminately; one double play can credit a fielder twice.
- Model tables: air1,629, ground1,454, framing15,248, throws829, blocking2,404. Air/ground responsibility may be inferred; OAA is custom model residual, not official Outs Above Average. Air responsibility selection has preprocessing leakage concerns. Ground time is simplified physics. Framing final catcher effects aren't the same as held-out raw location residuals. Blocking labels are assigned to a likely pitch within PA. These can be included as visibly exploratory historical models, not authoritative player rankings or extrapolated to fall.
- Catcher PopTime/ThrowSpeed measurements have target-base/confidence context. Compare 2B throws to 2B; don't pool first/third-base throws. Stored historical steal-attempt labels partly come from PA context and may not identify exact pitch.

## Sources/estimates separation and publish scope

Historical custom Stuff+ is database-relative expected-whiff quality, not MLB-calibrated and not directly comparable to a separately fitted fall scale. Existing xBA/xwOBA models, draft grades and estimated bat speed must retain model labels and source version. Measured bat speed is not available. Draft roster health/coach adjustments are dated private scenario inputs, not new baseball observations and should not be published simply because the files exist.

Maintain source metadata, source cutoffs, eligible/excluded counts, model flags, and methodology in the app. Use blank/null for unavailable values, zero only for actual zero. Compute weighted aggregate rates from numerator/denominator totals. Do not combine full-game PBP batting totals with tracked-only pitch outcomes under an unlabeled denominator. Default current-fall view can be clear while spring results explicitly switch to full-game PBP and tracking charts remain coverage-aware.


## Game Room context and sequence contract

Historical matched PBP provides 27,029 pitch snapshots; another 214 are estimates. Bases and scores are PA-start snapshots, not live pitch state. The runner and score controls require matched context by default, with an explicit estimated-context option. Unknown context never passes empty-base, zero-out or tied-score criteria. Positive score difference is the pitching team's lead; the hitting lens reverses it. Fall 2026 provides recorded outs, count and inning but no runner or score snapshots.

Pitch-situation rates use pitches only, with their own swing, known-call and usable-measurement denominators. The page does not attach full-game PBP batting results to a pitch subset. Sequences group by logical game and PA key, use PitchOfGame order (which survives a suspended-game PitchNo restart), and retain every row's pitcher. There are 39 historical PAs with a pitching change. PA-start state may diverge after mid-PA events; event descriptions are shown when supplied.

Count checks describe discontinuities without guessing corrections. No pitch tempo is calculated from date-only PitchTime. Reconciled scoring remains separate from raw operator results, including the Fall Graham Johnson Sacrifice→Single correction. Four historical InPlay records resolving to strikeouts are explicitly flagged as source conflicts.
