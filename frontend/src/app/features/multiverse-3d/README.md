# Multiverse 3D Module — Mirror Future

Interactive Three.js WebGL 3D visualization and stochastic Monte Carlo trajectory charts.

## Overview

The **Multiverse 3D** module renders 180-day life projection trajectories calculated by the Mirror Future causal engine:
- **`DrJefCausalGraph3dComponent`**: Interactive Three.js WebGL scene presenting the central agent node, radial social contact network, and three stochastic percentile trajectory branches (P10 Risk, P50 Probable, and P90 Optimal).
- **`MonteCarloChartComponent`**: High-performance SVG visualization displaying confidence bands, inflection points (Day 48 fatigue inflection and Day 120 completion milestones), critical thresholds, and 4D quad-view trajectory analytics.

## Key Features

1. **Stochastic Trajectory Branches:**
   - **P90 (Optimal Scenario - Gold/Amber):** Maximum progress and milestone attainment under recommended daily caps and restorative sleep.
   - **P50 (Probable Scenario - Blue):** Baseline progress following observed habits.
   - **P10 (Risk Scenario - Red):** Severe exhaustion and burnout risk under persistent sleep deficit.
2. **Radial Social Network:**
   - Visualizes contact distances proportional to response latency.
   - Color-coded emotional reaction classifications.
3. **Interactive 180-Day Scrubber:**
   - Scrub through time to inspect exact metric values on any given day.
4. **Causal Prescription Integration:**
   - Displays inverse engineering recommendations powered by Meta Llama 3.3 (70B) and NumPy.
