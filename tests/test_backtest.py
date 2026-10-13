import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import pandas as pd
from backtest import backtest, buy_hold_signal


def test_next_open_and_fee():
    p = pd.DataFrame({'Open': [10., 20., 30.], 'Close': [15., 25., 40.]},
                     index=pd.date_range('2020-01-01', periods=3))
    r = backtest(p, buy_hold_signal(p), initial_cash=100, cost_bps=0)
    assert r['Equity'].iloc[0] == 100
    assert r['Shares'].iloc[1] == 5
    assert r['Equity'].iloc[1] == 125
    assert r['Equity'].iloc[2] == 200


def test_fee_reduces_equity():
    p = pd.DataFrame({'Open': [10., 10.], 'Close': [10., 10.]},
                     index=pd.date_range('2020-01-01', periods=2))
    r = backtest(p, buy_hold_signal(p), initial_cash=100, cost_bps=100)
    assert abs(r['Equity'].iloc[-1] - 100 / 1.01) < 1e-8
