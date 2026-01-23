# Palloy Examples

This directory contains example test suites for exploring different architectural parameters using Palloy.

## Test Suites

### 0. Helloworld Test ([hello/](hello/))
A simple test to verify Palloy installation and functionality.

```bash
cd hello
python test_hello.py
```

### 1. Simple Core Comparison ([simple/](cores/))
Compare **cluster only** performance between two different core counts on a MobileNetV1 workload.

**Default**: 4 cores vs 8 cores

```bash
cd simple
python test_simple.py [cores1] [cores2]
```

### 2. L1 Memory Size Comparison ([l1_size/](l1/))
Compare **cluster only** performance between two different L1 memory sizes on a MobileNetV1 workload. Warning: Ensure that the workload fits in the specified L1 sizes (usually, at least 16 KB).

**Default**: 64 KB vs 256 KB

```bash
cd l1
python test_l1.py [size1] [size2]
```

### 3. L2 Memory Size Comparison ([l2_size/](l2/))
Compare **cluster only** performance between two different L2 memory sizes on a MobileNetV1 workload. Note that the default number of banks is set to 8, but this can be adjusted in the script if needed.

**Default**: 1024 KB vs 2048 KB

```bash
cd l2
python test_l2.py [size1] [size2]
```

## Output Structure

Each test creates its own `out/` directory containing:
- JSON result files for each configuration
- Summary files (where applicable)
- Generated plots (for sweep tests)

## Dependencies

For tests that generate plots:
```bash
pip install matplotlib
```
