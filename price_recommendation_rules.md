# Price Recommendation Rules

## Overview
The price recommendation engine analyzes historical sales data and applies intelligent pricing strategies based on product seasonality, sales velocity, and stock levels. The system operates in different modes with Steady mode being the default.

## Core Constraints
- **Minimum Price**: Never price below `cost × 1.10` (10% minimum margin)
- **Maximum Price**: Never exceed RRP from skusummary table (when available)
- **Rounding**: All prices rounded to 2 decimal places

## Processing Flow

### Step 1: Review Date Check
- **IF** next review date exists in `groupid_performance` (SHP channel) and is in the future
- **THEN** return `None` (skip processing - no action needed)
- **PURPOSE**: Respects manual review scheduling

### Step 2: Stock Level Check
- **FOR** in-season items: Must have stock > 0 to proceed
- **FOR** out-of-season items: Proceed regardless of stock level
- **PURPOSE**: Out-of-season items need pricing for when stock returns

### Step 3: Sales Velocity Check (In-Season Items Only)
- **IF** no sales in 3+ weeks (21 days) AND item is in-season
- **THEN** apply 5% price reduction (if above minimum price)
- **PURPOSE**: Move slow-moving in-season inventory

### Step 4: Mode-Specific Logic
Proceed to mode-specific pricing logic based on recent sales patterns.

---

## Mode: Ignore
- **Action**: Return `None` immediately
- **Use Case**: Items you don't want the system to recommend prices for

---

## Mode: Steady (Default)
**Objective**: Find the price that maximizes average daily gross profit while experimenting with increases when demand is steady.

### Scenario 1: No Historical Sales Data
- **In-Season Items**: Reduce current price by 2% (minimum price floor applies)
- **Out-of-Season Items**: Maintain current price (no reduction)

### Scenario 2: Out-of-Season Items with No Stock
- **Condition**: Winter/Summer items with no current stock
- **Action**: Set price to **90% of RRP**
- **Purpose**: Position well for next season when stock returns
- **Example**: RRP £90 → Set to £81

### Scenario 3: Out-of-Season Items with Stock but No Sales (30 days)
- **Action**: Increase current price by **10%** (capped by RRP)
- **Purpose**: Move away from clearance prices, prepare for next season
- **Constraint**: Cannot exceed RRP

### Scenario 4: Steady Sales Detected (2+ sales in 30 days)
- **Action**: Experiment with **5% price increase** from current price
- **Logic**: If demand is steady, test higher prices to maximize profit
- **Constraints**: 
  - Must be ≥ minimum price
  - Must be ≤ RRP (if available)
- **Fallback**: If experimental price not viable, use historical best price

### Scenario 5: Insufficient Recent Sales (<2 in 30 days)
- **Action**: Use historical best price (highest average daily gross profit)
- **Logic**: Stick to proven price points when demand is uncertain

---

## Mode: Profit
- **Base**: Calculate Steady mode price first
- **Uplift**: Apply additional **2% increase** to Steady price
- **Purpose**: More aggressive profit maximization
- **Constraints**: Same minimum/maximum rules apply

---

## Mode: Clearance
- **Objective**: Maximize units sold per day (velocity over profit)
- **Logic**: Find price point with highest average daily unit sales
- **Fallback**: If no historical data, reduce current price by 5%
- **Constraints**: Always respect minimum price floor

---

## Seasonal Logic

### Season Detection
- **Source**: `season` field in `skusummary` table
- **Values**: "Winter", "Summer", "Any"
- **Current Season Logic**:
  - Winter items are out-of-season during Apr-Sep
  - Summer items are out-of-season during Oct-Mar
  - "Any" items are always in-season

### Out-of-Season Behavior
1. **Skip automatic reductions** when no sales in 3+ weeks
2. **Allow pricing without stock** (prepare for next season)
3. **More aggressive increases** to escape clearance pricing
4. **Special no-stock rule**: 90% of RRP when no inventory

---

## Key Features

### Experimental Price Increases
- **Trigger**: 2+ sales in last 30 days
- **Increase**: 5% above current price
- **Purpose**: Test market tolerance for higher prices
- **Safety**: Capped by RRP and minimum margin rules

### Historical Data Analysis
- **Source**: `price_track` table
- **Metrics**: Average daily gross profit, units per day
- **Filtering**: Only profitable price points considered
- **Calculation**: `(price - cost) × average_daily_units`

### RRP Integration
- **Source**: `rrp` field in `skusummary` (varchar, converted to numeric)
- **Usage**: Hard ceiling for all price recommendations
- **Validation**: Invalid RRP values are ignored with warning

### Stock-Aware Pricing
- **In-Season**: Requires stock to adjust prices
- **Out-of-Season**: Prices set regardless of stock level
- **Logic**: Out-of-season items need positioning for future stock arrivals

---

## Examples

### Example 1: In-Season Item with Steady Sales
- **Item**: Summer sandals in July
- **Current Price**: £38.25
- **Recent Sales**: 3 in last 30 days
- **Action**: 5% increase to £40.16
- **Reasoning**: Test higher price with steady demand

### Example 2: Out-of-Season Item with No Stock
- **Item**: Winter boots in summer
- **Current Price**: £59.40 (clearance price)
- **Stock**: 0 units
- **RRP**: £90.00
- **Action**: Set to £81.00 (90% of RRP)
- **Reasoning**: Position for winter season return

### Example 3: Out-of-Season Item with Stock, No Sales
- **Item**: Winter boots with stock in summer
- **Current Price**: £52.21
- **Recent Sales**: 0 in last 30 days
- **Action**: 10% increase to £57.43
- **Reasoning**: Escape summer clearance pricing

### Example 4: In-Season Item, No Recent Sales
- **Item**: Summer item with no sales in 3+ weeks
- **Current Price**: £45.00
- **Action**: 5% reduction to £42.75
- **Reasoning**: Stimulate demand for slow-moving inventory

---

## Database Dependencies
- **skusummary**: cost, shopifyprice, season, rrp
- **price_track**: Historical price and sales data
- **sales**: Recent sales velocity analysis
- **localstock**: Current inventory levels
- **groupid_performance**: Review date scheduling (SHP channel)

---

## Last Updated
2025-07-15 - Added out-of-season no-stock rule (90% of RRP)
