# PPM Encoding Differences: ASP vs SMT

This document explains the differences in encoding the **PPM (Order-Preserving Pattern Matching)** problem in SMT-LIB and ASP.

## 1. Mapping Representation
* **SMT**: Declares a direct function mapping pattern indices to text indices:
  ```smt2
  (declare-fun map (Int) Int)
  ```
* **ASP**: Relies on a cumulative predicate `geq(K, I)` representing $\text{map}(K) \ge I$ to model the mapping:
  ```prolog
  { geq(K,I) } :- kval(K), t(I,E).
  :- geq(K, I+1), not geq(K, I).
  ```

## 2. Monotonicity of Mapping
* **SMT**: Declared as a standard inequality assertion over functions:
  ```smt2
  (assert (forall ((x1 Int) (x2 Int))
              (=> (and (smallnumber x1) (smallnumber x2) (< x1 x2))
                  (< (map x1) (map x2)))))
  ```
* **ASP**: Bounded using cumulative logic rules:
  ```prolog
  :- geq(K-1, I), not geq(K, I+1).
  ```

## 3. Retrieving Mapped Colors
* **SMT**: Directly evaluated by composing functions:
  ```smt2
  tf(map(x))
  ```
* **ASP**: Uses a rule to uniquely identify the text index $I$ where $\text{map}(K) = I$, retrieving its color $E$ from `t(I, E)`:
  ```prolog
  solution(K,E) :- kval(K), t(I,E), geq(K,I), not geq(K,I+1).
  ```

## 4. Order Preservation Constraint
* **SMT**: Asserted directly using inequalities ($\le$):
  ```smt2
  (assert (forall ((x1 Int) (x2 Int))
              (=> (and (smallnumber x1) (smallnumber x2) (<= (pf x1) (pf x2)))
                  (<= (tf (map x1)) (tf (map x2))))))
  ```
* **ASP**: Collects pairs with ordered pattern colors (`P1 <= P2`) and forbids mapping combinations where the matched text colors are out of order (`E2 < E1`):
  ```prolog
  pair(K1,K2) :- kval(K1), kval(K2), p(K1,P1), p(K2,P2), P1 <= P2.
  :- pair(K1,K2), solution(K1,E1), solution(K2,E2), E2 < E1.
  ```
