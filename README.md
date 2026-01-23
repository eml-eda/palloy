# 🏐 Palloy

**Palloy** (PULP-Alloy) is a Python framework for automating PULP GVSoC simulation workflows. It streamlines the process of building customized PULP architectures, compiling workloads, running simulations, and extracting performance metrics.

## Requirements

- Python 3.x
- PULP RISC-V toolchain
- System dependencies (build-essential, cmake, git, libsdl2-dev, etc.)

## Setup

### Option 1: Docker (Recommended)

Use the provided Dockerfile for a complete containerized setup with all dependencies pre-installed:

```bash
cd docker
./build.sh    # Build the Docker image
./run.sh      # Run the container
```

See [docker/palloy.dockerfile](docker/palloy.dockerfile) for details.

### Option 2: Local Installation

1. **Install PULP RISC-V toolchain:**
```bash
curl -L https://github.com/pulp-platform/pulp-riscv-gnu-toolchain/releases/download/v1.0.16/v1.0.16-pulp-riscv-gcc-ubuntu-18.tar.bz2 -o riscv32.tar.bz2
tar -xf riscv32.tar.bz2
sudo mv ./v1.0.16-pulp-riscv-gcc-ubuntu-18 /opt/pulp_toolchain
rm riscv32.tar.bz2

# Add to ~/.bashrc
export PULP_RISCV_GCC_TOOLCHAIN=/opt/pulp_toolchain
export PATH=$PULP_RISCV_GCC_TOOLCHAIN/bin:$PATH
```

2. **Clone and initialize repository:**
```bash
git clone https://github.com/eml-eda/palloy.git
cd palloy
git submodule update --init --recursive
```

3. **Create GVSoC virtual environment:**
```bash
./venv.sh
```

## Quick Start

### Basic Usage

```python
from palloy import PalloySimulator

# Initialize simulator with default configuration
sim = PalloySimulator()

# Run complete workflow
metrics = sim.run_full_workflow()

# Save results
sim.save_results("results.json")
```

### Using Configuration File

Palloy automatically loads parameters from `palloy_config.json`:

```json
{
    "num_cluster_cores": 8,
    "l1_size_kb": 64,
    "l2_size_kb": 1600,
    "l2_num_banks": 4,
    "workload_path": "./pulp-sdk/tests/hello/"
}
```

Override parameters programmatically:

```python
sim = PalloySimulator(
    workload_path="./pulp-sdk/applications/MyApp/",
    num_cluster_cores=4,
    l1_size_kb=128
)
```

### Command Line Usage

```bash
# Edit palloy_config.json then run
python3 palloy.py
```

## Configuration

### Parameters

**Main Parameters:**
- `workload_path`: Path to application (default: "./pulp-sdk/tests/hello/")
- `num_cluster_cores`: Number of cluster cores (default: 8)
- `l1_size_kb`: L1 cache size in KB (default: 64)
- `l2_size_kb`: L2 memory size in KB (default: 1600)
- `l2_num_banks`: Number of L2 memory banks (default: 4)
- `debug`: Enable debug output streaming (default: False)
- `trace_filter`: Filter for trace output (default: instructions only)

**Build & Environment:**
- `config`: Config file name (default: "palloy.sh")
- `target`: GVSoC target name (default: "palloy")
- `venv_dir`: Virtual environment path (default: "./.venv/")
- `gvsoc_dir`: GVSoC directory (default: "./gvcuck/")
- `sdk_dir`: PULP SDK directory (default: "./pulp-sdk/")

**Configuration Files:**
- `trace_file`: Trace output path (default: "./traces.log")
- `palloy_config_file`: Config file path (default: "palloy_config.json")
- `cluster_config_file`: Cluster config output
- `soc_config_file`: SoC config output  

### Programmatic Configuration

```python
# View current configuration
sim.palloy_config.print_config()

# Update parameters
sim.palloy_config.update(num_cluster_cores=16)

# Apply to architecture files
sim.set_params()
```

## Workflow

### Complete Workflow

The `run_full_workflow()` executes all steps:

```python
metrics = sim.run_full_workflow()
```

**Steps:**
1. Update configuration files
2. Rebuild GVSoC architecture
3. Recompile workload
4. Run simulation
5. Extract metrics

### Individual Steps

```python
sim.set_params()                 # Update config files
sim.rebuild_architecture()       # Build GVSoC target
sim.recompile_workload()         # Compile application
sim.run_simulation()             # Execute simulation
metrics = sim.extract_metrics()  # Parse results
```

## Output Metrics

Results are returned as a dictionary:

- `cycles`: Number of simulation cycles
- `timestamp_ps`: Simulation timestamp in picoseconds
- `num_cluster_cores`: Core count used
- `workload`: Workload path

## Examples

### Parameter Sweep

```python
from palloy import PalloySimulator

sim = PalloySimulator()

for cores in [2, 4, 8, 16]:
    sim.palloy_config.update(num_cluster_cores=cores)
    sim.num_cluster_cores = cores
    
    metrics = sim.run_full_workflow()
    sim.save_results(f"results_{cores}cores.json")
```

### Memory Configuration Study

```python
l2_configs = [
    {"l2_size_kb": 512, "l2_num_banks": 2},
    {"l2_size_kb": 1024, "l2_num_banks": 4},
    {"l2_size_kb": 2048, "l2_num_banks": 8},
]

for config in l2_configs:
    sim = PalloySimulator(**config)
    metrics = sim.run_full_workflow()
    print(f"L2 {config['l2_size_kb']}KB: {metrics['cycles']} cycles")
```

### Debug Mode

Enable `debug=True` to stream all command outputs in real-time:

```python
sim = PalloySimulator(debug=True)
metrics = sim.run_full_workflow()
```

### Trace Filtering

Specify `trace_filter` to limit trace output to specific components or type of traces. For example, to capture instruction traces only:

```python
sim = PalloySimulator(trace_filter="insn")
metrics = sim.run_full_workflow()
```

`trace_filter` can also be a list of filters. For example, to only capture instruction traces from all cluster cores:

```python
cluster_cores = 8
trace_filter = [f"pe{core_id}/insn" for core_id in range(cluster_cores)]

sim = PalloySimulator(num_cluster_cores=cluster_cores, trace_filter=trace_filter)
metrics = sim.run_full_workflow()
```

This can be useful to focus on the performance of specific components in the architecture, since the metrics extraction will only consider the deltas in the filtered traces. For more details on GVSoC traces, see the [GVSoC documentation](https://gvsoc.readthedocs.io/en/latest/system_traces.html).

### More Examples

For additional examples ready to run, see [examples/README.md](examples/README.md).