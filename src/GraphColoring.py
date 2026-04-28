from random import Random

from src.run import run_cvc5, run_xmt, run_z3


## create the graph

size = 2500 #  # of nodes
density = 0.01 # 1 % of node pairs are edges
prng = Random(f"GraphColoring-{size}-{density}")  # Random(f"GraphColoring") is much faster !
graph = [(int((number) / size + 1), number % size + 1)
    for number in prng.sample(range(size * size), int(size * size * density))]

#  Run the scripts

smt = f"""
    (declare-datatype Color ((red) (blue) (green) (orange) (purple)))
    (define-fun edge ((x Int) (y Int)) Bool
        (or
            { "\n            ".join([f"(and (= x {a}) (= y {b}))" for (a, b) in graph])}
        ))
    (declare-fun colorOf (Int) Color)
    (assert
        (forall ((x Int) (y Int))
            (=> (edge x y) (not (= (colorOf x) (colorOf y))))
        )
    )
    (check-sat)
"""
# run_z3(smt)
# run_cvc5(smt)

xmt = f"""
    (set-option :backend Z3)
    (declare-datatype Color ((red) (blue) (green) (orange) (purple)))
    (declare-fun edge (Int Int) Bool)
    (declare-fun colorOf (Int) Color)
    (assert
        (forall ((x Int) (y Int))
            (=> (edge x y) (not (= (colorOf x) (colorOf y))))
        )
    )
    (x-interpret-pred edge (x-set
        { "\n        ".join([f"({a} {b})" for (a, b) in graph])}
    ))
    (check-sat)
"""
run_xmt(xmt)

