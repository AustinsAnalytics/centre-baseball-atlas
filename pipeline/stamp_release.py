"""Stamp a site build/publication in UTC; the app displays Eastern time."""
from pathlib import Path
from datetime import datetime, timezone
import json,os
root=Path(__file__).resolve().parents[1]
def stamp():
 release={'updatedAt':datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00','Z'),'revision':os.environ.get('GITHUB_SHA'),'timeZone':'America/New_York'}
 (root/'site/release.json').write_text(json.dumps(release,separators=(',',':')))
 return release
if __name__=='__main__':print(json.dumps(stamp()))
