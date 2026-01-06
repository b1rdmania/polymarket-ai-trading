#!/usr/bin/env python3
"""
Initialize databases for all models.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
MODELS = ['conservative', 'moderate', 'aggressive']

SCHEMA = """
CREATE TABLE IF NOT EXISTS trades (
    id TEXT PRIMARY KEY,
    market_id TEXT NOT NULL,
    market_question TEXT NOT NULL,
    token_id TEXT NOT NULL,
    side TEXT NOT NULL,
    size REAL NOT NULL,
    price REAL NOT NULL,
    value_usd REAL NOT NULL,
    pnl REAL DEFAULT 0,
    status TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata TEXT
);

CREATE INDEX IF NOT EXISTS idx_status ON trades(status);
CREATE INDEX IF NOT EXISTS idx_created_at ON trades(created_at);
CREATE INDEX IF NOT EXISTS idx_market_id ON trades(market_id);
"""

def init_database(model_name: str):
    """Initialize database for a model."""
    db_path = BASE_DIR / 'data' / f'trades_{model_name}.db'
    
    print(f"Initializing database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute schema
    cursor.executescript(SCHEMA)
    conn.commit()
    conn.close()
    
    print(f"✅ {model_name} database ready")

def main():
    """Initialize all databases."""
    print("="*60)
    print("DATABASE INITIALIZATION")
    print("="*60 + "\n")
    
    # Create data directory
    (BASE_DIR / 'data').mkdir(exist_ok=True)
    
    for model in MODELS:
        init_database(model)
    
    print(f"\n✅ All databases initialized!")
    print(f"\nLocations:")
    for model in MODELS:
        print(f"  data/trades_{model}.db")

if __name__ == '__main__':
    main()


