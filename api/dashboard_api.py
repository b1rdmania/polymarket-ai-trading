#!/usr/bin/env python3
"""
Multi-Model Dashboard API

FastAPI backend that serves trading data for the web dashboard.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import httpx
import os
from openai import OpenAI
import numpy as np

app = FastAPI(title="Polymarket Trading Dashboard")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).parent.parent
MODELS = ['conservative', 'moderate', 'aggressive']

# Initialize OpenAI client
openai_client = None
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Polymarket API endpoints
CLOB_API = "https://clob.polymarket.com"
GAMMA_API = "https://gamma-api.polymarket.com"

# Cache for embeddings
EMBEDDINGS_CACHE_PATH = BASE_DIR / 'data' / 'embeddings_cache.json'
embeddings_cache = {}


def get_model_stats(model_name: str) -> Dict:
    """Get statistics for a model from SQLite database."""
    db_path = BASE_DIR / 'data' / f'trades_{model_name}.db'
    
    if not db_path.exists():
        return {
            'model': model_name,
            'status': 'No data yet',
            'total_trades': 0,
            'open_positions': 0,
            'winners': 0,
            'losers': 0,
            'win_rate': 0,
            'total_pnl': 0,
            'avg_pnl': 0,
            'best_trade': 0,
            'worst_trade': 0,
            'today_trades': 0,
            'today_pnl': 0,
            'last_trade': None,
        }
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Total trades (all statuses)
        cursor.execute("SELECT COUNT(*) FROM trades")
        total_trades = cursor.fetchone()[0] or 0
        
        # Open positions (lowercase 'open')
        cursor.execute("SELECT COUNT(*) FROM trades WHERE status = 'open'")
        open_positions = cursor.fetchone()[0] or 0
        
        # Closed trades with P&L (lowercase 'closed')
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winners,
                SUM(CASE WHEN pnl <= 0 THEN 1 ELSE 0 END) as losers,
                SUM(pnl) as total_pnl,
                AVG(pnl) as avg_pnl,
                MAX(pnl) as best,
                MIN(pnl) as worst
            FROM trades WHERE status = 'closed' AND pnl IS NOT NULL
        """)
        
        row = cursor.fetchone()
        closed_trades = row[0] or 0
        winners = row[1] or 0
        losers = row[2] or 0
        total_pnl = row[3] or 0
        avg_pnl = row[4] or 0
        best = row[5] or 0
        worst = row[6] or 0
        
        # Today's trades (use 'timestamp' column)
        today = datetime.now().date().isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM trades WHERE timestamp LIKE ?
        """, (f"{today}%",))
        today_trades = cursor.fetchone()[0] or 0
        
        # Last trade (use 'timestamp' column)
        cursor.execute("""
            SELECT market_question, side, entry_price, size_usd, timestamp, status
            FROM trades 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        
        last_trade_row = cursor.fetchone()
        last_trade = None
        if last_trade_row:
            last_trade = {
                'market': last_trade_row[0],
                'side': last_trade_row[1],
                'price': last_trade_row[2],
                'size': last_trade_row[3],
                'time': last_trade_row[4],
                'status': last_trade_row[5]
            }
        
        conn.close()
        
        return {
            'model': model_name,
            'status': 'Active' if total_trades > 0 else 'Scanning',
            'total_trades': total_trades,
            'open_positions': open_positions,
            'winners': winners,
            'losers': losers,
            'win_rate': (winners / closed_trades * 100) if closed_trades > 0 else 0,
            'total_pnl': total_pnl,
            'avg_pnl': avg_pnl,
            'best_trade': best,
            'worst_trade': worst,
            'today_trades': today_trades,
            'today_pnl': 0,  # Would need closed trades today
            'last_trade': last_trade,
        }
    
    except Exception as e:
        return {
            'model': model_name,
            'status': f'Error: {e}',
            'total_trades': 0,
            'winners': 0,
            'losers': 0,
            'win_rate': 0,
            'total_pnl': 0,
        }


