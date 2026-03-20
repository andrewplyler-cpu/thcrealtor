import os
import re
import json
import random
from datetime import datetime
from zoneinfo import ZoneInfo

BASE_URL = "https://plyler.realtor"
POSTS_JSON = "blog/posts/posts.json"
BLOG_HTML_ROOT = "blog.html"
BLOG_INDEX = "blog/index.html"
BLOG_CSS = "blog/blog.css"


def ensure_dir(path: str) -> None:
    if not path:
        return
    os.makedirs(path, exist_ok=True)


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text


def load_posts():
    try:
        with open(POSTS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def normalize_posts(posts: list) -> list:
    normalized = []
    for p in posts:
        slug = p.get("slug") or slugify(p.get("title", ""))
        if not slug:
            continue
        date = p.get("date") or datetime.now(ZoneInfo("America/New_York")).date().isoformat()
        url = p.get("url") or f"{BASE_URL}/blog/{slug}/"
        normalized.append({
            "date": str(date),
            "slug": slug,
            "url": url,
            "title": p.get("title") or "High Country Real Estate",
            "category": p.get("category") or "Local",
            "description": p.get("description") or "High Country real estate and lifestyle notes."
        })
    normalized.sort(key=lambda x: x["date"], reverse=True)
    return normalized


def save_posts(posts: list) -> None:
    ensure_dir(os.path.dirname(POSTS_JSON))
    with open(POSTS_JSON, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2)


def make_blog_css() -> str:
    return """
:root{
  --bg:#0d0f0c;
  --panel:#ffffff;
  --text:#0b0c0a;
}
body{margin:0;background:var(--bg);font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";}
a{color:inherit;}
.container{max-width:980px;margin:0 auto;padding:24px;}
.hero{display:grid;grid-template-columns:1fr;gap:20px;padding-top:8px;padding-bottom:32px;color:white;}
.hero h1{font-family: ui-serif, Georgia, "Times New Roman", serif;font-size:72px;line-height:0.9;margin:0;}
.hero p{margin:0;font-size:18px;line-height:1.4;color:rgba(255,255,255,0.85);}
@media(min-width: 780px){
 .hero{grid-template-columns:420px 1fr;padding-top:16px;padding-bottom:40px;}
 .hero h1{font-size:92px;}
}
.cards{display:grid;gap:18px;margin:0 4px;}
@media(min-width: 640px){
  .cards{grid-template-columns:1fr 1fr;}
}
.card{background:rgba(255,255,255,0.95);border-radius:18px;padding:18px;box-shadow:0 18px 50px rgba(0,0,0,0.15);color:var(--text);min-height:220px;display:flex;flex-direction:column;justify-content:space-between;}
.card small{color:rgba(11,12,10,0.65);letter-spacing:0.06em;}
.card h2{margin:8px 0 10px;font-size:22px;line-height:1.15;}
.card p{margin:0;font-size:16px;line-height:1.35;color:rgba(11,12,10,0.85);}
.card .cta{margin-top:14px;font-weight:600;display:inline-flex;align-items:center;gap:6px;}
.footer{padding:40px 0 20px;color:rgba(255,255,255,0.7);text-align:center;font-size:13px;}
.post{background:#ffffff;border-radius:18px;padding:22px;box-shadow:0 18px 50px rgba(0,0,0,0.15);color:var(--text);}
.post h1{margin:0;font-size:34px;}
.post p{line-height:1.5;}
"""


def make_blog_index(posts: list) -> str:
    cards = []
    for p in posts[:10]:
        cards.append(f"""
        <a class=\"card\" href=\"{p['url']}\">
          <div>
            <small>{p['category']} · {p['date']}</small>
            <h2>{p['title']}</h2>
            <p>{p['description']}</p>
          </div>
          <div class=\"cta\">Read post →</div>
        </a>
        """)
    cards_html = "\n".join(cards)

    return f"""
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Blog & Insights | Andrew Plyler</title>
    <meta name=\"description\" content=\"High Country real estate blog for Boone, Blowing Rock, Banner Elk, Ashe County, Watauga County, and Avery County.\" />
    <link rel=\"stylesheet\" href=\"/blog/blog.css\" />
    <link rel=\"stylesheet\" href=\"/base.css\" />
    <link rel=\"stylesheet\" href=\"/style.css\" />
  </head>
  <body>
    <div class=\"container\">
      <section class=\"hero\">
        <h1>Blog &amp;<br />Insights</h1>
        <p>Market updates, buying guides, and honest takes on life and real estate in the NC High Country… new post twice per week.</p>
      </section>
      <section class=\"cards\">{cards_html}</section>
      <div class=\"footer\">
        <p>© {datetime.now(ZoneInfo('America/New_York')).year} Andrew Plyler, REALTOR®/Broker. Equal Housing Opportunity.</p>
      </div>
    </div>
  </body>
</html>
"""


def make_post_html(post: dict, body_html: str) -> str:
    return f"""
<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>{post['title']} | Andrew Plyler</title>
    <meta name=\"description\" content=\"{post['description']}\" />
    <link rel=\"stylesheet\" href=\"/blog/blog.css\" />
    <link rel=\"stylesheet\" href=\"/base.css\" />
    <link rel=\"stylesheet\" href=\"/style.css\" />
  </head>
  <body>
    <div class=\"container\">
      <div class=\"post\">
        <a href=\"/blog/\">← Back to Blog</a>
        <p><small>{post['category']} · {post['date']}</small></p>
        <h1>{post['title']}</h1>
        {body_html}
        <p style=\"margin-top:18px;\">Buying or selling up here is simple… with the right local strategy. <a href=\"/contact\">Contact Andrew</a> if you want a plan for the High Country.</p>
      </div>
    </div>
  </body>
</html>
"""


def write_sitemap(posts: list):
    urls = [
        {"loc": f"{BASE_URL}/", "lastmod": datetime.now(ZoneInfo("UTC")).date().isoformat()},
        {"loc": f"{BASE_URL}/blog/", "lastmod": datetime.now(ZoneInfo("UTC")).date().isoformat()},
    ]
    urls.extend({"loc": p["url"], "lastmod": p["date"]} for p in posts)
    lines = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        "<urlset xmlns=\"https://www.sitemaps.org/schemas/sitemap/0.9\">",
    ]
    for u in urls:
        lines.append("  <url>")
        lines.append("    <loc>" + u["loc"] + "</loc>")
        lines.append("    <lastmod>" + u["lastmod"] + "</lastmod>")
        lines.append("  </url>")
    lines.append("</urlset>")
    with open("sitemap.xml", "w", encoding=\"utf-8\") as f:
        f.write("\n".join(lines))


def main():
    dt_et = datetime.now(ZoneInfo("America/New_York"))
    posts = normalize_posts(load_posts())

    title_options = [
        "High Country Market Pulse",
        "Buying Smarter in the NC High Country",
        "Living Like a Local in Boone, Blowing Rock, and Banner Elk",
    ]
    category_options = ["Market", "Lifestyle", "Seasonal", "Seasonal", "Local"]

    title = random.choice(title_options)
    category = random.choice(category_options)
    desc = "High Country real estate and lifestyle notes for Boone, Blowing Rock, Banner Elk, and the NC High Country."

    slug = f"{dt_et.date()}-{slugify(title)}"
    post_dir = os.path.join("blog", slug)
    post_url = f"{BASE_URL}/blog/{slug}/"

    # avoid duplicates on the same day
    if os.path.exists(post_dir):
        return

    post = {
        "date": dt_et.date().isoformat(),
        "slug": slug,
        "url": post_url,
        "title": title,
        "category": category,
        "description": desc,
    }

    posts.append(post)
    posts = normalize_posts(posts)

    # write assets
    ensure_dir(os.path.dirname(BLOG_CSS))
    with open(BLOG_CSS, "w", encoding=\"utf-8\") as f:
        f.write(make_blog_css())

    ensure_dir(os.path.dirname(BLOG_INDEX))
    index_html = make_blog_index(posts)
    with open(BLOG_HTML_ROOT, "w", encoding=\"utf-8\") as f:
        f.write(index_html)
    with open(BLOG_INDEX, "w", encoding=\"utf-8\") as f:
        f.write(index_html)

    save_posts(posts)
    write_sitemap(posts)

    ensure_dir(post_dir)
    body_html = "<p>The High Country has its own rhythm. The more you listen to it, the smarter your real estate decisions get.</p>"
    post_html = make_post_html(post, body_html)
    with open(os.path.join(post_dir, "index.html"), "w", encoding=\"utf-8\") as f:
        f.write(post_html)


if __name__ == "__main__":
    main()
