import solvers
import polynomials

system = [[(2, {"x" : 2}), (-1, {"y" : 1}), (-1, {})], [(1, {"y" : 1})]]
print(f"Printing system\n{polynomials.system_to_string(system)}\nSystem Done")

is_sat = solvers.check_sat_using_smt_reals(system)
print(f"is_sat: {is_sat}")

is_sat = solvers.check_sat_by_sweeping_primes(system)
print(f"is_sat: {is_sat}")
