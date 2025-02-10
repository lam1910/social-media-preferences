# Follow-up session 1

For this follow-up session, you need to do a demo of the following components: (**please refer to the project instructions for details of each section**)

1. Webapp, API and database
<p align="center">
    <img
        height="250"
        src="../images/project-webapp-api-db.png"
        alt="Webapp - API - DB components"
    />
</p>

2. Notebook to generate data issues in your raw dataset

3. Script to generate data for data ingestion job

4. Simple ingestion pipeline

An airflow dag to ingest the data from *raw-data* folder to *good-data* folder one file at a time.

This dag should be composed of 2 tasks for now:

- read-data: reads one file randomly from *raw-data* and return the file path
- save-file: moves the file from *raw-data* to *good-data*


## Grading criteria

- Only integrated services and working features will be validated
- All code should be in a `Github` repository in the `main` branch
- Up to date `README.md` with installation and setup steps
- Commits in the main branch correspond to each of the components (1 commit for UI, 1 commit for API, 1 commit for UI and API integration, etc)
- Each group member should have a minimum of one (real ;) commit in the branch) to be considered as contributing to the project

Good luck 🤞 🍀
