# GithubStars

## Project Overview
This project aims to collect and visualize the star counts of GitHub repositories related to a specific topic, such as artificial intelligence. The workflow is divided into four main steps:
1.  **Scrape arXiv Papers**: Use the `arxiv_scraper.py` script to fetch paper information from arXiv within a specified category and time range.
2.  **Extract GitHub Links**: Use the `githublink_extractor.py` script to identify and extract GitHub repository links from the scraped papers.
3.  **Scrape Star Counts**: Use the `star_scraper.py` script to get the current star count for each GitHub repository.
4.  **Generate a Visualization Webpage**: Use the `visualization.py` script to process the collected data and create an interactive webpage for visualization.

## Prerequisites
Before running any scripts, ensure you have all the necessary Python libraries installed.
```bash
pip install -r requirements.txt
```

## Usage Guide
### 1. Scrape arXiv Papers
Run the `arxiv_scraper.py` script to download paper information. You can specify the search query, maximum number of results, and date range using command-line arguments.

**Example Command:**
```bash
python arxiv_scraper.py --query "computer science" --max_results 100 --start_date "2024-01-01" --end_date "2024-02-01"
```
This script will save the scraped data to a file named `arxiv_papers.json`.

### 2. Extract GitHub Links
Run the `githublink_extractor.py` script to extract GitHub links from the `arxiv_papers.json` file generated in the previous step.

**Example Command:**
```bash
python githublink_extractor.py
```
This script will save the extracted GitHub repository links to a file named `github_repos.json`.

### 3. Scrape Star Counts
Run the `star_scraper.py` script, which will read the links from `github_repos.json` and fetch the star count for each repository.

**Example Command:**
```bash
python star_scraper.py
```
This script will save the repository names and their corresponding star counts to a file named `repo_stars.json`.

### 4. Generate Visualization Webpage
Run the `visualization.py` script to generate the final visualization webpage. This script will read the `repo_stars.json` file and create an interactive chart in a file named `visualization.html`.

**Example Command:**
```bash
python visualization.py
```
After execution, you can find `visualization.html` in the project directory and open it with a browser to view the results.