def get_recent_trades(model_name: str, limit: int = 20) -> List[Dict]:
    """Get recent trades for a model from SQLite database."""
    db_path = BASE_DIR / 'data' / f'trades_{model_name}.db'
    
    if not db_path.exists():
        return []
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                market_question,
                side,
                size_usd,
                entry_price,
                pnl,
                status,
                timestamp,
                notes
            FROM trades
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        trades = []
        for row in cursor.fetchall():
            trades.append({
                'market': row[0],
                'side': row[1],
                'size': row[2],
                'price': row[3],
                'pnl': row[4],
                'status': row[5],
                'timestamp': row[6],
                'notes': row[7],
            })
        
        conn.close()
        return trades
    
    except Exception as e:
        return []


# ============================================================================
# LIVE SIGNAL FEED ENDPOINTS
# ============================================================================

@app.get("/api/signals/live")
async def get_live_signals(limit: int = 50):
    """Get recent trades from all models."""
    all_signals = []
    
    for model in MODELS:
        db_path = BASE_DIR / 'data' / f'trades_{model}.db'
        if not db_path.exists():
            continue
            
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    market_question,
                    side,
                    entry_price,
                    size_usd,
                    timestamp,
                    status,
                    pnl,
                    notes
                FROM trades
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            for row in cursor.fetchall():
                all_signals.append({
                    'model': model,
                    'market': row[0] or 'Unknown',
                    'direction': row[1],
                    'entry_price': row[2],
                    'size': row[3],
                    'timestamp': row[4],
                    'status': row[5],
                    'pnl': row[6],
                    'notes': row[7],
                    'strength': 'STRONG' if model == 'conservative' else 'MODERATE' if model == 'moderate' else 'WEAK'
                })
            
            conn.close()
        except Exception as e:
            print(f"Error fetching signals for {model}: {e}")
            continue
    
    # Sort by timestamp descending
    all_signals.sort(key=lambda x: x['timestamp'] or '', reverse=True)
    return {
        'signals': all_signals[:limit],
        'timestamp': datetime.now().isoformat()
    }


# ============================================================================
# MARKET QUALITY SCORING ENDPOINTS
# ============================================================================

