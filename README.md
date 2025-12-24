# 🏐 Palloy

**Palloy** (PULP-Alloy) is a Python framework for automating PULP GVSoC simulation workflows. It streamlines the process of building custom architectures, compiling workloads, running simulations, and finally extracting performance metrics.

## Quick Start

### Basic Usage

```python
from palloy import PalloySimulator

# Initialize the simulator with default configuration
sim = PalloySimulator(
    config="palloy.sh",
    target="palloy"
)

# Run the complete workflow (uses palloy_config.json parameters)
metrics = sim.run_full_workflow()

# Save results to JSON
sim.save_results("results.json")
```

### Using Configuration File

Palloy automatically loads parameters from `palloy_config.json` if it exists:

```json
{
    "num_cluster_cores": 8,
    "l1_size_kb": 64,
    "l2_size_kb": 1600,
    "l2_num_banks": 4,
    "workload_path": "./pulp-sdk/tests/hello/"
}
```

You can also override parameters when creating the simulator:

```python
sim = PalloySimulator(
    workload_path="./pulp-sdk/applications/YourApp/",
    num_cluster_cores=4,
    l1_size_kb=128,
    l2_size_kb=2048,
    l2_num_banks=8
)
```

### Running from Command Line

```bash
# Edit the configuration in palloy_config.json or palloy.py
python3 palloy.py
```

## Configuration Management

### Configuration File (palloy_config.json)

Palloy uses a JSON configuration file to manage simulation parameters. The configuration is automatically loaded on initialization:

**Default Parameters:**
- `num_cluster_cores`: Number of cluster cores (default: 8)
- `l1_size_kb`: L1 cache size in KB (default: 64)
- `l2_size_kb`: L2 memory size in KB (default: 1600)
- `l2_num_banks`: Number of L2 memory banks (default: 4)
- `workload_path`: Path to the application (default: "./pulp-sdk/tests/hello/")

### Updating Architecture Configuration

The `set_params()` method automatically updates the GVSoC architecture configuration files:

```python
# Updates cluster.json and soc.json with current parameters
sim.set_params()
```

This method:
- Updates `cluster.new.json` with core count and L1 size
- Updates `soc.new.json` with L2 size and bank configuration
- Reads from baseline files (`cluster.json`, `soc.json`)
- Automatically called during `run_full_workflow()`

### Viewing Current Configuration

```python
# Print current configuration
sim.palloy_config.print_config()
```
```

## Workflow Steps

### Complete Workflow

The `run_full_workflow()` method executes all steps automatically:

```python
metrics = sim.run_full_workflow()
```

This performs:
1. **Update Configuration**: Apply parameters to architecture config files
2. **Rebuild Architecture**: Build the GVSoC target with specified configuration
3. **Recompile Workload**: Compile the application with the specified parameters
4. **Run Simulation**: Execute the GVSoC simulation
5. **Extract Metrics**: Parse the trace file to extract performance data

### Individual Steps

You can also run individual steps of the workflow:

```python
# Step 0: Update configuration files
sim.set_params()

# Step 1: Rebuild architecture
sim.rebuild_architecture()

# Step 2: Recompile workload
sim.recompile_workload()

# Step 3: Run simulation
sim.run_simulation()

# Step 4: Extract metrics
metrics = sim.extract_metrics()
```



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
- VENV virtual environment with GVSoC dependencies

## Setup

Before running the simulator for the first time, create the GVSoC virtual environment:

```bash
./venv.sh
```

This will set up the necessary Python environment with all GVSoC dependencies.

## Advanced Configuration

### PalloySimulator Parameters

Initialize `PalloySimulator` with the following parameters (all optional, will use values from `palloy_config.json` if not provided):

**Core Parameters:**
- `workload_path`: Path to your application directory
- `num_cluster_cores`: Number of cluster cores (default from config: 8)
- `l1_size_kb`: L1 cache size in KB (default from config: 64)
- `l2_size_kb`: L2 memory size in KB (default from config: 1600)
- `l2_num_banks`: Number of L2 banks (default from config: 4)

**Build & Environment:**
- `config`: Config file name in `pulp-sdk/configs/` (default: "palloy.sh")
- `target`: GVSoC target name (default: "palloy")
- `venv_dir`: Virtual environment path (default: "./.venv/")
- `gvsoc_dir`: GVSoC directory path (default: "./gvcuck/")
- `sdk_dir`: PULP SDK directory path (default: "./pulp-sdk/")

**Configuration Files:**
- `palloy_config_file`: Palloy configuration file (default: "palloy_config.json")
- `cluster_config_file`: Cluster config output (default: "./gvcuck/pulp/pulp/chips/pulp_open/cluster.new.json")
- `soc_config_file`: SoC config output (default: "./gvcuck/pulp/pulp/chips/pulp_open/soc.new.json")
- `trace_file`: Trace output file path (default: "./traces.log")

### Example: Full Initialization

```python
sim = PalloySimulator(
    workload_path="./pulp-sdk/applications/MyApp/",
    num_cluster_cores=16,
    l1_size_kb=128,
    l2_size_kb=3200,
    l2_num_banks=8,
    config="palloy.sh",
    target="palloy",
    palloy_config_file="my_config.json"
)
```

## Usage Examples

### Example 1: Parameter Sweep

```python
from palloy import PalloySimulator

# Initialize simulator
sim = PalloySimulator()

# Test different core configurations
for cores in [2, 4, 8, 16]:
    print(f"\n=== Testing with {cores} cores ===")
    
    # Update configuration
    sim.palloy_config.update(num_cluster_cores=cores)
    sim.num_cluster_cores = cores
    
    # Run workflow
    metrics = sim.run_full_workflow()
    
    # Save results
    sim.save_results(f"results_{cores}cores.json")
```

### Example 2: Memory Configuration Study

```python
from palloy import PalloySimulator

# Test different L2 configurations
l2_configs = [
    {"l2_size_kb": 512, "l2_num_banks": 2},
    {"l2_size_kb": 1024, "l2_num_banks": 4},
    {"l2_size_kb": 2048, "l2_num_banks": 8},
]

for config in l2_configs:
    sim = PalloySimulator(**config)
    metrics = sim.run_full_workflow()
    print(f"L2 {config['l2_size_kb']}KB, {config['l2_num_banks']} banks: {metrics['cycles']} cycles")
```
