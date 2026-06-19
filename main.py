import argparse
import inspect
import random
random.seed(0)
from src.run import run_z3, run_cvc5, run_xmt, TIMEOUT, save_smt_files
import src.CommonItems
import src.CompleteSets
import src.GraphColoring.GraphColoring
import src.GraphColoring.int_assert
import src.GraphColoring.datatype_define
import src.GraphColoring.datatype_assert
import src.GraphColoring.grounded
import src.GraphColoring.int_define_no_eq
import src.GraphColoring.int_assert_no_eq
import src.GraphColoring.datatype_define_no_eq
import src.GraphColoring.datatype_assert_no_eq
import src.N_queens
import src.NonPartitionRemovalColoring
import src.PackingProblem
import src.PPM
import src.QuasiGroup
import src.RamseyNumbers
import src.TGCheckSat

DIRT_BENCHMARKS = [
    src.CommonItems,
    src.CompleteSets,
    src.GraphColoring.GraphColoring,
    src.N_queens,
    src.NonPartitionRemovalColoring,
    src.PackingProblem,
    src.PPM,
    src.QuasiGroup,
    src.RamseyNumbers,
    src.TGCheckSat,
]

def main():
    parser = argparse.ArgumentParser(description="Benchmark Runner CLI")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--coloring", action="store_true", help="Run coloring benchmarks")
    group.add_argument("--dirt", action="store_true", help="Run DIRT benchmarks on SMT solvers")
    group.add_argument("--dirtWrite", action="store_true", help="Generate SMT-LIB benchmark files for DIRT benchmarks")
    group.add_argument("--asp", action="store_true", help="Run DIRT benchmarks on ASP solver (clingo)")
    group.add_argument("--idp3", action="store_true", help="Run DIRT benchmarks on IDP3 solver")
    group.add_argument("--sli", action="store_true", help="Run DIRT benchmarks on SLI solver")
    group.add_argument("--find", action="store_true", help="Find suitable SMT benchmarks")
    group.add_argument("--findQF", action="store_true", help="Find suitable QF SMT benchmarks")
    group.add_argument("--smt", action="store_true", help="Run found SMT benchmarks")

    args = parser.parse_args()

    # Default to --smt if no option is selected
    if not (args.coloring or args.find or args.smt or args.dirt or args.asp or args.idp3 or args.sli):
        args.coloring = True
        args.dirt = True

    if args.coloring:
        benchmarks = [
            src.GraphColoring.GraphColoring,
            src.GraphColoring.datatype_define,
            src.GraphColoring.int_assert,
            src.GraphColoring.datatype_assert,
            src.GraphColoring.grounded,
        ]

        solvers = [run_z3, run_xmt, run_cvc5]  #
        for solver in solvers:
            solver_benchmarks = benchmarks.copy()
            if solver == run_z3:
                solver_benchmarks.extend([
                    src.GraphColoring.int_define_no_eq,
                    src.GraphColoring.datatype_define_no_eq,
                    src.GraphColoring.int_assert_no_eq,
                    src.GraphColoring.datatype_assert_no_eq,
                ])
            for benchmark in solver_benchmarks:
                size = 50
                while size <= 3000:
                    solver_name = solver.__name__.replace("run_", "")
                    print(f"========================================")
                    print(f"Running benchmark: {benchmark.name} | Solver: {solver_name} | Size: {size}")
                    print(f"========================================")

                    # Generate the SMT scripts with current size
                    smt = benchmark.smt(size)

                    # Execute solver run
                    success = solver(smt, benchmark, size, csv="coloring.csv")

                    if not success:
                        print(f"Solver {solver_name} timed out for {benchmark.name} at size {size}. Stopping size loop.")
                        break

                    size = int(size * 1.2)
                    plot_coloring_results()

    if args.find or args.findQF:
        import os
        import shutil
        for f in ["error.md", "smt-lib.md"]:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception as e:
                    print(f"Error removing {f}: {e}")
        for d in ["~/Downloads/Errors", "~/Downloads/SMT-LIB"]:
            expanded = os.path.expanduser(d)
            if os.path.exists(expanded):
                try:
                    shutil.rmtree(expanded)
                except Exception as e:
                    print(f"Error removing directory {d}: {e}")

        src.run.TIMEOUT = 20
        src.run.MEMORY_LIMIT = 5 * src.run.GB
        import urllib.request
        import json
        url = "https://zenodo.org/api/records/16740866"
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                for file_info in data.get("files", []):
                    name = file_info.get("key", "")
                    download_url = file_info.get("links", {}).get("self", "")
                    if name.endswith(".tar.zst"):
                        if args.find and not any(x in name for x in ("QF", "BV", "NIA", "FP")) and not name.startswith("A"):
                            find_benchmarks(name, download_url, False)
                        if args.findQF and "QF" in name and not any(x in name for x in ("BV", "NIA", "FP")) and not name.startswith("A"):
                            find_benchmarks(name, download_url, True)
        except Exception as e:
            print(f"Error fetching benchmarks: {e}")

    if args.smt:
        import os
        import glob
        import re

        smt_dir = os.path.expanduser("~/Downloads/SMT-LIB")
        smt_files = sorted(glob.glob(os.path.join(smt_dir, "*.smt2")))

        selected_files = smt_files  #[:5]
        print(f"Selected SMT files: {selected_files}")

        for file_path in selected_files:
            file_name = os.path.basename(file_path)
            benchmark_name = os.path.splitext(file_name)[0]

            with open(file_path, "r", encoding="utf-8") as f:
                script = f.read()

            logic_match = re.search(r"\(set-logic\s+([^\s\)]+)\)", script)
            logic = logic_match.group(1) if logic_match else "ALL"

            status_match = re.search(r"\(set-info\s+:status\s+(\w+)\)", script)
            result = status_match.group(1) if status_match else ""

            class MockBenchmark:
                def __init__(self, name, logic, result):
                    self.name = name
                    self.logic = logic
                    self.result = result

            bench = MockBenchmark(benchmark_name, logic, result)

            print(f"========================================")
            print(f"Running SMT benchmark: {benchmark_name}")
            print(f"========================================")

            csv_file = "Result_smt.csv"
            run_z3(script, bench, 1, csv=csv_file)
            run_xmt(script, bench, 1, csv=csv_file)

    if args.dirt:
        for benchmark in DIRT_BENCHMARKS:
            print(f"========================================")
            print(f"Running benchmark: {benchmark.name}")
            print(f"========================================")

            # Generate the SMT scripts with default parameters
            smt = benchmark.smt()
            sig = inspect.signature(benchmark.smt)
            first_param = list(sig.parameters.values())[0]
            size = 1 if first_param.name == "file_path" else first_param.default

            # Execute solver runs
            run_z3(smt, benchmark, size, csv="Result_dirt.csv")
            run_cvc5(smt, benchmark, size, csv="Result_dirt.csv")
            run_xmt(smt, benchmark, size, csv="Result_dirt.csv")

    if args.asp:
        from src.run import run_asp
        for benchmark in DIRT_BENCHMARKS:
            print(f"========================================")
            print(f"Running ASP benchmark: {benchmark.name}")
            print(f"========================================")

            # Generate the ASP scripts with default parameters
            asp_script = benchmark.asp()
            sig = inspect.signature(benchmark.asp)
            first_param = list(sig.parameters.values())[0]
            size = 1 if first_param.name == "file_path" else first_param.default

            # Execute solver run
            run_asp(asp_script, benchmark, size, csv="Result_asp.csv")

    if args.idp3:
        from src.run import run_idp3
        for benchmark in DIRT_BENCHMARKS:
            print(f"========================================")
            print(f"Running IDP3 benchmark: {benchmark.name}")
            print(f"========================================")

            if not hasattr(benchmark, "idp3"):
                print("No idp3 method found, skipping")
                continue

            # Generate the IDP3 scripts with default parameters
            sig = inspect.signature(benchmark.idp3)
            first_param = list(sig.parameters.values())[0]
            size = 1 if first_param.name == "file_path" else first_param.default

            # Execute solver runs
            idp3_script = benchmark.idp3()
            run_idp3(idp3_script, benchmark, size, csv="Result_idp3.csv")

    if args.sli:
        from src.run import run_sli
        for benchmark in DIRT_BENCHMARKS:
            print(f"========================================")
            print(f"Running SLI benchmark: {benchmark.name}")
            print(f"========================================")

            if not hasattr(benchmark, "sli"):
                print("No sli method found, skipping")
                continue

            # Generate the SLI scripts with default parameters
            sig = inspect.signature(benchmark.sli)
            first_param = list(sig.parameters.values())[0]
            size = 1 if first_param.name == "file_path" else first_param.default

            # Execute solver runs
            sli_script = benchmark.sli()
            run_sli(sli_script, benchmark, size, csv="Result_sli.csv")

    if args.dirtWrite:
        for benchmark in DIRT_BENCHMARKS:
            print(f"========================================")
            print(f"Generating SMT script for: {benchmark.name}")
            print(f"========================================")

            # Generate the SMT scripts with default parameters
            smt = benchmark.smt()
            save_smt_files(smt, benchmark)

