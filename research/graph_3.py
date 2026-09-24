import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#Loading the Datasets

backtest_df = pd.read_csv("../data/final_backtest_results.csv")
logs_df = pd.read_csv("../data/hormone_transaction_logs.csv")

#Merging Data on Index

market_data = backtest_df[['market_panic']]
merged_df = pd.merge(logs_df, market_data, left_on='index', right_index=True, how='inner')

#Simulating Parameters

# $10,000 Starting Portfolio

INITIAL_CAPITAL = 10000  

# Baseline Leverage

STANDARD_LEVERAGE = 10.0      

# 0.1% cost for every 1x change in leverage

SLIPPAGE_RATE = 0.001         

#Simulating Market Returns

# Keep the random walk consistent

np.random.seed(50)

# Base random market noise

base_returns = np.random.normal(0.002, 0.015, len(merged_df))

# When 'market_panic' is high, force a severe market drop

panic_penalty = merged_df['market_panic'] * 0.05 
merged_df['market_return'] = base_returns - panic_penalty

#Calculating Standard Portfolio (No Bio-Limits) Always uses 10x leverage, taking full damage during panic. No slippage.

merged_df['standard_return'] = merged_df['market_return'] * STANDARD_LEVERAGE
merged_df['standard_portfolio'] = INITIAL_CAPITAL * (1 + merged_df['standard_return']).cumprod()

# Calculate Hormone-Responsive Portfolio

# Uses dynamic leverage cap

merged_df['hormone_return'] = merged_df['market_return'] * merged_df['leverage_cap']

# Calculating Slippage Cost (The penalty for the circuit breaker firing)

leverage_change = merged_df['leverage_cap'].diff().fillna(0).abs()
merged_df['slippage_cost_pct'] = leverage_change * SLIPPAGE_RATE

# Net Hormone Return = Market Return - Slippage

merged_df['net_hormone_return'] = merged_df['hormone_return'] - merged_df['slippage_cost_pct']
merged_df['hormone_portfolio'] = INITIAL_CAPITAL * (1 + merged_df['net_hormone_return']).cumprod()

# Building the Graph
plt.figure(figsize=(12, 6))

plt.plot(merged_df.index, merged_df['standard_portfolio'], label="Standard 10x Portfolio (No Biological Limits)", color='blue', linestyle='--', linewidth=2)
plt.plot(merged_df.index, merged_df['hormone_portfolio'], label="Hormone-Responsive Portfolio (Net of Slippage)", color='orange', linewidth=3)

# Title and Labels
plt.title('Slippage-Adjusted Yield Comparison\n(Does avoiding crashes pay for the frequent rebalancing?)', fontsize=14, fontweight='bold')
plt.xlabel('Backtest Timeline (Simulated Periods)', fontsize=12)
plt.ylabel('Portfolio Value ($)', fontsize=12)

# Highlighting key moments where the Bio-Circuit Breaker fired aggressively
major_interventions = merged_df[leverage_change > 5]
if not major_interventions.empty:
    plt.scatter(major_interventions.index, major_interventions['hormone_portfolio'], color='red', s=80, zorder=5, label='Major Bio-Circuit Breaker Fired')

plt.legend(fontsize=10, loc='upper right')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

# Saving the Graph
output_filename = "../outcomes/graph_3_slippage_yield.png"
plt.savefig(output_filename, dpi=300, bbox_inches='tight')
print(f"Graph saved as: {output_filename}")

plt.close()