async def fetch_market_data(market_id: str) -> Optional[Dict]:
    """Fetch market data from Polymarket."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{GAMMA_API}/markets/{market_id}")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"Error fetching market {market_id}: {e}")
    return None


def calculate_quality_score(market: Dict) -> Dict:
    """Calculate quality score for a market."""
    # Liquidity score (0-35 points)
    volume_24h = float(market.get('volume24hr', 0))
    liquidity_score = min(35, (volume_24h / 10000) * 35)  # Max at $10k volume
    
    # Spread score (0-25 points) - tighter is better
    outcomes = market.get('outcomes', [])
    if len(outcomes) >= 2:
        best_bid = float(outcomes[0].get('price', 0.5))
        best_ask = float(outcomes[1].get('price', 0.5))
        spread_pct = abs(best_ask - best_bid) * 100
        spread_score = max(0, 25 - (spread_pct * 5))  # Penalize wide spreads
    else:
        spread_score = 0
    
    # Activity score (0-15 points) - recent activity
    activity_score = 15 if volume_24h > 1000 else (volume_24h / 1000) * 15
    
    # Clarity score (0-25 points) - question length and simplicity
    question = market.get('question', '')
    question_len = len(question)
    if 20 < question_len < 100:
        clarity_score = 25
    elif question_len > 150:
        clarity_score = 10
    else:
        clarity_score = 15
    
    total_score = liquidity_score + spread_score + activity_score + clarity_score
    
    # Assign grade
    if total_score >= 85:
        grade = 'A+'
    elif total_score >= 75:
        grade = 'A'
    elif total_score >= 65:
        grade = 'B'
    elif total_score >= 50:
        grade = 'C'
    else:
        grade = 'D'
    
    return {
        'total_score': round(total_score, 1),
        'grade': grade,
        'liquidity_score': round(liquidity_score, 1),
        'spread_score': round(spread_score, 1),
        'activity_score': round(activity_score, 1),
        'clarity_score': round(clarity_score, 1),
        'volume_24h': volume_24h
    }


@app.get("/api/quality/top-markets")
async def get_top_quality_markets(limit: int = 20):
    """Get highest quality markets for trading."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{CLOB_API}/markets")
            if response.status_code != 200:
                return {'error': 'Failed to fetch markets', 'markets': []}
            
            markets = response.json()[:50]  # Analyze top 50
            
            scored_markets = []
            for market in markets:
                quality = calculate_quality_score(market)
                scored_markets.append({
                    'market_id': market.get('condition_id', ''),
                    'question': market.get('question', ''),
                    'quality': quality,
                    'price': float(market.get('outcomes', [{}])[0].get('price', 0)),
                    'volume_24h': quality['volume_24h']
                })
            
            # Sort by score
            scored_markets.sort(key=lambda x: x['quality']['total_score'], reverse=True)
            
            return {
                'markets': scored_markets[:limit],
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        return {'error': str(e), 'markets': []}


# ============================================================================
# AI MARKET INSIGHTS ENDPOINTS
# ============================================================================

class MarketAnalysisRequest(BaseModel):
    market_question: str
    current_price: Optional[float] = None


@app.post("/api/ai/analyze-market")
async def analyze_market_with_ai(request: MarketAnalysisRequest):
    """Analyze a market question using AI."""
    if not openai_client:
        return {'error': 'OpenAI API not configured', 'analysis': None}
    
    try:
        # Generate embedding
        embedding_response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=request.market_question
        )
        embedding = embedding_response.data[0].embedding
        
        # Use GPT-4 to analyze the market
        analysis_prompt = f"""Analyze this prediction market question for trading opportunities:

Question: {request.market_question}
Current Price: {request.current_price if request.current_price else 'Unknown'}¢

Provide:
1. AI Confidence Score (0-100): How confident are you in predicting the outcome?
2. Risk Factors: List 2-3 specific risks (ambiguity, external events, etc.)
3. Probability Assessment: Your estimated probability of YES outcome
4. Key Reasoning: 2-3 sentences explaining your analysis

Format as JSON:
{{"confidence": <number>, "risk_factors": [<strings>], "probability": <number>, "reasoning": "<string>"}}"""
        
        completion = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": analysis_prompt}],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        analysis = json.loads(completion.choices[0].message.content)
        
        return {
            'analysis': analysis,
            'embedding_generated': True,
            'embedding_dimension': len(embedding),
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {'error': str(e), 'analysis': None}


# ============================================================================
# RESOLUTION TRACKER ENDPOINTS
# ============================================================================

@app.get("/api/resolution/recent")
async def get_recent_resolutions(limit: int = 20):
    """Get recently resolved markets."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{CLOB_API}/markets?closed=true")
            if response.status_code != 200:
                return {'resolutions': [], 'error': 'Failed to fetch'}
            
            markets = response.json()[:limit]
            
            resolutions = []
            for market in markets:
                # Check if we traded this market
                our_prediction = None
                outcome = None
                
                for model in MODELS:
                    db_path = BASE_DIR / 'data' / f'trades_{model}.db'
                    if db_path.exists():
                        try:
                            conn = sqlite3.connect(db_path)
                            cursor = conn.cursor()
                            cursor.execute("""
                                SELECT side, price, pnl, status 
                                FROM trades 
                                WHERE market_question LIKE ? 
                                LIMIT 1
                            """, (f"%{market.get('question', '')[:30]}%",))
                            
                            row = cursor.fetchone()
                            if row:
                                our_prediction = {
                                    'model': model,
                                    'side': row[0],
                                    'price': row[1],
                                    'pnl': row[2],
                                    'status': row[3]
                                }
                            conn.close()
                        except:
                            pass
                
                resolutions.append({
                    'question': market.get('question', ''),
                    'market_id': market.get('condition_id', ''),
                    'closed': market.get('closed', False),
                    'our_prediction': our_prediction,
                    'volume': float(market.get('volume', 0))
                })
            
            return {
                'resolutions': resolutions,
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        return {'resolutions': [], 'error': str(e)}


@app.get("/api/resolution/accuracy")
async def get_resolution_accuracy():
    """Calculate AI model accuracy on resolved markets."""
    total_resolved = 0
    correct_predictions = 0
    
    for model in MODELS:
        db_path = BASE_DIR / 'data' / f'trades_{model}.db'
        if not db_path.exists():
            continue
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*), SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END)
                FROM trades 
                WHERE status = 'CLOSED'
            """)
            
            row = cursor.fetchone()
            if row[0]:
                total_resolved += row[0]
                correct_predictions += row[1] or 0
            
            conn.close()
        except:
            pass
    
    accuracy = (correct_predictions / total_resolved * 100) if total_resolved > 0 else 0
    
    return {
        'accuracy': round(accuracy, 1),
        'total_resolved': total_resolved,
        'correct_predictions': correct_predictions,
        'timestamp': datetime.now().isoformat()
    }


