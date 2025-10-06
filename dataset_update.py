# This script combines the logic of your three previous scripts into one efficient workflow.
# It reads from APIs and writes directly to an SQLite database, avoiding high memory usage.
import os
import sqlite3
import pandas as pd
from tqdm import tqdm
from datetime import date
from dotenv import load_dotenv

from scripts.githublink_extractor import extract_github
from scripts.arxiv_scraper import arxiv_scraper
from scripts.star_scraper import crawl_star
from datetime import datetime, timedelta

# --- Configuration & Setup ---
load_dotenv()
# Load environment variables (ensure they are set in .env or Render dashboard)
GITHUB_API_KEY = os.getenv("STAR_API_KEY")
# ... add other initializations for your scrapers here ...
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
category = "cs.AI"


start_date = (datetime.now()-timedelta(days=3)).strftime('%Y-%m-%d')
end_date = (datetime.now()-timedelta(days=2)).strftime('%Y-%m-%d')
print(start_date)
print(end_date)
# The database will be stored on Render's persistent disk.
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "arxiv.db")

def initialize_database():
    """Create the database and tables if they don't exist."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Papers table: Stores general information about each paper.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                arxiv_id TEXT UNIQUE NOT NULL,
                title TEXT,
                pdf_link TEXT,
                published_date TEXT,
                github_link TEXT
            )
        ''')
        # Star Counts table: Stores star counts for each paper on different dates.
        # This "long" format is much more scalable than adding a new column every day.
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS star_counts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paper_id INTEGER,
                check_date TEXT,
                stars INTEGER,
                FOREIGN KEY (paper_id) REFERENCES papers (id),
                UNIQUE(paper_id, check_date)
            )
        ''')
            # Create indexes if they don't exist
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_star_counts_date ON star_counts(check_date);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_star_counts_paper ON star_counts(paper_id);")
        
        conn.commit()

def update_papers_from_arxiv():
    """
    Simulates arxiv_scraper.py and githublink_extractor.py.
    Fetches new papers, finds their GitHub links, and adds them to the database.
    """
    print("Fetching new papers from ArXiv...")
    
    # --- Your scraping logic goes here ---
    # Your arxiv_scraper.py should produce data in this format.
    # new_papers_list = your_arxiv_scraper_function()
    
    # For demonstration, we'll use a sample of the data you provided.

    new_papers_list = arxiv_scraper( 
                category=category,
                start_date=start_date, 
                end_date=end_date,
                output= False)
    # --- End of your scraping logic ---
    
    print(f"Found {len(new_papers_list)} new papers. Processing and adding to database...")
    
    # Prepare data for insertion
    papers_to_insert = []
    for paper_data in tqdm(new_papers_list, desc="Processing papers"):
        arxiv_id, title, pdf_link, published_date = paper_data
        
        # --- Your GitHub link extraction logic goes here ---
        # Call your function to find the GitHub link for the paper.
        # github_link = your_github_extractor_function(paper_data)
        # For demonstration, we'll use a placeholder.
        prompt1 = (
        "I will provide an article about AI. I need you to find out the GitHub link for the article's project. "
        "Do not provide any links that are cited or referenced. "
        "Provide the link with this form: 'The Github Link is: https://...' or I didn't find the project link"
    )
        prompt2 = (
        "The article ends. I need you to find out the GitHub link for the article's project. "
        "Do not provide any links that are cited or referenced."
    )
        github_link = extract_github(prompt1, prompt2, api_key= GEMINI_API_KEY, pdf_url=pdf_link)
        print(github_link)
        if github_link is None:
            github_link = "not_found"

        # --- End of your GitHub link logic ---
        
        papers_to_insert.append((arxiv_id, title, pdf_link, published_date, github_link))

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Use executemany for efficient bulk insertion.
        # INSERT OR IGNORE prevents errors if a paper's arxiv_id already exists.

        cursor.executemany('''
            INSERT INTO papers (arxiv_id, title, pdf_link, published_date, github_link)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(arxiv_id) DO UPDATE SET
            title = excluded.title,
            pdf_link = excluded.pdf_link,
            published_date = excluded.published_date,
            github_link = excluded.github_link
        ''', papers_to_insert)
        conn.commit()
        
    print(f"Database update complete. {cursor.rowcount} new papers were added.")


def update_star_counts():
    """
    Simulates star_scraper.py.
    Gets all papers from the DB and updates their star counts for the current day.
    """
    print("Updating star counts for all tracked papers...")
    with sqlite3.connect(DB_PATH) as conn:
        # Fetch all papers we need to check.
        cursor = conn.cursor()
        cursor.execute("SELECT id, github_link FROM papers WHERE github_link LIKE 'https://%'")
        papers_to_check = cursor.fetchall()

        today_str = date.today().isoformat()
        print(today_str)
        star_updates = []

        print(f"Found {len(papers_to_check)} papers with GitHub links to update.")
        for paper_id, github_link in tqdm(papers_to_check, desc="Checking GitHub links"):
            # --- Your star scraping logic goes here ---
            # Use the GITHUB_API_KEY to fetch the star count for github_link.
            # Example: stars = your_star_scraper_function(github_link, GITHUB_API_KEY)
            # For demonstration, we'll use a random number.
            stars = crawl_star(github_link, token = GITHUB_API_KEY)
            # --- End of your star scraping logic ---
            if stars is not None:
                star_updates.append((paper_id, today_str, stars))

        # Use INSERT OR REPLACE to add today's count or update it if the script is run twice.
        cursor.executemany('''
            INSERT OR REPLACE INTO star_counts (paper_id, check_date, stars)
            VALUES (?, ?, ?)
        ''', star_updates)
        conn.commit()
    print("Star counts updated for today.")


if __name__ == "__main__":
    initialize_database()
    update_papers_from_arxiv()
    update_star_counts()
    print("Database update process finished.")

