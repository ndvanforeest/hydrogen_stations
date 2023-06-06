import numpy as np
import pulp
from pytictoc import TicToc

pulp.LpSolverDefault.msg = False

t = TicToc()

t.tic()


def solve_hydrogen_stations(demand, distance, capacity):
    num_stations = len(demand)
    # Create the LP problem
    problem = pulp.LpProblem("Hydrogen_stations", pulp.LpMinimize)

    # Create the decision variables
    # x = pulp.LpVariable.dicts("x", range(1, num_stations + 1), lowBound=0, cat='Integer')
    x = pulp.LpVariable.dicts(
        "x", range(1, num_stations + 1), lowBound=0, cat='Continuous'
    )
    y = pulp.LpVariable.dicts(
        "y",
        (range(1, num_stations + 1), range(1, num_stations + 1)),
        lowBound=0,
        cat='Continuous',
    )

    # Set the objective function
    problem += pulp.lpSum(x.values())

    # Add constraints

    for i in range(1, num_stations + 1):
        problem += (
            pulp.lpSum(
                y[i][j]
                for j in range(1, num_stations + 1)
                if distance[i - 1, j - 1] <= 150
            )
            <= capacity * x[i]
        )

    t.toc()

    for j in range(1, num_stations + 1):
        problem += (
            pulp.lpSum(
                y[i][j]
                for i in range(1, num_stations + 1)
                if distance[i - 1, j - 1] <= 150
            )
            >= demand[j - 1]
        )

    t.toc()
    # Solve the problem
    t.toc()
    problem.solve(pulp.PULP_CBC_CMD(msg=0, timeLimit=5))
    t.toc("solved")
    # print(problem)

    # Print the solution
    print("Status:", pulp.LpStatus[problem.status])
    print("Optimal number of stations:")
    tot_capaciteit = 0
    for i in range(1, num_stations + 1):
        if x[i].value() > 0:
            print(f"Location {i}: {x[i].value()}")
            tot_capaciteit += x[i].value()
    print(tot_capaciteit)
    return

    print("Flow of stations:")
    for i in range(1, num_stations + 1):
        for j in range(1, num_stations + 1):
            if y[i][j].value() and y[i][j].value() > 0:
                # print(f"Station {i} to Location {j}: {pulp.value(y[i][j])}")
                print(f"Station {i} to Location {j}: {y[i][j].value()}")


# Example usage

rng = np.random.default_rng(3)
num_stations = 1000
# d = [600, 200, 15, 30]
d = rng.uniform(10, 50, size=num_stations)
print(d.sum())


c = 500

D = np.inf * np.ones((len(d), len(d)))

Min, Max = 5, 15

for i in range(len(d) - 1):
    D[i, i + 1] = rng.uniform(Min, Max)
for i in range(1, len(d)):
    D[i, i - 1] = rng.uniform(Min, Max)

# make symmetric
D += D.transpose()
D /= 2
t.toc()

solve_hydrogen_stations(d, D, c)
t.toc()
