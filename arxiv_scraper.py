import requests
import logging
import xml.etree.ElementTree as ET
import csv
import os
import time
from datetime import datetime, timedelta

# --- Configuration & Constants ---

# BEST PRACTICE: Use constants for URLs and namespaces
BASE_URL = "http://export.arxiv.org/api/query"
ARXIV_NS = {'atom': 'http://www.w3.org/2005/Atom'}
OPENSEARCH_NS = {'opensearch': 'http://a9.com/-/spec/opensearch/1.1/'}

# BEST PRACTICE: Set up basic logging to a file
logging.basicConfig(level=logging.INFO,
                    filename='logs/arxiv_scraper.log',
                    filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- Core Functions ---

def get_total_results(search_query: str) -> int:
    """
    Performs a single API query to get the total number of results for a search.
    This is used to check if a date range is too large.
    """
    params = {'search_query': search_query, 'max_results': 1}
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        total_results_tag = root.find('opensearch:totalResults', OPENSEARCH_NS)
        return int(total_results_tag.text) if total_results_tag is not None else 0
    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed while checking total results: {e}")
        return 0
    except ET.ParseError as e:
        logging.error(f"XML parse failed while checking total results: {e}")
        return 0

def crawl_paper_api(search_query: str, max_results: int = 100, start: int = 0) -> list:
    """
    Crawls arXiv using a specific search query and returns a list of papers.
    
    Args:
        search_query (str): The complete arXiv search query string.
        max_results (int): Maximum number of papers to retrieve per request.
        start (int): Starting index for pagination.
    
    Returns:
        list: List of [title, pdf_url, published_date] lists.
    """
    papers = []
    params = {
        'search_query': search_query,
        'start': start,
        'max_results': max_results,
        'sortBy': 'submittedDate',
        'sortOrder': 'descending'
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        entries = root.findall('.//atom:entry', ARXIV_NS)
        
        if not entries:
            return []
        
        for entry in entries:
            title = entry.find('atom:title', ARXIV_NS).text.strip()
            # The ID contains the version number, which we can strip
            arxiv_id_full = entry.find('atom:id', ARXIV_NS).text.split('/')[-1]
            arxiv_id = arxiv_id_full.split('v')[0] # remove version e.g. v1
            pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
            published_date = entry.find('atom:published', ARXIV_NS).text.strip()
            papers.append([arxiv_id,title, pdf_url, published_date])
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch papers (start={start}): {e}")
    except ET.ParseError as e:
        logging.error(f"Failed to parse XML response (start={start}): {e}")
    except Exception as e:
        logging.error(f"Unexpected error in crawl_paper_api (start={start}): {e}")
    
    return papers

def arxiv_scraper(csv_file_path, category="cs.AI", data_folder="data", start_date="2023-01-01", end_date=None):
    """
    Main function to crawl arXiv by breaking down the query into monthly chunks
    to avoid the total results limit, then paginates through each chunk.
    """
    
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m-%d')
    
    # Create data folder if it doesn't exist
    os.makedirs(data_folder, exist_ok=True)

    # Write header to CSV file
    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Arxiv_ID','Title', 'Pdf_Link', 'Published_Date'])

    logging.info(f"Starting crawl for category '{category}' from {start_date} to {end_date}.")
    print(f"Saving data to {csv_file_path}")

    # --- NEW: Date-chunking logic ---
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
    total_papers_crawled = 0

    while current_date <= end_datetime:
        # Define the start and end of the current month
        month_start = current_date.strftime('%Y%m%d')
        next_month = (current_date.replace(day=28) + timedelta(days=4))
        month_end_date = next_month - timedelta(days=next_month.day)
        month_end = month_end_date.strftime('%Y%m%d')

        # Construct the query for the current month
        date_query = f"submittedDate:[{month_start} TO {month_end}]"
        search_query = f'cat:{category} AND {date_query}'
        
        total_in_month = get_total_results(search_query)
        print(f"\nFound {total_in_month} papers for {current_date.strftime('%B %Y')}. Starting crawl...")
        logging.info(f"Querying month {month_start}-{month_end}. Total results: {total_in_month}")

        # --- MODIFIED: Pagination loop is now inside the date loop ---
        start_index = 0
        max_results_per_req = 1000 # You can keep this high
        
        while True:
            # BEST PRACTICE: Be a good citizen and don't spam the API
            time.sleep(3) 
            
            papers = crawl_paper_api(search_query, max_results=max_results_per_req, start=start_index)
            
            if not papers:
                break # No more papers in this month

            # Append results to the CSV
            with open(csv_file_path, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(papers)
            
            num_retrieved = len(papers)
            total_papers_crawled += num_retrieved
            print(f"  > Retrieved {num_retrieved} papers (total so far: {total_papers_crawled})")
            
            start_index += num_retrieved
            
            # This check is important if the API returns fewer than max_results
            if num_retrieved < max_results_per_req:
                break

        # Move to the first day of the next month
        current_date = month_end_date + timedelta(days=1)

    print(f"\nCrawl finished. Total papers saved: {total_papers_crawled}")
    return csv_file_path

if __name__ == "__main__":

    arxiv_scraper(csv_file_path="data/arxiv_test.csv", 
                  category="cs.AI",
                  start_date="2024-01-28", end_date="2024-01-31")
