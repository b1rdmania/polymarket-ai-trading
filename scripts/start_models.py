#!/usr/bin/env python3
"""
Multi-Model Paper Trading Launcher

Runs 3 different trading models simultaneously:
1. Conservative - High conviction only
2. Moderate - Balanced approach
3. Aggressive - High frequency

Each model:
- Runs in separate process
- Logs to separate database
- Records to separate directory
- Can be monitored independently
"""

import subprocess
import sys
import time
import signal
from pathlib import Path
import yaml
from datetime import datetime

MODELS = ['conservative', 'moderate', 'aggressive']
BASE_DIR = Path(__file__).parent.parent
PIDS_FILE = BASE_DIR / 'data' / 'model_pids.txt'


def load_model_config(model_name: str) -> dict:
    """Load configuration for a specific model."""
    config_path = BASE_DIR / 'config' / 'models.yaml'
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    model_config = config['models'][model_name]
    shared_config = config['shared']
    
    # Merge model-specific with shared
    return {
        'model_name': model_name,
        'model_config': model_config,
        'shared_config': shared_config
    }


def create_model_config_file(model_name: str) -> Path:
    """Create a temporary config file for this model."""
    config = load_model_config(model_name)
    
    # Create model-specific config
    model_config_data = {
        'trading': {
            'mode': 'paper',
            'model_name': model_name,
        },
        'risk': config['model_config']['risk'],
        'signals': config['model_config']['signals'],
        'execution': config['model_config']['execution'],
        'logging': config['shared_config']['logging'],
        'recording': config['shared_config']['recording'],
        'alerts': config['shared_config']['alerts'],
        
        # Model-specific data paths
        'data': {
            'db_path': f'data/trades_{model_name}.db',
            'recordings_dir': f'data/recordings_{model_name}',
            'logs_dir': f'logs/{model_name}',
        }
    }
    
    # Write to temp config file
    config_path = BASE_DIR / 'config' / f'active_{model_name}.yaml'
    with open(config_path, 'w') as f:
        yaml.dump(model_config_data, f, default_flow_style=False)
    
    return config_path


def start_model(model_name: str) -> subprocess.Popen:
    """Start a paper trading model."""
    
    print(f"\n{'='*60}")
    print(f"Starting Model: {model_name.upper()}")
    print('='*60)
    
    # Create config file
    config_path = create_model_config_file(model_name)
    print(f"✅ Config: {config_path}")
    
    # Create data directories
    data_dir = BASE_DIR / 'data' / f'recordings_{model_name}'
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Data dir: {data_dir}")
    
    # Create logs directory
    log_dir = BASE_DIR / 'logs' / model_name
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f'{model_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    print(f"✅ Log file: {log_file}")
    
    # Start the model
    cmd = [
        sys.executable,
        str(BASE_DIR / 'agents' / 'systematic_trader.py'),
        '--mode', 'paper',
        '--config', str(config_path),
        '--model', model_name
    ]
    
    print(f"✅ Command: {' '.join(cmd)}")
    
    with open(log_file, 'w') as f:
        process = subprocess.Popen(
            cmd,
            stdout=f,
            stderr=subprocess.STDOUT,
            cwd=BASE_DIR
        )
    
    print(f"✅ Started with PID: {process.pid}")
    
    return process


def save_pids(processes: dict):
    """Save process IDs to file."""
    PIDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(PIDS_FILE, 'w') as f:
        f.write(f"# Model Paper Trading PIDs\n")
        f.write(f"# Started: {datetime.now()}\n\n")
        for model, process in processes.items():
            f.write(f"{model}:{process.pid}\n")
    
    print(f"\n✅ PIDs saved to: {PIDS_FILE}")


def start_all_models():
    """Start all models in parallel."""
    
    print("="*60)
    print("MULTI-MODEL PAPER TRADING LAUNCHER")
    print("="*60)
    print(f"\nStarting {len(MODELS)} models in parallel...")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    processes = {}
    
    for model in MODELS:
        try:
            process = start_model(model)
            processes[model] = process
            time.sleep(2)  # Small delay between starts
        except Exception as e:
            print(f"❌ Failed to start {model}: {e}")
    
    if not processes:
        print("\n❌ No models started successfully")
        return
    
    # Save PIDs
    save_pids(processes)
    
    # Show status
    print(f"\n{'='*60}")
    print("ALL MODELS STARTED")
    print('='*60)
    print(f"\nRunning models: {len(processes)}/{len(MODELS)}")
    
    for model, process in processes.items():
        config = load_model_config(model)
        print(f"\n{model.upper()}:")
        print(f"  PID: {process.pid}")
        print(f"  Name: {config['model_config']['name']}")
        print(f"  Check interval: {config['model_config']['execution']['check_interval_seconds']}s")
        print(f"  Max position: ${config['model_config']['risk']['max_position_usd']}")
        print(f"  Kelly fraction: {config['model_config']['risk']['kelly_fraction']}")
        print(f"  Min signal: {config['model_config']['signals']['mean_reversion']['min_strength']}")
    
    print(f"\n{'='*60}")
    print("MONITORING")
    print('='*60)
    print(f"\nTo monitor results:")
    print(f"  python3 scripts/monitor_models.py")
    print(f"\nTo stop all models:")
    print(f"  python3 scripts/stop_models.py")
    print(f"\nLog files:")
    for model in processes.keys():
        print(f"  logs/{model}/")
    
    print(f"\nDatabases:")
    for model in processes.keys():
        print(f"  data/trades_{model}.db")
    
    print(f"\n{'='*60}")
    print("✅ All models running!")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*60)
    print()


def main():
    """Main entry point."""
    
    # Check if already running
    if PIDS_FILE.exists():
        print(f"⚠️  Found existing PID file: {PIDS_FILE}")
        print("Models may already be running.")
        response = input("Stop existing and restart? (y/N): ")
        
        if response.lower() == 'y':
            print("Stopping existing models...")
            subprocess.run([sys.executable, str(BASE_DIR / 'scripts' / 'stop_models.py')])
            time.sleep(2)
        else:
            print("Exiting. Use stop_models.py to stop existing models first.")
            return
    
    # Start all models
    start_all_models()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        print("Models are still running in background.")
        print("Use: python3 scripts/stop_models.py")


