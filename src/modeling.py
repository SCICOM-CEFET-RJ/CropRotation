import numpy as np

import pulp

def create_integer_vars(_crops_year, df):

    return dict(zip(_crops_year.keys(),
            [pulp.LpVariable(i, 
                                lowBound = df.loc[_crops_year[i], 'int_lb'] if not np.isnan(df.loc[_crops_year[i], 'int_lb']) else None, 
                                upBound  = df.loc[_crops_year[i], 'int_ub'] if not np.isnan(df.loc[_crops_year[i], 'int_ub']) else None,
                                cat='Integer') 
                    for i in _crops_year.keys()]))


def create_binary_vars(_crops_year, df):

    return dict(zip(_crops_year.keys(),
            [pulp.LpVariable(i, 
                                lowBound = df.loc[_crops_year[i], 'bin_lb'] if not np.isnan(df.loc[_crops_year[i], 'bin_lb']) else None, 
                                upBound  = df.loc[_crops_year[i], 'bin_ub'] if not np.isnan(df.loc[_crops_year[i], 'bin_ub']) else None,
                                cat='Binary') 
                    for i in _crops_year.keys()]))

def slice_dict(_crops_year, start, end):
    crops = dict(list(_crops_year.items())[start:end])
    return crops

def add_constraints(_model, _var, _const, _crops_year, n_crops, n_years, const_id = 0):

    for year in range(n_years):

        crops = slice_dict(_crops_year, year * n_crops, (year + 1) * n_crops)
    
        for row in _const.itertuples():

            constraint = pulp.lpSum([getattr(row, _crops_year[i]) * _var[i] for i in crops])
            rhs = getattr(row, 'RHS')

            match getattr(row, 'type'):
                case '<=':
                    constraint = constraint <= rhs
                case '<':
                    constraint = constraint < rhs
                case '>=':
                    constraint = constraint >= rhs
                case '>':
                    constraint = constraint > rhs
                case '==':
                    constraint = constraint == rhs
            
            _model += (constraint, f"C_{const_id}_{getattr(row, 'name')}", )

            const_id += 1
    
    return const_id

def add_binary_correlation(_model, _var_bin, _var_int, min_ua_crop, max_ua_available = (10**10),const_id = 0):
    for var in _var_bin.keys():
        constraint = min_ua_crop * _var_bin[var] - _var_int[var.replace('bin', 'int')]
        _model += (constraint <= 0, f"C_{const_id}_Min_UA_Per_Crop__Relation_Bin_Int", )
        const_id += 1

        constraint = _var_int[var.replace('bin', 'int')] - max_ua_available * _var_bin[var] <= 0
        _model += (constraint <= 0, f"C_{const_id}_Relation_Bin_Int", )
        const_id += 1

    return const_id

def add_crop_rotation_constraints(_model, var, crops_year, rotations, n_years, crops, str_var, const_id = 0):
    def aux(row, target_year):
        y = target_year + row['year_step']
        return pulp.lpSum([getattr(row, crops_year[str_var.format(y, i)]) * var[str_var.format(y, i)]  for i in crops])

    for year in range(0, n_years - 1):
        for group in rotations.group.unique().tolist():

            rotation_const = rotations[rotations.group == group]

            str_years = ", ".join([str(year + i) for i in rotation_const.year_step.unique().tolist()])

            constraint = pulp.lpSum(rotation_const.apply(lambda x: aux(x, year), axis=1).to_list()) <= 0

            _model += (constraint, f"C_{const_id}_Crop_Rotation_({str_years})", )

            const_id += 1

    return const_id

def min_max_normalization(of, min_max):
    zn = min_max[0]
    zp = min_max[1]

    _z = zp-zn

    return (of - zn)/_z

def weighted_sum(model, ofs, alphas):
    model += pulp.lpSum([ofs[i] * alphas[i] for i in range(len(ofs))])

def epsilon_constraint(model, ofs, idx_obj, epsilons):
    model += ofs[idx_obj]
    i = 0
    for idx in range(len(ofs)):
        if idx == idx_obj:
            continue
        model += ofs[idx] >= epsilons[i]
        i += 1


def sum_cost_of_values(_cost, _var_values, _crops_year, name, start, end):
    ofs_values = {f'{name}_total': 0} 
    for key, value in _var_values.items():
        var_value = round(value * _cost[_crops_year[key]], 2)
        key_of = f'{name}_{key[start:end]}' 

        if ofs_values.get(key_of) == None:
            ofs_values[key_of] = 0

        ofs_values[f'{name}_total'] += var_value
        ofs_values[key_of] += var_value
    return ofs_values

def sum_of_var_values(_var_values, name, start, end):
    ofs_values = {f'{name}_total': 0} 
    for key, value in _var_values.items():
        var_value = value
        key_of = f'{name}_{key[start:end]}' 

        if ofs_values.get(key_of) == None:
            ofs_values[key_of] = 0

        ofs_values[f'{name}_total'] += var_value
        ofs_values[key_of] += var_value
    return ofs_values

