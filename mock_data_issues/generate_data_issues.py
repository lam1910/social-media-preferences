import pandas as pd
import numpy as np
from typing import Callable
import random


def coin_flip(chances: float = 0.80) -> bool:
    if random.random() < chances:
        return True
    else:
        return False


def produce_outliers(value: str | int | None) -> str | int:
    print(f'Producing outlier, input value={value}')
    if str(value).isalpha():
        return value
    elif value is None:
        return value
    elif str(value).isnumeric() and value == 0:
        return np.random.randint(-100, -1)
    elif str(value).isnumeric():
        return -value


def set_string(value: str | int | None) -> str:
    print(f'Setting as String, input value={value}')
    if str(value).isalpha():
        return value
    elif str(value).isnumeric():
        return str(value)


def set_numeric(value: str | int | None) -> str | int:
    print(f'Setting numerical value, input value={value}')
    if str(value).isalpha():
        return value
    elif value is None:
        return pd.NA
    elif isinstance(value, str):
        return int(np.random.randint(0, 2009))


def produce_nulls(value: str | int | None) -> pd.NA:
    print('Producing Null value')
    value = pd.NA
    return value


def new_categories(value: str) -> str:
    if random.random() > 0.1:
        if value in ['F', 'M', 'NA']:
            print(f'Producing new category for gender, input value={value}')
            return np.random.choice(['B', 'NB', 'FTM', 'MTF', 'OTHER', ''])
        else:
            return produce_nulls(value)


def grad_year_issues(value: int) -> int | None:
    lower_grad_bound = np.random.randint(1900, 2005)
    upper_grad_bound = np.random.randint(2010, 2025)
    
    if random.random() > 0.3:
        print('Producing grad out of bounds values')
        return np.random.choice([lower_grad_bound, upper_grad_bound])
    else:
        if random.random() > 0.5:
            print('Producing null')
            return produce_nulls(value)
        else:
            print('Producing outliers')
            return produce_outliers(value)


def age_data_issues(value: float) -> int | None:
    random_old_age = np.random.randint(100, 150)
    if random.random() > 0.3:
        print('Producing unrealistic ages')
        return random_old_age
    else:
        if random.random() > 0.5:
            print('Producing null')
            return produce_nulls(value)
        else:
            print('Producing outliers')
            return produce_outliers(value)


def number_of_friends_issues(value: int) -> int | None:
    rand_num = np.random.randint(606, 10_000)

    if random.random() > 0.5:
        print('Producing more num of friends')
        return rand_num
    else:
        print('Producing null')
        return produce_nulls(value)


def new_feature(dataframe: pd.DataFrame) -> pd.DataFrame:
    protected_cols = ['gradyear', 'gender', 'age', 'NumberOffriends', 'volleyball', 'drunk', 'drugs']
    rename_candidates = [col for col in dataframe.columns if col not in protected_cols]

    new_features = ['iphone', 'highschool', 'summer', 'videogames', 'youtube', 'lol', 'tacos', 'tequila']
    random_new_feature = np.random.choice(new_features)

    if random.random() > 0.5:
        if rename_candidates:
            current_col_name = np.random.choice(rename_candidates)
            if not random_new_feature in dataframe.columns:
                dataframe = dataframe.rename(columns={current_col_name: random_new_feature})
            return dataframe
    else:
        dataframe[random_new_feature] = np.random.choice([0, 1], size=len(dataframe))

    return dataframe


issues_dict = {
    1: produce_nulls,
    2: new_categories,
    3: set_numeric,
    4: set_string,
    5: produce_outliers,
}


def apply_funcs(dataframe: pd.DataFrame, row: int, funcs: list[Callable]) -> pd.DataFrame:
    random_col = np.random.choice([
        'gradyear', 'gender', 'age', 
        'NumberOffriends', 'volleyball', 'drunk', 'drugs'
    ])
    
    col_idx = dataframe.columns.get_loc(random_col)
    current_value = dataframe.iat[row, col_idx]

    if random.random() > 0.3:
        if random_col == 'gradyear':
            data_issue = grad_year_issues(current_value)
        elif random_col == 'gender':
            data_issue = new_categories(current_value)
        elif random_col == 'age':
            data_issue = age_data_issues(current_value)
        elif random_col == 'NumberOffriends':
            data_issue = number_of_friends_issues(current_value)
        elif random_col in ['volleyball', 'drunk', 'drugs']:
            rand_func = np.random.choice(funcs)
            data_issue = rand_func(current_value)
        
        dataframe.iat[row, col_idx] = data_issue
        print(f"Affected column = {random_col}, affected row = {row}")
    else:
        print('Producing new feature')
        dataframe = new_feature(dataframe)

    return dataframe


def set_data_issues(dataframe: pd.DataFrame, affected_rows: dict) -> pd.DataFrame:
    check_key_value_match = [k for (k, v) in affected_rows.items() if k == v]
    print(f'Dropping col? {'yes' if check_key_value_match else 'no'}')
    protected_cols = ['gradyear', 'gender', 'age', 'NumberOffriends', 'volleyball', 'drunk', 'drugs']
    unprotected_columns = [col for col in dataframe.columns if col not in protected_cols]

    if unprotected_columns and random.random() < 0.2:
        col_to_drop = np.random.choice(unprotected_columns)
        print(f"Dropped column: {col_to_drop}")
        return dataframe.drop(columns=[col_to_drop])
    else:
        for k, v in affected_rows.items():
            pick_random_issue = np.random.choice(np.arange(1, 6), size=5, replace=False)
            funcs = [func for (k, func) in issues_dict.items() if k in pick_random_issue]
            dataframe = apply_funcs(dataframe, funcs=funcs, row=k)
        return dataframe


def determine_affected_rows(dataframe: pd.DataFrame) -> dict:
    number_of_rows = dataframe.shape[0] - 1
    print(f'Dataframe shape {dataframe.shape}')
    afected_rows = np.random.randint(1, number_of_rows, size=number_of_rows)
    set_issues_dict = {}
    for idx in afected_rows:
        if idx not in set_issues_dict.keys():
            set_issues_dict[idx] = 1
        else:
            set_issues_dict[idx] += 1
    return {k:v for (k, v) in set_issues_dict.items() if v > 1}


def generate_data_issues(dataframe: pd.DataFrame = None, chances: float = None) -> pd.DataFrame:
    if coin_flip(chances):
        affected_rows = determine_affected_rows(dataframe)
        dataframe = set_data_issues(dataframe, affected_rows)
        for col in ['drunk', 'volleyball', 'drugs']:
            dataframe[col] = pd.to_numeric(dataframe[col], errors='coerce').astype('Int16')
        return dataframe
    else:
        return dataframe
