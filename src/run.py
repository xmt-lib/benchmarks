import os
import time
import subprocess
import tempfile
import resource
import csv
from datetime import datetime

TIMEOUT = 60  # seconds
GB = 1024 * 1024 * 1024
MEMORY_LIMIT = 10 * GB

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

        if error and solver_name == "idp3":
            filtered = [line for line in error.splitlines() if not line.strip().startswith("Warning:")]
            error = "\n".join(filtered).strip()

        if stdout:
            print(f"Result:\n{stdout.strip()}")
            if solver_name in ["idp3", "sli"]:
                if benchmark.result.lower() == "sat":
                    if "model 1" not in stdout.lower() and "satisfiable" not in stdout.lower() and "model" not in stdout.lower():
                        print(f"*******  Incorrect result  !!!!!!!!!!")
                        error = f"Incorrect: {stdout}"
                else: # unsat
                    if "unsatisfiable" not in stdout.lower():
                        print(f"*******  Incorrect result  !!!!!!!!!!")
                        error = f"Incorrect: {stdout}"
            else:
                if not benchmark.result.lower() in stdout.lower():
                    print(f"*******  Incorrect result  !!!!!!!!!!")
                    error = f"Incorrect: {stdout}"
        if error:
            print(f"Error output:\n{error.strip()}")
            if not error.startswith("Incorrect:"):
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
        solve_time = TIMEOUT if error else end_time
        writer.writerow([benchmark.name, size, solver_name, solve_time, error or "", datetime.now().isoformat()])
    return error == ""


def run_xmt(script, benchmark, size, csv):
    return run_solver("xmt", ["../xmtcom/target/release/xmt-lib"], script, benchmark, size, csv, use_temp_file=True)


def run_z3(script, benchmark, size, csv):
    return run_solver("z3", ["/usr/bin/z3", "-in"], script, benchmark, size, csv)


def run_cvc5(script, benchmark, size, csv):
    return run_solver("cvc5", ["cvc5", "--lang=smt2", "--produce-models"], script, benchmark, size, csv)


def run_asp(script, benchmark, size, csv):
    # clingo reads from stdin. We can optionally specify a time limit in clingo, but
    # run_solver already handles the subprocess timeout.
    return run_solver("clingo", ["python", "-m", "clingo", "1"], script, benchmark, size, csv)


def run_idp3(script, benchmark, size, csv):
    default_idp3 = os.path.expanduser("~/.local/share/idp3_install/idp3-3.7.1-Linux/usr/local/bin/idp")
    default_idp3 = os.path.abspath(default_idp3)
    if not os.path.exists(default_idp3):
        default_idp3 = "idp"

    idp3_exec = os.environ.get("IDP3_EXEC", default_idp3)
    # IDP3 reads from stdin, but run_solver handles that.
    return run_solver("idp3", [idp3_exec], script, benchmark, size, csv, use_temp_file=True)


def run_sli(script, benchmark, size, csv):
    # use sli-lib CLI: sli expand <file>
    # DIRT uses `--satset`, which corresponds to `--interp-mode satset` in the latest sli expand.
    return run_solver("sli", ["sli", "expand", "--interp-mode", "satset"], script, benchmark, size, csv, use_temp_file=True)


def save_smt_files(script, benchmark):
    script = script.replace("\n(get-model)", "").replace("(get-model)", "")
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
