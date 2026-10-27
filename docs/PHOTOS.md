# Player photos

The October 27, 2026 release includes photos for 34 of the 36 Centre players represented in Fall 2026 tracking: 24 Centre returners, two transfers, and eight supplied photos. Mason Dugan and Cooper Burgin retain initials until a matching photo is provided.

## Sources and identity

- Returners: [Centre's 2026 baseball roster](https://centrecolonels.com/sports/baseball/roster/2026).
- Davis Peterson: [Sewanee's 2026 baseball roster](https://sewaneetigers.com/sports/baseball/roster/2026). The existing tracking identity is spelled **Davis Petersen**. The explicit user identification of this transfer supplies the photo match; this photo release does not rename or merge statistical records.
- Nate Wiles: [Mount St. Mary's 2026 baseball roster](https://mountathletics.com/sports/baseball/roster/2026).
- Supplied files: Caleb Thrasher, Isaac Mastin, Jon Harvey, Luc Roma, Nolan Kowski, Drew Miller, Lucas Driscoll and Camden Stout, matched by the filenames supplied by the user.

`site/assets/players/portraits.json` records each source page, original image URL where applicable, source name, dimensions, crop and SHA-256. Wesley Taylor on the Centre roster maps to the existing Wes Taylor identity. Photo keys combine team and canonical player name, so an opponent with the same name does not receive a Centre player's photo. Photo links on player notebooks lead to the source bio. Transfer photos are labeled as coming from the previous school.

## Framing and display

The app retains the original image pixels. User-supplied JPEGs have EXIF, XMP, IPTC and comment headers removed without re-encoding; a before/after decoded-pixel comparison verifies no visual alteration. Official school downloads retain their original bytes. Each image has a square CSS viewport defined as `[left, top, edge]` in original-image pixels. The framing concentrates on the head and shoulders, including for the supplied longer portraits. Faces are neither generated nor retouched. A photo shown in an older season is an identity portrait, not a claim about the player's appearance in that season.

Cards, search and leaderboard images load lazily; the profile hero loads immediately. Missing or failed photos retain initials and their reserved layout space. Photos are decorative beside visible player names, avoiding duplicate screen-reader labels. All 34 original images total about 1.2 MB; ordinary app use loads only the images needed by the current view.

## Add or replace a photo

1. Match the provided name or official roster record to a specific Centre identity in `site/data/index.json`. Do not infer identity from facial appearance.
2. Place the image in `site/assets/players/` with a descriptive lowercase filename and an extension matching its actual format. The school image CDN may serve WebP at a URL ending in `.jpg`.
3. Add or update the matching `TEAM|Last, First` entry in `portraits.json`, recording its source, dimensions, hash and square crop. Keep the crop within the original dimensions. For a supplied file, use `sourceType: "user"`, `credit: "User-supplied photo"` and null source URLs.
4. Remove the name from `missingCurrent` when supplied. Review the framing at profile and card sizes on desktop and mobile, in both themes. Check that all images decode in the browser.
5. Run `node --test tests/*.test.mjs` and `python3 pipeline/package.py`, then publish the changed assets and code through the existing Pages workflow. Statistical data does not need rebuilding for a photo-only update.

The local `Player Images` folder is not watched or uploaded automatically.
