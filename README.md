
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
