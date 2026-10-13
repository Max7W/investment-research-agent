"""Download and freeze a data snapshot; no silent overwrites."""
from pathlib import Path
from datetime import datetime, timezone
import json
import yfinance as yf

OUT = Path('data/raw')
OUT.mkdir(parents=True, exist_ok=True)
for ticker in ('SPY', 'QQQ', 'IWM'):
    frame = yf.download(ticker, start='2010-01-01', end='2026-01-01',
                        auto_adjust=False, actions=True, progress=False)
    if frame.empty:
        raise RuntimeError(f'No data for {ticker}')
    if frame.columns.nlevels > 1:
        frame.columns = frame.columns.get_level_values(0)
    path = OUT / f'{ticker}_2010_2025.csv'
    if path.exists():
        raise FileExistsError(f'Refusing to overwrite {path}')
    frame.to_csv(path)
    print(f'Saved {path}: {len(frame)} rows')
metadata = {'downloaded_at_utc': datetime.now(timezone.utc).isoformat(),
            'source': 'Yahoo Finance via yfinance', 'auto_adjust': False,
            'start': '2010-01-01', 'end_exclusive': '2026-01-01'}
(OUT / 'snapshot_metadata.json').write_text(json.dumps(metadata, indent=2))
