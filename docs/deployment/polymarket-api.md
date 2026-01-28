# Polymarket API Documentation

## Two APIs Available

Polymarket has **two APIs** for market data:

| API | URL | Use Case |
|-----|-----|----------|
| **Gamma API** | `https://gamma-api.polymarket.com` | Market data, prices, volume (recommended) |
| **CLOB API** | `https://clob.polymarket.com` | Order book, trading, order placement |

**We use the Gamma API** for market data because it has the fields we need (`volume`, `outcomePrices`).

---

## Gamma API (Market Data)

### Base URL

```
https://gamma-api.polymarket.com
```

### Endpoints

#### GET /markets

Fetch active markets with prices and volume.

**Request:**
```
GET https://gamma-api.polymarket.com/markets?limit=50&active=true&closed=false
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Max markets to return (default: 100) |
| `active` | boolean | Only active markets |
| `closed` | boolean | Filter by closed status |

**Response:** Array of market objects (not wrapped in `{data: [...]}`)

```json
[
  {
    "id": "0x...",
    "question": "Will X happen by Y date?",
    "conditionId": "0x...",
    "slug": "will-x-happen",
    "description": "Full market description...",
    "outcomes": ["Yes", "No"],
    "outcomePrices": ["0.65", "0.35"],
    "volume": "1234567.89",
    "volumeNum": 1234567.89,
    "volume24hr": "12345.67",
    "liquidity": "50000.00",
    "liquidityNum": 50000.00,
    "active": true,
    "closed": false,
    "archived": false,
    "endDate": "2026-12-31",
    "endDateIso": "2026-12-31T23:59:59.000Z",
    "category": "Politics",
    "bestBid": 0.64,
    "bestAsk": 0.66,
    "spread": 0.02,
    "lastTradePrice": 0.65,
    "oneDayPriceChange": -0.02,
    "oneWeekPriceChange": 0.05
  }
]
```

### Key Fields

| Field | Type | Description |
|-------|------|-------------|
| `question` | string | Market question text |
| `outcomePrices` | string[] | Prices as ["0.65", "0.35"] for [YES, NO] |
| `volume` | string | Total volume in USDC |
| `volumeNum` | number | Volume as number |
| `volume24hr` | string | 24-hour volume |
| `liquidity` | string | Current liquidity |
| `active` | boolean | Market is active |
| `closed` | boolean | Market has resolved |
| `bestBid` | number | Best bid price |
| `bestAsk` | number | Best ask price |
| `spread` | number | Bid-ask spread |
| `lastTradePrice` | number | Last trade price |

---

## CLOB API (Order Book)

### Base URL

```
https://clob.polymarket.com
```

### Response Format

CLOB API wraps data in `{data: [...]}`:

```json
{
  "data": [...],
  "next_cursor": "abc123",
  "limit": 100,
  "count": 1000
}
```

### Market Object (CLOB)

Different structure from Gamma API:

```json
{
  "condition_id": "0x...",
  "question_id": "0x...",
  "question": "Market question",
  "tokens": [
    {
      "token_id": "123...",
      "outcome": "Yes",
      "price": 0.65,
      "winner": false
    },
    {
      "token_id": "456...",
      "outcome": "No",
      "price": 0.35,
      "winner": false
    }
  ],
  "active": true,
  "closed": false,
  "minimum_order_size": 15,
  "minimum_tick_size": 0.01
}
```

**Note:** CLOB API does NOT have `volume` field. Use Gamma API for volume data.

---

## Our Integration Setup

### Exact Configuration

```javascript
// API endpoint
const API = 'https://gamma-api.polymarket.com';

// Fetch active markets
const response = await fetch(`${API}/markets?limit=50&active=true&closed=false`);
const markets = await response.json(); // Returns array directly

// Filter criteria
const filtered = markets
    .filter(m => parseFloat(m.volume || 0) > 1000)  // Min $1k volume
    .sort((a, b) => parseFloat(b.volume) - parseFloat(a.volume))
    .slice(0, 20);

// Parse price (outcomePrices[0] = YES price)
const yesPrice = parseFloat(market.outcomePrices[0]);  // 0.65 = 65%
const noPrice = parseFloat(market.outcomePrices[1]);   // 0.35 = 35%
```

### Filter Criteria

| Criterion | Value | Reason |
|-----------|-------|--------|
| `active` | `true` | Skip inactive markets |
| `closed` | `false` | Skip resolved markets |
| `volume` | `> $1,000` | Minimum liquidity for trading |
| Sort by | `volume DESC` | Prioritize liquid markets |
| Limit | `20` | Top markets only |

### Polling Frequency

- **Dashboard:** Every 30 seconds
- **Trading models:** Every 60 seconds
- No official rate limits, but be reasonable

---

## Price = Probability

**Core Concept:** Prices represent probabilities.

| YES Price | Meaning |
|-----------|---------|
| 65¢ | 65% probability of YES outcome |
| 35¢ | 35% probability (NO would be 65¢) |
| 95¢ | 95% probability (high confidence) |
| 5¢ | 5% probability (unlikely) |

### How Shares Work

1. **Buy YES at 65¢** → If YES wins, get $1.00 (profit: 35¢)
2. **Buy NO at 35¢** → If NO wins, get $1.00 (profit: 65¢)
3. **Sell early** → Lock in profits or cut losses before resolution
4. **Resolution** → Winning shares = $1.00, losing shares = $0.00

### Mean Reversion Opportunities

We look for:
- **Overreaction:** Price jumps from 50¢ to 80¢ on news, may revert
- **Extreme prices:** 95¢+ or 5¢- often overconfident
- **Volume spikes:** High volume + price movement = potential reversion

---

## Authentication

### Read-Only (No Auth Required)

Market data is **public**:
```bash
curl https://gamma-api.polymarket.com/markets?limit=5
```

### Trading (Auth Required)

Order placement requires:
- Ethereum wallet
- EIP712 signed orders
- API credentials

**We use paper trading only** - no auth needed.

---

## CORS

Both APIs allow cross-origin requests:

```
Access-Control-Allow-Origin: *
```

Frontend JavaScript can call directly without proxy.

---

## Fees

| Type | Fee |
|------|-----|
| Maker | 0 bps (0%) |
| Taker | 0 bps (0%) |

**Currently zero fees for all trades.**

Fee formula (when applied):
```
fee = baseRate × min(price, 1 - price) × size
```

---

## Additional Resources

- [Polymarket Docs](https://docs.polymarket.com/)
- [CLOB Introduction](https://docs.polymarket.com/developers/CLOB/introduction)
- [Exchange Contract](https://github.com/Polymarket/ctf-exchange)
- [Audit Report](https://github.com/Polymarket/ctf-exchange/blob/main/audit/ChainSecurity_Polymarket_Exchange_audit.pdf)

---

**Last Updated:** January 28, 2026  
**Tested Endpoints:**
- `https://gamma-api.polymarket.com/markets` ✓
- `https://clob.polymarket.com/markets` ✓ (different schema)
