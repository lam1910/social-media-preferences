
# PostgreSQL Setup Guide

This Setup Guide will walk you step-by-step through the process of installing PostgreSQL and setting up the database, schema and tables used for this project.

## Prerequisites

- OS: Windows

## Installation

### 1. Install PostgreSQL
- Download from [PostgreSQL Official Site](https://www.postgresql.org/download/)
- Follow the installation instructions for your OS.

### 2. Start PostgreSQL

- **Using Services Manager:**
   1. Press `Win + R`, type `services.msc`, and press `Enter`.
   2. In the **Services** window, scroll down to find **PostgreSQL** (it will typically be listed as **PostgreSQL <version>**).
   3. Right-click on the PostgreSQL service and select **Start** if it is not already running.
   4. If PostgreSQL does not appear in the service window, it might not have been appropriately installed. In this case, try reinstalling it.

## Verify Installation

Run:
```sh
psql --version
```
- If PostgreSQL is installed correctly, you should see a version number.

## Troubleshooting

- **Issue:** `"psql: command not found"`  
  **Solution:** Add PostgreSQL to your system's PATH.

  **Steps:**
    1. Open the Start menu, search for "Environment Variables," and select **Edit the system environment variables**.
    2. In the System Properties window, click **Environment Variables**.
    3. Under the **System variables** section, scroll down and select **Path**, then click **Edit**.
    4. Click **New** and add the path to the PostgreSQL `bin` directory (e.g., `C:\Program Files\PostgreSQL\<version>\bin`).
    5. Click **OK** to save the changes.
    6. Verify the changes by running:
       ```sh
       psql --version
       ```

  After following the steps for your operating system, reopen your terminal or command prompt and try running the `psql` command again.

## Database Setup

### 1. Open the PostgreSQL interactive terminal:
   - **Windows**:
     - Open **Command Prompt** or **PowerShell**, and type the following:
       ```sh
       psql -U postgres
       ```
     - You may need to navigate to the PostgreSQL `bin` directory if the `psql` command is not in your system’s PATH.

### 2. Create a new database:
   - Please refer to the Raw_Database.sql for more instructions.

### 3. Create a Schema:
   - Please refer to the Raw_Database.sql for more instructions.

## Configuration

- Default username: `postgres`
- Default port: `5432`
- To modify settings, edit `postgresql.conf`. This can be accessed through:
  - **Windows**: `C:\Program Files\PostgreSQL\<version>\data\postgresql.conf`

## Create the Raw Marketing Data Table
  - Please refer to the Raw_Database.sql for more instructions.

## Create the Past Predictions Table
  - Please refer to the Past_Predictions.sql for more instructions.



