#!/usr/bin/env python3
"""
L2 size comparison test: Compare two different L2 sizes
Default: 1024 KB vs 2048 KB
Usage: python test_l2.py [size1_kb] [size2_kb]
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import palloy
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from palloy import PalloySimulator

def main():
    # Parse command line arguments
    l2_size1 = int(sys.argv[1]) if len(sys.argv) > 1 else 1024
    l2_size2 = int(sys.argv[2]) if len(sys.argv) > 2 else 2048
    
    # Create out directory if it doesn't exist
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(exist_ok=True)
    
    # Prepare filter lists for all PEs
    cluster_cores = 8
    trace_filter = [f"pe{core_id}/insn" for core_id in range(cluster_cores)]
    
    print(f"\n=== L2 Size Comparison: {l2_size1} KB vs {l2_size2} KB ===\n")
    
    # First configuration
    print(f"\n--- Running with L2 size {l2_size1} KB ---")
    sim1 = PalloySimulator(
        workload_path=str(Path(__file__).parent.parent.parent / "pulp-sdk/tests/hello/"),
        num_cluster_cores=cluster_cores,
        l2_size_kb=l2_size1,
        l2_num_banks=8,
        trace_filter=trace_filter,
        debug=True
    )
    metrics1 = sim1.run_full_workflow()
    result_file1 = out_dir / f"results_l2_{l2_size1}kb.json"
    sim1.save_results(str(result_file1))
    
    # Second configuration
    print(f"\n--- Running with L2 size {l2_size2} KB ---")
    sim2 = PalloySimulator(
        workload_path=str(Path(__file__).parent.parent.parent / "pulp-sdk/tests/hello/"),
        num_cluster_cores=cluster_cores,
        l2_size_kb=l2_size2,
        l2_num_banks=8,
        trace_filter=trace_filter,
        debug=True
    )
    metrics2 = sim2.run_full_workflow()
    result_file2 = out_dir / f"results_l2_{l2_size2}kb.json"
    sim2.save_results(str(result_file2))
    
    # Compare results
    print(f"\n=== Comparison Results ===")
    print(f"{'Metric':<20} {l2_size1:>10} KB {l2_size2:>10} KB {'Ratio':>12}")
    print("-" * 60)
    
    if metrics1.get('results', {}).get('cycle_delta') and metrics2.get('results', {}).get('cycle_delta'):
        cycles1 = metrics1['results']['cycle_delta']
        cycles2 = metrics2['results']['cycle_delta']
        ratio = cycles1 / cycles2 if cycles2 > 0 else 0
        print(f"{'Cycles':<20} {cycles1:>13} {cycles2:>13} {ratio:>12.2f}x")
    
    if metrics1.get('results', {}).get('time_delta_ps') and metrics2.get('results', {}).get('time_delta_ps'):
        time1 = metrics1['results']['time_delta_ps']
        time2 = metrics2['results']['time_delta_ps']
        ratio = time1 / time2 if time2 > 0 else 0
        print(f"{'Time (ps)':<20} {time1:>13} {time2:>13} {ratio:>12.2f}x")
    
    print(f"\nResults saved to {out_dir}/")

if __name__ == "__main__":
    main()
