import argparse
import inspect
from src.run import run_z3, run_cvc5, run_xmt
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

        solvers = [run_z3, run_cvc5, run_xmt]
        for solver in solvers:
            for benchmark in benchmarks:
                size = 50
                while size <= 2500:
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

                    size = min(size * 2, 2501)
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

if __name__ == "__main__":
    main()

