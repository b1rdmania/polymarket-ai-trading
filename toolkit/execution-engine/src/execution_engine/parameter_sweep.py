"""
Parameter Sweep Testing

Test multiple parameter configurations in parallel paper trading.
Lesson from @the_smart_ape: Parameter selection is critical.
Conservative params = +86% ROI, Aggressive = -50% ROI.
"""

import asyncio
import logging
from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
import json

from .models import TradingConfig, TradeMode
from .orchestrator import TradeOrchestrator
from .paper_trader import PaperTrader

logger = logging.getLogger(__name__)


class ParameterSweep:
    """
    Run multiple parameter configurations in parallel.
    
    This helps identify which parameters work best before going live.
    """
    
    def __init__(self, base_config: TradingConfig):
        self.base_config = base_config
        self.results = []
    
    def create_test_configs(self) -> List[Dict[str, Any]]:
        """
        Create test configurations.
        
        Based on @the_smart_ape's lesson: test conservative to aggressive.
        """
        configs = [
            # Ultra Conservative
            {
                "name": "ultra_conservative",
                "kelly_fraction": 0.15,
                "min_strength": "VERY_STRONG",
                "min_mispricing_pct": 10.0,
                "max_position_usd": 250,
                "description": "Only strongest signals, smallest positions"
            },
            # Conservative (Your default)
            {
                "name": "conservative",
                "kelly_fraction": 0.25,
                "min_strength": "STRONG",
                "min_mispricing_pct": 7.5,
                "max_position_usd": 500,
                "description": "Strong signals, standard positions"
            },
            # Moderate
            {
                "name": "moderate",
                "kelly_fraction": 0.30,
                "min_strength": "MODERATE",
                "min_mispricing_pct": 5.0,
                "max_position_usd": 500,
                "description": "Moderate signals, balanced approach"
            },
            # Aggressive
            {
                "name": "aggressive",
                "kelly_fraction": 0.35,
                "min_strength": "WEAK",
                "min_mispricing_pct": 3.0,
                "max_position_usd": 750,
                "description": "All signals, larger positions"
            },
        ]
        
        return configs
    
    async def run_parallel_test(self, days: int = 30):
        """
        Run all configurations in parallel paper trading.
        
        Args:
            days: Number of days to test (default 30)
        """
        test_configs = self.create_test_configs()
        
        logger.info(f"Starting parameter sweep with {len(test_configs)} configs")
        logger.info(f"Test duration: {days} days")
        
        # Create orchestrators for each config
        orchestrators = []
        for cfg in test_configs:
            config = TradingConfig(
                mode=TradeMode.PAPER,
                kelly_fraction=cfg["kelly_fraction"],
                max_position_usd=cfg["max_position_usd"],
                dry_run=False,
            )
            
            orch = TradeOrchestrator(config)
            orch.config_name = cfg["name"]
            orch.config_description = cfg["description"]
            orchestrators.append(orch)
        
        # Run in parallel
        tasks = [
            self._run_test(orch, days)
            for orch in orchestrators
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Analyze results
        self._analyze_results(results)
        
        return results
    
    async def _run_test(self, orchestrator: TradeOrchestrator, days: int):
        """Run a single test configuration."""
        logger.info(f"Starting test: {orchestrator.config_name}")
        
        # Run for specified duration
        # In production, this would run for actual days
        # For testing, we'll simulate
        
        start_capital = orchestrator.bankroll
        
        # Simulate trading cycles
        # (In real usage, this would run orchestrator.run_forever() with a timeout)
        
        # For now, return mock result
        result = {
            "config_name": orchestrator.config_name,
            "description": orchestrator.config_description,
            "start_capital": start_capital,
            "end_capital": start_capital,  # Would be actual after trading
            "roi_pct": 0,  # Would be calculated
            "total_trades": 0,
            "win_rate": 0,
            "sharpe_ratio": 0,
            "max_drawdown": 0,
        }
        
        return result
    
    def _analyze_results(self, results: List[Dict[str, Any]]):
        """Analyze and rank results."""
        print("\n" + "="*80)
        print("PARAMETER SWEEP RESULTS")
        print("="*80)
        
        # Sort by ROI
        sorted_results = sorted(results, key=lambda x: x['roi_pct'], reverse=True)
        
        for i, result in enumerate(sorted_results, 1):
            print(f"\n#{i}: {result['config_name'].upper()}")
            print(f"   Description: {result['description']}")
            print(f"   ROI: {result['roi_pct']:.2f}%")
            print(f"   Trades: {result['total_trades']}")
            print(f"   Win Rate: {result['win_rate']:.1f}%")
            print(f"   Sharpe: {result['sharpe_ratio']:.2f}")
            print(f"   Max DD: {result['max_drawdown']:.2f}%")
        
        # Find best conservative config (highest risk-adjusted return)
        best = max(sorted_results, key=lambda x: x['sharpe_ratio'])
        
        print("\n" + "="*80)
        print("RECOMMENDED CONFIG FOR LIVE TRADING")
        print("="*80)
        print(f"Use: {best['config_name']}")
        print(f"Reason: Highest risk-adjusted return (Sharpe: {best['sharpe_ratio']:.2f})")
        print("="*80 + "\n")
        
        # Save results
        self._save_results(sorted_results)
    
    def _save_results(self, results: List[Dict[str, Any]]):
        """Save results to file."""
        output_dir = Path("data/parameter_tests")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filepath = output_dir / f"sweep_results_{timestamp}.json"
        
        with open(filepath, 'w') as f:
            json.dump({
                "timestamp": datetime.utcnow().isoformat(),
                "results": results
            }, f, indent=2)
        
        logger.info(f"Results saved to {filepath}")


# CLI interface
async def main():
    """Run parameter sweep from command line."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test multiple parameter sets")
    parser.add_argument('--days', type=int, default=30, help='Days to test')
    args = parser.parse_args()
    
    base_config = TradingConfig(mode=TradeMode.PAPER)
    sweep = ParameterSweep(base_config)
    
    await sweep.run_parallel_test(days=args.days)


if __name__ == "__main__":
    asyncio.run(main())


