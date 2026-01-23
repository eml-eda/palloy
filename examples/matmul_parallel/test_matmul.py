#!/usr/bin/env python3
"""
Matrix Multiplication Parallel Test: Compare different core counts
Shows how parallelization scales with more cores
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import palloy
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from palloy import PalloySimulator

def main():
    # Test with different core counts
    core_configs = [2, 4, 8, 16]
    
    # Create out directory if it doesn't exist
    out_dir = Path(__file__).parent / "out"
    out_dir.mkdir(exist_ok=True)
    
    print(f"\n=== Parallel Matrix Multiplication Scaling Test ===\n")
    print(f"Testing configurations: {core_configs} cores\n")
    
    results = {}
    
    for cores in core_configs:
        print(f"\n{'='*60}")
        print(f"Running with {cores} core(s)")
        print(f"{'='*60}")
        
        # Prepare filter for all cores
        trace_filter = [f"pe{core_id}/insn" for core_id in range(cores)]
        
        sim = PalloySimulator(
            workload_path=str(Path(__file__).parent.parent.parent / "pulp-sdk/tests/cluster/matmul_parallel/"),
            num_cluster_cores=cores,
            trace_filter=trace_filter,
            debug=True
        )
        
        metrics = sim.run_full_workflow()
        results[cores] = metrics
        
        result_file = out_dir / f"results_{cores}cores.json"
        sim.save_results(str(result_file))
    
    # Print comparison table
    print(f"\n{'='*80}")
    print(f"SCALING ANALYSIS")
    print(f"{'='*80}")
    print(f"{'Cores':<10} {'Cycles':<15} {'Time (ps)':<15} {'Speedup':<12} {'Efficiency':<12}")
    print("-" * 80)
    
    # Get baseline from minimum core count (first in sorted list)
    min_cores = min(core_configs)
    baseline_metrics = results[min_cores]
    baseline_cycles = baseline_metrics.get('results', {}).get('cycle_delta')
    baseline_time = baseline_metrics.get('results', {}).get('time_delta_ps')
    
    for cores in sorted(core_configs):
        metrics = results[cores]
        cycles = metrics.get('results', {}).get('cycle_delta')
        time_ps = metrics.get('results', {}).get('time_delta_ps')
        
        if cycles and time_ps and baseline_cycles:
            speedup = baseline_cycles / cycles if cycles > 0 else 0
            # Efficiency relative to baseline: speedup / (cores / min_cores)
            efficiency = (speedup / (cores / min_cores)) * 100
            
            print(f"{cores:<10} {cycles:<15} {time_ps:<15} {speedup:<12.2f}x {efficiency:<12.1f}%")
    
    print(f"\n{'='*80}")
    print(f"Results saved to {out_dir}/")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()
