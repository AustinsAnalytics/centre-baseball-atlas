"""Human-readable release report from the adjudicated ledger."""
from pathlib import Path
import json,html,pandas as pd
from identity_audit import ROOT,OUT
r=json.loads((ROOT/'pipeline/pitch_review_summary.json').read_text());cases=r['cases'];ids=pd.read_csv(OUT/'identity_decisions.csv');x=pd.read_pickle(OUT/'final_audit_frame.pkl')
rows=[]
for season,g in x.groupby('Season',sort=False):
 rows.append([season,len(g),int(g.Eligible.sum()),int(g.FinalPitcher.ne(g.Pitcher).sum()),int(g.FinalType.ne(g.AtlasType).sum())])
md=f'''# Seven-season pitch identity and type audit

Reviewed October 27, 2026. Scope: all {r['records']:,} source records across seven seasons; {r['eligible']:,} eligible pitches in Atlas. Original exports are unchanged. This is a reproducible analytical review, not a claim that every remaining tag is perfect.

## Results

- **{r['knownIdentityChanges']:,} pitches reassigned to a named pitcher:** {r['identityOfficial']} supported by official appearance/substitution records plus pitch context; {r['identityInferred']} inferred from release, movement, velocity and recording continuity; {r.get('identityConfirmed',0)} explicitly confirmed by the user.
- **15 formerly unidentified pitches are now credited to Isaac Rone:** September 22, 2024, top of inning 2, pitches #32–46. The user explicitly confirmed the identity on October 27, 2026. Pitch #38 is also reviewed from Slider to Changeup using Rone’s reference profile; the outing contains nine fastballs, four curveballs and two changeups.
- **{r['typeChanges']} additional pitch-type decisions**, after identity correction. These supplement the prior 27 historical and 82 eligible Fall 2026 type changes. Analytical labels describe likely families, not independently verified grip or intent.
- **Cowdrey: zero remaining Slider labels; three Unclassified pitches.** {r['cowdreyRemoved']} pitches previously attributed to him were removed. One pitch previously tagged Carr was restored to Cowdrey after a separate boundary review.
- All existing eligible pitches, batting outcomes, contact/location measurements and replays remain. Player IDs and headshot links are stable.

## Cowdrey, specifically

The prior Atlas view contained 150 Slider labels under Cowdrey (including one earlier analytical relabel). Of these, 42 move with corrected pitcher identities; the remaining 108 receive 87 Curveball, 14 Changeup, 6 Cutter and 1 Unclassified labels. Two other undefined pitches are also Unclassified.

| Session | Decision | Evidence |
|---|---|---|
| February 1, 2025, innings 3–4 | 40 pitches → Zach Heavern | Two-inning cluster with Heavern-like fastball run, breaking-ball shape and release; distinctly different from Cowdrey innings 1–2. Strong inference. |
| February 1, 2025, innings 5–6 | 43 pitches → Aidan Christmas | Low release around 4.7 ft, wide release side, running fastball and sweeping breaker match Christmas references. Strong inference. |
| March 28, 2026 at Millsaps, inning 4 | 11 pitches → Tommy Severson | Official substitution plus lower release and lower-velocity shape continuing into named Severson pitches. |
| April 18, 2025 vs Sewanee, pitch 194 | 1 pitch → Zach Heavern | Official substitution and first-pitch continuity. |
| September 22, 2024, inning 2 | 15 pitches → Isaac Rone | Explicit user confirmation after comparison of nearby outings; original Cowdrey attribution preserved. |
| October 12, 2025, pitch 28 | 1 pitch from Carr → Cowdrey | Early name change; same fastball shape and uninterrupted timing as Cowdrey preceding pitches. |

## Coverage by season

| Season | Source records | Eligible | Identity decisions applied | Additional type decisions |
|---|---:|---:|---:|---:|
'''
md+='\n'.join('| '+' | '.join(map(str,row))+' |' for row in rows)
md+='''

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

- February 21, 2026 vs Trine: ten pitches tagged Reid Courtwright have a left-handed release; the official feed continues Brody Bond with a right-handed profile. TrackMan identity is retained with a source-conflict flag, rather than forcing Bond.
- March 21, 2026 at Rhodes: the official feed omits John Kosobud although the recorded late outing has his distinct release/arsenal. The 13 matched conflicts are retained and flagged; three additional unaligned pitches stay under their original Kosobud identity.
- Cowdrey unclassified: May 4, 2024 pitch 189 lacks usable tracking; February 28, 2025 pitch 196 has low-quality/incomplete tracking; October 4, 2025 pitch 53 overlaps plausible families. None is forced into a named type.
- Same-family naming (especially slider/curve and fastball/sinker), measurement outliers, missing video and incomplete practice charts limit certainty. A screen cannot establish every grip, intent or player identity. Retained candidates remain available for coach review.

### September 22 confirmation and follow-up

Centre’s [2024 schedule](https://centrecolonels.com/sports/baseball/schedule/2024), [2025 schedule](https://centrecolonels.com/sports/baseball/schedule/2025), [2024 baseball news archive](https://centrecolonels.com/sports/baseball/archives?season=2024&path=baseball) and all-season searches for “intrasquad” and “fall” did not yield a game report or play-by-play for the September 22, 2024 intrasquad. This is a search limitation, not proof that no private chart exists.

An additional comparison of fastball and curveball measurements against individual Centre outings favors **Isaac Rone’s September 29, 2024 outing** as an exploratory lead. Rone’s low-spin fastball is closer; some Zach Heavern references overlap the curveball and release profile. The combined standardized distances (0.625 for that Rone outing and 0.729 for Heavern’s February 10, 2024 outing) are close and are **not probabilities**. The initial review left the outing unidentified. **The user subsequently confirmed all 15 pitches as Rone, and that confirmation now determines the attribution.** `pipeline/investigate_unidentified.py` preserves the earlier comparison, which is not treated as independent proof of identity. The all-season type screen was rerun with Rone’s corrected profile; pitch #38 now meets the changeup threshold. November 2 pitch #140 remains a Slider after direct release/movement review, despite a small change to the season-wide threshold score.

## Source-name resolution

Spelling/abbreviation matches were separated from pitcher substitutions: Sheperd/Shepherd, Hatrick/Hartrick, JD Van Hook/J. Hook, Jake Hartman/J. jr, John Parker Rambo and Drew/Andrew Harbison. Existing canonical IDs are preserved. Dominican's Grayson Downing and Austin Doty entries were different stale identities; the March 1, 2026 box and official roster identify Langdon Downing and Austin Long. New names that lack a verified full-name match retain the official abbreviation.

Primary sources include [Centre official game records](https://centrecolonels.com/sports/baseball/stats), [Dominican 2026 pitching statistics](https://dustars.com/sports/baseball/stats/2026), [Langdon Downing](https://dustars.com/sports/baseball/roster/langdon-downing/4955), [Jake Thometz's DePauw roster](https://depauwtigers.com/sports/baseball/roster/2024), and [Andrew Harbison's Spalding bio](https://spaldingathletics.com/sports/baseball/roster/andrew-harbison/3666). Every official-supported identity decision links to its specific game. The follow-up also resolves B. Hoover’s missing handedness as Right using [Ben Hoover’s official 2024 Birmingham-Southern bio](https://bscsports.net/sports/baseball/roster/ben-hoover/7453); the published player ID remains stable.

## Files and reproduction

- `pipeline/pitch_review_overlay.json`: exact-UID applied changes with expected prior values, status, reason and source.
- `pipeline/pitch_review_events.json`: applied and retained identity/type evidence.
- `pipeline/player_registry.json`: stable published player identities; append new players, never renumber existing IDs.
- `site/review/all-pitch-decisions.csv.gz`: complete 40,126-record ledger, including eligibility and original-file/previous/reviewed identity.
- `site/review/pitcher-decisions.csv` and `pitch-type-decisions.csv`: searchable review queues.
- `audit_2026_10_27/`: local-only working data, cached public boxscore HTML, baseline copies and detailed packets. This folder is excluded from repository packaging.

The build consumes the approved versioned overlay; it does not automatically approve new model suggestions. To reproduce the investigation locally, run identity_audit.py, raw_identity_crosscheck.py, fetch_pitching_boxes.py, reconcile_pitcher_events.py, review_identity_cases.py, adjudicate_identity.py, audit_pitch_types.py, finalize_pitch_review.py, export_pitch_audit.py, write_audit_report.py, then build.py. Review any new candidate before changing adjudication rules. Source files remain outside the public repository.
'''
(ROOT/'docs/PITCH_AUDIT.md').write_text(md)
esc=html.escape
cards=''.join(f'<article class="card case" data-search="{esc((c["game"]+" "+c["original"]+" "+c["candidate"]+" "+c["status"]).lower())}"><div class="eyebrow">{esc(c["status"])} · {c["n"]} pitches</div><h3>{esc(c["original"])} → {esc(c["candidate"])}</h3><p><strong>{esc(c["game"])}</strong></p><p>{esc(c["reason"])}</p>'+ (f'<a href="{esc(c["source"])}" target="_blank" rel="noopener">Official game source ↗</a>' if c['source'].startswith('https://') else '')+'</article>' for c in cases)
body=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Pitch audit · Centre Atlas</title><link rel="icon" href="../favicon.svg"><script>try{{document.documentElement.dataset.theme=localStorage.getItem('atlas-theme')||'light'}}catch{{}}</script><link rel="stylesheet" href="../style.css?v=1.2.1"><style>main{{max-width:1200px;margin:auto;padding:36px 24px}}h1{{font-size:clamp(36px,6vw,68px);line-height:1.05;margin:24px 0}}.case-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,330px),1fr));gap:16px}}.case h3{{font-size:20px;overflow-wrap:anywhere}}.case p{{line-height:1.6}}.case[hidden]{{display:none}}.audit-search{{width:100%;padding:16px;margin:20px 0}}.links{{display:flex;gap:16px;flex-wrap:wrap;margin:20px 0}}.report-lead{{font-size:20px;max-width:850px;line-height:1.6}}.report-note{{padding:22px;margin:22px 0;border-left:4px solid var(--gold);background:var(--surface)}}.report-table{{overflow:auto;margin:22px 0}}.report-nav{{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}}</style></head><body><main><div class="report-nav"><a class="button-link" href="../#data">← Centre Atlas · Data & methods</a><time id="report-updated" class="site-updated"></time></div><div class="eyebrow" style="margin-top:35px">OCTOBER 27, 2026 · SEVEN SEASONS</div><h1>Better data starts<br>with the right pitcher.</h1><p class="report-lead">{r['records']:,} source records screened. {r['knownIdentityChanges']} pitches reassigned to named pitchers, including {r.get('identityConfirmed',0)} user-confirmed pitches, and {r['typeChanges']} additional type decisions. Every correction keeps its evidence.</p><div class="report-note"><strong>Cowdrey now has zero slider labels.</strong> His suspect pitches were a mixture of mistagged types and other pitchers' outings. Three types remain unclassified. Statistical inference is labeled separately from official-source support.</div><div class="grid2"><section class="card"><h2>What changed</h2><p>{r['identityOfficial']} identity changes have official appearance/substitution support plus pitch context. {r['identityInferred']} are strong analytical inferences; {r.get('identityConfirmed',0)} are user-confirmed. September 22, 2024 inning 2 is now credited to Isaac Rone. No eligible pitch or batting outcome was deleted.</p></section><section class="card"><h2>What remains uncertain</h2><p>Practice identities lack complete independent charts. Slider/curve naming can overlap. The Courtwright/Trine and Kosobud/Rhodes records conflict with the official feed, so those identities remain flagged. A retained label is not a guarantee of correctness.</p></section></div><div class="links"><a class="button-link" href="pitcher-decisions.csv" download>Pitcher decisions ↓</a><a class="button-link" href="pitch-type-decisions.csv" download>Pitch-type decisions ↓</a><a class="button-link" href="all-pitch-decisions.csv.gz" download>Complete ledger (.csv.gz) ↓</a><a class="button-link" href="https://github.com/AustinsAnalytics/centre-baseball-atlas/blob/main/docs/PITCH_AUDIT.md">Full method & limitations ↗</a></div><section class="report-note"><h2>September 22: Isaac Rone confirmed</h2><p>The user confirmed all 15 pitches (#32–46, top of inning 2) as <strong>Isaac Rone</strong> on October 27, 2026. His player totals now include them. Original Cowdrey tags remain in the ledger. Rechecking pitch types resolves the outing as nine fastballs, four curveballs and two changeups. The earlier official-site search had not located a public intrasquad chart; the identity is labeled user-confirmed.</p><a href="https://centrecolonels.com/sports/baseball/archives?season=2024&amp;path=baseball">Centre’s 2024 baseball archive ↗</a></section><h2>Follow each identity decision</h2><p>Search a player, date or status. “Retained” cases explain why an attractive statistical candidate was not applied.</p><input class="audit-search" id="case-search" type="search" placeholder="Cowdrey, Heavern, 2024, unresolved…" aria-label="Search identity decisions"><p id="case-count" aria-live="polite">{len(cases)} cases</p><div class="case-grid">{cards}</div><p class="report-note">Original TM/PP exports remain unchanged. Reviewed data is applied through exact-UID overlays. The complete ledger includes all three excluded source records and marks their eligibility. Public information excludes personal documents and private roster-health notes.</p></main><script>document.querySelector('#case-search').addEventListener('input',e=>{{const terms=e.target.value.toLowerCase().trim().split(/\\s+/);let n=0;document.querySelectorAll('.case').forEach(c=>{{c.hidden=!terms.every(t=>c.dataset.search.includes(t));if(!c.hidden)n++}});document.querySelector('#case-count').textContent=n+' matching cases'}})</script><script type="module">import{{releaseLabel}}from'../release.js';fetch('../release.json',{{cache:'no-cache'}}).then(r=>r.ok?r.json():null).then(r=>{{const label=releaseLabel(r?.updatedAt);if(label){{const t=document.querySelector('#report-updated');t.dateTime=r.updatedAt;t.textContent='Last updated '+label}}}}).catch(()=>{{}})</script></body></html>'''
(ROOT/'site/review/audit-report.html').write_text(body)
print('Report created',len(cases),'identity cases')
