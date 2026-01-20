#!/usr/bin/env python3
"""
Core test: Compare two different core counts
Default: 4 cores vs 8 cores
Usage: python test_cores.py [cores1] [cores2]
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import palloy
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from palloy import PalloySimulator

def main():
    # Parse command line arguments
    cores1 = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    cores2 = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    
    # Create out directory if it doesn't exist
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(exist_ok=True)
    
    print(f"\n=== Simple Core Comparison: {cores1} cores vs {cores2} cores ===\n")
    
    # First configuration
    print(f"\n--- Running with {cores1} cores ---")
    sim1 = PalloySimulator(
        workload_path=str(Path(__file__).parent.parent.parent / "pulp-sdk/applications/MobileNetV1/"),
        num_cluster_cores=cores1,
        debug=True
    )
    metrics1 = sim1.run_full_workflow()
    result_file1 = out_dir / f"results_{cores1}cores.json"
    sim1.save_results(str(result_file1))
    
    # Second configuration
    print(f"\n--- Running with {cores2} cores ---")
    sim2 = PalloySimulator(
        workload_path=str(Path(__file__).parent.parent.parent / "pulp-sdk/applications/MobileNetV1/"),
        num_cluster_cores=cores2,
        debug=True
    )
    metrics2 = sim2.run_full_workflow()
    result_file2 = out_dir / f"results_{cores2}cores.json"
    sim2.save_results(str(result_file2))
    
    # Compare results
    print(f"\n=== Comparison Results ===")
    print(f"{'Metric':<20} {cores1:>12} cores {cores2:>12} cores {'Speedup':>12}")
    print("-" * 72)
    
    if metrics1.get('cycles') and metrics2.get('cycles'):
        cycles1 = metrics1['cycles']
        cycles2 = metrics2['cycles']
        speedup = cycles1 / cycles2 if cycles2 > 0 else 0
        print(f"{'Cycles':<20} {cycles1:>16} {cycles2:>16} {speedup:>12.2f}x")
    
    if metrics1.get('timestamp_ps') and metrics2.get('timestamp_ps'):
        time1 = metrics1['timestamp_ps']
        time2 = metrics2['timestamp_ps']
        speedup = time1 / time2 if time2 > 0 else 0
        print(f"{'Time (ps)':<20} {time1:>16} {time2:>16} {speedup:>12.2f}x")
    
    print(f"\nResults saved to {out_dir}/")

if __name__ == "__main__":
    main()
