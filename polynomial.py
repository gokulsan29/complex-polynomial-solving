import math
from typing import Dict, List, Tuple

Term     = Tuple[int, Dict[str, int]] # (coeff, {var1: exponent1, var2: exponent2})
Equation = List[Term]
System   = List[Equation]

def equation_to_string(eqn: Equation) -> str:
    """Human-readable rendering with original integer coefficients."""
    parts = []
    for coeff, mono in eqn:
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

def system_to_string(sys : System) -> str:
  parts = []
  for eqn in sys:
    parts.append(equation_to_string(eqn))
  return "\n".join(parts).strip()

def split_equation_into_real_and_complex(eqn : Equation) -> Tuple[Equation, Equation]:
  real_eq = []
  imag_eq = []

  for coeff, vars_dict in eqn:
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

def split_system_into_real_and_complex(sys : System) -> Tuple[System, System]:
  real_system = []
  imag_system = []

  for eqn in sys:
    real_equation, imag_equation = split_equation_into_real_and_complex(eqn)
    real_system.append(real_equation)
    imag_system.append(imag_equation)

  return real_system, imag_system