def plot_coloring_results(csv_path="Result_coloring.csv", output_path="Result_coloring.png"):
    import os
    import csv
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from collections import defaultdict

    if not os.path.exists(csv_path):
        print(f"No {csv_path} found to generate plot.")
        return

    # Read data and handle potential duplicates by keeping the latest entry for each (solver, name, size)
    latest_runs = {}
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                name = row["name"]
                size = int(row["size"])
                solver = row["solver"]
                error = row.get("error", "").strip()
                if error:
                    solve_time = float(TIMEOUT)
                else:
                    solve_time = float(row["solve time"])
                latest_runs[(solver, name, size)] = solve_time
            except (ValueError, KeyError):
                continue

    # Group by (solver, name) -> list of (size, solve_time)
    plot_data = defaultdict(list)
    for (solver, name, size), solve_time in latest_runs.items():
        plot_data[(solver, name)].append((size, solve_time))

    # Sort the points by size for each line
    for key in plot_data:
        plot_data[key].sort(key=lambda x: x[0])

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 6))

    for (solver, name), points in plot_data.items():
        sizes = [p[0] for p in points]
        times = [p[1] for p in points]

        # Thick line for xmt lines, and a regular line for all others
        linewidth = 3.0 if solver == "xmt" else 1.5
        ax.plot(sizes, times, linewidth=linewidth)

    ax.set_yscale('log')
    ax.set_xlabel('Size')
    ax.set_ylabel('Solve Time (s) [log scale]')
    ax.set_title('Graph Coloring Benchmarks - Solve Time vs Size')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"Generated plot saved to {output_path}")

