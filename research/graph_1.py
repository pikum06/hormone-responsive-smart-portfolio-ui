import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Loading the Datasets

logs_df = pd.read_csv("../data/hormone_transaction_logs.csv")
backtest_df = pd.read_csv("../data/final_backtest_results.csv")

#Extracting only what we need from the backtest to prevent duplicate columns

market_data = backtest_df[['BTC_Rolling_Vol_30d', 'market_panic']]

# Merging using the 'index' from Solana logs to align with the backtest rows

merged_df = pd.merge(logs_df, market_data, left_on='index', right_index=True, how='inner')

# Defining Trading Parameters for Simulation

# Base portfolio size ($10,000)

POSITION_SIZE = 10000  

# Normal leverage without biological intervention

STANDARD_LEVERAGE = 10.0  

# Simulating a sudden 5% market drop during panic

MARKET_DROP = 0.05      
    
# Calculating the Metrics

# X-Axis: Market Volatility (Using your exact column name)

volatility = merged_df['BTC_Rolling_Vol_30d'] 

# Y-Axis: Stress Level

# Max leverage (10) = 0 Stress. Lower leverage cap = High Stress.

merged_df['Stress_Level'] = STANDARD_LEVERAGE - merged_df['leverage_cap']

# Z-Axis: Avoided Loss 

# Standard loss vs Capped loss during the simulated 5% market drop

standard_loss = POSITION_SIZE * STANDARD_LEVERAGE * MARKET_DROP
capped_loss = POSITION_SIZE * merged_df['leverage_cap'] * MARKET_DROP
merged_df['Avoided_Loss'] = standard_loss - capped_loss

# 3D Scatter Plot

fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')

# Plotting the points
scatter = ax.scatter(
    merged_df['BTC_Rolling_Vol_30d'], 
    merged_df['Stress_Level'], 
    merged_df['Avoided_Loss'],
    c=merged_df['Avoided_Loss'], 
    cmap='coolwarm', 
    s=100,
    edgecolor='k',
    alpha=0.8
)

# Formatting the Graph

ax.set_title(' Bio-Responsive Circuit Breaker Efficiency', fontsize=14, fontweight='bold')
ax.set_xlabel('\nMarket Volatility (30d Rolling)', fontsize=10)
ax.set_ylabel('\nPhysiological Stress Level', fontsize=10)
ax.set_zlabel('\nAvoided Loss ($)', fontsize=10)

# Adding a color bar legend for the Avoided Loss
cbar = plt.colorbar(scatter, ax=ax, pad=0.1, shrink=0.7)
cbar.set_label('Capital Saved ($)')

# Optimizing viewing angle

ax.view_init(elev=20, azim=45)
plt.tight_layout()

# Saving to file
output_filename = "../outcomes/graph_1_avoided_loss.png"
plt.savefig(output_filename, dpi=300, bbox_inches='tight')
print(f"Graph saved as: {output_filename}")

plt.close()