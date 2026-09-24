import numpy as np
import matplotlib.pyplot as plt

# Defining the Experience Effect Weighting Function

def calculate_weights(age, lambda_param):
    "age: Current age of the trader (or years of trading experience)lambda_param: The decay factor Returns the array of weights for each past year."

    # k represents the age at which the past event occurred (from 1 to current age)

    k_values = np.arange(1, age + 1)
    
    # Calculating the time elapsed since the event

    time_elapsed = age - k_values
    
    numerators = (time_elapsed) ** lambda_param
    denominator = np.sum(numerators)
    
    # Avoiding division by zero for the very first year

    weights = numerators / denominator if denominator != 0 else np.zeros_like(numerators)
    return k_values, weights

# Setup the Parameters

current_age = 60

# Different Lambda values represent different trader psychologies

lambdas = {
    "λ = 0.5 (Long Memory / Slow Decay)": 0.5,
    "λ = 1.5 (Standard Human Baseline)": 1.5,
    "λ = 3.0 (Recency Bias / Fast Decay)": 3.0
}

# Build Graph 2
plt.figure(figsize=(10, 6))

for label, lam in lambdas.items():
    k, w = calculate_weights(current_age, lam)

    # Plotting Age at Event (X) vs Weight of Event (Y)

    plt.plot(k, w, linewidth=2.5, label=label)

#Formatting the Graph

plt.title("Experience Effect Decay\n(How Past Market Shocks Influence Current Biometric Risk Limits)", fontsize=14, fontweight='bold')
plt.xlabel("Age at the Time of the Market Event (Years)", fontsize=12)
plt.ylabel("Weight Applied to Current Risk Tolerance", fontsize=12)

# Highlighting the "Present Day"

plt.axvline(x=current_age, color='red', linestyle='--', alpha=0.5, label="Present Day (Age 60)")

plt.legend(fontsize=10, loc='upper right')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()

# Saving the Graph
output_filename = "../outcomes/graph_2_experience_decay.png"
plt.savefig(output_filename, dpi=300, bbox_inches='tight')
print(f"Graph saved locally as: {output_filename}")

plt.close()