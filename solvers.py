import enum
import random

import z3

import polynomials
from constants import PRIMES
from polynomials import Equation, System

NUM_PRIMES_TO_SAMPLE = 3

class SatResult(enum.Enum):
  SAT = 0
  UNSAT = 1
  UNKNOWN = 2

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
  print("Checking satisfiablilty using SMT reals")
  real_system, imag_system = polynomials.split_system_into_real_and_complex(sys)
  final_system = [*real_system, *imag_system]
  z3_expr = convert_system_to_z3_expr_using_reals(final_system)
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
      term_expr = (term_expr * z3.ToInt((z3_var ** z3.IntVal(exp)))) % p
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
  s = z3.Solver()
  s.add(z3_expr)
  s.set("timeout", 60000)
  return s.check()

def check_sat_using_smt_reals(sys: System) -> SatResult:
  is_sat = solve_using_smt_reals(sys)
  if is_sat == z3.sat:
    return SatResult.SAT
  elif is_sat == z3.unsat:
    return SatResult.UNSAT
  else:
    return SatResult.UNKNOWN

def check_sat_by_sweeping_primes(sys: System) -> SatResult:
  print(f"Checking satisfiablilty by sweeping primes using SMT ints")
  sampled_primes = random.sample(PRIMES, NUM_PRIMES_TO_SAMPLE)
  num_sat = 0
  had_timeout_or_unknown = False
  for prime in sampled_primes:
    print(f"Checking SAT for int mod {prime}")
    is_sat = solve_using_smt_int_mod_p(prime, sys)
    print(f"{is_sat}")
    if is_sat == z3.sat:
      num_sat += 1
    elif is_sat == z3.unknown:
      had_timeout_or_unknown = True

  ratio_of_sat = num_sat / NUM_PRIMES_TO_SAMPLE
  if ratio_of_sat >= 0.7:
    return SatResult.SAT

  if had_timeout_or_unknown:
    return SatResult.UNKNOWN

  if ratio_of_sat <= 0.3:
    return SatResult.UNSAT

  return SatResult.UNKNOWN
