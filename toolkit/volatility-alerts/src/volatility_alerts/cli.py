"""
CLI for Volatility Alerts.
"""

import asyncio
from typing import List, Optional

try:
    import typer
    from rich.console import Console
except ImportError:
    print("CLI requires: pip install typer rich")
    raise SystemExit(1)

from .config import AlertConfig
from .monitor import AlertMonitor
from .handlers import ConsoleHandler, FileHandler, WebhookHandler, DiscordHandler

app = typer.Typer(help="Polymarket Volatility Alert CLI")
console = Console()


@app.command()
def watch(
    markets: List[str] = typer.Argument(None, help="Market keywords to watch"),
    threshold: float = typer.Option(10.0, "--threshold", "-t", help="Price change % threshold"),
    interval: int = typer.Option(60, "--interval", "-i", help="Check interval in seconds"),
    webhook: Optional[str] = typer.Option(None, "--webhook", help="Webhook URL for alerts"),
    discord: Optional[str] = typer.Option(None, "--discord", help="Discord webhook URL"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file for alerts"),
):
    """Watch specific markets for volatility."""
    
    config = AlertConfig(
        price_threshold_pct=threshold,
        check_interval_sec=interval,
        markets=list(markets) if markets else []
    )
    
    monitor = AlertMonitor(config)
    
    # Add handlers
    monitor.add_handler(ConsoleHandler())
    
    if output:
        monitor.add_handler(FileHandler(output))
        console.print(f"[dim]Writing alerts to {output}[/dim]")
    
    if webhook:
        monitor.add_handler(WebhookHandler(webhook))
        console.print(f"[dim]Sending to webhook[/dim]")
    
    if discord:
        monitor.add_handler(DiscordHandler(discord))
        console.print(f"[dim]Sending to Discord[/dim]")
    
    console.print(f"\n[bold green]🚨 VOLATILITY MONITOR STARTED[/bold green]")
    console.print(f"Threshold: {threshold}% | Interval: {interval}s")
    if markets:
        console.print(f"Watching: {', '.join(markets)}")
    else:
        console.print("Watching: Top trending markets")
    console.print("")
    
    try:
        asyncio.run(monitor.start())
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitor stopped[/yellow]")


@app.command()
def trending(
    threshold: float = typer.Option(5.0, "--threshold", "-t", help="Price change % threshold"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of markets to monitor"),
    interval: int = typer.Option(60, "--interval", "-i", help="Check interval in seconds"),
):
    """Monitor trending markets for volatility."""
    
    config = AlertConfig(
        price_threshold_pct=threshold,
        check_interval_sec=interval,
        max_markets=limit,
        markets=[]  # Empty = trending
    )
    
    monitor = AlertMonitor(config)
    monitor.add_handler(ConsoleHandler())
    
    console.print(f"\n[bold green]🚨 TRENDING MARKET MONITOR[/bold green]")
    console.print(f"Threshold: {threshold}% | Watching top {limit} markets")
    console.print("")
    
    try:
        asyncio.run(monitor.start())
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitor stopped[/yellow]")


@app.command()
def once(
    threshold: float = typer.Option(5.0, "--threshold", "-t", help="Price change % threshold"),
    limit: int = typer.Option(20, "--limit", "-l", help="Number of markets to check"),
):
    """Run a single check cycle (no continuous monitoring)."""
    from .monitor import AlertMonitor
    from .handlers import ConsoleHandler
    
    async def _run_once():
        config = AlertConfig(
            price_threshold_pct=threshold,
            max_markets=limit
        )
        
        monitor = AlertMonitor(config)
        monitor.add_handler(ConsoleHandler())
        
        console.print(f"[bold]Checking top {limit} markets...[/bold]\n")
        await monitor._check_cycle()
        console.print("[dim]Check complete[/dim]")
    
    asyncio.run(_run_once())


if __name__ == "__main__":
    app()
