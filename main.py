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
        run_z3(smt, b.logic, b.name, b.result)
        run_cvc5(smt, b.name, b.result)
        run_xmt(xmt, b.name, b.result)

if __name__ == "__main__":
    main()
