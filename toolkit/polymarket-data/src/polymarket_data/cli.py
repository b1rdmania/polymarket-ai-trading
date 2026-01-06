"""
CLI for Polymarket Data Fetcher.

Usage:
    polymarket search "bitcoin"
    polymarket trending --timeframe 24h
    polymarket movers --threshold 10
"""

import asyncio
from typing import Optional

try:
    import typer
    from rich.console import Console
    from rich.table import Table
except ImportError:
    print("CLI requires: pip install typer rich")
    raise SystemExit(1)

from .client import PolymarketClient

app = typer.Typer(help="Polymarket Data Fetcher CLI")
console = Console()


def run_async(coro):
    """Run an async function."""
    return asyncio.get_event_loop().run_until_complete(coro)


@app.command()
def search(
    query: str,
    limit: int = typer.Option(10, "--limit", "-l", help="Max results"),
    active_only: bool = typer.Option(True, "--active/--all", help="Active markets only")
):
    """Search markets by keyword."""
    async def _search():
        client = PolymarketClient()
        return await client.search(query, limit=limit, active_only=active_only)
    
    markets = run_async(_search())
    
    table = Table(title=f"Markets matching '{query}'")
    table.add_column("Question", style="cyan", no_wrap=False)
    table.add_column("Volume 24h", justify="right", style="green")
    table.add_column("Active", justify="center")
    
    for m in markets:
        table.add_row(
            m.question[:60] + "..." if len(m.question) > 60 else m.question,
            f"${m.volume_24h:,.0f}",
            "✓" if m.active else "✗"
        )
    
    console.print(table)


@app.command()
def trending(
    timeframe: str = typer.Option("24h", "--timeframe", "-t", help="24h, 7d, or 30d"),
    limit: int = typer.Option(10, "--limit", "-l", help="Max results")
):
    """Get trending markets by volume."""
    async def _trending():
        client = PolymarketClient()
        return await client.get_trending(timeframe=timeframe, limit=limit)
    
    markets = run_async(_trending())
    
    volume_attr = {"24h": "volume_24h", "7d": "volume_7d", "30d": "volume_30d"}[timeframe]
    
    table = Table(title=f"Trending Markets ({timeframe})")
    table.add_column("#", style="dim", width=3)
    table.add_column("Question", style="cyan", no_wrap=False)
    table.add_column(f"Volume ({timeframe})", justify="right", style="green")
    
    for i, m in enumerate(markets, 1):
        vol = getattr(m, volume_attr, 0)
        table.add_row(
            str(i),
            m.question[:50] + "..." if len(m.question) > 50 else m.question,
            f"${vol:,.0f}"
        )
    
    console.print(table)


@app.command()
def movers(
    threshold: float = typer.Option(10.0, "--threshold", "-t", help="Min % change"),
    limit: int = typer.Option(10, "--limit", "-l", help="Max results")
):
    """Find markets with large price movements."""
    async def _movers():
        client = PolymarketClient()
        return await client.detect_movers(threshold_pct=threshold, limit=limit)
    
    results = run_async(_movers())
    
    if not results:
        console.print(f"[yellow]No markets found moving >{threshold}%[/yellow]")
        return
    
    table = Table(title=f"Markets Moving >{threshold}%")
    table.add_column("Question", style="cyan", no_wrap=False)
    table.add_column("Change", justify="right")
    table.add_column("Direction", justify="center")
    
    for r in results:
        change = r["price_change_pct"]
        color = "green" if change > 0 else "red"
        arrow = "↑" if change > 0 else "↓"
        
        table.add_row(
            r["market"].question[:50] + "...",
            f"[{color}]{change:+.1f}%[/{color}]",
            f"[{color}]{arrow}[/{color}]"
        )
    
    console.print(table)


@app.command()
def category(
    name: str = typer.Argument(..., help="Category name (Politics, Sports, Crypto)"),
    limit: int = typer.Option(10, "--limit", "-l", help="Max results")
):
    """Get markets by category."""
    async def _category():
        client = PolymarketClient()
        return await client.get_by_category(name, limit=limit)
    
    markets = run_async(_category())
    
    table = Table(title=f"{name} Markets")
    table.add_column("Question", style="cyan")
    table.add_column("Volume 24h", justify="right", style="green")
    
    for m in markets:
        table.add_row(
            m.question[:55] + "..." if len(m.question) > 55 else m.question,
            f"${m.volume_24h:,.0f}"
        )
    
    console.print(table)


@app.command()
def closing(
    hours: int = typer.Option(24, "--hours", "-h", help="Hours until close"),
    limit: int = typer.Option(10, "--limit", "-l", help="Max results")
):
    """Get markets closing soon."""
    async def _closing():
        client = PolymarketClient()
        return await client.get_closing_soon(hours=hours, limit=limit)
    
    markets = run_async(_closing())
    
    table = Table(title=f"Markets Closing Within {hours}h")
    table.add_column("Question", style="cyan")
    table.add_column("End Date", justify="right", style="yellow")
    
    for m in markets:
        end = m.end_date.strftime("%Y-%m-%d %H:%M") if m.end_date else "Unknown"
        table.add_row(
            m.question[:55] + "..." if len(m.question) > 55 else m.question,
            end
        )
    
    console.print(table)


if __name__ == "__main__":
    app()
