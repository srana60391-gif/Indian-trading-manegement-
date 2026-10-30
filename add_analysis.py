from pathlib import Path

p = Path("index.html")
s = p.read_text()

if "market-analysis-panel" in s:
    print("Market Analysis section already exists.")
    raise SystemExit

panel = r"""
<style>
#market-analysis-panel{background:#18212f;color:#fff;padding:18px;margin:18px 0;border-radius:14px;font-family:Arial}
#market-analysis-panel input,#market-analysis-panel select{padding:12px;margin:5px 0;border-radius:8px;border:1px solid #526078;background:#101722;color:white}
#market-analysis-panel button{padding:12px 18px;border:0;border-radius:8px;background:#16a085;color:white;font-weight:bold}
#market-analysis-panel .result{margin-top:14px;padding:14px;background:#101722;border-radius:10px;line-height:1.8}
</style>
<section id="market-analysis-panel">
<h2>📊 Market Analysis</h2>
<p>Daily market data analysis</p>
<input id="ma-symbol" value="RELIANCE" placeholder="Stock symbol">
<select id="ma-exchange"><option value="nse">NSE</option><option value="bse">BSE</option></select>
<button onclick="runMarketAnalysis()">Analyze Stock</button>
<div id="ma-result" class="result">Enter a stock symbol and press Analyze Stock.</div>
</section>
<script>
function ema(values, period) {
  const k=2/(period+1);
  let out=[], prev=values[0];
  for(let i=0;i<values.length;i++){
    prev=i===0?values[i]:values[i]*k+prev*(1-k);
    out.push(prev);
  }
  return out;
}
function rsi(values, period=14) {
  if(values.length<=period) return null;
  let gains=0, losses=0;
  for(let i=1;i<=period;i++){
    let d=values[i]-values[i-1];
    if(d>0) gains+=d; else losses-=d;
  }
  let ag=gains/period, al=losses/period;
  for(let i=period+1;i<values.length;i++){
    let d=values[i]-values[i-1];
    ag=(ag*(period-1)+Math.max(d,0))/period;
    al=(al*(period-1)+Math.max(-d,0))/period;
  }
  if(al===0) return 100;
  return 100-(100/(1+ag/al));
}
async function runMarketAnalysis(){
 const symbol=document.getElementById('ma-symbol').value.trim().toUpperCase();
 const exchange=document.getElementById('ma-exchange').value;
 const box=document.getElementById('ma-result');
 if(!symbol){box.textContent='Enter a stock symbol.';return;}
 box.textContent='Loading market data...';
 try{
  const response=await fetch('/api/ohlcv?symbol='+encodeURIComponent(symbol)+'&exchange='+exchange);
  const json=await response.json();
  if(!response.ok || !json.data || json.data.length<27) throw new Error(json.error||'Not enough candle data');
  const rows=json.data;
  const closes=rows.map(x=>Number(x.close));
  const last=rows[rows.length-1];
  const e9=ema(closes,9), e21=ema(closes,21);
  const fast=ema(closes,12), slow=ema(closes,26);
  const macd=fast.map((v,i)=>v-slow[i]);
  const signal=ema(macd,9);
  const rv=rsi(closes,14);
  const bullish=e9.at(-1)>e21.at(-1) && rv>50 && macd.at(-1)>signal.at(-1);
  const bearish=e9.at(-1)<e21.at(-1) && rv<50 && macd.at(-1)<signal.at(-1);
  const decision=bullish?'BUY BIAS':bearish?'SELL BIAS':'WAIT';
  const tr=rows.map((x,i)=>{
    if(i===0) return x.high-x.low;
    return Math.max(x.high-x.low,Math.abs(x.high-rows[i-1].close),Math.abs(x.low-rows[i-1].close));
  });
  const atr=tr.slice(-14).reduce((a,b)=>a+b,0)/Math.min(14,tr.length);
  const stop=last.close-1.5*atr;
  const target=last.close+3*atr;
  box.innerHTML='<h3>'+decision+'</h3>'+
   'Symbol: '+symbol+' ('+exchange.toUpperCase()+')<br>'+
   'Last candle: '+last.date+'<br>'+
   'Last close: ₹'+last.close.toFixed(2)+'<br>'+
   'EMA 9: ₹'+e9.at(-1).toFixed(2)+'<br>'+
   'EMA 21: ₹'+e21.at(-1).toFixed(2)+'<br>'+
   'RSI 14: '+rv.toFixed(2)+'<br>'+
   'MACD: '+macd.at(-1).toFixed(3)+'<br>'+
   '<hr>Illustrative levels if bullish:<br>'+
   'Reference entry: ₹'+last.close.toFixed(2)+'<br>'+
   'Possible stop reference: ₹'+stop.toFixed(2)+'<br>'+
   'Possible target reference: ₹'+target.toFixed(2)+'<br>'+
   '<small>Uses daily historical candles only. Not a live signal or guaranteed trade. Confirm price, volume and risk before any trade.</small>';
 }catch(e){box.textContent='Analysis error: '+e.message;}
}
</script>
"""

if "</body>" not in s:
    raise SystemExit("Could not find </body> in index.html")
p.write_text(s.replace("</body>", panel + "\n</body>"))
print("Market Analysis section added successfully.")
