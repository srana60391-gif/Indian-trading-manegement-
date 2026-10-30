const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8080;
const cache = new Map();

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);

  res.setHeader('Access-Control-Allow-Origin', '*');

  if (url.pathname === '/api/ohlcv') {
    const symbol = (url.searchParams.get('symbol') || 'RELIANCE').toUpperCase();
    const exchange = (url.searchParams.get('exchange') || 'nse').toLowerCase();
    const interval = (url.searchParams.get('interval') || '5m').toLowerCase();

    if (!/^[A-Z0-9][A-Z0-9.-]{0,29}$/.test(symbol) ||
        !['nse', 'bse'].includes(exchange) || !['1m', '5m'].includes(interval)) {
      res.writeHead(400, {'Content-Type':'application/json'});
      return res.end(JSON.stringify({error:'Invalid symbol or exchange'}));
    }

    const ticker = symbol.endsWith('.NS') || symbol.endsWith('.BO')
      ? symbol
      : symbol + (exchange === 'nse' ? '.NS' : '.BO');

    const key = ticker + ':' + interval;
    const saved = cache.get(key);

    if (saved && Date.now() - saved.time < 30000) {
      res.writeHead(200, {'Content-Type':'application/json'});
      return res.end(JSON.stringify(saved.data));
    }

    try {
      const api = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(ticker)}?range=5d&interval=${interval}`;

      const response = await fetch(api, {
        headers: {'User-Agent':'Mozilla/5.0'}
      });

      if (!response.ok) throw new Error('Yahoo HTTP ' + response.status);

      const json = await response.json();
      const result = json.chart && json.chart.result && json.chart.result[0];

      if (!result || !result.timestamp) {
        throw new Error('No market data found for ' + ticker);
      }

      const quote = result.indicators.quote[0];

      const data = result.timestamp.map((time, i) => ({
        date: new Date(time * 1000).toISOString(),
        open: quote.open[i],
        high: quote.high[i],
        low: quote.low[i],
        close: quote.close[i],
        volume: quote.volume[i]
      })).filter(x =>
        Number.isFinite(x.close) &&
        Number.isFinite(x.high) &&
        Number.isFinite(x.low)
      );

      const output = {
        symbol: ticker,
        exchange: exchange.toUpperCase(),
        currency: result.meta.currency,
        price: result.meta.regularMarketPrice,
        marketTime: result.meta.regularMarketTime,
        data: data
      };

      cache.set(key, {time:Date.now(), data:output});

      res.writeHead(200, {'Content-Type':'application/json'});
      return res.end(JSON.stringify(output));

    } catch (error) {
      res.writeHead(502, {'Content-Type':'application/json'});
      return res.end(JSON.stringify({error:error.message}));
    }
  }

  const requested = url.pathname === '/' ? 'index.html' : url.pathname.slice(1);
  const file = path.join(__dirname, requested);

  if (!file.startsWith(__dirname + path.sep) ||
      !fs.existsSync(file) ||
      !fs.statSync(file).isFile()) {
    res.writeHead(404);
    return res.end('Not Found');
  }

  const types = {
    '.html':'text/html',
    '.js':'text/javascript',
    '.json':'application/json',
    '.css':'text/css'
  };

  res.writeHead(200, {'Content-Type':types[path.extname(file)] || 'application/octet-stream'});
  fs.createReadStream(file).pipe(res);
});

server.listen(PORT, '0.0.0.0', () => {
  console.log('Indian Risk Manager running on port ' + PORT);
});
