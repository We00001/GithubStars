python arxiv_scraper.py --category "cs.AI" --start_date $(date -v -2d +%Y-%m-%d)
python githublink_extractor.py --path "data"
python star_scraper.py --path "data"