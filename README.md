
## Purpose

This repository contains the tools used to evaluate the xmt-lib grounder
for the paper "Table-based Quantifier Elimination".


## Result Files

When running the benchmarks, the results are logged in CSV format and sometimes plotted as images:
- **`Result_coloring.csv`**: Contains the detailed solving times and sizes for Graph Coloring benchmarks across different solvers.
- **`Result_coloring.png`**: A plotted graph (Solve Time vs. Size in log scale) generated from `Result_coloring.csv`.
- **`Result_dirt.csv`**: Logs the execution results of general DIRT benchmarks (e.g., N-Queens, Packing Problem, Ramsey Numbers) across SMT and ASP solvers.
- **`Result_smt.csv`**: Contains the results of running automatically discovered SMT benchmarks.
- **`Result_qf.csv`**: Logs structural information about Quantifier-Free (QF) SMT benchmarks found during the search process.

## How to Replicate the Results

Ensure you have Python installed, along with the necessary solvers (`z3`, `cvc5`, `clingo`, etc.) in your PATH.

To replicate the results, you can use the CLI options provided by `main.py`:

- **Default Run**: Running `uv run main.py` without arguments defaults to running both Graph Coloring and DIRT benchmarks.
- **Graph Coloring Results**: Run `uv run main.py --coloring` to generate scalable graph coloring benchmarks, solve them using `z3`, `cvc5`, `xmt`, and `ultimate_eliminator`, and automatically generate the `Result_coloring.png` plot.
- **DIRT Benchmarks**: Run `uv run main.py --dirt` to execute the DIRT benchmark suite on SMT solvers.
- **Other Solvers**: You can execute DIRT benchmarks on specific solvers using `--asp` (clingo), `--idp3`, or `--sli`.
- **Finding SMT Benchmarks**: Use `uv run main.py --find` or `--findQF` to automatically download and filter SMT benchmarks from the SMT-COMP Zenodo archive.

## CLI Usage

```
usage: main.py [-h]
               [--coloring | --dirt | --dirtWrite | --find | --findQF | --smt]

Benchmark Runner CLI

options:
  -h, --help   show this help message and exit
  --coloring   Run coloring benchmarks
  --dirt       Run DIRT benchmarks on SMT solvers
  --dirtWrite  Generate SMT-LIB benchmark files for DIRT benchmarks
  --find       Find suitable SMT benchmarks
  --findQF     Find suitable QF SMT benchmarks
  --smt        Run found SMT benchmarks
```

## Ultimate Eliminator Installation

To run the `ultimate_eliminator` solver with Z3 backend, ensure the tool is downloaded next to this repository:

1. Download the tool from the SMT-COMP 2023 Zenodo archive:
   ```bash
   wget -O UltimateEliminator.zip https://zenodo.org/api/records/20639695/files/UltimateEliminator.zip/content
   ```
2. Unzip it alongside this repository:
   ```bash
   unzip UltimateEliminator.zip -d ../UltimateEliminator
   ```
3. Prepare a wrapper script in `../UltimateEliminator/run_ue_z3.sh` that delegates to Z3:
   ```bash
   sed 's/"$SCRIPTDIR\/mathsat"/z3/g' ../UltimateEliminator/ultimateeliminator.sh > ../UltimateEliminator/run_ue_z3.sh
   chmod +x ../UltimateEliminator/run_ue_z3.sh
   ```
4. Ensure `java` and `z3` are in your `PATH`.
