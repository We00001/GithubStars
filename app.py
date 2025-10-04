# app.py
# This is the updated Flask application that reads data from the SQLite database.
# It is memory-efficient and combines database logic with language translations.
import os
import sqlite3
from flask import Flask, render_template, request, url_for, redirect, g
from urllib.parse import urlencode

app = Flask(__name__)
app.debug = True

DATABASE = 'data/arxiv.db'

TRANSLATIONS = {
    'en': {
        'page_title': 'Star History Viewer', 'main_header': 'Paper Star Rankings',
        'sub_header': 'Browse rankings by date and see growth trends.', 'select_date': 'Select Date',
        'growth_period': 'Growth Period', 'sort_by': 'Sort By', 'stars': 'Stars', 'growth': 'Growth',
        'day': 'Day', 'days': 'Days', 'year': 'Year', 'title': 'Title', 'links': 'Links',
        'showing': 'Showing', 'to': 'to', 'of': 'of', 'results': 'results', 'page': 'Page',
        'prev': 'Prev', 'next': 'Next', 'no_data': 'No data available for this date.',
        'prev_day': 'Previous Day', 'next_day': 'Next Day', 'error_no_db': 'Database not found. Please run the update script.'
    },
    'zh': {
        'page_title': 'Star 历史查看器', 'main_header': '论文 Star 排行榜',
        'sub_header': '按日期浏览排名并查看增长趋势。', 'select_date': '选择日期',
        'growth_period': '增长周期', 'sort_by': '排序方式', 'stars': '收藏数', 'growth': '增长',
        'day': '天', 'days': '天', 'year': '年', 'title': '标题', 'links': '链接',
        'showing': '显示', 'to': '到', 'of': '，共', 'results': '条结果', 'page': '第',
        'prev': '上一页', 'next': '下一页', 'no_data': '选定日期无可用数据。',
        'prev_day': '前一天', 'next_day': '后一天', 'error_no_db': '数据库未找到，请先运行更新脚本。'
    }
}

# --- Database Connection Handling ---
def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    if 'db' not in g:
        if not os.path.exists(DATABASE):
            return None # Return None if the database file does not exist
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    """Closes the database again at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# --- Jinja2 Context Processor ---
@app.context_processor
def utility_processor():
    """Make helper functions available in templates."""
    def url_for_params(endpoint, **values):
        args = request.args.copy()
        for key, value in values.items():
            args[key] = value
        return url_for(endpoint, **args)
    return dict(url_for_params=url_for_params)

# --- Routes ---
@app.route("/")
def index():
    db = get_db()
    lang = request.args.get('lang', 'en')
    if lang not in TRANSLATIONS:
        lang = 'en'
    T = TRANSLATIONS[lang]

    if db is None:
        return render_template("index.html", error=T['error_no_db'], T=T, lang=lang)

    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT check_date FROM star_counts ORDER BY check_date DESC")
    available_dates = [row['check_date'] for row in cursor.fetchall()]

    if not available_dates:
        return render_template("index.html", data=[], available_dates=[], T=T, lang=lang, no_data=True)

    # --- 1. Get Parameters ---
    selected_date = request.args.get("date", available_dates[0])
    growth_days = int(request.args.get("growth_days", 7))
    sort_by = request.args.get("sort_by", "stars")
    order = request.args.get("order", "desc")
    page = int(request.args.get("page", 1))
    per_page = 50

    # --- 2. Build SQL Query ---
    order_direction = "ASC" if order.lower() == "asc" else "DESC"
    sort_column = "growth" if sort_by == "growth" else "current_stars"

    # CORRECTED QUERY: Use aliases (e.g., p.title AS "Title") to match the case
    # expected by the HTML template. This fixes the missing titles and links.
    query = f"""
        SELECT
            p.title AS "Title",
            p.pdf_link AS "Pdf_Link",
            p.github_link AS "Github_Link",
            p.arxiv_id AS "Arxiv_ID",
            s1.stars AS current_stars,
            (s1.stars - IFNULL(s2.stars, s1.stars)) AS growth
        FROM papers p
        JOIN star_counts s1 ON p.id = s1.paper_id
        LEFT JOIN star_counts s2 ON p.id = s2.paper_id AND s2.check_date = (
            SELECT MAX(check_date)
            FROM star_counts
            WHERE paper_id = p.id AND check_date < DATE(?, '-{growth_days} days')
        )
        WHERE s1.check_date = ?
        ORDER BY {sort_column} {order_direction}, current_stars DESC
    """

    cursor.execute(query, (selected_date, selected_date))
    all_data = cursor.fetchall()

    # --- 3. Pagination ---
    total_items = len(all_data)
    total_pages = (total_items + per_page - 1) // per_page
    
    if page > total_pages and total_pages > 0:
        return redirect(url_for_params('index', page=total_pages))

    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    paginated_data = all_data[start_index:end_index]

    # --- 4. Previous/Next Day Navigation ---
    prev_date, next_date = None, None
    if selected_date in available_dates:
        current_index = available_dates.index(selected_date)
        if current_index < len(available_dates) - 1:
            prev_date = available_dates[current_index + 1] # Dates are DESC
        if current_index > 0:
            next_date = available_dates[current_index - 1]

    return render_template(
        "index.html",
        data=[dict(row) for row in paginated_data], # Convert rows to dicts
        page=page,
        total_pages=total_pages,
        total_items=total_items,
        start_index=start_index,
        end_index=min(end_index, total_items),
        sort_by=sort_by,
        order=order,
        date_cols=available_dates,
        selected_date=selected_date,
        growth_days=growth_days,
        growth_col_name="growth", # For consistency in template
        prev_date=prev_date,
        next_date=next_date,
        lang=lang,
        T=T
    )

if __name__ == "__main__":
    if not os.path.exists('data'):
        os.makedirs('data')
    app.run(host="0.0.0.0", port=5555, debug=True)

