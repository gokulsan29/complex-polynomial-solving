import enum
import random
from typing import Callable

from cvc5 import pythonic as cvc5
import z3

import polynomials
from constants import PRIMES
from polynomials import Equation, System

NUM_PRIMES_TO_SAMPLE = 3

class SatResult(enum.Enum):
  SAT = 0
  UNSAT = 1
  UNKNOWN = 2

  @staticmethod
  def from_z3_sat_result(sat_result : z3.CheckSatResult) -> SatResult:
    if sat_result == z3.sat:
      return SatResult.SAT
    elif sat_result == z3.unsat:
      return SatResult.UNSAT
    else:
      return SatResult.UNKNOWN

  @staticmethod
  def from_cvc5_sat_result(sat_result : cvc5.CheckSatResult) -> SatResult:
    if sat_result == cvc5.sat:
      return SatResult.SAT
    elif sat_result == cvc5.unsat:
      return SatResult.UNSAT
    else:
      return SatResult.UNKNOWN

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

def generate_pow_z3_expr(z3_var : z3.ExprRef, exp : int, p : int) -> z3.ExprRef:
  if exp < 1:
    raise Exception("exp < 1 is not supported")

  expr : z3.ExprRef = z3_var
  for _ in range(exp - 1):
    expr = (expr * z3_var) % p
  return expr

def convert_equation_to_z3_expr_using_int_mod_p(p : int, eqn : Equation) -> z3.ExprRef:
  eqn_expr : z3.ExprRef = None
  for coeff, vars_dict in eqn:
    term_expr = z3.IntVal(coeff % p)
    for var, exp in vars_dict.items():
      z3_var = z3.Int(var) % p
      term_expr = (term_expr * generate_pow_z3_expr(z3_var, exp, p)) % p
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

def generate_pow_cvc5_expr(cvc5_var : cvc5.ExprRef, exp : int) -> cvc5.ExprRef:
  if exp < 1:
    raise Exception("exp < 1 is not supported")

  expr : cvc5.ExprRef = cvc5_var
  for _ in range(exp - 1):
    expr = expr * cvc5_var
  return expr

def convert_equation_to_cvc5_expr_using_finite_field(p : int, eqn : Equation) -> cvc5.ExprRef:
  eqn_expr : cvc5.ExprRef = None
  for coeff, vars_dict in eqn:
    term_expr = cvc5.FiniteFieldVal(coeff, p)
    for var, exp in vars_dict.items():
      cvc5_var = cvc5.FiniteFieldElem(var, p)
      term_expr = term_expr * generate_pow_cvc5_expr(cvc5_var, exp)
    if eqn_expr is None:
      eqn_expr = term_expr
    else:
      eqn_expr += term_expr
  if eqn_expr is not None:
    return (eqn_expr == 0)
  return z3.BoolVal(True)

def convert_system_to_cvc5_expr_using_finite_field(p : int, sys : System) -> cvc5.ExprRef:
  exprs_for_eqns = []
  for eqn in sys:
    exprs_for_eqns.append(convert_equation_to_cvc5_expr_using_finite_field(p, eqn))
  return cvc5.And(*exprs_for_eqns)

def solve_using_smt_reals(sys : System) -> SatResult:
  print("Checking satisfiablilty using SMT reals")
  real_system, imag_system = polynomials.split_system_into_real_and_complex(sys)
  final_system = [*real_system, *imag_system]
  z3_expr = convert_system_to_z3_expr_using_reals(final_system)
  s = z3.Solver()
  s.add(z3_expr)
  s.set("timeout", 60000)
  return SatResult.from_z3_sat_result(s.check())

def solve_using_z3_int_mod_p(p : int, sys : System) -> SatResult:
  z3_expr = convert_system_to_z3_expr_using_int_mod_p(p, sys)
  s = z3.Solver()
  s.add(z3_expr)
  s.set("timeout", 60000)
  return SatResult.from_z3_sat_result(s.check())

def solve_using_cvc5_finite_field(p : int, sys : System) -> SatResult:
  cvc5_expr = convert_system_to_cvc5_expr_using_finite_field(p, sys)
  s = cvc5.Solver()
  s.set("tlimit", 60000)
  s.add(cvc5_expr)
  return SatResult.from_cvc5_sat_result(s.check())

def check_sat_using_smt_reals(sys: System) -> SatResult:
  return solve_using_smt_reals(sys)

def check_sat_by_sweeping_primes(sys : System,
                                 solve_fn : Callable[[int, System], SatResult]) -> SatResult:
  sampled_primes = random.sample(PRIMES, NUM_PRIMES_TO_SAMPLE)
  num_sat = 0
  had_timeout_or_unknown = False
  for prime in sampled_primes:
    print(f"Checking SAT for int mod {prime}")
    is_sat = solve_fn(prime, sys)
    print(f"{is_sat}")
    if is_sat == SatResult.SAT:
      num_sat += 1
    elif is_sat == SatResult.UNKNOWN:
      had_timeout_or_unknown = True

  ratio_of_sat = num_sat / NUM_PRIMES_TO_SAMPLE
  if ratio_of_sat >= 0.7:
    return SatResult.SAT

  if had_timeout_or_unknown:
    return SatResult.UNKNOWN

  if ratio_of_sat <= 0.3:
    return SatResult.UNSAT

  return SatResult.UNKNOWN

def check_sat_by_sweeping_primes_z3(sys: System) -> SatResult:
  print(f"Checking satisfiablilty by sweeping primes using Z3 ints")
  return check_sat_by_sweeping_primes(sys, solve_using_z3_int_mod_p)

def check_sat_by_sweeping_primes_cvc5(sys: System) -> SatResult:
  print(f"Checking satisfiablilty by sweeping primes using CVC5 Finite Field")
  return check_sat_by_sweeping_primes(sys, solve_using_cvc5_finite_field)
