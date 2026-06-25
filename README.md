# 📈 Live Stock Tracker

A simple web app: type **any** stock name or ticker symbol and watch its price
move in real time, with a live-updating chart, intraday/historical ranges, and
key stats (open, prev close, day high/low, volume).

![overview](https://img.shields.io/badge/stack-Node.js%20·%20zero%20deps-4c8dff)

## Features

- 🔎 **Search by name or symbol** — type "Apple", "Tesla", "BTC" and pick from
  live autocomplete suggestions (stocks, ETFs, crypto, indices, FX).
- ⚡ **Live updates** — the price refreshes every 5 seconds with an up/down
  flash, and a pulsing **LIVE** badge (auto-pauses when the tab is hidden).
- 📊 **Custom chart** — a dependency-free canvas chart with gradient fill,
  hover crosshair + tooltip, and range buttons (1D · 5D · 1M · 6M · 1Y).
- 💹 **Key stats** — open, previous close, day high/low, volume, exchange.
- 🔗 **Deep links** — open `?symbol=NVDA` to jump straight to a stock.

## Run it

Requires **Node.js 18+** (no `npm install` needed — there are no dependencies).

```bash
npm start
# or: node server.js
```

Then open **http://localhost:3000**.

Set a different port with `PORT=8080 npm start`.

## How it works

The browser never calls the data provider directly (that would be blocked by
CORS). Instead, a tiny Node HTTP server in [`server.js`](server.js):

1. Serves the static frontend from [`public/`](public/).
2. Proxies two Yahoo Finance endpoints:
   - `GET /api/search?q=<text>` → symbol autocomplete
   - `GET /api/quote?symbol=<SYM>&range=<r>&interval=<i>` → live price +
     intraday/historical points + stats

The frontend ([`public/app.js`](public/app.js)) polls `/api/quote` on an
interval and redraws the price and chart.

```
browser ──> /api/* ──> Node server ──> Yahoo Finance
   ▲                                         │
   └──────────── JSON quotes ◄───────────────┘
```

> **Note on networks:** if you run this somewhere that routes outbound HTTPS
> through a proxy, the server honours the `HTTPS_PROXY` environment variable
> automatically (via the `undici` module bundled with Node).

## Disclaimer

Data is sourced from Yahoo Finance for **informational purposes only** — it is
not investment advice, and quotes may be delayed. The Yahoo Finance endpoints
are unofficial and may change or rate-limit at any time.
