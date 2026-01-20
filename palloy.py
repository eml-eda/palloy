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


class PalloyConfig:
    """Manages Palloy simulation configuration parameters"""
    
    def __init__(self, 
                 config_file: str = "palloy_config.json",
                 cluster_base_file: str = "./gvcuck/pulp/pulp/chips/pulp_open/cluster.json",
                 soc_base_file: str = "./gvcuck/pulp/pulp/chips/pulp_open/soc.json"):
        """
        Initialize configuration manager
        
        Args:
            config_file: Path to the palloy configuration file
            cluster_base_file: Path to baseline cluster config
            soc_base_file: Path to baseline SoC config
        """
        self.config_file = Path(config_file)
        self.cluster_base_file = Path(cluster_base_file)
        self.soc_base_file = Path(soc_base_file)
        
        # Default parameters
        self.params = {
            "num_cluster_cores": 8,
            "l1_size_kb": 64,
            "l2_size_kb": 1600,
            "l2_num_banks": 4,
            "workload_path": "./pulp-sdk/tests/hello/"
        }
        
        # Load configuration if exists
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file if it exists"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    loaded_params = json.load(f)
                    # Update only existing keys, keep defaults for missing ones
                    for key, value in loaded_params.items():
                        if key in self.params:
                            self.params[key] = value
                print(f"{Colors.GREEN}✓ Loaded configuration from {self.config_file}{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.YELLOW}⚠ Warning: Could not load config file: {e}{Colors.RESET}")
                print(f"{Colors.YELLOW}  Using default parameters{Colors.RESET}")
    
    def update(self, **kwargs):
        """Update configuration parameters"""
        for key, value in kwargs.items():
            if key in self.params and value is not None:
                self.params[key] = value
    
    def get(self, key: str, default=None):
        """Get a configuration parameter"""
        return self.params.get(key, default)
    
    def print_config(self):
        """Print current configuration"""
        print(f"\n{Colors.CYAN}{Colors.BOLD}Current Configuration:{Colors.RESET}")
        print(f"  Workload:      {self.params['workload_path']}")
        print(f"  Cluster Cores: {self.params['num_cluster_cores']}")
        print(f"  L1 Size:       {self.params['l1_size_kb']} KB")
        print(f"  L2 Size:       {self.params['l2_size_kb']} KB")
        print(f"  L2 Banks:      {self.params['l2_num_banks']}")


