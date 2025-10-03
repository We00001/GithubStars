import requests
from urllib.parse import urlparse
import logging
import os


logging.basicConfig(level=logging.INFO,
                    filename='logs/star_scraper.log',
                    filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def crawl_star(github_link, token):
    
    if "/" not in github_link:
        return ""
    
    parsed_url = urlparse(github_link)
    parts = parsed_url.path.strip("/").split("/")
    
    if len(parts) >= 2:
        username, repo_name = parts[0], parts[1]
    else:
        return "Error: Invalid GitHub URL"

    if username is None or repo_name is None:
        return "Error: Invalid GitHub URL"

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
            logging.info(f"{url}Error: {response.status_code} - {response.json().get('message', 'Unknown error')}")

            return None

import pandas as pd
from datetime import date
from tqdm import tqdm
def star_scraper(input_file, output_file, token = os.getenv("GITHUB_API_KEY")):
    today = date.today()
    tqdm.pandas(desc="Crawling GitHub Stars")
    df = pd.read_csv(input_file)
    # If today's column already exists, overwrite it
    if today in df.columns:
        df.drop(columns=[today], inplace=True)
    df[today] = df["Github_Link"].progress_apply(crawl_star, token = token)
    df.to_csv(output_file,index=False)
    return None
        
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, default= "data", help="the path of folder you want to save the data")
    args = parser.parse_args()

    from dotenv import load_dotenv
    import os
    load_dotenv()
    token = os.getenv("GITHUB_API_KEY")

    file_path = os.path.join(args.path, "star.csv")
    backup_path = os.path.join(args.path, "star_backup.csv")

    import shutil

    if not os.path.exists(file_path):
        shutil.copyfile(os.path.join(args.path, "githublink.csv"),file_path)
        df = pd.read_csv(file_path)
        df = df.drop_duplicates
        df.to_csv(file_path, index=False)
    else:
        shutil.copyfile(file_path, backup_path)
        df = pd.read_csv(file_path)
        df_new = pd.read_csv(os.path.join(args.path, "githublink.csv"))
        key = "Arxiv_ID"
        df_filtered = df_new[~df_new[key].isin(df[key])]
        df = pd.concat([df, df_filtered], ignore_index=True)
        df.to_csv(file_path, index=False)

    star_scraper(file_path, file_path, token)
