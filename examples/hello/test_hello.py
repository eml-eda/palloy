#!/usr/bin/env python3
"""
Helloworld: simple test to print Hello World using a default configuration
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import palloy
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from palloy import PalloySimulator

def main():
    cores = 8
    
    # Create out directory if it doesn't exist
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(exist_ok=True)
    
    print(f"\n=== Helloworld Test ===\n")
    
    # Run simulation
    sim = PalloySimulator(
        workload_path=str(Path(__file__).parent.parent.parent / "pulp-sdk/tests/hello/"),
        num_cluster_cores=cores,
        debug=True
    )
    metrics = sim.run_full_workflow()
    
    if metrics:
        result_file = out_dir / f"results.json"
        sim.save_results(str(result_file))

    print(f"\nResults saved to {out_dir}/")

if __name__ == "__main__":
    main()
