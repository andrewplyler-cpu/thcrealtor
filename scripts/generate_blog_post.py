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


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def load_posts():
    try:
        with open(POSTS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def normalize_posts(posts):
    normalized = []
    for p in posts:
        if not isinstance(p, dict):
            continue

        title = p.get("title")
        slug = p.get("slug")
        date_str = p.get("date")
        category = p.get("category") or "General"
        description = p.get("description") or "High Country real estate notes."

        if not title or not slug or not date_str:
            continue

        url = p.get("url")
        if not url:
            url = BASE_URL.rstrip("/") + "/blog/" + slug + "/"

        normalized.append({
            "title": title,
            "slug": slug,
            "date": date_str,
            "category": category,
            "description": description,
            "url": url,
        })

    def sort_key(p):
        try:
            return datetime.fromisoformat(p["date"])
        except Exception:
            return datetime(1970, 1, 1)

    normalized.sort(key=sort_key, reverse=True)
    return normalized


CSS = """
:root {
  --bg: #111827;
  --card: rgba(255,255,255,0.92);
  --text: #111827;
  --muted: #4b5563;
}

html, body {
  margin: 0;
  padding: 0;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
  background: var(--bg);
  color: white;
}

main {
  min-height: 100vh;
}

.hero {
  padding: 28px 22px;
}

.hero h1 {
  margin: 0;
  font-size: 54px;
  line-height: 0.9;
  letter-spacing: -0.04em;
}

.hero p {
  margin: 14px 0 0;
  max-width: 520px;
  color: rgba(255,255,255,0.75);
  font-size: 16px;
  line-height: 1.4;
}

.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 18px;
  padding: 0 18px 40px;
}

.card {
  background: var(--card);
  color: var(--text);
  border-radius: 22px;
  padding: 18px;
  box-shadow: 0 8px 26px rgba(0,0,0,0.16);
}

.card a {
  color: inherit;
  text-decoration: none;
}

.card a:hover {
  text-decoration: underline;
}

.pills {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.pill {
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(17,24,39,0.18);
  font-size: 12px;
  color: rgba(17,24,39,0.75);
}

.card h2 {
  margin: 12px 0 6px;
  font-size: 22px;
  letter-spacing: -0.02em;
}

.card p {
  margin: 0;
  font-size: 16px;
  line-height: 1.4;
  color: var(--muted);
}

footer {
  padding: 18px;
  color: rgba(255,255,255,0.65);
}

.article {
  padding: 22px 22px 44px;
}

.article h1 {
  margin: 0;
  font-size: 42px;
  letter-spacing: -0.04em;
}

.article .meta {
  margin: 10px 0 18px;
  color: rgba(255,255,255,0.7);
}

.article .card {
  margin-top: 18px;
}
"""


def write_css():
    ensure_dir(os.path.dirname(BLOG_CSS))
    with open(BLOG_CSS, "w", encoding="utf-8") as f:
        f.write(CSS.strip())


def make_blog_index(posts):
    cards = []
    for p in posts:
        url = p.get("url")
        title = p.get("title")
        if not url or not title:
            continue

        pills = []
        cat = p.get("category")
        dt = p.get("date")
        if cat:
            pills.append(cat)
        if dt:
            pills.append(dt)

        pills_html = "".join(f"<span class='pill'>{x}</span>" for x in pills)
        desc = p.get("description") or ""
        cards.append(
            f"<article class='card'><a href='{url}'><div class='pills'>{pills_html}</div><h2>{title}</h2><p>{desc}</p></a></article>"
        )

    cards_html = "\n".join(cards)

    return f"""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Blog & Insights | Andrew Plyler</title>
    <meta name="description" content="High Country real estate blog for Boone, Blowing Rock, Banner Elk, and the NC High Country." />
    <link rel="canonical" href="{BASE_URL}/blog" />
    <link rel="stylesheet" href="/base.css" />
    <link rel="stylesheet" href="/style.css" />
    <link rel="stylesheet" href="/blog/blog.css" />
  </head>
  <body>
    <main>
      <section class="hero">
        <h1>Blog & Insights</h1>
        <p>Market updates, buying guides, and honest takes on life and real estate in the NC High Country... new post twice per week.</p>
      </section>
      <section class="grid">
        {cards_html}
      </section>
      <footer>
        <p><a href="/">Home</a> · <a href="/contact">Contact</a></p>
      </footer>
    </main>
  </body>
</html>
"""


def make_post_html(post, body_html):
    url = post["url"]
    title = post["title"]
    cat = post.get("category")
    dt = post.get("date")
    pills = []
    if cat:
        pills.append(cat)
    if dt:
        pills.append(dt)
    pills_html = "".join(f"<span class='pill'>{x}</span>" for x in pills)

    return f"""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title} | Andrew Plyler</title>
    <meta name="description" content="{post.get('description', '')}" />
    <link rel="canonical" href="{url}" />
    <link rel="stylesheet" href="/base.css" />
    <link rel="stylesheet" href="/style.css" />
    <link rel="stylesheet" href="/blog/blog.css" />
  </head>
  <body>
    <main>
      <section class="article">
        <div class='pills'>{pills_html}</div>
        <h1>{title}</h1>
        <p class="meta"><a href="/blog">← All posts</a></p>
        <article class="card">
          {body_html}
        </article>
      </section>
      <footer>
        <p><a href="/">Home</a> · <a href="/contact">Contact</a></p>
      </footer>
    </main>
  </body>
</html>
"""


def choose_topic():
    topics = [
        (
            "Market Update",
            "Buying a Mountain Home in Spring",
            "Spring buyers show up fast in the High Country... and the best plan is the one that wins quietly.",
        ),
        (
            "Lifestyle",
            "Living in the High Country",
            "Life up here rewards preparation... the right vehicle, the right contractor, and the right expectations.",
        ),
        (
            "Buyer Guide",
            "High Country Land Buying Basics",
            "Land in Boone, Blowing Rock, Banner Elk, and beyond comes down to access, water, and lifestyle fit.",
        ),
        (
            "Seasonal",
            "Winter Proofing a High Country House",
            "In winter, you learn what a house is made of... and what it will cost to maintain.",
        ),
    ]
    return random.choice(topics)


def main():
    dt_et = datetime.now(ZoneInfo("America/New_York"))

    ensure_dir(os.path.dirname(BLOG_HTML_ROOT))
    ensure_dir(os.path.dirname(BLOG_INDEX))
    ensure_dir(os.path.dirname(BLOG_CSS))

    posts = normalize_posts(load_posts())

    category, title, description = choose_topic()
    slug_base = slugify(title)
    slug = f"{dt_et.date()}-{slug_base}"

    # Skip if already generated
    if any(p.get("slug") == slug for p in posts):
        write_css()
        html = make_blog_index(posts[:50])
        with open(BLOG_HTML_ROOT, "w", encoding="utf-8") as f:
            f.write(html)
        with open(BLOG_INDEX, "w", encoding="utf-8") as f:
            f.write(html)
        save_posts(posts)
        return

    url = BASE_URL.rstrip("/") + "/blog/" + slug + "/"

    post = {
        "title": title,
        "slug": slug,
        "date": dt_et.date().isoformat(),
        "category": category,
        "description": description,
        "url": url,
    }

    body_html = ""
    body_html += f"<p>{description}</p>"
    body_html += "<p>When you're ready to look at property in Watauga, Ashe, or Avery Counties... I’m here to help.</p>"

    ensure_dir(os.path.join("blog", slug))
    with open(os.path.join("blog", slug, "index.html"), "w", encoding="utf-8") as f:
        f.write(make_post_html(post, body_html))

    posts.append(post)
    posts = normalize_posts(posts)

    write_css()
    save_posts(posts)

    html = make_blog_index(posts[:50])
    with open(BLOG_HTML_ROOT, "w", encoding="utf-8") as f:
        f.write(html)
    with open(BLOG_INDEX, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
