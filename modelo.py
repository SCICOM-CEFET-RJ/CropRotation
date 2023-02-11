import numpy as np
import pandas as pd

import pulp

income = pd.read_csv('dados/al_rasheed/net_income.csv', sep=';')
constraints = pd.read_csv('dados/al_rasheed/constraints.csv', sep=';')
crops = list(income.columns)
lb = dict(zip(crops, list((np.array(crops) == 'Wheat').astype(np.int64)*1500)))
years = 1
rotation = pd.read_csv('dados/al_rasheed/rotations.csv', sep=';')


prob = pulp.LpProblem("Modelo_1", pulp.LpMaximize)


crops_year = dict(zip([f"{i}y_{j}" for j in crops for i in range(1,years+1)], years*crops))

def create_vars():

    return dict(zip(crops_year.keys(),
            [pulp.LpVariable(i, 
                                lowBound = lb[crops_year[i]], 
                                upBound=None) 
                    for i in crops_year.keys()]))


crops_var = create_vars()


def objective_function():
    of = []
    for row in income.itertuples():
        of.append(pulp.lpSum([getattr(row, crops_year[i]) * crops_var[i] for i in crops_year]))

    return of[0]

prob += objective_function()

i=0
for row in constraints[~constraints.RHS.isna()].itertuples():
    prob += (
        pulp.lpSum([getattr(row, crops_year[i]) * crops_var[i] for i in crops_year]) <= getattr(row, 'RHS'),
        f"C_{i}",
    )

    i += 1



prob.writeLP('model_1y.lp')
solution = prob.solve()

print("\nStatus = {} \nValue = {}".format(pulp.LpStatus[solution], pulp.value(prob.objective)))
    

