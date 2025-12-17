#!/usr/bin/env python3
"""
Palloy - Python framework for automated GVSoC simulation workflow
Handles architecture building, workload compilation, simulation execution, and metrics extraction
"""

import os
import subprocess
import sys
import re
from pathlib import Path
from typing import Optional, Dict, Any
import json

# ANSI color codes
class Colors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


class PalloySimulator:
    """Main class for managing GVSoC simulations"""
    
    def __init__(self, 
                 workload_path: str,
                 num_cluster_cores: int = 4,
                 config: str = "palloy.sh",
                 target: str = "palloy",
                 venv_dir: str = "./.venv/",
                 gvsoc_dir: str = "./gvcuck/",
                 sdk_dir: str = "./pulp-sdk/",
                 trace_file: str = "./traces.log"):
        """
        Initialize the Palloy simulator
        
        Args:
            workload_path: Path to the application directory
            num_cluster_cores: Number of cluster cores to use
            config: Configuration file name (in pulp-sdk/configs/)
            target: Target name for GVSoC build
            venv_dir: Path to virtual environment
            gvsoc_dir: Path to GVSoC directory
            sdk_dir: Path to PULP SDK directory
            trace_file: Path to trace output file
        """
        self.workload_path = Path(workload_path).resolve()
        self.num_cluster_cores = num_cluster_cores
        self.config = config
        self.target = target
        self.venv_dir = Path(venv_dir).resolve()
        self.gvsoc_dir = Path(gvsoc_dir).resolve()
        self.sdk_dir = Path(sdk_dir).resolve()
        self.trace_file = Path(trace_file).resolve()
        
        # Store original working directory
        self.original_cwd = Path.cwd()
        
        # Results storage
        self.last_results: Dict[str, Any] = {}
        
    def set_params(self, num_cluster_cores: Optional[int] = None, 
                   workload_path: Optional[str] = None):
        """
        Change simulation parameters
        
        Args:
            num_cluster_cores: Number of cluster cores
            workload_path: Path to workload/application
        """
        
        # TODO: params are not actually changed as of now
        if num_cluster_cores is not None:
            self.num_cluster_cores = num_cluster_cores
            print(f"{Colors.GREEN}✓ Updated cluster cores: {self.num_cluster_cores}{Colors.RESET}")
            
        if workload_path is not None:
            self.workload_path = Path(workload_path).resolve()
            print(f"{Colors.GREEN}✓ Updated workload path: {self.workload_path}{Colors.RESET}")
    
    def _run_command(self, cmd: str, cwd: Optional[Path] = None, 
                     env: Optional[Dict] = None, shell: bool = True) -> subprocess.CompletedProcess:
        """
        Run a shell command and return the result
        
        Args:
            cmd: Command to run
            cwd: Working directory for command
            env: Environment variables
            shell: Whether to run in shell mode
            
        Returns:
            CompletedProcess object
        """
        run_env = os.environ.copy()
        if env:
            run_env.update(env)
            
        print(f"{Colors.GRAY}Running: {cmd}{Colors.RESET}")
        result = subprocess.run(
            cmd,
            shell=shell,
            executable='/bin/bash',
            cwd=cwd or self.original_cwd,
            env=run_env,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print(f"{Colors.RED}✗ Error running command: {cmd}{Colors.RESET}")
            print(f"{Colors.YELLOW}STDOUT: {result.stdout}{Colors.RESET}")
            print(f"{Colors.RED}STDERR: {result.stderr}{Colors.RESET}")
            
        return result
    
    def rebuild_architecture(self) -> bool:
        """
        Rebuild the GVSoC architecture/target
        
        Returns:
            True if successful, False otherwise
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}[1/4] REBUILDING ARCHITECTURE: {self.target}{Colors.RESET}")
        
        # Build command
        cmd = f"make TARGETS={self.target} build -j16"
        
        result = self._run_command(cmd, cwd=self.gvsoc_dir)
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}✓ Architecture rebuild successful{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}✗ Architecture rebuild failed{Colors.RESET}")
            return False
    
    def recompile_workload(self) -> bool:
        """
        Recompile the workload/application
        
        Returns:
            True if successful, False otherwise
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}[2/4] RECOMPILING WORKLOAD: {self.workload_path}{Colors.RESET}")
        print(f"{Colors.CYAN}Cluster cores: {self.num_cluster_cores}{Colors.RESET}")
        
        if not self.workload_path.exists():
            print(f"{Colors.RED}✗ Workload path does not exist: {self.workload_path}{Colors.RESET}")
            return False
        
        # Source config and compile
        config_path = self.sdk_dir / "configs" / self.config
        
        # Build command that sources config and compiles
        cmd = f"source {config_path} && make all -j16 -B CORE={self.num_cluster_cores}"
        
        # Need to activate venv in the same shell
        activate_script = self.venv_dir / "bin" / "activate"
        full_cmd = f"source {activate_script} && {cmd}"
        
        result = self._run_command(full_cmd, cwd=self.workload_path)
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}✓ Workload compilation successful{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}✗ Workload compilation failed{Colors.RESET}")
            return False
    
    def run_simulation(self) -> bool:
        """
        Run the GVSoC simulation
        
        Returns:
            True if successful, False otherwise
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}[3/4] RUNNING SIMULATION{Colors.RESET}")
        
        # Set trace file environment variable
        env = {"TRACE_FILE": str(self.trace_file)}
        
        # Source config and run
        config_path = self.sdk_dir / "configs" / self.config
        cmd = f"source {config_path} && make run -j16"
        
        # Activate venv
        activate_script = self.venv_dir / "bin" / "activate"
        full_cmd = f"source {activate_script} && {cmd}"
        
        result = self._run_command(full_cmd, cwd=self.workload_path, env=env)
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}✓ Simulation completed successfully{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}✗ Simulation failed{Colors.RESET}")
            return False
    
    def extract_metrics(self) -> Dict[str, Any]:
        """
        Extract performance metrics from simulation results
        
        Returns:
            Dictionary containing extracted metrics
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}[4/4] EXTRACTING METRICS{Colors.RESET}")
        
        metrics = {
            "num_cluster_cores": self.num_cluster_cores,
            "workload": str(self.workload_path),
            "cycles": None,
            "timestamp_ps": None,
        }
        
        # Extract cycles from last line of trace file
        # Format: timestamp_ps: cycles: ...
        if self.trace_file.exists():
            try:
                with open(self.trace_file, 'r') as f:
                    # Read last non-empty line
                    lines = f.readlines()
                    last_line = None
                    for line in reversed(lines):
                        if line.strip():
                            last_line = line
                            break
                    
                    if last_line:
                        # Parse format: "3570976278: 104301: ..."
                        match = re.match(r'^(\d+):\s*(\d+):', last_line)
                        if match:
                            metrics["timestamp_ps"] = int(match.group(1))
                            metrics["cycles"] = int(match.group(2))
                            print(f"{Colors.GREEN}✓ Parsed from trace: timestamp={metrics['timestamp_ps']} ps, cycles={metrics['cycles']}{Colors.RESET}")
                        else:
                            print(f"{Colors.YELLOW}⚠ Warning: Could not parse last line format: {last_line[:100]}{Colors.RESET}")
                    else:
                        print(f"{Colors.YELLOW}⚠ Warning: Trace file is empty{Colors.RESET}")
                        
            except Exception as e:
                print(f"{Colors.YELLOW}⚠ Warning: Could not read trace file: {e}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}⚠ Warning: Trace file not found: {self.trace_file}{Colors.RESET}")
        
        self.last_results = metrics
        
        print(f"\nExtracted Metrics:")
        print(f"  Workload: {metrics['workload']}")
        print(f"  Cluster Cores: {metrics['num_cluster_cores']}")
        print(f"  Cycles: {metrics['cycles']}")
        print(f"  Timestamp (ps): {metrics['timestamp_ps']}")
        
        return metrics
    
    def run_full_workflow(self) -> Dict[str, Any]:
        """
        Run the complete workflow: rebuild, recompile, simulate, extract metrics
        
        Returns:
            Dictionary containing performance metrics
        """
        print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*60}")
        print(f"STARTING FULL SIMULATION WORKFLOW")
        print(f"Workload: {self.workload_path}")
        print(f"Cores: {self.num_cluster_cores}")
        print(f"{'='*60}{Colors.RESET}")
        
        # Step 1: Rebuild architecture
        if not self.rebuild_architecture():
            print(f"\n{Colors.RED}✗ Workflow failed at architecture rebuild{Colors.RESET}")
            return {}
        
        # Step 2: Recompile workload
        if not self.recompile_workload():
            print(f"\n{Colors.RED}✗ Workflow failed at workload compilation{Colors.RESET}")
            return {}
        
        # Step 3: Run simulation
        if not self.run_simulation():
            print(f"\n{Colors.RED}✗ Workflow failed at simulation{Colors.RESET}")
            return {}
        
        # Step 4: Extract metrics
        metrics = self.extract_metrics()
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}{'='*60}")
        print(f"WORKFLOW COMPLETED SUCCESSFULLY")
        print(f"{'='*60}{Colors.RESET}")
        
        return metrics
    
    def save_results(self, output_file: str = "results.json"):
        """
        Save the last results to a JSON file
        
        Args:
            output_file: Path to output file
        """
        output_path = Path(output_file)
        with open(output_path, 'w') as f:
            json.dump(self.last_results, f, indent=2)
        print(f"{Colors.GREEN}✓ Results saved to {output_path}{Colors.RESET}")


# Example usage
if __name__ == "__main__":
    # Example configuration
    sim = PalloySimulator(
        #workload_path="./pulp-sdk/applications/MobileNetV1/",
        workload_path="./pulp-sdk/tests/hello/",
        num_cluster_cores=4,
        config="palloy.sh",
        target="palloy"
    )
    
    # Run the full workflow
    metrics = sim.run_full_workflow()
    
    # Save results
    if metrics:
        sim.save_results("results.json")
    
    # Example: Run with different parameters
    # sim.set_params(num_cluster_cores=8)
    # metrics_8cores = sim.run_full_workflow()