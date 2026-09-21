"""Master execution script to reproduce all results, figures, and tables."""
import os
import subprocess
import sys

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    experiments_dir = os.path.join(root_dir, "experiments")
    
    scripts = [
        "baseline.py",
        "timing.py",
        "heterogeneity.py",
        "sensitivity.py",
        "targeting.py",
        "estimator_validation.py"
    ]
    
    print("Beginning full simulation reproduction pipeline...")
    print(f"Results will be populated in: {os.path.join(root_dir, 'results')}\n")
    
    for script in scripts:
        print(f"--- Running {script} ---")
        script_path = os.path.join(experiments_dir, script)
        try:
            subprocess.run([sys.executable, script_path], check=True, cwd=root_dir)
            print(f"✓ {script} complete.\n")
        except subprocess.CalledProcessError as e:
            print(f"✗ Error running {script}: {e}")
            sys.exit(1)
            
    print("All experiments completed successfully! Check the results/figures and results/tables directories.")

if __name__ == "__main__":
    main()