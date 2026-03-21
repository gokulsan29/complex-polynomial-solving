import math
from typing import Dict, List, Tuple

import z3

Term        = Tuple[int, Dict[str, int]]          # (coeff, {var1: exponent1, var2: exponent2})
Equation    = List[Term]
System      = List[Equation]

def equation_to_string(equation: Equation) -> str:
    """Human-readable rendering with original integer coefficients."""
    parts = []
    for coeff, mono in equation:
        c = int(coeff)
        if c == 0:
            continue
        sign = "+" if c > 0 else "-"
        ac = abs(c)
        mono_str = ""
        if mono:
            factors = []
            for v, e in mono.items():
                factors.append(f"{v}^{e}" if e > 1 else v)
            mono_str = "·".join(factors)
        if mono_str:
            if ac == 1:
                parts.append(f" {sign} {mono_str}")
            else:
                parts.append(f" {sign} {ac}·{mono_str}")
        else:
            parts.append(f" {sign} {ac}")
    s = "".join(parts).strip()
    if s.startswith("+ "):
        s = s[2:]
    return (s if s else "0") + " = 0"

def system_to_string(system : System) -> str:
  parts = []
  for equation in system:
    parts.append(equation_to_string(equation))
  return "\n".join(parts).strip()

def split_equation_into_real_and_complex(equation : Equation) -> Tuple[Equation, Equation]:
  real_eq = []
  imag_eq = []

  for coeff, vars_dict in equation:
    current_terms : List[Tuple[int, Dict[str, int], int]] = [(coeff, {}, 0)]

    for var_name, exponent in vars_dict.items():
      new_terms = []
      for c_val, c_vars, c_i_pow in current_terms:
        for k in range(exponent + 1):
          new_coeff = c_val * math.comb(exponent, k)
          new_vars = c_vars.copy()

          if exponent - k > 0:
            new_vars[f"{var_name}_r"] = exponent - k
          if k > 0:
            new_vars[f"{var_name}_i"] = k

          new_terms.append((new_coeff, new_vars, c_i_pow + k))
      current_terms = new_terms

    for val, v_dict, i_pow in current_terms:
      if i_pow % 2 == 0:
        real_eq.append((val * (1 if i_pow % 4 == 0 else -1), v_dict))
      else:
        imag_eq.append((val * (1 if i_pow % 4 == 1 else -1), v_dict))

  return real_eq, imag_eq


def split_system_into_real_and_complex(system : System) -> Tuple[System, System]:
  real_system = []
  imag_system = []

  for equation in system:
    real_equation, imag_equation = split_equation_into_real_and_complex(equation)
    real_system.append(real_equation)
    imag_system.append(imag_equation)

  return real_system, imag_system

def convert_equation_to_z3_expr_using_reals(equation : Equation) -> z3.ExprRef:
  eqn_expr = None
  for coeff, vars_dict in equation:
    term_expr = z3.RealVal(coeff)
    for var, exp in vars_dict.items():
      z3_var = z3.Real(var)
      term_expr = term_expr * (z3_var ** exp)
    if eqn_expr is None:
      eqn_expr = term_expr
    else:
      eqn_expr += term_expr
  return (eqn_expr == 0)

def convert_system_to_z3_expr_using_reals(system : System) -> z3.ExprRef:
  exprs_for_eqns = []
  for equation in system:
    exprs_for_eqns.append(convert_equation_to_z3_expr_using_reals(equation))
  return z3.And(*exprs_for_eqns)

def solve_using_smt_reals(system : System) -> z3.CheckSatResult:
  real_system, imag_system = split_system_into_real_and_complex(system)
  final_system = [*real_system, *imag_system]
  z3_expr = convert_system_to_z3_expr_using_reals(final_system)
  print(f"Printing z3 expr\n{z3_expr}\nz3 expr done")
  s = z3.Solver()
  s.add(z3_expr)
  s.set("timeout", 60000)
  return s.check()

def convert_equation_to_z3_expr_using_int_mod_p(p : int, equation : Equation) -> z3.ExprRef:
  eqn_expr : z3.ExprRef = None
  for coeff, vars_dict in equation:
    term_expr = z3.IntVal(coeff % p)
    for var, exp in vars_dict.items():
      z3_var = z3.Int(var) % p
      term_expr = term_expr * z3.ToInt((z3_var ** z3.IntVal(exp)))
    if eqn_expr is None:
      eqn_expr = term_expr
    else:
      eqn_expr += term_expr
  if eqn_expr is not None:
    eqn_expr = eqn_expr % p
    return (eqn_expr == 0)
  return z3.BoolVal(True)

def convert_system_to_z3_expr_using_int_mod_p(p: int, system : System) -> z3.ExprRef:
  exprs_for_eqns = []
  for equation in system:
    exprs_for_eqns.append(convert_equation_to_z3_expr_using_int_mod_p(p, equation))
  return z3.And(*exprs_for_eqns)

def solver_using_smt_int_mod_p(p : int, system : System) -> z3.CheckSatResult:
  z3_expr = convert_system_to_z3_expr_using_int_mod_p(p, system)
  print(f"Printing z3 expr\n{z3_expr}\nz3 expr done")
  s = z3.Solver()
  s.add(z3_expr)
  s.set("timeout", 60000)
  return s.check()

system = [[(2, {"x" : 2}), (-1, {"y" : 1}), (-1, {})], [(1, {"y" : 1})]]
print(f"Printing system\n{system_to_string(system)}\nSystem Done")
print("Checking satisfiablilty using SMT reals")
is_sat = solve_using_smt_reals(system)
print(f"is_sat: {is_sat}")

p = 11
print(f"Checking satisfiablilty using SMT int mod {p}")
is_sat = solver_using_smt_int_mod_p(p, system)
print(f"is_sat: {is_sat}")