# ============================================================================
# VECTOR SEARCH / SEMANTIC SIMILARITY ENDPOINTS
# ============================================================================

@app.post("/api/vector/search")
async def semantic_search(query: str, limit: int = 10):
    """Find similar markets using semantic search."""
    if not openai_client:
        return {'error': 'OpenAI API not configured', 'results': []}
    
    try:
        # Generate embedding for query
        embedding_response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = np.array(embedding_response.data[0].embedding)
        
        # Fetch active markets and compute similarity
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{CLOB_API}/markets")
            if response.status_code != 200:
                return {'results': [], 'error': 'Failed to fetch markets'}
            
            markets = response.json()[:50]  # Top 50 markets
            
            results = []
            for market in markets:
                question = market.get('question', '')
                
                # Generate embedding for market question
                market_embedding_response = openai_client.embeddings.create(
                    model="text-embedding-3-small",
                    input=question
                )
                market_embedding = np.array(market_embedding_response.data[0].embedding)
                
                # Compute cosine similarity
                similarity = np.dot(query_embedding, market_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(market_embedding)
                )
                
                results.append({
                    'question': question,
                    'market_id': market.get('condition_id', ''),
                    'similarity': float(similarity),
                    'price': float(market.get('outcomes', [{}])[0].get('price', 0))
                })
            
            # Sort by similarity
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            return {
                'query': query,
                'results': results[:limit],
                'timestamp': datetime.now().isoformat()
            }
    except Exception as e:
        return {'error': str(e), 'results': []}


# ============================================================================
# EXISTING ENDPOINTS
# ============================================================================

@app.get("/api/models")
async def get_all_models():
    """Get stats for all models."""
    return {
        'models': [get_model_stats(model) for model in MODELS],
        'timestamp': datetime.now().isoformat()
    }


@app.get("/api/model/{model_name}")
async def get_model(model_name: str):
    """Get detailed stats for one model."""
    if model_name not in MODELS:
        return {'error': 'Model not found'}
    
    return {
        'stats': get_model_stats(model_name),
        'recent_trades': get_recent_trades(model_name),
        'timestamp': datetime.now().isoformat()
    }


@app.get("/api/comparison")
async def get_comparison():
    """Get comparison data for all models."""
    models = [get_model_stats(model) for model in MODELS]
    
    return {
        'models': models,
        'aggregate': {
            'total_trades': sum(m['total_trades'] for m in models),
            'total_pnl': sum(m['total_pnl'] for m in models),
            'today_trades': sum(m['today_trades'] for m in models),
            'today_pnl': sum(m['today_pnl'] for m in models),
        },
        'timestamp': datetime.now().isoformat()
    }


