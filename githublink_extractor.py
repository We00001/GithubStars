from hmac import new
import requests
import csv
import re
import logging
import pikepdf
import time
import xml.etree.ElementTree as ET
from google import genai
from google.genai import types
from bs4 import BeautifulSoup
from logging.handlers import RotatingFileHandler
from pdfminer.high_level import extract_text
from urllib.parse import urlparse

# crawl_paper, obtain title and pdf link with url

def pre_analyze(url, pdf_path="temp.pdf"):
    """" Return True if the PDF contains a GitHub link, otherwise False. """

    # download the pdf
    response = requests.get(url)
    if response.status_code == 200:
        with open(pdf_path, "wb") as f:
            f.write(response.content)
    else:
        logging.info(f"pre_analyze1: {url}, Failed to download PDF: {response.status_code}")
    
    try:
        # extract the clickable URLs
        pdf_file = pikepdf.Pdf.open(pdf_path)
        urls = []
        # iterate over PDF pages
        for page in pdf_file.pages:
            if page.get("/Annots") is not None:
                for annots in page.get("/Annots"):
                    action = annots.get("/A")
                    if action is not None:
                        uri = action.get("/URI")
                    else:
                        uri = None 
                    if uri is not None:
                        urls.append(uri)
        
        # extract the in-text URLs
        url_regex = r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*[a-zA-Z0-9/])" # extract raw text from pdf
        text = extract_text(pdf_path)

        # extract all urls using the regular expression
        for match in re.finditer(url_regex, text):
            url = match.group()
            urls.append(url)

        if any("github" in str(url) for url in urls):
            return True, text 
        else:
            return False, None
        
    except Exception as e:
        logging.info(f"pre_analyze2: {url}, Failed to extract URLs or PDF file: {e}")
        return False, None

def analyze(text, prompt1, prompt2, api_key):

    attempt = 0
    delay = 5
    while attempt < 5:
        try:
            client = genai.Client(api_key= api_key)
            response = client.models.generate_content(
                model=os.getenv("GOOGLE_MODEL"), 
                contents= prompt1 + text + prompt2,
                config=types.GenerateContentConfig(temperature=0,
                                                    top_p = 0.3,
                                                    top_k = 40)
            )
            return True, response.text
        
        except Exception as e:
            print(e)
            if "503" in str(e):
                logging.info(f"Analyze1: Attempt {attempt + 1}: Got 503 error, retrying in {delay} seconds...")
                attempt += 1
                time.sleep(delay)
            else:
                logging.info(f"Analyze2: Failed to analyze text: {e}")
                return False, str(e)


def analyze_response(response):

    # return the requir urls
    url_pattern1 = r"https?://github\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+[a-zA-Z0-9_-]"
    url_pattern2 = r"\bgithub\.com/[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+\b"
    if response is not None:
        urls = re.findall(url_pattern1, response)
        urls2 = re.findall(url_pattern2, response)
        for link in urls2:
            urls.append("https://" + link)
        urls = set(urls)

        # check the urls
        # Regular expression to check if a URL is a GitHub link
        github_url_pattern = re.compile(r"https://github\.com/")

        # Filter out only GitHub URLs
        github_urls = [url for url in urls if github_url_pattern.match(url)]

        if len(github_urls) == 1:
            return True, github_urls[0]
        else:
            return False, "Error: Multiple GitHub URLs found"
    else:
        return False, None
    

