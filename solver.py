import z3

import polynomial
from polynomial import Equation, System

def convert_equation_to_z3_expr_using_reals(eqn : Equation) -> z3.ExprRef:
  eqn_expr = None
  for coeff, vars_dict in eqn:
    term_expr = z3.RealVal(coeff)
    for var, exp in vars_dict.items():
      z3_var = z3.Real(var)
      term_expr = term_expr * (z3_var ** exp)
    if eqn_expr is None:
      eqn_expr = term_expr
    else:
      eqn_expr += term_expr
  return (eqn_expr == 0)

def convert_system_to_z3_expr_using_reals(sys : System) -> z3.ExprRef:
  exprs_for_eqns = []
  for eqn in sys:
    exprs_for_eqns.append(convert_equation_to_z3_expr_using_reals(eqn))
  return z3.And(*exprs_for_eqns)

def solve_using_smt_reals(sys : System) -> z3.CheckSatResult:
  real_system, imag_system = polynomial.split_system_into_real_and_complex(sys)
  final_system = [*real_system, *imag_system]
  z3_expr = convert_system_to_z3_expr_using_reals(final_system)
  print(f"Printing z3 expr\n{z3_expr}\nz3 expr done")
  s = z3.Solver()
  s.add(z3_expr)
  s.set("timeout", 60000)
  return s.check()

def convert_equation_to_z3_expr_using_int_mod_p(p : int, eqn : Equation) -> z3.ExprRef:
  eqn_expr : z3.ExprRef = None
  for coeff, vars_dict in eqn:
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

def convert_system_to_z3_expr_using_int_mod_p(p: int, sys : System) -> z3.ExprRef:
  exprs_for_eqns = []
  for eqn in sys:
    exprs_for_eqns.append(convert_equation_to_z3_expr_using_int_mod_p(p, eqn))
  return z3.And(*exprs_for_eqns)

def solve_using_smt_int_mod_p(p : int, sys : System) -> z3.CheckSatResult:
  z3_expr = convert_system_to_z3_expr_using_int_mod_p(p, sys)
  print(f"Printing z3 expr\n{z3_expr}\nz3 expr done")
  s = z3.Solver()
  s.add(z3_expr)
  s.set("timeout", 60000)
  return s.check()
