import os
import re
import json
from datetime import datetime
from zoneinfo import ZoneInfo

BASE_URL = "https://plyler.realtor"
POSTS_JSON = "blog/posts/posts.json"
BLOG_ROOT = "blog.html"
BLOG_INDEX = "blog/index.html"


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[\s_-]+", "-", text).strip("-")
    return text


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def load_posts():
    if not os.path.exists(POSTS_JSON):
        return []
    with open(POSTS_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def save_posts(posts):
    ensure_dir(os.path.dirname(POSTS_JSON))
    with open(POSTS_JSON, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=2)


def make_post_html(post):
    canonical = f"{BASE_URL}/blog/{post['slug']}/"
    title = post['title']
    category = post.get('category', 'Update')
    date = post['date']
    body = post['body']

    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>{title} | Andrew Plyler</title>
    <meta name=\"description\" content={title}. High Country real estate insights for Boone, Blowing Rock, Banner Elk, and the NC High Country." />
    <link rel=\"canonical\" href=\"{canonical}\" />
    <link rel=\"stylesheet\" href=\"/base.css\" />
    <link rel=\"stylesheet\" href=\"/style.css\" />
  </head>
  <body>
    <main>
      <p><a href=\"/\">Home</a> · <a href=\"/blog\">Blog</a></p>

      <h1>{title}</h1>
      <p><em>{category} · {date}</em></p>

      {body}

      <section>
        <h2>Ready for a plan that fits the High Country</h2>
        <p>When you want the right property in the right spot… you need a local strategy, not just a search bar.</p>
        <p><a href=\"/contact.html\">Contact Andrew</a> · <a href=\"/services.html\">Services</a> · <a href=\"/areas.html\">Areas</a></p>
      </section>

      <footer>
        <p>© 2026 Andrew Plyler, REALTOR®/Broker. Equal Housing Opportunity.</p>
      </footer>
    </main>
  </body>
</html>
"""


def make_blog_html(posts):
    cards = []
    for post in posts:
        cards.append(
            f"""
    <article>
      <p><em>{post.get('category', 'Update')} · {post['date']}</em></p>
      <h2><a href=\"/blog/{post['slug']}/\">{post['title']}</a></h2>
      <p>{post.get('preview', '')}</p>
    </article>
    <hr />"""
        )
    cards_html = "\n".join(cards)

    return f"""<!doctype html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Blog & Insights | Andrew Plyler</title>
    <meta name=\"description\" content=\"High Country real estate blog: Boone, Blowing Rock, Banner Elk, Ashe, Watauga, and Avery Counties.\" />
    <link rel=\"canonical\" href=\"{BASE_URL}/blog\" />
    <link rel=\"stylesheet\" href=\"/base.css\" />
    <link rel=\"stylesheet\" href=\"/style.css\" />
  </head>
  <body>
    <main>
      <p><a href=\"/\">Home</a></p>
      <h1>Blog & Insights</h1>
      <p>Twice-weekly High Country real estate content… plus the local life context that matters when you’re buying or selling up here.</p>

      {cards_html}
    </main>
  </body>
</html>
"""


def main():
    now = datetime.now(ZoneInfo("America/New_York"))
    today = now.date().isoformat()

    category = random.choice(["Market Update", "Lifestyle", "Buying Guide", "Seasonal", "Local" ])
    title = random.choice([
        "High Country Real Estate Notes",
        "What Buyers Ask About Watauga County",
        "Blowing Rock, Banner Elk, and Boone – a Practical Snapshot",
        "The Most Common Deal Killers in Mountain Properties",
        "A Clean Offer Matters More Than a Clever One",
    ])
    slug = f"{today}-{slugify(title)}"

    bullets_html = """<ul>
<li>Inventory and pricing are changing week-by-week. The cleanest offers win the fastest.</li>
<li>Good due diligence matters: access, drainage, heating, and realistic maintenance.</li>
<li>Your plan should match your lifestyle and your budget… not social media trends.</li>
</ul>"""
    body = f"""<section>
<h2>Quick take</h2>
{bullets_html}
</section>"""

    preview = "High Country context for Boone, Blowing Rock, Banner Elk, Ashe, Watauga, and Avery Counties."

    posts = load_posts()
    if not any(p.get("slug") == slug for p in posts):
        posts.append({
            "date": today,
            "slug": slug,
            "title": f"{title} ({today})",
            "category": category,
            "preview": preview,
            "body": body,
        })

    posts.sort(key=lambda p: p["date"], reverse=True)
    save_posts(posts)

    blog_html = make_blog_html(posts[:50])
    ensure_dir("blog")
    with open(BLOG_ROOT, "w", encoding="utf-8") as f:
        f.write(blog_html)
    with open(BLOG_INDEX, "w", encoding="utf-8") as f:
        f.write(blog_html)

    latest = posts[0]
    ensure_dir(os.path.join("blog", latest["slug"]))
    with open(os.path.join("blog", latest["slug"], "index.html"), "w", encoding="utf-8") as f:
        f.write(make_post_html(latest))


if __name__ == "__main__":
    import random
    main()
