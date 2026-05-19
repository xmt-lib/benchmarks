import os
import time
import subprocess
import tempfile
import resource
import csv
from datetime import datetime

timeout = 60  # seconds
GB = 1024 * 1024 * 1024
MEMORY_LIMIT = 10 * GB
WRITE = False

print(subprocess.check_output(["z3", "--version"], text=True))

def write_result(csv_path, name, solver, end_time, error):
    file_exists = os.path.exists(csv_path)
    with open(csv_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['name', 'solver', 'solve time', 'error', 'run date'])
        writer.writerow([name, solver, end_time, error or "", datetime.now().isoformat()])

def limit_memory():
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, MEMORY_LIMIT))

def run_xmt(script, name, result, csv):
    print("running xmt")
    with tempfile.NamedTemporaryFile("w") as file:
        file.write(script)
        file.flush()

        start_time = time.time()
        error = ""

        try:
            # call xmt-lib with a timeout
            process = subprocess.run(
                ["../xmtcom/target/release/xmt-lib", file.name],
                text=True,
                capture_output=True,
                timeout=timeout,
                preexec_fn=limit_memory
            )
            stdout = process.stdout
            error = process.stderr

            if stdout:
                print(f"Result:\n{stdout.strip()}")
                if not result in stdout:
                    print(f"*******  Incorrect result  !!!!!!!!!!")
                    error = f"Incorrect: {stdout}"
            if error:
                print(f"Error output:\n{error.strip()}")
                error = f"stderr : {error.strip()}"

        except subprocess.TimeoutExpired:
            print(f"Error: xmt-lib execution timed out after {timeout} seconds.")
            error = "Time out"
        except Exception as e:
            print(f"Error evaluating SMT-LIB: {e}")
            error = str(e)

    end_time = f"{time.time() - start_time:.4f}"
    print(f"Total time taken: {end_time} seconds")

    write_result(csv, name, "xmt", end_time, error)


def run_z3(script, logic, name, result, csv):
    print("running z3")

    if WRITE:
        output_dir = os.path.join(
            "..",
            "benchmark-submission",
            "non-incremental",
            logic,
            "2026-04-28-Grounders"
        )
        os.makedirs(output_dir, exist_ok=True)

        path = os.path.join(output_dir, f"{name}.smt")
        with open(path, "w", encoding="utf-8") as file:
            file.write(script)

        print(f"Saved SMT script to: {path}")

    start_time = time.time()

    try:
        # call /usr/bin/z3 with a timeout
        process = subprocess.run(
            ["/usr/bin/z3", "-in"],
            input=script,
            text=True,
            capture_output=True,
            timeout=timeout,
            preexec_fn=limit_memory
        )
        stdout = process.stdout
        error = process.stderr

        if stdout:
            print(f"Result:\n{stdout.strip()}")
            if not result in stdout:
                print(f"*******  Incorrect result  !!!!!!!!!!")
                error = f"Incorrect: {stdout}"
        if error:
            print(f"Error output:\n{error.strip()}")
            error = f"stderr : {error.strip()}"

    except subprocess.TimeoutExpired:
        print(f"Error: xmt-lib execution timed out after {timeout} seconds.")
        error = "Time out"
    except Exception as e:
        print(f"Error evaluating SMT-LIB: {e}")
        error = str(e)

    end_time = f"{time.time() - start_time:.4f}"
    print(f"Total time taken: {end_time} seconds")

    write_result(csv, name, "z3", end_time, error)

def run_cvc5(script, name, result, csv):
    print("running cvc5")
    start_time = time.time()

    try:
        # call cvc5 with a 10s timeout
        process = subprocess.run(
            ["cvc5", "--lang=smt2"],
            input=script,
            text=True,
            capture_output=True,
            timeout=timeout,
            preexec_fn=limit_memory
        )
        stdout = process.stdout
        error = process.stderr

        if stdout:
            print(f"Result:\n{stdout.strip()}")
            if not result in stdout:
                print(f"*******  Incorrect result  !!!!!!!!!!")
                error = f"Incorrect: {stdout}"
        if error:
            print(f"Error output:\n{error.strip()}")
            error = f"stderr : {error.strip()}"

    except subprocess.TimeoutExpired:
        print(f"Error: xmt-lib execution timed out after {timeout} seconds.")
        error = "Time out"
    except Exception as e:
        print(f"Error evaluating SMT-LIB: {e}")
        error = str(e)

    end_time = f"{time.time() - start_time:.4f}"
    print(f"Total time taken: {end_time} seconds")

    write_result(csv, name, "cvc5", end_time, error)
