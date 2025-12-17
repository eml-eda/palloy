# Palloy

**Palloy** is a Python framework for automating GVSoC simulation workflows. It streamlines the process of building architectures, compiling workloads, running simulations, and extracting performance metrics.

## Features

- 🔧 **Architecture Building**: Automatically rebuild GVSoC targets
- 📦 **Workload Compilation**: Compile applications with configurable parameters
- 🚀 **Simulation Execution**: Run GVSoC simulations seamlessly
- 📊 **Metrics Extraction**: Extract performance metrics (cycles, timestamps) from trace files

## Quick Start

### Basic Usage

```python
from palloy import PalloySimulator

# Initialize the simulator
sim = PalloySimulator(
    workload_path="./pulp-sdk/applications/YourApp/",
    num_cluster_cores=4,
    config="palloy.sh",
    target="palloy"
)

# Run the complete workflow
metrics = sim.run_full_workflow()

# Save results to JSON
sim.save_results("results.json")
```

### Running from Command Line

```bash
# Edit the configuration in palloy.py
python3 palloy.py
```

### Changing Parameters

```python
# Change number of cluster cores
sim.set_params(num_cluster_cores=8)

# Change workload path
sim.set_params(workload_path="./pulp-sdk/applications/AnotherApp/")

# Run again with new parameters
metrics = sim.run_full_workflow()
```

### Individual Steps

You can also run individual steps of the workflow:

```python
# Step 1: Rebuild architecture
sim.rebuild_architecture()

# Step 2: Recompile workload
sim.recompile_workload()

# Step 3: Run simulation
sim.run_simulation()

# Step 4: Extract metrics
metrics = sim.extract_metrics()
```

## Workflow Steps

The `run_full_workflow()` method executes:

1. **Rebuild Architecture**: Builds the GVSoC target with specified configuration
2. **Recompile Workload**: Compiles the application with the specified number of cores
3. **Run Simulation**: Executes the GVSoC simulation
4. **Extract Metrics**: Parses the trace file to extract performance data (cycles, timestamps)

## Output Metrics

The framework extracts the following metrics:

- **cycles**: Number of simulation cycles
- **timestamp_ps**: Simulation timestamp in picoseconds
- **num_cluster_cores**: Number of cluster cores used
- **workload**: Path to the workload/application

Results are returned as a dictionary and can be saved to JSON format.

## Requirements

- Python 3.x
- GVSoC simulator
- PULP SDK
- Virtual environment with GVSoC dependencies

## Setup

Before running the simulator for the first time, create the GVSoC virtual environment:

```bash
./venv.sh
```

This will set up the necessary Python environment with all GVSoC dependencies.

## Configuration

Initialize `PalloySimulator` with:

- `workload_path`: Path to your application directory
- `num_cluster_cores`: Number of cluster cores (default: 4)
- `config`: Config file name in `pulp-sdk/configs/` (default: "palloy.sh")
- `target`: GVSoC target name (default: "palloy")
- `venv_dir`: Virtual environment path (default: "./.venv/")
- `gvsoc_dir`: GVSoC directory path (default: "./gvcuck/")
- `sdk_dir`: PULP SDK directory path (default: "./pulp-sdk/")
- `trace_file`: Trace output file path (default: "./traces.log")
