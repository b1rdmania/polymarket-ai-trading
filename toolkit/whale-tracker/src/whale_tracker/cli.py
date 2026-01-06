"""
CLI for Whale Tracker.
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

from .config import WatchlistConfig
from .monitor import WhaleMonitor

app = typer.Typer(help="Whale Tracker - Monitor large trades on Polymarket")
console = Console()


def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@app.command("large-trades")
def large_trades(
    min_size: float = typer.Option(1000, "--min-size", "-m", help="Minimum trade size in USD"),
    hours: int = typer.Option(24, "--hours", "-h", help="Hours to look back"),
    limit: int = typer.Option(20, "--limit", "-l", help="Max trades to show"),
):
    """Find large trades in recent history."""
    
    config = WatchlistConfig(min_trade_size=min_size)
    monitor = WhaleMonitor(config)
    
    console.print(f"\n[bold green]🐋 LARGE TRADES (>${min_size:,.0f})[/bold green]")
    console.print(f"Last {hours} hours\n")
    
    trades = run_async(monitor.get_large_trades(hours=hours, min_size=min_size))
    
    if not trades:
        console.print("[yellow]No large trades found[/yellow]")
        return
    
    table = Table()
    table.add_column("Market", no_wrap=False, width=45)
    table.add_column("Volume", justify="right", style="green")
    table.add_column("Whale?", justify="center")
    
    for trade in trades[:limit]:
        whale_emoji = "🐋" if trade.is_whale else ""
        table.add_row(
            trade.market_question[:43] + "..." if len(trade.market_question) > 43 else trade.market_question,
            f"${trade.value_usd:,.0f}",
            whale_emoji
        )
    
    console.print(table)


@app.command("top-traders")
def top_traders(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of traders to show"),
):
    """Get top traders from PredictFolio."""
    
    monitor = WhaleMonitor()
    traders = run_async(monitor.get_top_traders(limit=limit))
    
    console.print(f"\n[bold green]🏆 TOP TRADERS[/bold green]\n")
    
    table = Table()
    table.add_column("#", width=3)
    table.add_column("Trader", width=20)
    table.add_column("Volume", justify="right")
    table.add_column("PnL", justify="right")
    table.add_column("ROI", justify="right")
    
    for trader in traders:
        pnl_color = "green" if trader.pnl >= 0 else "red"
        table.add_row(
            str(trader.rank),
            trader.username or "Anonymous",
            f"${trader.total_volume/1_000_000:.1f}M",
            f"[{pnl_color}]${trader.pnl/1000:,.0f}k[/{pnl_color}]",
            f"{trader.pnl_pct:.1f}%"
        )
    
    console.print(table)
    console.print("\n[dim]Data from PredictFolio leaderboard[/dim]")


@app.command()
def flow(
    market_id: str = typer.Argument(..., help="Market ID to analyze"),
    hours: int = typer.Option(24, "--hours", "-h", help="Hours to analyze"),
):
    """Analyze trade flow for a specific market."""
    
    monitor = WhaleMonitor()
    trade_flow = run_async(monitor.get_market_flow(market_id, hours=hours))
    
    console.print(f"\n[bold]📊 TRADE FLOW ANALYSIS[/bold]")
    console.print(f"Period: {trade_flow.period_start.strftime('%m/%d %H:%M')} - {trade_flow.period_end.strftime('%m/%d %H:%M')}\n")
    
    console.print(f"Total Volume: ${trade_flow.total_volume:,.0f}")
    console.print(f"  Buy Volume: [green]${trade_flow.buy_volume:,.0f}[/green] ({trade_flow.buy_ratio*100:.0f}%)")
    console.print(f"  Sell Volume: [red]${trade_flow.sell_volume:,.0f}[/red] ({(1-trade_flow.buy_ratio)*100:.0f}%)")
    
    flow_color = "green" if trade_flow.net_flow >= 0 else "red"
    flow_direction = "NET BUYING" if trade_flow.net_flow >= 0 else "NET SELLING"
    console.print(f"\n[{flow_color}]{flow_direction}: ${abs(trade_flow.net_flow):,.0f}[/{flow_color}]")


@app.command()
def alerts(
    min_size: float = typer.Option(10000, "--min-size", "-m", help="Minimum whale size"),
):
    """Scan for whale activity alerts."""
    
    config = WatchlistConfig(whale_threshold=min_size)
    monitor = WhaleMonitor(config)
    
    console.print(f"\n[bold green]🐋 SCANNING FOR WHALES (>${min_size:,.0f})[/bold green]\n")
    
    whale_alerts = run_async(monitor.scan_for_whales())
    
    if not whale_alerts:
        console.print("[yellow]No whale activity detected[/yellow]")
        return
    
    for alert in whale_alerts:
        console.print(f"🐋 [bold]{alert.message}[/bold]")
    
    console.print(f"\n[dim]Found {len(whale_alerts)} whale trades[/dim]")


if __name__ == "__main__":
    app()
