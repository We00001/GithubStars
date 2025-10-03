# [GithubStars](https://arxiv-star-viewer-ra4s.onrender.com)

## Project Overview
This project aims to collect and visualize the star counts of GitHub repositories related to a specific topic, such as artificial intelligence. The workflow is divided into four main steps:
1.  **Scrape arXiv Papers**: Use the `arxiv_scraper.py` script to fetch paper information from arXiv within a specified category and time range.
2.  **Extract GitHub Links**: Use the `githublink_extractor.py` script to identify and extract GitHub repository links from the scraped papers.
3.  **Scrape Star Counts**: Use the `star_scraper.py` script to get the current star count for each GitHub repository.
4.  **Generate a Visualization Webpage**: Use the `visualization.py` script to process the collected data and create an interactive webpage for visualization.

## Web Server
Run the `app.py` script to start the web server. Run the `dataset_update.py` script to update new articles. NOTE: the `dataset_update.py` script captures the article from 3 days before running day to 2 days before running day.


## Prerequisites & Setup

Before running the project, make sure you have **Python 3.8+** installed.  

Clone the repository:
```bash
git clone https://github.com/We00001/GithubStars.git
cd GithubStars
```

Create a virtual environment:
```bash
python3 -m venv myenv
```

Activate the virtual environment (choose the command for your OS):

Linux/macOS:
```bash
source myenv/bin/activate
```

Windows (Command Prompt):
```bash
myenv\Scripts\activate.bat
```

Windows (PowerShell):
```bash
myenv\Scripts\Activate.ps1
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration  
The `.env.example` file lists the environment variables that may need to be configured (such as the arXiv API key, GitHub token, etc.).
Copy `.env.example` to `.env` and fill in the actual values.

## Usage Guide
### 1. Scrape arXiv Papers
Run the `arxiv_scraper.py` script to download paper information. You can specify the search query, maximum number of results, and date range using command-line arguments.

**Example Command:**
```bash
python arxiv_scraper.py
```
This script will save the scraped data to a file named `arxiv_papers.json`.

### 2. Extract GitHub Links
Run the `githublink_extractor.py` script to extract GitHub links from the `arxiv_test.csv` file generated in the previous step.

**Example Command:**
```bash
python githublink_extractor.py
```
This script will save the extracted GitHub repository links to a file named `githublink_test.csv`.

### 3. Scrape Star Counts
Run the `star_scraper.py` script, which will read the links from `github_repos.json` and fetch the star count for each repository.

**Example Command:**
```bash
python star_scraper.py
```
This script will save the repository names and their corresponding star counts to a file named `star_test.csv`.

### 4. Generate Visualization Webpage
Run the `visualization.py` script to generate the final visualization webpage. This script will read the `repo_stars.json` file and create an interactive chart in a file named `visualization.html`.

**Example Command:**
```bash
python visualization.py
```
After execution, you can find `visualization.html` in the project directory and open it with a browser to view the results.
