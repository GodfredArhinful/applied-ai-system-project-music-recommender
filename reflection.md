# Phase 4: Reflection & Experiment Outputs

### Evaluation Comparison

Comparing our Rock vs EDM profiles from our Stress Test:
"Deep Intense Rock" wants Rock songs with Intense mood and 0.85 energy. Because the catalog only has one perfect Rock song ("Storm Runner"), it ranked #1 correctly. However, songs #2 and #3 were randomly filled by "Gym Hero" and "Sunrise City" (both Pop) because they also had high energy (0.93 and 0.82 respectively). 
"Edge Case Sad EDM" wants EDM songs with Sad mood and 0.95 energy. It correctly found our single EDM track ("Neon Pulse"). But yet again, because there are no *sad* EDM tracks with high energy, the secondary results defaulted back to high-energy metal ("Thunder Forge") and pop ("Gym Hero"). 

**Summary:** 
Overall, both profiles definitively prove that the system inherently understands the mathematics behind Energy matching, scaling points appropriately, but perfectly adapting to user constraints completely falls apart when the data catalog is too small! We've also proven that our "Weight-Shift" experiment (halving genre weighting) exacerbates this issue by creating a free-for-all on numeric energy levels instead of textual classifications.
