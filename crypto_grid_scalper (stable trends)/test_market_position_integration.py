#!/usr/bin/env python3
"""
Test script to verify market position manager integration
"""

import sys
import json
import subprocess
from pathlib import Path

def test_analyze_ticker_json_output():
    """Test that analyze_ticker outputs valid JSON"""
    print("Testing analyze_ticker JSON output...")
    
    detector_path = Path("../Volatility_Detector_Crypto")
    
    if not detector_path.exists():
        print(f"ERROR: Volatility Detector path not found: {detector_path}")
        return False
    
    try:
        cmd = ['python', '-m', 'src.bot.analyze_ticker', 'BTCUSDT', '--json']
        result = subprocess.run(
            cmd,
            cwd=str(detector_path),
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            print(f"ERROR: Command failed with return code {result.returncode}")
            print(f"STDERR: {result.stderr}")
            return False
        
        # Try to parse JSON
        output = json.loads(result.stdout)
        print(f"✓ JSON output parsed successfully")
        print(f"  Symbol: {output.get('symbol')}")
        print(f"  Trend: {output.get('trend')}")
        print(f"  Momentum: {output.get('momentum')}")
        print(f"  Stoch_K: {output.get('stoch_k')}")
        
        return True
        
    except subprocess.TimeoutExpired:
        print("ERROR: Command timed out")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON: {e}")
        print(f"Output was: {result.stdout}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_market_position_manager_import():
    """Test that market position manager can be imported"""
    print("\nTesting market position manager import...")
    
    try:
        from src.market_position_manager import MarketPositionManager
        print("✓ MarketPositionManager imported successfully")
        return True
    except ImportError as e:
        print(f"ERROR: Failed to import MarketPositionManager: {e}")
        return False

def test_config_loading():
    """Test that config loads new variables"""
    print("\nTesting config loading...")
    
    try:
        from src.config import load_config
        config = load_config()
        
        required_keys = [
            'enableMarketPositionLogic',
            'analysisIntervalMinutes',
            'volatilityDetectorMaxRetries',
            'volatilityDetectorPath'
        ]
        
        for key in required_keys:
            if key not in config:
                print(f"ERROR: Missing config key: {key}")
                return False
            print(f"✓ {key}: {config[key]}")
        
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Market Position Integration Tests")
    print("=" * 60)
    
    tests = [
        test_config_loading,
        test_market_position_manager_import,
        test_analyze_ticker_json_output,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"ERROR in {test.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    sys.exit(0 if all(results) else 1)