def write_csv(file_name, data, mode): #write data to cvs
    with open(file_name, mode = mode, newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def extract_github(prompt1, prompt2, api_key, pdf_url = None): # find the github link from articles' author
    if pdf_url is not None:
        # check whether the pdf contain likns.
        url_exist, text = pre_analyze(pdf_url)


        if url_exist:
            sucess, output= analyze(text, prompt1, prompt2, api_key)   # using AI to get author's github link
            #extract the urls from AI's answer
            if not sucess:
                return output
            else:
                url_correct, urls = analyze_response(output)# NEED IMPROVEMENT FOR STRUCTURED OUTPUT


            if url_correct: # make sure the AI give correct urls format
                return urls
            else: 
                return "github link uncorrect"
                # NEED IMPROVEMENT TO HANDLE WRONG MESSAGE FROM GEMINI
                # print(urls)
                # return urls

        else:
            return None
    else:
        return None
    
import shutil
import pandas as pd
from tqdm import tqdm
def githublink_extractor(data_path, gemini_api_key, input_file = "arxiv.csv", output_file = "githublink.csv"):
    prompt1 = "I will provide an article about AI. I need you to find out the GitHub link for the article's project. Do not provide any links that are cited or referenced. Provide the link with this form: 'The Github Link is: https://...' or I didn't find the project link"
    prompt2 = "The article ends. I need you to find out the GitHub link for the article's project. Do not provide any links that are cited or referenced."
    csv_file_path = os.path.join(data_path, output_file)
    if not os.path.exists(csv_file_path):
        shutil.copyfile(os.path.join(data_path, input_file), csv_file_path)
        df = pd.read_csv(csv_file_path)
        df["Github_Link"] = ""
    else:
        df = pd.read_csv(csv_file_path)
    
    
    with open (csv_file_path, "r", encoding = "utf-8") as file:
        reader = csv.reader(file)
        header = next(reader)
        all_row = list(reader)
        for row in tqdm(all_row, desc="Processing articles", unit="article"):
            # print(row)
            url = row[2]
            # print(url)
            github_link = extract_github(prompt1, prompt2, gemini_api_key, pdf_url = url)
            if github_link is not None:
                row_new = row + [github_link]
                # print(row_new)
                with open (output_file, "a", encoding = "utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(row_new)

    return None

import os
import shutil
import pandas as pd
from tqdm import tqdm

def githublink_extractor(data_path, gemini_api_key, input_file="arxiv.csv", output_file="githublink.csv"):
    prompt1 = (
        "I will provide an article about AI. I need you to find out the GitHub link for the article's project. "
        "Do not provide any links that are cited or referenced. "
        "Provide the link with this form: 'The Github Link is: https://...' or I didn't find the project link"
    )
    prompt2 = (
        "The article ends. I need you to find out the GitHub link for the article's project. "
        "Do not provide any links that are cited or referenced."
    )
    
    output_file_path = os.path.join(data_path, output_file)
    input_file_path = os.path.join(data_path, input_file)

    # If the output file does not exist, copy the input file and add a new column for GitHub links
    if not os.path.exists(output_file_path):
        shutil.copyfile(input_file_path, output_file_path)
        df = pd.read_csv(output_file_path)
        df["Github_Link"] = ""
    else:
        df = pd.read_csv(output_file_path)
        # Ensure the Github_Link column exists
        if "Github_Link" not in df.columns:
            df["Github_Link"] = ""

    # Iterate over rows and fill in missing GitHub links
    for idx in tqdm(df.index, desc="Processing articles", unit="article"):
        if pd.isna(df.at[idx, "Github_Link"]) or df.at[idx, "Github_Link"] == "":
            # Assuming the 3rd column is "url". Replace "url" with the actual column name if different
            url = df.at[idx, "Pdf_Link"]  
            github_link = extract_github(prompt1, prompt2, gemini_api_key, pdf_url=url)
            
            if github_link is not None:
                df.at[idx, "Github_Link"] = github_link
            else:
                df.at[idx, "Github_Link"] = "not_found"


            # Save progress after each row to prevent data loss if interrupted
            df.to_csv(output_file_path, index=False)

    return None



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, default= "data", help="the path of folder you want to save the data")
    args = parser.parse_args()

    from dotenv import load_dotenv
    import os
    load_dotenv()
       
    githublink_extractor(data_path = args.path, gemini_api_key = os.getenv("GEMINI_API_KEY"))