class PalloySimulator:
    """Main class for managing GVSoC simulations"""
    
    def __init__(self, 
                 workload_path: Optional[str] = None,
                 config: str = "palloy.sh",
                 target: str = "palloy",
                 venv_dir: str = "./.venv/",
                 gvsoc_dir: str = "./gvcuck/",
                 sdk_dir: str = "./pulp-sdk/",
                 trace_file: str = "./traces.log",
                 cluster_config_file: str = "./gvcuck/pulp/pulp/chips/pulp_open/cluster.new.json",
                 soc_config_file: str = "./gvcuck/pulp/pulp/chips/pulp_open/soc.new.json",
                 num_cluster_cores: Optional[int] = None,
                 l1_size_kb: Optional[int] = None,
                 l2_size_kb: Optional[int] = None,
                 l2_num_banks: Optional[int] = None,
                 palloy_config_file: str = "palloy_config.json",
                 debug: bool = False):
        """
        Initialize the Palloy simulator
        
        Args:
            workload_path: Path to the application directory (None = use from config)
            config: Configuration file name (in pulp-sdk/configs/)
            target: Target name for GVSoC build
            venv_dir: Path to virtual environment
            gvsoc_dir: Path to GVSoC directory
            sdk_dir: Path to PULP SDK directory
            trace_file: Path to trace output file
            cluster_config_file: Path to cluster config JSON
            soc_config_file: Path to SoC config JSON
            num_cluster_cores: Number of cluster cores to use (None = use from config)
            l1_size_kb: L1 memory size in KB (None = use from config)
            l2_size_kb: L2 memory size in KB (None = use from config)
            l2_num_banks: Number of L2 banks (None = use from config)
            palloy_config_file: Path to palloy configuration file
            debug: Enable debug mode with streaming output (default: False)
        """
        # Get the directory of this script
        script_dir = Path(__file__).resolve().parent
        
        # Initialize configuration manager with paths relative to script
        cluster_base = script_dir / Path(cluster_config_file).parent / "cluster.json"
        soc_base = script_dir / Path(soc_config_file).parent / "soc.json"
        self.palloy_config = PalloyConfig(
            str(script_dir / palloy_config_file),
            str(cluster_base),
            str(soc_base)
        )
        
        # Update config with provided parameters
        self.palloy_config.update(
            workload_path=workload_path,
            num_cluster_cores=num_cluster_cores,
            l1_size_kb=l1_size_kb,
            l2_size_kb=l2_size_kb,
            l2_num_banks=l2_num_banks
        )
        
        # Set instance variables from config
        self.workload_path = Path(self.palloy_config.get('workload_path')).resolve()
        self.num_cluster_cores = self.palloy_config.get('num_cluster_cores')
        self.l1_size_kb = self.palloy_config.get('l1_size_kb')
        self.l2_size_kb = self.palloy_config.get('l2_size_kb')
        self.l2_num_banks = self.palloy_config.get('l2_num_banks')
        
        self.config = config
        self.target = target
        self.debug = debug
        self.venv_dir = (script_dir / venv_dir).resolve()
        self.gvsoc_dir = (script_dir / gvsoc_dir).resolve()
        self.sdk_dir = (script_dir / sdk_dir).resolve()
        self.trace_file = (script_dir / trace_file).resolve()
        self.cluster_config_file = (script_dir / cluster_config_file).resolve()
        self.soc_config_file = (script_dir / soc_config_file).resolve()
        
        # Base configuration files
        self.cluster_base_file = cluster_base
        self.soc_base_file = soc_base
        
        # Store original working directory
        self.original_cwd = Path.cwd()
        
        # Results storage
        self.last_results: Dict[str, Any] = {}
        
    def _update_cluster_config(self, cores_per_cluster: int, l1_size_kb: int) -> bool:
        """
        Update cluster configuration JSON file
        
        Args:
            cores_per_cluster: Number of cores per cluster
            l1_size_kb: L1 memory size in KB
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.cluster_base_file, 'r') as f:
                config = json.load(f)
            
            # Update core count (+1 for control core)
            config["nb_pe"] = cores_per_cluster + 1
            config["icache"]["config"]["nb_cores"] = cores_per_cluster + 1
            config["peripherals"]["event_unit"]["config"]["nb_core"] = cores_per_cluster + 1
            
            # Update L1 size
            l1_size_bytes = l1_size_kb * 1024
            config["l1"]["mapping"]["size"] = f"0x{l1_size_bytes:08x}"
            
            with open(self.cluster_config_file, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"{Colors.RED}✗ Error updating cluster config: {e}{Colors.RESET}")
            return False

    def _update_soc_config(self, l2_size_kb: int, l2_num_banks: int) -> bool:
        """
        Update SoC configuration JSON file
        
        Args:
            l2_size_kb: L2 memory size in KB
            l2_num_banks: Number of L2 banks
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.soc_base_file, 'r') as f:
                config = json.load(f)
            
            # Update L2 sizes (2 banks of 32KB reserved for L2 private)
            l2_size_bytes = l2_size_kb * 1024
            l2_shared_size_bytes = l2_size_bytes - (0x00008000 * 2)
            config["l2"]["size"] = f"0x{l2_size_bytes:08x}"
            config["l2"]["shared"]["mapping"]["size"] = f"0x{l2_shared_size_bytes:08x}"
            config["l2"]["shared"]["nb_banks"] = l2_num_banks
            
            with open(self.soc_config_file, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"{Colors.RED}✗ Error updating SoC config: {e}{Colors.RESET}")
            return False
    
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
    
    def _run_command_streaming(self, cmd: str, cwd: Optional[Path] = None, 
                               env: Optional[Dict] = None, shell: bool = True) -> subprocess.CompletedProcess:
        """
        Run a shell command with real-time output streaming
        
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
        
        # Start the process without capturing output for true real-time streaming
        # Use unbuffered output by setting PYTHONUNBUFFERED
        run_env['PYTHONUNBUFFERED'] = '1'
        
        process = subprocess.Popen(
            cmd,
            shell=shell,
            executable='/bin/bash',
            cwd=cwd or self.original_cwd,
            env=run_env,
            stdout=None,  # Direct output to terminal
            stderr=None,  # Direct errors to terminal
            text=True
        )
        
        # Wait for process to complete
        returncode = process.wait()
        
        # Create a CompletedProcess-like object to maintain compatibility
        # Note: stdout/stderr are empty since we streamed directly to terminal
        result = subprocess.CompletedProcess(
            args=cmd,
            returncode=returncode,
            stdout='',
            stderr=''
        )
        
        if result.returncode != 0:
            print(f"{Colors.RED}✗ Error running command (exit code {result.returncode}){Colors.RESET}")
            
        return result
    
    
    
    #
    # Main workflow methods
    #
    
    def set_params(self) -> bool:
        """
        Update configuration files based on current parameters
        
        Returns:
            True if successful, False otherwise
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}[0/4] UPDATING CONFIGURATION{Colors.RESET}")
        
        # Get parameters from config
        self.num_cluster_cores = self.palloy_config.get('num_cluster_cores', self.num_cluster_cores)
        self.l1_size_kb = self.palloy_config.get('l1_size_kb', self.l1_size_kb)
        self.l2_size_kb = self.palloy_config.get('l2_size_kb', self.l2_size_kb)
        self.l2_num_banks = self.palloy_config.get('l2_num_banks', self.l2_num_banks)
        workload = self.palloy_config.get('workload_path', str(self.workload_path))
        self.workload_path = Path(workload).resolve()
        
        # Update configuration files
        cluster_ok = self._update_cluster_config(self.num_cluster_cores, self.l1_size_kb)
        soc_ok = self._update_soc_config(self.l2_size_kb, self.l2_num_banks)
        
        if cluster_ok and soc_ok:
            print(f"{Colors.GREEN}✓ Configuration files updated successfully{Colors.RESET}")
            return True
        return False
    
    def rebuild_architecture(self) -> bool:
        """
        Rebuild the GVSoC architecture/target
        
        Returns:
            True if successful, False otherwise
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}[1/4] REBUILDING ARCHITECTURE: {self.target}{Colors.RESET}")
        
        activate_script = self.venv_dir / "bin" / "activate"
        cmd = (
            f"source {activate_script} && "
            f"make TARGETS={self.target} build -j$(nproc) "
        )
        
        run_method = self._run_command_streaming if self.debug else self._run_command
        result = run_method(cmd, cwd=self.gvsoc_dir)
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}✓ Architecture rebuild successful{Colors.RESET}")
            return True
        
        print(f"{Colors.RED}✗ Architecture rebuild failed{Colors.RESET}")
        return False
    
    def recompile_workload(self) -> bool:
        """
        Recompile the workload/application
        
        Returns:
            True if successful, False otherwise
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}[2/4] RECOMPILING WORKLOAD: {self.workload_path}{Colors.RESET}")
        
        if not self.workload_path.exists():
            print(f"{Colors.RED}✗ Workload path does not exist: {self.workload_path}{Colors.RESET}")
            return False
        
        activate_script = self.venv_dir / "bin" / "activate"
        config_path = self.sdk_dir / "configs" / self.config
        cmd = (
            f"source {activate_script} && source {config_path} && "
            f"make all -j$(nproc) -B "
            f"CONFIG_NB_CLUSTER_PE={self.num_cluster_cores} "
            f"CORE={self.num_cluster_cores} "
            f"NUM_CORES={self.num_cluster_cores} "
            f"ARCHI_CLUSTER_NB_PE={self.num_cluster_cores} "
            f"USE_CLUSTER=1"
        )
        
        run_method = self._run_command_streaming if self.debug else self._run_command
        result = run_method(cmd, cwd=self.workload_path)
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}✓ Workload compilation successful{Colors.RESET}")
            return True
        
        print(f"{Colors.RED}✗ Workload compilation failed{Colors.RESET}")
        return False
    
    def run_simulation(self) -> bool:
        """
        Run the GVSoC simulation
        
        Returns:
            True if successful, False otherwise
        """
        print(f"\n{Colors.BLUE}{Colors.BOLD}[3/4] RUNNING SIMULATION{Colors.RESET}")
        
        activate_script = self.venv_dir / "bin" / "activate"
        config_path = self.sdk_dir / "configs" / self.config
        cmd = (
            f"source {activate_script} && source {config_path} "
            f"&& make run -j$(nproc) "
            f"runner_args='--trace=insn:{self.trace_file} --trace-level=DEBUG --debug-mode' "
            f"CONFIG_NB_CLUSTER_PE={self.num_cluster_cores}"
        )
        
        run_method = self._run_command_streaming if self.debug else self._run_command
        result = run_method(cmd, cwd=self.workload_path)
        
        if result.returncode == 0:
            print(f"{Colors.GREEN}✓ Simulation completed successfully{Colors.RESET}")
            return True
        
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
        
        # Extract cycles from last line of trace file (format: "timestamp_ps: cycles: ...")
        if not self.trace_file.exists():
            print(f"{Colors.YELLOW}⚠ Trace file not found: {self.trace_file}{Colors.RESET}")
        else:
            try:
                with open(self.trace_file, 'rb') as f:
                    f.seek(0, 2)
                    file_size = f.tell()
                    
                    if file_size == 0:
                        print(f"{Colors.YELLOW}⚠ Trace file is empty{Colors.RESET}")
                    else:
                        # Read last portion of file to extract the last line
                        buffer_size = min(8192, file_size)
                        f.seek(max(0, file_size - buffer_size))
                        buffer = f.read().decode('utf-8', errors='ignore')
                        lines = buffer.splitlines()
                        
                        # Find last non-empty line
                        last_line = next((line for line in reversed(lines) if line.strip()), None)
                        
                        if not last_line:
                            print(f"{Colors.YELLOW}⚠ No valid content in trace file{Colors.RESET}")
                        else:
                            # Parse timestamp and cycles from line
                            match = re.match(r'^(\d+):\s*(\d+):', last_line)
                            if match:
                                metrics["timestamp_ps"] = int(match.group(1))
                                metrics["cycles"] = int(match.group(2))
                                print(f"{Colors.GREEN}✓ Parsed from trace: timestamp={metrics['timestamp_ps']} ps, cycles={metrics['cycles']}{Colors.RESET}")
                            else:
                                print(f"{Colors.YELLOW}⚠ Could not parse last line: {last_line[:100]}{Colors.RESET}")
                                
            except Exception as e:
                print(f"{Colors.YELLOW}⚠ Could not read trace file: {e}{Colors.RESET}")
        
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
        print(f"{'='*60}{Colors.RESET}")
        
        # Print configuration
        self.palloy_config.print_config()
        
        # Step 0: Update configuration files using set_params
        if not self.set_params():
            print(f"\n{Colors.RED}✗ Workflow failed at configuration update{Colors.RESET}")
            return {}
        
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
    # Example helloworld configuration
    sim = PalloySimulator(
        config="palloy.sh",
        target="palloy",
        workload_path="./pulp-sdk/tests/hello/",
    )
    
    # Run the full workflow
    metrics = sim.run_full_workflow()
    
    # Save results
    if metrics:
        sim.save_results("results.json")
    