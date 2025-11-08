# [GithubStars](https://arxiv-star-viewer.onrender.com)

## View the Website [GithubStars](https://arxiv-star-viewer.onrender.com)

## Project Overview
This project aims to collect and visualize the star counts of GitHub repositories related to a specific topic, such as artificial intelligence. The workflow is divided into four main steps:
1.  **Scrape arXiv Papers**: Use the `arxiv_scraper.py` script to fetch paper information from arXiv within a specified category and time range.
2.  **Extract GitHub Links**: Use the `githublink_extractor.py` script to identify and extract GitHub repository links from the scraped papers with LLM model: Gemini 2.5 pro.
3.  **Scrape Star Counts**: Use the `star_scraper.py` script to get the current star count for each GitHub repositories.
4.  **Generate a Visualization Webpage**: Use the `app.py` script to host an interactive webpage for visualization.

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
