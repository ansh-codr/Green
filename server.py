import csv, json, math, os, random, sqlite3, statistics
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = Path(os.getenv('GREEN_DB', ROOT / 'data' / 'market.db'))
CATEGORIES = {'Books': ['Engineering Mathematics', 'Python Handbook', 'Physics Textbook', 'Data Structures Guide'], 'Calculators': ['Scientific Calculator', 'Graphing Calculator', 'Basic Calculator'], 'Cycles': ['Campus Bicycle', 'Mountain Bicycle', 'City Bicycle']}
CONDITIONS = ['Excellent', 'Good', 'Fair']

def seed():
    rng = random.Random(42)
    records = []
    for i in range(200):
        category = list(CATEGORIES)[i % 3]; condition = CONDITIONS[(i // 3) % 3]
        age = rng.randint(0, 5); original = rng.choice({'Books':[400,600,800,1200], 'Calculators':[800,1200,1600,2000], 'Cycles':[4000,6000,8000,10000]}[category])
        base = {'Books': .78, 'Calculators': .82, 'Cycles': .84}[category]
        decay = {'Books': .08, 'Calculators': .10, 'Cycles': .07}[category]
        ratio = max(.18, base * (1-decay)**age * {'Excellent':1, 'Good':.82, 'Fair':.63}[condition] * rng.uniform(.94, 1.06))
        records.append((rng.choice(CATEGORIES[category]), category, condition, age, original, round(original * ratio)))
    return records

def init():
    DB.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB) as db:
        db.execute('CREATE TABLE IF NOT EXISTS sales (item TEXT, category TEXT, condition TEXT, age REAL, original REAL, sold REAL)')
        db.execute('CREATE TABLE IF NOT EXISTS listings (id INTEGER PRIMARY KEY, item TEXT, category TEXT, condition TEXT, age REAL, original REAL, price INTEGER, trade TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP)')
        if not db.execute('SELECT count(*) FROM sales').fetchone()[0]: db.executemany('INSERT INTO sales VALUES (?,?,?,?,?,?)',seed())
    csvpath=ROOT/'data'/'past_listings.csv'
    if not csvpath.exists():
        with csvpath.open('w',newline='') as f:
            w=csv.writer(f); w.writerow(['item','category','condition','age_years','original_price_inr','sold_price_inr']); w.writerows(seed())

def validate(d):
    item=str(d.get('item','')).strip(); cat=d.get('category'); cond=d.get('condition'); trade=d.get('trade','Sell')
    if not item or len(item)>100: raise ValueError('Enter an item name (1–100 characters).')
    if cat not in CATEGORIES or cond not in CONDITIONS or trade not in ('Sell','Swap'): raise ValueError('Choose a valid category, condition and listing type.')
    try: age=float(d.get('age')); original=float(d.get('original'))
    except (ValueError,TypeError): raise ValueError('Enter a valid age and original price.')
    if not math.isfinite(age) or not 0<=age<=30 or not math.isfinite(original) or not 1<=original<=1000000: raise ValueError('Age must be 0–30 years and price ₹1–₹10,00,000.')
    return {'item':item,'category':cat,'condition':cond,'age':age,'original':original,'trade':trade}

def estimate(d):
    d=validate(d)
    with sqlite3.connect(DB) as db:
        rows=db.execute('SELECT item,age,original,sold FROM sales WHERE category=? AND condition=?',(d['category'],d['condition'])).fetchall()
    # nearest examples by age, using normalized resale fraction to adjust for purchase price
    rows.sort(key=lambda r: abs(r[1]-d['age']))
    nearest=rows[:min(12,len(rows))]
    if not nearest: raise ValueError('No comparable data available.')
    fraction=statistics.median(r[3]/r[2] for r in nearest)
    price=max(1,round(d['original']*fraction))
    return {'suggested_price':price,'range_low':round(price*.9),'range_high':round(price*1.1),'retained_percent':round(fraction*100,1),'comparables_count':len(nearest),'comparable_age_min':min(r[1] for r in nearest),'comparable_age_max':max(r[1] for r in nearest),'method':'Median sold/original price ratio of up to 12 same-category, same-condition synthetic sales closest in age, multiplied by your original price.','synthetic':True}

class Handler(BaseHTTPRequestHandler):
    def sendjson(self, data, code=200):
        raw=json.dumps(data).encode(); self.send_response(code); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_GET(self):
        u=urlparse(self.path)
        if u.path=='/api/listings':
            q=parse_qs(u.query); sql='SELECT id,item,category,condition,age,original,price,trade,created FROM listings WHERE 1=1'; args=[]
            for key,col in [('category','category'),('condition','condition'),('trade','trade')]:
                if q.get(key) and q[key][0]: sql+=' AND '+col+'=?'; args.append(q[key][0])
            if q.get('q') and q['q'][0]: sql+=' AND item LIKE ?'; args.append('%'+q['q'][0]+'%')
            if q.get('max_price') and q['max_price'][0]:
                try:
                    max_price=float(q['max_price'][0])
                    if not math.isfinite(max_price) or max_price<0: raise ValueError()
                except ValueError: return self.sendjson({'error':'Invalid maximum price'},400)
                sql+=' AND price<=?'; args.append(max_price)
            with sqlite3.connect(DB) as db:
                db.row_factory=sqlite3.Row; rows=[dict(r) for r in db.execute(sql+' ORDER BY id DESC',args)]
            return self.sendjson(rows)
        if u.path=='/api/insights':
            with sqlite3.connect(DB) as db:
                rows=db.execute('SELECT category,condition,round(avg(sold*100.0/original),1),count(*) FROM sales GROUP BY category,condition ORDER BY category,condition').fetchall()
            return self.sendjson({'total_sales':200,'groups':[{'category':a,'condition':b,'average_retained_percent':c,'count':n} for a,b,c,n in rows], 'synthetic':True})
        files={'/':'index.html','/app.js':'app.js','/style.css':'style.css'}
        if u.path not in files: self.send_error(404); return
        f=ROOT/'static'/files[u.path]; raw=f.read_bytes(); self.send_response(200); self.send_header('Content-Type',{'html':'text/html; charset=utf-8','js':'text/javascript; charset=utf-8','css':'text/css; charset=utf-8'}[f.suffix[1:]]); self.send_header('Content-Length',str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def do_POST(self):
        if self.path not in ('/api/estimate','/api/listings'): return self.sendjson({'error':'Not found'},404)
        try:
            n=int(self.headers.get('Content-Length','0'))
            if n>10000: raise ValueError('Request too large')
            d=validate(json.loads(self.rfile.read(n))); result=estimate(d)
            if self.path=='/api/listings':
                with sqlite3.connect(DB) as db:
                    cur=db.execute('INSERT INTO listings(item,category,condition,age,original,price,trade) VALUES (?,?,?,?,?,?,?)',(*[d[k] for k in ('item','category','condition','age','original')],result['suggested_price'],d['trade']))
                    result['id']=cur.lastrowid
            self.sendjson(result,201 if self.path=='/api/listings' else 200)
        except (ValueError,TypeError,json.JSONDecodeError) as e: self.sendjson({'error':str(e)},400)

if __name__=='__main__':
    init(); port=int(os.getenv('PORT','8000')); print(f'GREEN running at http://localhost:{port}',flush=True); ThreadingHTTPServer(('0.0.0.0',port),Handler).serve_forever()
