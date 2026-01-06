"""
CLI for Mean Reversion Signals.
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

from .config import SignalConfig
from .generator import SignalGenerator
from .models import SignalDirection, SignalStrength

app = typer.Typer(help="Mean Reversion Signal Generator")
console = Console()


def run_async(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@app.command()
def scan(
    min_mispricing: float = typer.Option(5.0, "--min-mispricing", "-m", help="Minimum mispricing %"),
    limit: int = typer.Option(20, "--limit", "-l", help="Max signals to show"),
    horizon_min: int = typer.Option(7, "--horizon-min", help="Min days until resolution"),
    horizon_max: int = typer.Option(21, "--horizon-max", help="Max days until resolution"),
):
    """Scan markets for mean reversion signals."""
    
    config = SignalConfig(
        min_mispricing_pct=min_mispricing,
        horizon_days=(horizon_min, horizon_max)
    )
    
    generator = SignalGenerator(config)
    
    console.print(f"\n[bold green]📊 SCANNING FOR MEAN REVERSION SIGNALS[/bold green]")
    console.print(f"Horizon: {horizon_min}-{horizon_max} days | Min mispricing: {min_mispricing}%\n")
    
    signals = run_async(generator.scan(limit=limit))
    
    if not signals:
        console.print("[yellow]No signals found matching criteria[/yellow]")
        return
    
    table = Table(title=f"Found {len(signals)} Signals")
    table.add_column("Type", style="cyan", width=12)
    table.add_column("Dir", justify="center", width=4)
    table.add_column("Market", no_wrap=False, width=40)
    table.add_column("Price", justify="right", width=6)
    table.add_column("Misp%", justify="right", width=7)
    table.add_column("Size", justify="right", width=8)
    table.add_column("Days", justify="right", width=5)
    
    for s in signals:
        dir_color = "green" if s.direction == SignalDirection.BUY else "red"
        dir_symbol = "↑ BUY" if s.direction == SignalDirection.BUY else "↓ SELL"
        
        misp_color = "green" if s.mispricing_pct > 0 else "red"
        
        table.add_row(
            s.type.value,
            f"[{dir_color}]{dir_symbol.split()[0]}[/{dir_color}]",
            s.market_question[:38] + "..." if len(s.market_question) > 38 else s.market_question,
            f"{s.current_price:.2f}",
            f"[{misp_color}]{s.mispricing_pct:+.1f}%[/{misp_color}]",
            f"${s.position_size:.0f}",
            str(s.horizon_days) if s.horizon_days else "?"
        )
    
    console.print(table)
    
    # Summary
    buys = sum(1 for s in signals if s.direction == SignalDirection.BUY)
    sells = len(signals) - buys
    total_size = sum(s.position_size for s in signals)
    
    console.print(f"\n[dim]Summary: {buys} buys, {sells} sells | Total size: ${total_size:,.0f}[/dim]")


@app.command()
def summary():
    """Get summary of current market signals."""
    
    generator = SignalGenerator()
    summary = run_async(generator.get_summary())
    
    console.print(f"\n[bold]📈 SIGNAL SUMMARY[/bold]")
    console.print(f"Total signals: {summary.total_signals}")
    console.print(f"  Buy signals: [green]{summary.buy_signals}[/green]")
    console.print(f"  Sell signals: [red]{summary.sell_signals}[/red]")
    console.print(f"  Strong signals: [yellow]{summary.strong_signals}[/yellow]")
    console.print(f"  Total position: ${summary.total_position_size:,.0f}")
    
    if summary.top_signals:
        console.print(f"\n[bold]Top Signals:[/bold]")
        for i, s in enumerate(summary.top_signals, 1):
            dir_str = "[green]BUY[/green]" if s.direction == SignalDirection.BUY else "[red]SELL[/red]"
            console.print(f"  {i}. {dir_str} {s.market_question[:50]}... ({s.mispricing_pct:+.1f}%)")


@app.command()
def analyze(
    market_id: str = typer.Argument(..., help="Market ID or slug to analyze")
):
    """Analyze a specific market for signals."""
    
    generator = SignalGenerator()
    signal = run_async(generator.analyze(market_id))
    
    if not signal:
        console.print(f"[yellow]No signal generated for {market_id}[/yellow]")
        console.print("[dim]Market may not be in optimal horizon range or mispricing below threshold[/dim]")
        return
    
    dir_color = "green" if signal.direction == SignalDirection.BUY else "red"
    
    console.print(f"\n[bold]{signal.type.value.upper()}[/bold]")
    console.print(f"Market: {signal.market_question}")
    console.print(f"Direction: [{dir_color}]{signal.direction.value.upper()}[/{dir_color}]")
    console.print(f"Current price: {signal.current_price:.3f}")
    console.print(f"Fair value estimate: {signal.fair_value_estimate:.3f}")
    console.print(f"Mispricing: [{dir_color}]{signal.mispricing_pct:+.1f}%[/{dir_color}]")
    console.print(f"Days to resolution: {signal.horizon_days}")
    console.print(f"\nRecommended position: ${signal.position_size:.0f}")
    console.print(f"Edge estimate: {signal.edge_estimate*100:.1f}%")
    console.print(f"\nRationale: {signal.rationale}")


if __name__ == "__main__":
    app()
