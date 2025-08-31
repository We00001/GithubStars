import requests
from urllib.parse import urlparse
import logging
import os

logging.basicConfig(level=logging.INFO,
                    filename='logs/star_scraper.log',
                    filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def crawl_star(github_link, token):
        
    parsed_url = urlparse(github_link)
    parts = parsed_url.path.strip("/").split("/")
    
    if len(parts) >= 2:
        username, repo_name = parts[0], parts[1]
    else:
        return False, "Error: Invalid GitHub URL"

    if username is None or repo_name is None:
        return False, "Error: Invalid GitHub URL"

    else:
        url = f"https://api.github.com/repos/{username}/{repo_name}"
        # Set up headers for authentication (optional)
        headers = {"Authorization": f"token {token}"} if token else {}
        # Send GET request to GitHub API
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data['stargazers_count']
        else:
            logging.info(f"Error: {response.status_code} - {response.json().get('message', 'Unknown error')}")

            return None

import pandas as pd
from datetime import date
from tqdm import tqdm
def star_scraper(input_file, output_file, token = os.getenv("GITHUB_API_KEY")):
    today = date.today()
    tqdm.pandas(desc="Crawling GitHub Stars")
    df = pd.read_csv(input_file)
    df[today] = df["Github_Link"].progress_apply(crawl_star, token = token)
    df.to_csv(output_file,index=False)
    return None
        
if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    load_dotenv()
    token = os.getenv("GITHUB_API_KEY")
    star_scraper("data/star_test.csv", "data/star_test.csv", token)
