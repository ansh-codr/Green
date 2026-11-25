import json, tempfile, threading, unittest, urllib.request, urllib.error, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import server
class MarketplaceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.temp=tempfile.TemporaryDirectory(); server.DB=Path(cls.temp.name)/'test.db'; server.init(); cls.http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler); cls.thread=threading.Thread(target=cls.http.serve_forever,daemon=True); cls.thread.start(); cls.base='http://127.0.0.1:'+str(cls.http.server_port)
 @classmethod
 def tearDownClass(cls): cls.http.shutdown(); cls.http.server_close(); cls.temp.cleanup()
 def request(self,path,data=None):
  req=urllib.request.Request(self.base+path,data=json.dumps(data).encode() if data else None,headers={'Content-Type':'application/json'})
  with urllib.request.urlopen(req) as r: return json.load(r)
 def test_judge_flow_and_filters(self):
  d={'item':'Unique scientific calculator','category':'Calculators','condition':'Good','age':2,'original':1200,'trade':'Swap'}
  estimate=self.request('/api/estimate',d); self.assertGreater(estimate['suggested_price'],0); self.assertEqual(estimate['comparables_count'],12); self.assertTrue(estimate['synthetic'])
  posted=self.request('/api/listings',d); self.assertEqual(estimate['suggested_price'],posted['suggested_price'])
  listings=self.request('/api/listings?q=Unique&category=Calculators&condition=Good&max_price=1200'); self.assertEqual(len(listings),1); self.assertEqual(listings[0]['trade'],'Swap')
  self.assertEqual(self.request('/api/listings?q=Unique&condition=Fair'),[])
 def test_invalid_data(self):
  with self.assertRaises(urllib.error.HTTPError) as ctx: self.request('/api/estimate',{'item':'x','category':'Books','condition':'Good','age':-1,'original':100})
  self.assertEqual(ctx.exception.code,400)
 def test_sales_count(self): self.assertEqual(len(server.seed()),200)
if __name__=='__main__': unittest.main()