def find_benchmarks(name, download_url, qf, folder_timeout=300):
    import urllib.request
    import os
    import subprocess
    import shutil
    import tempfile
    import resource
    import random
    import time
    import csv
    random.seed(0)

    GB = 1024 * 1024 * 1024
    MEMORY_LIMIT = 10 * GB

    def limit_memory():
        resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT, MEMORY_LIMIT))

    qf_csv_path = "Result_qf.csv"
    if qf and not os.path.exists(qf_csv_path):
        with open(qf_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["file", "successive", "skeleton"])

    print(f"Downloading {name}...")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            archive_path = os.path.join(temp_dir, name)
            urllib.request.urlretrieve(download_url, archive_path)

            temp_extract_dir = os.path.join(temp_dir, "extract")
            os.makedirs(temp_extract_dir, exist_ok=True)

            print(f"Extracting {name}...")
            subprocess.run(
                ["tar", "--zstd", "-xf", archive_path, "-C", temp_extract_dir],
                check=True
            )

            # check files in each folder
            for root, _, files in os.walk(temp_extract_dir):
                smt_files = [f for f in files if not f.startswith(".") and f.endswith(".smt2")]

                start_time = time.time()
                can_benefit_files = []
                for idx, file in enumerate(smt_files):
                    if time.time() - start_time > folder_timeout:
                        print(f"Timeout reached for folder {root}. Skipping remaining {len(smt_files) - idx} files.")
                        break
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, temp_extract_dir)

                    try:
                        cmd =  "../xmtcom/target/release/check"
                        cmd = [cmd, "--qf", full_path] if qf else [cmd, full_path]
                        res = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            preexec_fn=limit_memory
                        )
                        stdout = res.stdout
                        has_error = (res.returncode != 0)
                        if qf and not has_error:
                            if "******" in stdout or "at position" in stdout or "Error:" in stdout:
                                has_error = True
                        can_benefit = "This file can benefit from xmt-lib." in stdout

                        if has_error:
                            print(f"Found error: {rel_path}")
                            last_10 = "\n".join(stdout.splitlines()[-10:])
                            # write to error.md
                            with open("error.md", "a") as md_file:
                                md_file.write(f"# {rel_path}\n{last_10}\n")

                            # copy to ~/Downloads/Errors
                            dest_dir = os.path.expanduser("~/Downloads/Errors")
                            os.makedirs(dest_dir, exist_ok=True)
                            dest_file = os.path.join(dest_dir, os.path.basename(rel_path))
                            shutil.copy2(full_path, dest_file)

                        elif qf:
                            stdout_clean = stdout.strip()
                            if "," in stdout_clean:
                                parts = stdout_clean.split(",", 1)
                                try:
                                    successive = int(parts[0])
                                    skeleton = parts[1]
                                    if successive > 10:
                                        with open(qf_csv_path, "a", newline="", encoding="utf-8") as f:
                                            writer = csv.writer(f)
                                            writer.writerow([rel_path, successive, skeleton])
                                except ValueError:
                                    pass

                        elif can_benefit:
                            can_benefit_files.append((full_path, rel_path, stdout))

                    except Exception as e:
                        print(f"Error checking file {rel_path}: {e}")

                if can_benefit_files:
                    selected_benefit = can_benefit_files
                    if len(selected_benefit) > 5:
                        selected_benefit = random.sample(selected_benefit, 5)
                    for full_path, rel_path, stdout in selected_benefit:
                        print(f"Found match (benefit): {rel_path}")
                        last_10 = "\n".join(stdout.splitlines()[-10:])
                        with open("smt-lib.md", "a") as md_file:
                            md_file.write(f"# {rel_path}\n{last_10}\n")

                        # Write the .smt2 file to the Downloads/SMT-LIB directory
                        dest_dir = os.path.expanduser("~/Downloads/SMT-LIB")
                        os.makedirs(dest_dir, exist_ok=True)
                        dest_file = os.path.join(dest_dir, os.path.basename(rel_path))
                        shutil.copy2(full_path, dest_file)
    except Exception as e:
        print(f"Error processing {name}: {e}")

if __name__ == "__main__":
    main()

