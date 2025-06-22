#!/usr/bin/env python3
"""
Price Drop Automation Configuration
Centralized configuration for all price drop scripts
"""

# === SAFETY CONFIGURATION ===
# Master switch - must be True to enable any automation
ENABLE_PRICE_DROPS = False

# Individual bucket automation switches
ENABLE_BUCKET_1_AUTO = False  # Dead stock (180+ days, stock >= 10)
ENABLE_BUCKET_2_AUTO = False  # Market mismatch (overpriced vs lowbench)
ENABLE_BUCKET_3_AUTO = False  # Stock heavy (no benchmark, high stock)
ENABLE_BUCKET_4_AUTO = False  # Low margin (< £15 profit)
ENABLE_BUCKET_5_AUTO = False  # Slow mover (moderate stock, stale)

# === OPERATIONAL LIMITS ===
MAX_DAILY_CHANGES = 50        # Maximum price changes per day
MIN_PRICE_CHANGE = 0.01       # Minimum price change to apply (£)
SAFETY_DELAY_DAYS = 10        # Delay for non-urgent buckets
RECENT_CHANGE_COOLDOWN = 7    # Days to wait after recent price change

# === BUCKET CONFIGURATION ===
BUCKET_CONFIG = {
    1: {
        "name": "Dead Stock",
        "description": "180+ days no sales, stock >= 10",
        "priority": "HIGH",
        "auto_enabled_var": "ENABLE_BUCKET_1_AUTO",
        "typical_reduction": "35%",
        "safety_floor": "cost + £1"
    },
    2: {
        "name": "Market Mismatch", 
        "description": "Price >= 110% of lowbench, 30+ days stale",
        "priority": "HIGH",
        "auto_enabled_var": "ENABLE_BUCKET_2_AUTO",
        "typical_reduction": "Set to 98% of lowbench",
        "safety_floor": "cost"
    },
    3: {
        "name": "Stock Heavy",
        "description": "No lowbench, stock >= 15, 30-179 days stale", 
        "priority": "MEDIUM",
        "auto_enabled_var": "ENABLE_BUCKET_3_AUTO",
        "typical_reduction": "25%",
        "safety_floor": "cost"
    },
    4: {
        "name": "Low Margin",
        "description": "Margin < £15, 30+ days stale",
        "priority": "MEDIUM", 
        "auto_enabled_var": "ENABLE_BUCKET_4_AUTO",
        "typical_reduction": "Set to cost + £0.01",
        "safety_floor": "cost + £0.01"
    },
    5: {
        "name": "Slow Mover",
        "description": "Stock 5-14, 60+ days stale, margin >= £15",
        "priority": "LOW",
        "auto_enabled_var": "ENABLE_BUCKET_5_AUTO", 
        "typical_reduction": "15% or lowbench",
        "safety_floor": "cost"
    },
    6: {
        "name": "Low Stock/Recent",
        "description": "Stock <= 4 OR sold within 30 days",
        "priority": "NONE",
        "auto_enabled_var": None,
        "typical_reduction": "No change",
        "safety_floor": "N/A"
    },
    7: {
        "name": "Early Warning", 
        "description": "Stock >= 15, stale 30-59 days, fairly priced",
        "priority": "LOW",
        "auto_enabled_var": None,
        "typical_reduction": "10%",
        "safety_floor": "cost"
    }
}

# === PRIORITY GROUPINGS ===
HIGH_PRIORITY_BUCKETS = [1, 2]      # Immediate attention required
MEDIUM_PRIORITY_BUCKETS = [3, 4]    # Review within 24-48 hours  
LOW_PRIORITY_BUCKETS = [5, 7]       # Monitor and consider
AUTOMATION_ELIGIBLE_BUCKETS = [1, 2, 3, 4, 5]  # Buckets that can be automated

# === REPORTING CONFIGURATION ===
DAILY_REPORT_BUCKETS = [1, 2, 3]    # Buckets to highlight in daily reports
MAX_ITEMS_PER_BUCKET_REPORT = 10    # Max items to show per bucket in detailed reports

# === API CONFIGURATION ===
SHOPIFY_API_RATE_LIMIT_DELAY = 0.5  # Seconds between API calls
SHOPIFY_API_TIMEOUT = 30             # Request timeout in seconds

# === LOGGING CONFIGURATION ===
LOG_RETENTION_DAYS = 7               # Days to keep log files
LOG_LEVEL = "INFO"                   # DEBUG, INFO, WARNING, ERROR

# === EMAIL CONFIGURATION (Future) ===
EMAIL_ENABLED = False
EMAIL_RECIPIENTS = []
EMAIL_SUBJECT_PREFIX = "[Brookfield] Price Drop Alert"

def get_enabled_buckets():
    """Return list of buckets enabled for automation"""
    enabled = []
    if ENABLE_PRICE_DROPS:
        if ENABLE_BUCKET_1_AUTO:
            enabled.append(1)
        if ENABLE_BUCKET_2_AUTO:
            enabled.append(2)
        if ENABLE_BUCKET_3_AUTO:
            enabled.append(3)
        if ENABLE_BUCKET_4_AUTO:
            enabled.append(4)
        if ENABLE_BUCKET_5_AUTO:
            enabled.append(5)
    return enabled

def is_bucket_enabled(bucket_number):
    """Check if a specific bucket is enabled for automation"""
    if not ENABLE_PRICE_DROPS:
        return False
    
    bucket_map = {
        1: ENABLE_BUCKET_1_AUTO,
        2: ENABLE_BUCKET_2_AUTO, 
        3: ENABLE_BUCKET_3_AUTO,
        4: ENABLE_BUCKET_4_AUTO,
        5: ENABLE_BUCKET_5_AUTO
    }
    
    return bucket_map.get(bucket_number, False)

def get_bucket_info(bucket_number):
    """Get configuration info for a bucket"""
    return BUCKET_CONFIG.get(bucket_number, {})

def print_configuration():
    """Print current configuration for review"""
    print("PRICE DROP AUTOMATION CONFIGURATION")
    print("=" * 50)
    print(f"Master Switch (ENABLE_PRICE_DROPS): {ENABLE_PRICE_DROPS}")
    print(f"Max Daily Changes: {MAX_DAILY_CHANGES}")
    print(f"Min Price Change: £{MIN_PRICE_CHANGE}")
    print(f"Recent Change Cooldown: {RECENT_CHANGE_COOLDOWN} days")
    print()
    
    print("BUCKET AUTOMATION STATUS:")
    print("-" * 30)
    for bucket_num in sorted(BUCKET_CONFIG.keys()):
        config = BUCKET_CONFIG[bucket_num]
        enabled = is_bucket_enabled(bucket_num)
        status = "ENABLED" if enabled else "DISABLED"
        print(f"Bucket {bucket_num} ({config['name']}): {status}")
    print()
    
    enabled_buckets = get_enabled_buckets()
    if enabled_buckets:
        print(f"Currently enabled buckets: {enabled_buckets}")
    else:
        print("No buckets currently enabled for automation")

if __name__ == "__main__":
    print_configuration()
