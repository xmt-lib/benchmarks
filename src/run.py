import time
import subprocess
import tempfile
import resource

print(subprocess.check_output(["z3", "--version"], text=True))

timeout = 60
GB = 1024 * 1024 * 1024
MEMORY_LIMIT = 4 * GB

def limit_memory():
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, MEMORY_LIMIT))

def run_xmt(script):
    print("running xmt")
    with tempfile.NamedTemporaryFile("w") as file:
        file.write(script)
        file.flush()

        start_time = time.time()

        try:
            # call xmt-lib with a timeout
            process = subprocess.run(
                ["../xmtcom/target/release/xmt-lib", file.name],
                text=True,
                capture_output=True,
                timeout=timeout,
                preexec_fn=limit_memory
            )
            result = process.stdout
            error = process.stderr

            end_time = time.time()

            if result:
                print(f"Result:\n{result.strip()}")
            if error:
                print(f"Error output:\n{error.strip()}")
            print(f"Total time taken: {end_time - start_time:.4f} seconds")

        except subprocess.TimeoutExpired:
            print(f"Error: xmt-lib execution timed out after {timeout} seconds.")
        except Exception as e:
            print(f"Error evaluating SMT-LIB: {e}")

def run_z3(script):
    print("running z3")
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
        result = process.stdout
        error = process.stderr

        end_time = time.time()

        if result:
            print(f"Result:\n{result.strip()}")
        if error:
            print(f"Error output:\n{error.strip()}")
        print(f"Total time taken: {end_time - start_time:.4f} seconds")

    except subprocess.TimeoutExpired:
        print(f"Error: Z3 execution timed out after {timeout} seconds.")
    except Exception as e:
        print(f"Error evaluating SMT-LIB: {e}")

def run_cvc5(script):
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
        result = process.stdout
        error = process.stderr

        end_time = time.time()

        if result:
            print(f"Result:\n{result.strip()}")
        if error:
            print(f"Error output:\n{error.strip()}")
        print(f"Total time taken: {end_time - start_time:.4f} seconds")

    except subprocess.TimeoutExpired:
        print(f"Error: cvc5 execution timed out after {timeout} seconds.")
    except Exception as e:
        print(f"Error evaluating SMT-LIB: {e}")
