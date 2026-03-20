import os
import re
import json
import random
from datetime import datetime
from zoneinfo import ZoneInfo

BASE_URL = "https://plyler.realtor"
POSTS_JSON = "blog/posts/posts.json"
BLOG_HTML = "blog.html"
BLOG_DIR_INDEX = "blog/index.html"
BLOG_CSS = "blog/blog.css"


def ensure_dir(path: str) -> None:
    if not path:
        return
    os.makedirs(path, exist_ok=True)


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text


def load_posts() -> list:
    try:
        with open(POSTS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def normalize_posts(posts: list) -> list:
    normalized = []
    for p in posts:
        title = p.get("title", "NC High Country real estate notes")
        category = p.get("category", "Market")
        date = p.get("date", datetime.now(ZoneInfo("America/New_York")).date().isoformat())
        slug = p.get("slug")
        if not slug:
            slug = slugify(f"{date}-{title}")
        url = p.get("url")
        if not url:
            url = f"{BASE_URL}/blog/{slug}/"
        desc = p.get("description", "High Country real estate context for Boone, Blowing Rock, Banner Elk, and the surrounding communities.")
        normalized.append({
            "title": title,
            "category": category,
            "date": date,
            "slug": slug,
            "url": url,
            "description": desc,
        })
    normalized.sort(key=lambda x: x["date"], reverse=True)
    return normalized


def save_posts(posts: list) -> None:
    ensure_dir(os.path.dirname(POSTS_JSON))
    with open(POSTS_JSON, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2)


def make_blog_css() -> str:
    return """
:root{--bg0:#0f120f;--text0:#f6f7f2;--card:#fcfcf8;--muted:#aeb3a5;--shadow: 0 10px 30px rgba(0,0,0,0.12)}
html{background:var(--bg0)}
body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--text0)}
a{color:inherit}

.hero{display:flex;gap:24px;padding:44px 18px 30px;border-radius:24px;background:var(--bg0)}
.hero h1{margin:0;font-size:40px;line-height:0.9;font-weight:800}
.hero .sub{margin:0;margin-top:6px;opacity:.92;max-width:34ch}
.grid{padding:18px;display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}
.card{background:var(--card);color:#151714;border-radius:22px;box-shadow:var(--shadow);padding:18px;text-decoration:none}
.card:hover{transform:translateY(-1px);transition:transform .15s ease}
.card .meta{font-size:12px;color:var(--muted);letter-spacing:.06em;text-transform:uppercase;margin:0 0 8px 0}
.card .title{margin:0;font-size:18px;line-height:1.1;font-weight:700}
.card .desc{margin:10px 0 0 0;color:#41463a;font-size:14px}

.post{padding:18px}
.post h1{margin:18px 0 6px 0;font-size:28px;line-height:1.05}
.post .meta{margin:0;color:var(--muted)}
.post p{line-height:1.55;max-width:70ch}
.post footer{margin-top:30px;opacity:.75;font-size:12px}
"""


def make_blog_index(posts: list) -> str:
    cards = []
    for p in posts[:50]:
        cards.append(
            f"""
            <a class='card' href='{p['url']}'>
              <p class='meta'>{p['category']} · {p['date']}</p>
              <h2 class='title'>{p['title']}</h2>
              <p class='desc'>{p['description']}</p>
            </a>
            """
        )
    cards_html = "\n".join(cards)
    return f"""
<!doctype html>
<html lang='en'>
  <head>
    <meta charset='utf-8'/>
    <meta name='viewport' content='width=device-width, initial-scale=1'/>
    <title>Blog & Insights | Andrew Plyler</title>
    <meta name='description' content='High Country real estate blog: Boone, Blowing Rock, Banner Elk, and the NC High Country.' />
    <link rel='canonical' href='{BASE_URL}/blog.html' />
    <link rel='stylesheet' href='/base.css' />
    <link rel='stylesheet' href='/style.css' />
    <link rel='stylesheet' href='/blog/blog.css' />
  </head>
  <body>
    <main>
      <section class='hero'>
        <h1>Blog & Insights</h1>
        <p class='sub'>Market updates, buying guides, and honest takes on life and real estate in the NC High Country… new post twice per week.</p>
      </section>
      <section class='grid'>
        {cards_html}
      </section>
    </main>
  </body>
</html>
"""


def make_post_html(title: str, category: str, dt_et: datetime) -> str:
    return f"""
<!doctype html>
<html lang='en'>
  <head>
    <meta charset='utf-8'/>
    <meta name='viewport' content='width=device-width, initial-scale=1'/>
    <title>{title} | Andrew Plyler</title>
    <meta name='description' content='{title}. High Country real estate insights for Boone, Blowing Rock, and Banner Elk.' />
    <link rel='canonical' href='{BASE_URL}/blog/{dt_et.date()}-{slugify(title)}/' />
    <link rel='stylesheet' href='/base.css' />
    <link rel='stylesheet' href='/style.css' />
    <link rel='stylesheet' href='/blog/blog.css' />
  </head>
  <body>
    <main class='post'>
      <a href='/blog/'>&larr; Back to blog</a>
      <h1>{title}</h1>
      <p class='meta'>{category} · {dt_et.strftime('%B %d, %Y')}</p>
      <p>Buying or selling here means balancing timing, weather, access, and how much you want to manage day-to-day. If you want a plan that fits the High Country, reach out and we’ll keep it simple.</p>
      <p><a href='/contact.html'>Contact</a> · <a href='/services.html'>Services</a> · <a href='/areas.html'>Areas</a></p>
      <footer>© 2026 Andrew Plyler, REALTOR®/Broker.</footer>
    </main>
  </body>
</html>
"""


def write_sitemap(posts: list) -> None:
    urls = [
        {"loc": f"{BASE_URL}/", "lastmod": datetime.now(ZoneInfo("UTC")).date().isoformat()},
        {"loc": f"{BASE_URL}/about.html", "lastmod": datetime.now(ZoneInfo("UTC")).date().isoformat()},
        {"loc": f"{BASE_URL}/areas.html", "lastmod": datetime.now(ZoneInfo("UTC")).date().isoformat()},
        {"loc": f"{BASE_URL}/services.html", "lastmod": datetime.now(ZoneInfo("UTC")).date().isoformat()},
        {"loc": f"{BASE_URL}/faq.html", "lastmod": datetime.now(ZoneInfo("UTC")).date().isoformat()},
        {"loc": f"{BASE_URL}/blog.html", "lastmod": datetime.now(ZoneInfo("UTC")).date().isoformat()},
        {"loc": f"{BASE_URL}/contact.html", "lastmod": datetime.now(ZoneInfo("UTC")).date().isoformat()},
    ]
    for p in posts:
        urls.append({"loc": p["url"], "lastmod": p["date"]})
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write("<?xml version='1.0' encoding='UTF-8'?>\n")
        f.write("<urlset xmlns='https://www.sitemaps.org/schemas/sitemap/0.9'>\n")
        for u in urls:
            f.write("  <url>\n")
            f.write(f"    <loc>{u['loc']}</loc>\n")
            f.write(f"    <lastmod>{u['lastmod']}</lastmod>\n")
            f.write("  </url>\n")
        f.write("</urlset>\n")


def main() -> None:
    posts = normalize_posts(load_posts())
    dt_et = datetime.now(ZoneInfo("America/New_York"))

    topics = [
        ("Market", "High Country Market Pulse"),
        ("Seasonal", "Buying a Mountain Home"),
        ("Lifestyle", "Living in the High Country"),
        ("Investing", "Second Home Strategy"),
    ]
    category, theme = random.choice(topics)

    titles = [
        f"High Country Notes: {theme}",
        f"Boone, Blowing Rock, Banner Elk: {theme}",
        f"Practical High Country Real Estate: {theme}",
    ]
    title = random.choice(titles)

    # Avoid slug collisions from same day reruns
    slug_base = f"{dt_et.date()}-{slugify(title)}"
    slug = slug_base
    i = 2
    while os.path.exists(os.path.join("blog", slug)):
        slug = f"{slug_base}-{i}"
        i += 1

    post_url = f"{BASE_URL}/blog/{slug}/"
    description = "High Country real estate context for Boone, Blowing Rock, and Banner Elk."

    posts.insert(0, {
        "date": dt_et.date().isoformat(),
        "slug": slug,
        "url": post_url,
        "title": title,
        "category": category,
        "description": description,
    })
    posts = normalize_posts(posts)

    save_posts(posts)

    ensure_dir(os.path.dirname(BLOG_CSS))
    with open(BLOG_CSS, "w", encoding="utf-8") as f:
        f.write(make_blog_css())

    html_index = make_blog_index(posts)

    with open(BLOG_HTML, "w", encoding="utf-8") as f:
        f.write(html_index)

    ensure_dir(os.path.dirname(BLOG_DIR_INDEX))
    with open(BLOG_DIR_INDEX, "w", encoding="utf-8") as f:
        f.write(html_index)

    ensure_dir(os.path.dirname(os.path.join("blog", slug, "index.html")))
    with open(os.path.join("blog", slug, "index.html"), "w", encoding="utf-8") as f:
        f.write(make_post_html(title, category, dt_et))

    write_sitemap(posts)


if __name__ == "__main__":
    main()
