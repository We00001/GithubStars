import pandas as pd
import os
import re
import math

def create_website_from_csv(file_path='data.csv'):
    """
    Generates the website with a robust conditional layout for long and short bars,
    ensuring bar lengths are always correct.
    """

    # --- 1. Read the data ---
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
        print("Creating a sample 'data.csv' for demonstration purposes.")
        # Using sample data that matches your latest screenshot
        sample_data = {
            'Title': [
                'Procedural terrain generation with style transfer',
                'FedFair^3: Unlocking Threefold Fairness in Federated...',
                'Towards Urban General Intelligence: A Review...',
                'M2-Encoder: Advancing Bilingual Imag...',
                'A Comprehensive Survey on Graph Re...',
                'LLaMP: Large Language Model Made Powerful for High...',
                'MouSi: Poly-Visual-Expert Vision-Langua...',
                'SERNet-Former: Semantic Segmentation by Efficient Residu...'
            ],
            'Pdf_Link': ['link1','link2','link3','link4','link5','link6','link7','link8'],
            'Github_Link': ['gh1','gh2','gh3','gh4','gh5','gh6','gh7','gh8'],
            '2025-08-30': [462.0, 377.0, 181.0, 164.0, 164.0, 85.0, 74.0, 72.0],
            '2025-08-31': [462.0, 377.0, 181.0, 164.0, 164.0, 85.0, 74.0, 72.0]
        }
        df = pd.DataFrame(sample_data)
        df.to_csv(file_path, index=False)

    date_columns = sorted([col for col in df.columns if re.match(r'^\d{4}-\d{2}-\d{2}$', col)])
    output_dir = 'arxiv_visualizer_website'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # --- SVG data for icons (no changes) ---
    arxiv_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>"""
    github_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>"""
    
    # --- 2. UPDATED CSS for the robust conditional layout ---
    css_content = f"""
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f4f4f4; }}
    h1, h2 {{ color: #0056b3; }}
    .bar-wrapper {{ display: flex; align-items: center; min-height: 0.5in; margin-bottom: 10px; }}
    .bar {{ background-color: #79a1d4; border-radius: 3px; display: flex; align-items: center; min-height: 0.5in; flex-shrink: 0; }}
    .bar-label {{ display: flex; align-items: center; flex-grow: 1; padding-left: 10px; min-width: 0; }}
    /* Content styling for INSIDE the bar (long bars) */
    .bar .title-text, .bar .bar-value, .bar .icon-link svg {{ color: white; stroke: white; }}
    /* Content styling for OUTSIDE the bar (short bars) */
    .bar-label .title-text {{ color: #212529; }}
    .bar-label .bar-value, .bar-label .icon-link svg {{ color: #495057; stroke: #495057; }}
    /* General content layout */
    .title-text {{ flex-grow: 1; padding: 0 10px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; cursor: pointer; min-width: 0; }}
    .title-text.expanded {{ white-space: normal; overflow-wrap: break-word; }}
    .bar-value {{ padding: 0 15px; font-weight: bold; }}
    .bar-links {{ display: flex; align-items: center; margin-left: auto; }}
    .icon-link svg {{ width: 20px; height: 20px; margin-left: 8px; }}
    .icon-link:hover svg {{ stroke: #0056b3; }}
    .graph-description {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; margin-bottom: 20px; font-size: 0.9em; color: #495057; }}
    .legend-item {{ display: inline-flex; align-items: center; gap: 5px; margin-right: 15px;}}
    .legend-item svg {{ width: 18px; height: 18px; stroke: #495057; }}
    .navigation-container {{ display: flex; justify-content: space-between; align-items: center; margin: 20px 0; }}
    .nav-button {{ background-color: #0056b3; color: white !important; padding: 10px 15px; border-radius: 5px; text-decoration: none; font-weight: bold; }}
    """
    with open(os.path.join(output_dir, 'style.css'), 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    # --- 3. Generate index.html (omitted for brevity) ---
    index_html_content = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Arxiv Data Visualizer</title><link rel="stylesheet" href="style.css"></head><body><h1>Arxiv Data Visualization</h1><h2>Available Dates</h2><ul class="index-list">{''.join([f'<li><a href="{date}.html">{date}</a></li>' for date in date_columns])}</ul></body></html>"""
    with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(index_html_content)

    for i, date in enumerate(date_columns):
        nav_html = f"""<div class="navigation-container">{'<a href="'+date_columns[i-1]+'.html" class="nav-button">&larr; Previous Day</a>' if i > 0 else '<div></div>'}{'<a href="'+date_columns[i+1]+'.html" class="nav-button">Next Day &rarr;</a>' if i < len(date_columns) - 1 else ''}</div>"""
        description_html = f"""<div class="graph-description"><p>The length of each bar is proportional to the natural logarithm (ln) of its GitHub star count.</p><div><strong>Icons:</strong><span class="legend-item">{arxiv_svg} Arxiv Article</span><span class="legend-item">{github_svg} GitHub Repo</span></div></div>"""
        
        page_df = df[['Title', 'Pdf_Link', 'Github_Link', date]].copy()
        page_df.rename(columns={date: 'value'}, inplace=True)
        page_df['value'] = pd.to_numeric(page_df['value'], errors='coerce').fillna(0)
        page_df['log_value'] = page_df['value'].apply(lambda x: math.log(max(1, x)))
        max_log_value = page_df['log_value'].max()
        page_df_sorted = page_df.sort_values(by='value', ascending=False).reset_index(drop=True)

        date_html_body = ""
        for _, row in page_df_sorted.iterrows():
            bar_width_percentage = (row['log_value'] / max_log_value) * 100 if max_log_value > 0 else 0
            
            github_link_html = f'<a href="{row["Github_Link"]}" target="_blank" class="icon-link">{github_svg}</a>' if pd.notna(row['Github_Link']) and row['Github_Link'] else ''
            
            # This block of HTML content is now used in two different places
            content_html = f"""
                <span class="title-text">{row['Title']}</span>
                <span class="bar-value">{row['value']}</span>
                <div class="bar-links">
                    <a href="{row['Pdf_Link']}" target="_blank" class="icon-link">{arxiv_svg}</a>
                    {github_link_html}
                </div>
            """
            
            # --- UPDATED: The robust conditional layout logic ---
            if bar_width_percentage < 50:
                # SHORT BAR: The bar is empty, content goes in the label next to it.
                # This prevents content from stretching the bar, fixing the length bug.
                date_html_body += f"""
                <div class="bar-wrapper">
                    <div class="bar" style="width: {bar_width_percentage}%;"></div>
                    <div class="bar-label">{content_html}</div>
                </div>
                """
            else:
                # LONG BAR: Content goes inside the bar.
                date_html_body += f"""
                <div class="bar-wrapper">
                    <div class="bar" style="width: {bar_width_percentage}%;">{content_html}</div>
                </div>
                """

        # JavaScript is unchanged and works for both layouts
        javascript_code = """<script>document.addEventListener('DOMContentLoaded',function(){document.querySelectorAll('.title-text').forEach(t=>{if(t.scrollWidth>t.clientWidth){t.setAttribute('title','Click to expand title');t.addEventListener('click',function(){this.classList.toggle('expanded')})}})});</script>"""
        
        date_html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Data for {date}</title><link rel="stylesheet" href="style.css"></head><body><h1>Visualization for {date}</h1><p><a href="index.html">&larr; Back to Index</a></p>{nav_html}{description_html}<div class="chart-container">{date_html_body}</div>{javascript_code}</body></html>"""
        with open(os.path.join(output_dir, f'{date}.html'), 'w', encoding='utf-8') as f:
            f.write(date_html)

    print(f"Website successfully generated in the '{output_dir}' directory.")
    print("Final fix for bar lengths and conditional layouts implemented.")
    
if __name__ == "__main__":
    create_website_from_csv('data/star_test.csv')