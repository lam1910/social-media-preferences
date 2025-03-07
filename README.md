# Students' Social Network Profile Clustering

This project focuses on clustering students' social network profiles to identify distinct friend groups based on various attributes. The dataset used for this project is sourced from Kaggle: [Students Social Network Profile Clustering](https://www.kaggle.com/datasets/zabihullah18/students-social-network-profile-clustering).

## Table of Contents
1. [Introduction](#introduction)
2. [Dataset](#dataset)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Methodology](#methodology)
6. [Results](#results)
7. [Contributing](#contributing)

## Introduction
The aim of this project is to cluster students into distinct friend groups based on their social network profiles. Clustering allows us to understand the underlying patterns and relationships among students, which can be useful for sociological studies, targeted educational interventions, and enhancing social experiences within educational institutions.

## Dataset
The dataset contains the social network profiles of students and includes various attributes such as:
- Age
- Gender
- Number of friends
- Interests gauging by frequency of word on social media post

You can access the dataset [here](https://www.kaggle.com/datasets/zabihullah18/students-social-network-profile-clustering).

## Installation
To run this project locally, please follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/lam1910/social-media-preferences.git
    ```

2. Navigate to the project directory:
    ```bash
    cd social-media-preferences
    ```

3. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage
To perform clustering on the dataset, follow these steps:

1. Load the dataset:
    ```python
    import pandas as pd
   
    df = pd.read_csv('03_Clustering_Marketing.csv')
    ```

2. Preprocess the data (handling missing values, encoding categorical variables, etc.)

3. Apply clustering algorithms (e.g., K-means, hierarchical):
    ```python
    from sklearn.cluster import KMeans

    kmeans = KMeans(n_clusters=7)
    kmeans.fit(df)
    ```

## Methodology
The methodology followed in this project includes:

1. Data Preprocessing: Cleaning and preparing the dataset for clustering.
2. Feature Selection: Selecting relevant features for clustering.
3. Clustering: Applying different clustering algorithms to identify friend groups.

## Results
The results of this project include the identification of 7 distinct friend groups among students based on their social network profiles. See more at [cluster notebook](model/notebook/cluster-friend-gropup.ipynb)

## Contributing
Contributions are welcome! If you have any suggestions or improvements, please fork the repository and submit a pull request.