import pandas as pd
import numpy as np
from typing import Callable
import random


def coin_flip(chanches: float = 0.80) -> bool:
    if random.random() < chanches:
        return True
    else:
        return False


def produce_outliers(value: str | int | None) -> str | int:
    if str(value).isalpha():
        return value
    elif value is None:
        return value
    elif str(value).isnumeric() and value == 0:
        return np.random.randint(-100, -1)
    elif str(value).isnumeric():
        return -value


def set_string(value: str | int | None) -> str:
    if str(value).isalpha():
        return value
    elif str(value).isnumeric():
        return str(value)


def set_numeric(value: str | int | None) -> str | int:
    if str(value).isalpha():
        return value
    elif value is None:
        return pd.NA
    elif isinstance(value, str):
        return np.random.randint(0, 2009)


def new_categories(value: str) -> str:
    if value in ['F', 'M']:
        return np.random.choice(['B', 'NB', 'FTM', 'MTF', 'OTHER', ''])
 

def produce_nulls(value: str | int | None) ->   None:
    value = pd.NA
    return value


def apply_funcs(dataframe: pd.DataFrame, funcs: list[Callable], row: int) -> pd.DataFrame:
    random_affected_cols = np.random.choice(np.arange(0, 39), size=len(funcs), replace=False)
    for func, col  in zip(funcs, random_affected_cols):
        current_value = dataframe.iat[row, col]
        data_issue = func(current_value) 
        dataframe.iloc[[row], [col]] = data_issue
    return dataframe


def set_data_issues(dataframe: pd.DataFrame, affected_rows: dict) -> pd.DataFrame:
    check_key_value_match = [k for (k,v) in affected_rows.items() if k == v]
    issues_dict = {1: produce_nulls, 2: new_categories, 3: set_numeric, 4: set_string, 5: produce_outliers}
    if check_key_value_match:
        col_number = np.random.randint(0, 39)
        return dataframe.drop(dataframe.columns[col_number], axis=1)

    else:
        for k, v in affected_rows.items():
            pick_random_issue = np.random.choice(np.arange(1, 6), size=5, replace=False)
            funcs = [func for (k, func) in issues_dict.items() if k in pick_random_issue]
            dataframe = apply_funcs(dataframe, funcs, row=k)
            
        return dataframe


def determine_affected_rows(dataframe: pd.DataFrame) -> dict:
    number_of_rows = dataframe.shape[0] - 1
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
        return dataframe
    else:
        return dataframe
