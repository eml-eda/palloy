# Palloy Examples

This directory contains example test suites for exploring different architectural parameters using Palloy.

## Test Suites

### 0. Helloworld Test ([hello/](hello/))
A simple test to verify Palloy installation and functionality.

```bash
cd hello
python test_hello.py
```

### 1. Simple Core Comparison ([simple/](simple/))
Compare performance between two different core counts on a MobileNetV1 workload.

**Default**: 4 cores vs 8 cores

```bash
cd simple
python test_simple.py [cores1] [cores2]
```

## Output Structure

Each test creates its own `out/` directory containing:
- JSON result files for each configuration
- Summary files (where applicable)
- Generated plots (for sweep tests)

## Dependencies

For tests that generate plots (e.g., cores sweep):
```bash
pip install matplotlib
```
