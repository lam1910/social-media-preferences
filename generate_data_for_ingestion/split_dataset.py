from pathlib import Path
import pandas as pd
import numpy as np
import argparse


def split_dataset(partitions: int, path: str = None, shuffle: bool = False) -> None:
    # Define folder/directory for data ingestion
    data_folder = Path('airflow/data/raw_data')

    # Convert into Path the path argument
    source_file_path = Path(path)

    # Make sure to create the data_folder directories
    if not data_folder.exists():
        data_folder.mkdir(parents=True, exist_ok=True)

    try:
        # Read the provided csv into a DataFrame
        df = pd.read_csv(source_file_path, dtype={'gender': 'str'}, keep_default_na=False)

        if shuffle:
            df = df.sample(frac=1).reset_index(drop=True)

        # Get the index of the last record
        max_index = int(df.tail(1).index[0])

        # Create equidistant data points from 0 to max index
        index_partitions = np.linspace(start=0, stop=max_index, num=partitions * 2, dtype=np.int16).tolist()

        # Zip index partitions in pairs
        ordered_ranges = zip(index_partitions[0::2], index_partitions[1::2])

        # For every pair, create a csv file into the raw_data directory
        for pair in ordered_ranges:
            df.iloc[pair[0]:pair[1]].to_csv(
                path_or_buf=Path(data_folder / f'dataset_partition_{pair[0]}_{pair[1]}.csv'),
                index=False
            )

        print('Data split done!')

    except Exception as e:
        print(f'Something went wrong: {e}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Split a dataset into partitions.')
    parser.add_argument('--path', type=str, required=True, help='Path to the CSV file')
    parser.add_argument('--partitions', type=int, required=True, help='Number of partitions')
    parser.add_argument('--shuffle', action='store_true', help='Shuffle the data before splitting')

    args = parser.parse_args()

    split_dataset(partitions=args.partitions, path=args.path, shuffle=args.shuffle)




