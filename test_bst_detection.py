#!/usr/bin/env python3
"""
Test script to demonstrate BST/GMT detection
"""

import pytz
from datetime import datetime

def is_bst_active():
    """Check if British Summer Time (BST) is currently active"""
    uk_tz = pytz.timezone('Europe/London')
    uk_time = datetime.now(uk_tz)
    # BST is active when timezone shows 'BST', GMT when it shows 'GMT'
    return uk_time.strftime('%Z') == 'BST'

def test_bst_detection():
    """Test BST detection with current time and examples"""
    uk_tz = pytz.timezone('Europe/London')
    uk_time = datetime.now(uk_tz)
    
    print(f"Current UK time: {uk_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Is BST active: {is_bst_active()}")
    print(f"Timezone abbreviation: {uk_time.strftime('%Z')}")
    print()
    
    # Test with specific dates throughout the year
    test_dates = [
        datetime(2025, 1, 15, 12, 0, 0),   # January - GMT
        datetime(2025, 3, 29, 12, 0, 0),   # Before BST starts
        datetime(2025, 3, 31, 12, 0, 0),   # After BST starts  
        datetime(2025, 7, 15, 12, 0, 0),   # July - BST
        datetime(2025, 10, 25, 12, 0, 0),  # Before BST ends
        datetime(2025, 10, 27, 12, 0, 0),  # After BST ends
        datetime(2025, 12, 15, 12, 0, 0),  # December - GMT
    ]
    
    print("BST/GMT throughout the year:")
    for test_date in test_dates:
        # Convert to UK timezone
        uk_date = uk_tz.localize(test_date)
        tz_name = uk_date.strftime('%Z')
        is_bst = tz_name == 'BST'
        print(f"  {uk_date.strftime('%Y-%m-%d %H:%M:%S %Z')} - BST: {is_bst}")

if __name__ == "__main__":
    test_bst_detection()
