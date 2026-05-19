import argparse
from src.run import run_z3, run_cvc5, run_xmt
import src.CommonItems
import src.CompleteSets
import src.GraphColoring
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
        args.smt = True

    if args.coloring:
        print("Option --coloring is not defined yet.")
    elif args.smt:
        benchmarks = [
            src.CommonItems,
            src.CompleteSets,
            src.GraphColoring,
            src.N_queens,
            src.NonPartitionRemovalColoring,
            src.PackingProblem,
            src.PPM,
            src.QuasiGroup,
            src.RamseyNumbers,
            src.TGCheckSat,
        ]

        for b in benchmarks:
            print(f"========================================")
            print(f"Running benchmark: {b.name}")
            print(f"========================================")

            # Generate the SMT/XMT scripts with default parameters
            smt, xmt = b.generate()

            # Execute solver runs
            run_z3(smt, b.logic, b.name, b.result, csv="smt.csv")
            run_cvc5(smt, b.name, b.result, csv="smt.csv")
            run_xmt(xmt, b.name, b.result, csv="smt.csv")
    elif args.asp:
        print("Option --asp is not defined yet.")

if __name__ == "__main__":
    main()

