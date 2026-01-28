# Polymarket API Documentation

## CLOB (Central Limit Order Book) Introduction

### System Overview

Polymarket's Order Book, or CLOB (Central Limit Order Book), is **hybrid-decentralized**:

- **Off-chain**: Operator handles matching and ordering
- **On-chain**: Settlement executed non-custodially via signed order messages

#### Exchange Contract

- Custom Exchange contract for atomic swaps
- Between binary Outcome Tokens (CTF ERC1155 assets and ERC20 PToken assets)
- And collateral assets (ERC20)
- Designed for binary markets
- Complementary tokens match across unified order book

#### Order Structure

- Orders are **EIP712-signed structured data**
- Matched orders: one maker + one or more takers
- Price improvements benefit the taker
- Operator handles off-chain order management
- Submits matched trades to blockchain for on-chain execution

---

## API Capabilities

The Polymarket Order Book API enables:

- **Market Makers**: Programmatically manage market orders
- **Traders**: Create, list, fetch orders of any amount
- **Data Access**: 
  - All available markets
  - Market prices
  - Order history
  - REST and WebSocket endpoints

### Key Endpoints

- **REST API**: `https://clob.polymarket.com`
- **Markets endpoint**: `/markets`
- Returns: `{"data": [...]}`  array of market objects

---

## Security

### Audit

- Exchange contract audited by **Chainsecurity**
- [View Audit Report](https://github.com/Polymarket/ctf-exchange/blob/main/audit/ChainSecurity_Polymarket_Exchange_audit.pdf)

### Operator Privileges (Limited)

Operators can only:
- Match orders
- Ensure non-censorship
- Maintain correct ordering

Operators **cannot**:
- Set prices
- Execute unauthorized trades

### User Rights

- Users can cancel orders **on-chain independently**
- No trust required in operator for order cancellation

---

## Fees

### Current Fee Schedule

> Subject to change

| Volume Level | Maker Fee (bps) | Taker Fee (bps) |
|--------------|-----------------|-----------------|
| >0 USDC      | 0               | 0               |

**Currently: 0% fees for all traders**

### Fee Calculation (When Applied)

Fees apply symmetrically in output assets (proceeds).

**Selling outcome tokens (base) for collateral (quote):**
```
feeQuote = baseRate × min(price, 1 - price) × size
```

**Buying outcome tokens (base) with collateral (quote):**
```
feeBase = baseRate × min(price, 1 - price) × (size / price)
```

---

## Market Data Structure

### Response Format

```json
{
  "data": [
    {
      "condition_id": "0x...",
      "question_id": "0x...",
      "question": "Will X happen?",
      "description": "Market description...",
      "outcomes": [
        {
          "price": "0.65",  // Price in USDC (65¢ = 65% probability)
          "side": "YES"
        },
        {
          "price": "0.35",
          "side": "NO"
        }
      ],
      "volume": "123456.78",  // 24h volume in USDC
      "closed": false,
      "active": true,
      "accepting_orders": true,
      "minimum_order_size": 15,
      "minimum_tick_size": 0.01
    }
  ]
}
```

### Key Fields

- **`condition_id`**: Unique market identifier
- **`question`**: Human-readable market question
- **`outcomes[].price`**: Price = probability (0.65 = 65% chance)
- **`volume`**: 24-hour trading volume in USDC
- **`closed`**: Boolean, market resolved or not
- **`minimum_order_size`**: Min order size (usually 15 USDC)
- **`minimum_tick_size`**: Price increment (usually 0.01 = 1¢)

---

## Price = Probability

**Core Concept**: Prices on Polymarket represent probabilities

- If YES shares trade at **65¢**, it means **65% probability** of outcome
- If NO shares trade at **35¢**, it means **35% probability** of opposite
- YES + NO always equals $1.00 (100%)

### How Shares Work

1. **Buying**: Buy YES at 65¢, if outcome happens → get $1.00 (35¢ profit)
2. **Selling**: Can sell before resolution to lock in profits or cut losses
3. **Resolution**: Winning shares pay $1.00, losing shares pay $0.00

---

## Additional Resources

- [Exchange contract source code](https://github.com/Polymarket/ctf-exchange/tree/main/src)
- [Exchange contract documentation](https://github.com/Polymarket/ctf-exchange/blob/main/docs/Overview.md)
- [Full Polymarket Documentation](https://docs.polymarket.com/)

---

## Integration Notes for Our Models

### What We Use

1. **CLOB API** (`https://clob.polymarket.com/markets`)
   - Fetch all active markets
   - Get current prices (probabilities)
   - Check volume and liquidity

2. **Data We Need**
   - `question`: Market description
   - `outcomes[0].price`: Current YES price
   - `volume`: Trading volume (liquidity proxy)
   - `closed`: Skip resolved markets

3. **Our Filters**
   - Volume > $100 (minimum liquidity)
   - Sort by volume descending
   - Only show active markets

### Rate Limits

- No official rate limits documented
- We poll every 60 seconds
- Well within reasonable usage

### No Authentication Required

- Market data is **public**
- No API key needed for read-only access
- Only need keys for order placement (we're paper trading)

---

**Last Updated**: January 28, 2026  
**Source**: https://docs.polymarket.com/developers/CLOB/introduction
