import os
import time
import subprocess
import tempfile
import resource
import csv
from datetime import datetime

TIMEOUT = 60  # seconds
GB = 1024 * 1024 * 1024
MEMORY_LIMIT = 4 * GB

print(subprocess.check_output(["z3", "--version"], text=True))

def limit_memory():
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, MEMORY_LIMIT))


def run_solver(solver_name, cmd, script, benchmark, size, csv_path, use_temp_file=False):
    print(f"running {solver_name}")
    start_time = time.time()
    error = ""
    stdout = ""

    try:
        if use_temp_file:
            with tempfile.NamedTemporaryFile("w") as file:
                file.write(script)
                file.flush()
                process = subprocess.run(
                    cmd + [file.name],
                    text=True,
                    capture_output=True,
                    timeout=TIMEOUT,
                    preexec_fn=limit_memory
                )
                stdout = process.stdout
                error = process.stderr
        else:
            process = subprocess.run(
                cmd,
                input=script,
                text=True,
                capture_output=True,
                timeout=TIMEOUT,
                preexec_fn=limit_memory
            )
            stdout = process.stdout
            error = process.stderr

        if stdout:
            print(f"Result:\n{stdout.strip()}")
            if not benchmark.result in stdout:
                print(f"*******  Incorrect result  !!!!!!!!!!")
                error = f"Incorrect: {stdout}"
        if error:
            print(f"Error output:\n{error.strip()}")
            error = f"stderr : {error.strip()}"

    except subprocess.TimeoutExpired:
        print(f"Error: {solver_name} execution timed out after {TIMEOUT} seconds.")
        error = "Time out"
    except Exception as e:
        print(f"Error evaluating SMT-LIB: {e}")
        error = str(e)

    end_time = f"{time.time() - start_time:.4f}"
    print(f"Total time taken: {end_time} seconds")

    file_exists = os.path.exists(csv_path)
    with open(csv_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['name', 'size', 'solver', 'solve time', 'error', 'run date'])
        solve_time = 300 if error else end_time
        writer.writerow([benchmark.name, size, solver_name, solve_time, error or "", datetime.now().isoformat()])
    return error == ""


def run_xmt(script, benchmark, size, csv):
    return run_solver("xmt", ["../xmtcom/target/release/xmt-lib"], script, benchmark, size, csv, use_temp_file=True)


def run_z3(script, benchmark, size, csv):
    return run_solver("z3", ["/usr/bin/z3", "-in"], script, benchmark, size, csv)


def run_cvc5(script, benchmark, size, csv):
    return run_solver("cvc5", ["cvc5", "--lang=smt2"], script, benchmark, size, csv)


def save_smt_files(script, benchmark):
    output_dir = os.path.join(
        "..",
        "benchmark-submission",
        "non-incremental",
        benchmark.logic,
        "20260521-Grounders"
    )
    os.makedirs(output_dir, exist_ok=True)

    path = os.path.join(output_dir, f"{benchmark.name}.smt2")
    with open(path, "w", encoding="utf-8") as file:
        file.write(script)

    print(f"Saved SMT script to: {path}")

    # to xmt-lib benchmarks
    output_dir = os.path.join(
        "..",
        "xmtcom",
        "benchmarks"
    )
    os.makedirs(output_dir, exist_ok=True)

    path = os.path.join(output_dir, f"{benchmark.name}.smt2")
    with open(path, "w", encoding="utf-8") as file:
        file.write(script)

    print(f"Saved SMT script to: {path}")
