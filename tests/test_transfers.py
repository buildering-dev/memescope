"""Offline test for analyze.py filter 3 (transfer clusters). No network."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import analyze as A

ok = True
def check(name, cond, info=''):
    global ok
    print(('[PASS] ' if cond else '[FAIL] ') + name, info if not cond else '')
    ok = ok and cond

# creator buys 1000 tokens for 10 SOL, gives 500 each to two fresh wallets, which sell for 6 SOL each.
# An unrelated trader buys and sells. A pool-leg trade (tokens not conserved) must NOT be merged.
tr = [
    (1, 100, 0, 'CREATOR', 1000.0, -10.0),
    (2, 101, 0, 'CREATOR', -1000.0, -0.000005), (2, 101, 0, 'FRESH1', 500.0, 0.0), (2, 101, 0, 'FRESH2', 500.0, 0.0),
    (3, 102, 0, 'FRESH1', -500.0, 6.0),
    (3, 102, 1, 'FRESH2', -500.0, 6.0),
    (4, 103, 0, 'TRADER', 50.0, -0.004), (4, 103, 0, 'OTHER', -20.0, 0.003),   # tiny trades in one tx, pool leg -> not a transfer
    (5, 104, 0, 'TRADER', -50.0, 0.006),
]
out, merged = A.merge_transfers(tr)
check('two recipients merged into the creator', merged == 2, merged)
check('transfer rows dropped, pool-leg tx kept', len(out) == len(tr) - 3, len(out))
check('recipient sells booked to creator', sum(1 for r in out if r[3] == 'CREATOR') == 3)
tok, ws = A.parse_token_common(out, 'CREATOR', 100)
W = {w['w']: w for w in ws}
check('creator cluster closed with net +2 SOL', W['CREATOR']['closed'] and abs(W['CREATOR']['net_q'] - 2.0) < 1e-6, W['CREATOR'])
check('no zero-cost "independent" winners', 'FRESH1' not in W and 'FRESH2' not in W)
check('unrelated traders untouched', 'TRADER' in W and 'OTHER' in W)
print('TRANSFER TEST PASSED' if ok else 'TRANSFER TEST FAILED')
sys.exit(0 if ok else 1)
