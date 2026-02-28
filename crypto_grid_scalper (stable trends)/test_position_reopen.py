#!/usr/bin/env python3
"""
Test script to verify position reopening logic
"""

import sys
from decimal import Decimal

def test_position_reopen_manager_import():
    """Test that position reopen manager can be imported"""
    print("Testing position reopen manager import...")
    
    try:
        from src.position_reopen_manager import PositionReopenManager
        print("✓ PositionReopenManager imported successfully")
        return True
    except ImportError as e:
        print(f"ERROR: Failed to import PositionReopenManager: {e}")
        return False

def test_config_reopen_variable():
    """Test that config loads position reopen variable"""
    print("\nTesting config position reopen variable...")
    
    try:
        from src.config import load_config
        config = load_config()
        
        if 'enablePositionReopen' not in config:
            print("ERROR: Missing config key: enablePositionReopen")
            return False
        
        print(f"✓ enablePositionReopen: {config['enablePositionReopen']}")
        return True
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_position_reopen_queue():
    """Test position reopen queue functionality"""
    print("\nTesting position reopen queue...")
    
    try:
        from src.position_reopen_manager import PositionReopenManager
        
        # Create mock config and exchange
        mock_config = {'enablePositionReopen': True}
        mock_exchange = None
        
        manager = PositionReopenManager(mock_config, mock_exchange)
        
        # Test adding position to queue
        manager.add_position_to_reopen(
            grid_level=Decimal('100.50'),
            side='SELL',
            quantity=1.5,
            position_idx='1'
        )
        
        if manager.get_queue_size() != 1:
            print(f"ERROR: Expected queue size 1, got {manager.get_queue_size()}")
            return False
        
        print(f"✓ Position added to queue successfully")
        print(f"✓ Queue size: {manager.get_queue_size()}")
        
        # Test clearing queue
        manager.clear_reopen_queue()
        
        if manager.get_queue_size() != 0:
            print(f"ERROR: Expected queue size 0 after clear, got {manager.get_queue_size()}")
            return False
        
        print(f"✓ Queue cleared successfully")
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_position_side_conversion():
    """Test position index to side conversion"""
    print("\nTesting position index to side conversion...")
    
    try:
        from src.position_reopen_manager import PositionReopenManager
        
        mock_config = {'enablePositionReopen': True}
        manager = PositionReopenManager(mock_config, None)
        
        test_cases = [
            ('0', 'LONG'),
            ('1', 'SHORT'),
            ('2', 'BOTH'),
        ]
        
        for idx, expected_side in test_cases:
            result = manager._get_position_side_from_idx(idx)
            if result != expected_side:
                print(f"ERROR: Index {idx} should map to {expected_side}, got {result}")
                return False
            print(f"✓ Index {idx} → {result}")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Position Reopening Logic Tests")
    print("=" * 60)
    
    tests = [
        test_config_reopen_variable,
        test_position_reopen_manager_import,
        test_position_reopen_queue,
        test_position_side_conversion,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"ERROR in {test.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    sys.exit(0 if all(results) else 1)
