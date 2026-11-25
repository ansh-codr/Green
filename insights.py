from server import seed
from statistics import median
rows=seed()
print('Synthetic data: patterns reflect generator assumptions, not observed sales.')
for cat in ['Books','Calculators','Cycles']:
 for condition in ['Excellent','Good','Fair']:
  for lo,hi in [(0,1),(2,3),(4,5)]:
   values=[sold/original*100 for _,c,cond,age,original,sold in rows if c==cat and cond==condition and lo<=age<=hi]
   if values: print(f'{cat} | {condition} | {lo}-{hi} years | median {median(values):.1f}% | n={len(values)}')
