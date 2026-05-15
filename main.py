import solvers
import polynomials

system = [[(2, {"x" : 2}), (-1, {"y" : 1}), (-1, {})], [(1, {"y" : 1})]]
print("Printing system")
print(polynomials.system_to_string(system))
print("System Done")

is_sat = solvers.check_sat_using_smt_reals(system)
print(f"is_sat: {is_sat}")

is_sat = solvers.check_sat_by_sweeping_primes_z3(system)
print(f"is_sat: {is_sat}")