@app.get("/api/markets/live")
async def get_live_markets():
    """
    Proxy endpoint for Polymarket Gamma API.
    Frontend can't call Gamma API directly due to CORS restrictions.
    Returns top markets sorted by 24hr volume (recent activity).
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Fetch more markets to get better selection
            response = await client.get(
                f"{GAMMA_API}/markets",
                params={
                    "limit": 200,
                    "active": "true",
                    "closed": "false"
                }
            )
            response.raise_for_status()
            markets = response.json()
            
            if isinstance(markets, list):
                # Filter for markets with meaningful volume
                filtered = [
                    m for m in markets
                    if float(m.get('volume', 0) or 0) > 10000  # Min $10k total volume
                ]
                
                # Sort by 24hr volume (recent activity) - more relevant than all-time
                filtered.sort(
                    key=lambda x: float(x.get('volume24hr', 0) or 0), 
                    reverse=True
                )
                
                # Return top 25 most active markets
                top_markets = filtered[:25]
                
                return {
                    "markets": top_markets,
                    "count": len(top_markets),
                    "total_scanned": len(markets),
                    "timestamp": datetime.now().isoformat()
                }
            
            return {"markets": [], "count": 0, "error": "Invalid response format"}
            
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Polymarket API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@app.get("/api/health")
async def health():
    """Health check endpoint with detailed status."""
    # Check if models are running via PID file
    pids_file = BASE_DIR / 'data' / 'model_pids.txt'
    models_running = pids_file.exists()
    pids_content = None
    if pids_file.exists():
        try:
            pids_content = pids_file.read_text()
        except:
            pass
    
    # Count total trades and open positions across all models
    total_trades = 0
    open_positions = 0
    last_trade = None
    
    for model in MODELS:
        db_path = BASE_DIR / 'data' / f'trades_{model}.db'
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM trades")
                total_trades += cursor.fetchone()[0] or 0
                cursor.execute("SELECT COUNT(*) FROM trades WHERE status = 'open'")
                open_positions += cursor.fetchone()[0] or 0
                cursor.execute("SELECT timestamp FROM trades ORDER BY timestamp DESC LIMIT 1")
                row = cursor.fetchone()
                if row and (last_trade is None or row[0] > last_trade):
                    last_trade = row[0]
                conn.close()
            except:
                pass
    
    return {
        'status': 'ok',
        'models_running': models_running,
        'total_trades': total_trades,
        'open_positions': open_positions,
        'last_trade': last_trade,
        'pids': pids_content,
        'timestamp': datetime.now().isoformat()
    }


@app.get("/api/debug/positions")
async def debug_positions():
    """Debug endpoint - simulate checking positions for sells."""
    import json as json_mod
    
    results = {}
    
    # Get current market prices - both YES and NO
    current_prices = {}  # question -> {yes: x, no: y}
    market_ids = {}  # question -> id
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{GAMMA_API}/markets", params={"limit": 50, "active": "true", "closed": "false"})
            markets = resp.json()
            for m in markets:
                q = m.get('question', '')
                mid = m.get('id', '')
                prices_str = m.get('outcomePrices', '[]')
                if isinstance(prices_str, str):
                    prices = json_mod.loads(prices_str)
                else:
                    prices = prices_str
                if prices and len(prices) >= 2:
                    current_prices[q] = {'yes': float(prices[0]), 'no': float(prices[1])}
                    market_ids[q] = mid
    except Exception as e:
        results['price_fetch_error'] = str(e)
    
    for model in MODELS:
        db_path = BASE_DIR / 'data' / f'trades_{model}.db'
        if not db_path.exists():
            results[model] = {'error': 'DB not found', 'path': str(db_path)}
            continue
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get open positions with details - match the trader query
            cursor.execute("""
                SELECT id, market_id, market_question, side, entry_price, size_usd, shares, model
                FROM trades WHERE status = 'open' AND model = ?
            """, (model,))
            
            positions = []
            should_sell = []
            for row in cursor.fetchall():
                entry_price = row[4]
                question = row[2] or 'Unknown'
                side = row[3]
                
                # Get correct price based on side (YES or NO)
                prices = current_prices.get(question, None)
                if prices:
                    current_price = prices['yes'] if side == 'YES' else prices['no']
                else:
                    current_price = None
                
                # Check if market ID matches
                api_market_id = market_ids.get(question)
                stored_market_id = row[1]
                id_match = str(api_market_id) == str(stored_market_id) if api_market_id else False
                
                pnl_pct = None
                sell_trigger = False
                if current_price and entry_price > 0:
                    pnl_pct = ((current_price - entry_price) / entry_price) * 100
                    if pnl_pct >= 50 or pnl_pct <= -50:  # Take profit or stop loss
                        sell_trigger = True
                        should_sell.append({
                            'question': question[:40],
                            'side': side,
                            'entry': entry_price,
                            'current': current_price,
                            'pnl_pct': round(pnl_pct, 1),
                            'id_match': id_match
                        })
                
                positions.append({
                    'id': row[0],
                    'market_id': stored_market_id,
                    'api_market_id': api_market_id,
                    'id_match': id_match,
                    'question': question[:40],
                    'side': side,
                    'entry': entry_price,
                    'current': current_price,
                    'pnl_pct': round(pnl_pct, 1) if pnl_pct else None,
                    'should_sell': sell_trigger
                })
            
            conn.close()
            
            results[model] = {
                'positions_loaded': len(positions),
                'should_sell': should_sell,
                'sample': positions[:3]
            }
        except Exception as e:
            results[model] = {'error': str(e)}
    
    return results


@app.get("/api/debug/force-check")
async def force_check():
    """Force a position check and return what WOULD happen."""
    import json as json_mod
    
    results = {'actions': [], 'errors': []}
    
    # Get current markets from API
    markets = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{GAMMA_API}/markets", params={"limit": 100, "active": "true"})
            markets = resp.json()
    except Exception as e:
        results['errors'].append(f"Fetch markets error: {e}")
        return results
    
    # Build lookups
    market_by_id = {}
    market_by_question = {}
    for m in markets:
        mid = m.get('id')
        if mid:
            market_by_id[str(mid)] = m
        q = m.get('question', '')
        if q:
            market_by_question[q] = m
    
    results['markets_fetched'] = len(markets)
    results['market_ids'] = list(market_by_id.keys())[:10]
    
    for model in MODELS:
        db_path = BASE_DIR / 'data' / f'trades_{model}.db'
        if not db_path.exists():
            continue
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, market_id, market_question, side, entry_price
                FROM trades WHERE status = 'open' AND model = ?
            """, (model,))
            
            for row in cursor.fetchall():
                trade_id, market_id, question, side, entry_price = row
                
                # Find market
                market = market_by_id.get(str(market_id))
                if not market:
                    market = market_by_question.get(question)
                
                if not market:
                    results['errors'].append(f"{model}: Market not found for {question[:30]}")
                    continue
                
                # Get price
                prices_str = market.get('outcomePrices', '[]')
                if isinstance(prices_str, str):
                    prices = json_mod.loads(prices_str)
                else:
                    prices = prices_str
                
                if len(prices) < 2:
                    results['errors'].append(f"{model}: No prices for {question[:30]}")
                    continue
                
                current_price = float(prices[0]) if side == 'YES' else float(prices[1])
                pnl_pct = ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
                
                action = 'HOLD'
                if pnl_pct >= 50:
                    action = 'SELL (take profit)'
                elif pnl_pct <= -50:
                    action = 'SELL (stop loss)'
                
                if action != 'HOLD':
                    results['actions'].append({
                        'model': model,
                        'trade_id': trade_id,
                        'question': question[:40],
                        'side': side,
                        'entry': entry_price,
                        'current': current_price,
                        'pnl_pct': round(pnl_pct, 1),
                        'action': action
                    })
            
            conn.close()
        except Exception as e:
            results['errors'].append(f"{model}: {e}")
    
    return results


@app.get("/")
async def root():
    """Serve the dashboard."""
    dashboard_path = BASE_DIR / 'dashboard' / 'trading' / 'index.html'
    if dashboard_path.exists():
        return FileResponse(dashboard_path)
    return {"message": "Dashboard not found. Run from project root."}


# Mount static files (commented out - using Vercel frontend now)
# app.mount("/static", StaticFiles(directory=str(BASE_DIR / "dashboard" / "trading")), name="static")


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Trading Dashboard API...")
    print("📊 Dashboard: http://localhost:8000")
    print("🔌 API Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

