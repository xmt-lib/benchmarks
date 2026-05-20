import argparse
import inspect
from src.run import run_z3, run_cvc5, run_xmt, TIMEOUT
import src.CommonItems
import src.CompleteSets
import src.GraphColoring.int_define
import src.GraphColoring.int_assert
import src.GraphColoring.datatype_define
import src.GraphColoring.datatype_assert
import src.GraphColoring.grounded
import src.N_queens
import src.NonPartitionRemovalColoring
import src.PackingProblem
import src.PPM
import src.QuasiGroup
import src.RamseyNumbers
import src.TGCheckSat

def main():
    parser = argparse.ArgumentParser(description="Benchmark Runner CLI")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--coloring", action="store_true", help="Run coloring benchmarks")
    group.add_argument("--smt", action="store_true", help="Run SMT benchmarks (default)")
    group.add_argument("--asp", action="store_true", help="Run ASP benchmarks")

    args = parser.parse_args()

    # Default to --smt if no option is selected
    if not (args.coloring or args.smt or args.asp):
        args.coloring = True

    if args.coloring:
        benchmarks = [
            src.GraphColoring.int_define,
            src.GraphColoring.datatype_define,
            src.GraphColoring.int_assert,
            src.GraphColoring.datatype_assert,
            src.GraphColoring.grounded,
        ]

        solvers = [run_z3, run_xmt]  # , run_cvc5
        for solver in solvers:
            for benchmark in benchmarks:
                size = 50
                while size <= 1000:
                    solver_name = solver.__name__.replace("run_", "")
                    print(f"========================================")
                    print(f"Running benchmark: {benchmark.name} | Solver: {solver_name} | Size: {size}")
                    print(f"========================================")

                    # Generate the SMT/XMT scripts with current size
                    smt, xmt = benchmark.generate(size)

                    # Execute solver run
                    script = xmt if solver == run_xmt else smt
                    success = solver(script, benchmark, size, csv="coloring.csv")

                    if not success:
                        print(f"Solver {solver_name} timed out for {benchmark.name} at size {size}. Stopping size loop.")
                        break

                    size = int(size * 1.2)
                    plot_coloring_results()
    elif args.smt:
        benchmarks = [
            src.CommonItems,
            src.CompleteSets,
            src.GraphColoring.int_define,
            src.N_queens,
            src.NonPartitionRemovalColoring,
            src.PackingProblem,
            src.PPM,
            src.QuasiGroup,
            src.RamseyNumbers,
            src.TGCheckSat,
        ]

        for benchmark in benchmarks:
            print(f"========================================")
            print(f"Running benchmark: {benchmark.name}")
            print(f"========================================")

            # Generate the SMT/XMT scripts with default parameters
            smt, xmt = benchmark.generate()
            sig = inspect.signature(benchmark.generate)
            first_param = list(sig.parameters.values())[0]
            size = 1 if first_param.name == "file_path" else first_param.default

            # Execute solver runs
            run_z3(smt, benchmark, size, csv="smt.csv")
            run_cvc5(smt, benchmark, size, csv="smt.csv")
            run_xmt(xmt, benchmark, size, csv="smt.csv")
    elif args.asp:
        print("Option --asp is not defined yet.")

def plot_coloring_results(csv_path="coloring.csv", output_path="coloring.png"):
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

if __name__ == "__main__":
    main()

