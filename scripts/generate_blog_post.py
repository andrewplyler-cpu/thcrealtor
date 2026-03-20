import os
import re
import json
import random
from datetime import datetime
from zoneinfo import ZoneInfo

BASE_URL = "https://plyler.realtor"
POSTS_JSON = "blog/posts/posts.json"
BLOG_ROOT = "blog.html"
BLOG_INDEX = "blog/index.html"
BLOG_CSS = "blog/blog.css"


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


def write_blog_css():
    ensure_dir("blog")
    css = """
:root{
  --bg:#0c0c0f;
  --panel:rgba(255,255,255,.03);
  --panel2:rgba(255,255,255,.05);
  --stroke:rgba(255,255,255,.12);
  --text:rgba(255,255,255,.9);
  --muted:rgba(255,255,255,.65);
  --accent:#9be7ff;
}

body{
  background: radial-gradient(1200px 600px at 10% 0%, rgba(155,231,255,.35), transparent 65%),
              linear-gradient(180deg, rgba(255,255,255,.03), rgba(255,255,255,0));
  color: var(--text);
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
  padding-bottom: 48px;
}

main.blog-layout{
  max-width: 980px;
  margin: 0 auto;
  padding: 28px 16px;
}

.hero{
  padding: 10px 0 18px 0;
}

.hero-title{
  margin: 0;
  font-size: clamp(28px, 3.2vw, 44px);
  letter-spacing: -0.01em;
}

.hero-intro{
  margin: 10px 0 0;
  max-width: 66ch;
  color: var(--muted);
  font-size: 16px;
  line-height: 1.6;
}

.grid{
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

.card{
  border-radius: 16px;
  border: 1px solid var(--stroke);
  background: linear-gradient(180deg, var(--panel2), var(--panel));
  padding: 16px;
  box-shadow: 0 18px 60px rgba(0,0,0,.35);
  transition: transform .12s ease, border-color .12s ease;
}

.card:hover{ transform: translateY(-1px); border-color: rgba(255,255,255,.22); }

.card-meta{
  font-size: 12px;
  color: var(--muted);
  letter-spacing: .08em;
  text-transform: uppercase;
}

.card-title{
  margin: 6px 0;
  font-size: 18px;
}

.card-title a{
  color: var(--text);
  text-decoration: none;
}

.card-title a:hover{ color: var(--accent); }

.card-preview{
  margin: 10px 0 0;
  color: var(--muted);
  line-height: 1.7;
  font-size: 15px;
}

.prose{
  max-width: 74ch;
  color: var(--text);
  line-height: 1.75;
}

.prose h2{ margin-top: 24px; margin-bottom: 8px; font-size: 18px; }

.prose ul{ margin: 10px 0 0 18px; color: var(--muted); }

.cta{
  margin-top: 28px;
  padding: 18px;
  border-radius: 16px;
  border: 1px dashed var(--stroke);
}

.pills{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 12px; }

.pill{
  border-radius: 999px;
  border: 1px solid var(--stroke);
  padding: 8px 12px;
  color: var(--text);
  text-decoration: none;
  background: rgba(255,255,255,.02);
}

.pill:hover{ border-color: rgba(255,255,255,.24); }

.footer{
  margin-top: 28px;
  color: var(--muted);
  font-size: 13px;
}
""".strip()

    with open(BLOG_CSS, "w", encoding="utf-8") as f:
        f.write(css)


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
    <meta name=\"description\" content=\"{post.get('preview','')}\" />
    <link rel=\"canonical\" href=\"{canonical}\" />
    <link rel=\"stylesheet\" href=\"/base.css\" />
    <link rel=\"stylesheet\" href=\"/style.css\" />
    <link rel=\"stylesheet\" href=\"/blog/blog.css\" />
  </head>
  <body>
    <main class=\"blog-layout\">
      <header class=\"hero\">
        <h1 class=\"hero-title\">{title}</h1>
        <p class=\"card-meta\">{category} · {date}</p>
      </header>

      <div class=\"prose\">{body}</div>

      <section class=\"cta\">
        <h2>Ready to talk strategy</h2>
        <p>If you want the cleanest plan for buying or selling in Boone, Blowing Rock, Banner Elk, Ashe County, Watauga County, or Avery County… reach out.</p>
        <p class=\"pills\">
          <a class=\"pill\" href=\"/contact\">Contact</a>
          <a class=\"pill\" href=\"/services\">Services</a>
          <a class=\"pill\" href=\"/areas\">Areas</a>
          <a class=\"pill\" href=\"/blog\">Blog</a>
        </p>
      </section>

      <footer class=\"footer\">© 2026 Andrew Plyler, REALTOR®/Broker. Equal Housing Opportunity.</footer>
    </main>
  </body>
</html>
"""


def make_blog_html(posts):
    cards = []
    for post in posts:
        cards.append(
            f"""
      <article class=\"card\">
        <div class=\"card-meta\">{post.get('category', 'Update')} · {post['date']}</div>
        <h2 class=\"card-title\"><a href=\"/blog/{post['slug']}/\">{post['title']}</a></h2>
        <p class=\"card-preview\">{post.get('preview', '')}</p>
      </article>
      """
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
    <link rel=\"stylesheet\" href=\"/blog/blog.css\" />
  </head>
  <body>
    <main class=\"blog-layout\">
      <header class=\"hero\">
        <h1 class=\"hero-title\">Blog & Insights</h1>
        <p class=\"hero-intro\">Market updates, buying guides, and honest takes on life and real estate in the NC High Country… posted automatically twice per week.</p>
      </header>
      <div class=\"grid\">{cards_html}</div>
    </main>
  </body>
</html>
"""


def main():
    write_blog_css()

    now = datetime.now(ZoneInfo("America/New_York"))
    today = now.date().isoformat()

    category, title, preview, bullets = random.choice([
        (
            "Market Update",
            "Is 2026 a Good Year to Buy a Mountain Home?",
            "A practical look at inventory, pricing, and what actually matters to buyers and sellers in the High Country.",
            [
                "Inventory and pricing change fast here… the cleanest offers win the fastest.",
                "Good due diligence matters: access, drainage, heating, and realistic maintenance.",
                "Your plan should match your lifestyle and budget… not trends and headlines.",
            ],
        ),
        (
            "Lifestyle",
            "What Buyers Ask About Watauga County",
            "The questions I hear on repeat… and how to answer them with a local strategy.",
            [
                "Driveway, access, and winter maintenance are not optional topics.",
                "People buy lifestyle first… real estate is how they lock it in.",
                "If you like it here, plan to protect your time with good systems and good contacts.",
            ],
        ),
        (
            "Investor Guide",
            "Short-Term Rental Regulations in Watauga County",
            "Permits, occupancy taxes, zoning, and the basics you should understand before you close.",
            [
                "Not every property is a good rental… and not every good rental fits your goals.",
                "Know the rules before you plan on cash flow.",
                "A boring plan beats a hopeful one.",
            ],
        ),
        (
            "Seasonal",
            "Buying a Mountain Home in Spring",
            "Spring is when markets wake up fast… and you want your offer ready before you step into the first house.",
            [
                "Get financing clean and clear early.",
                "Know your must-haves and deal-breakers.",
                "Move quickly… but never sloppily.",
            ],
        ),
    ])

    slug = f"{today}-{slugify(title)}"
    bullets_html = "<ul>" + "".join(f"<li>{b}</li>" for b in bullets) + "</ul>"
    body = f"<div class='prose'><h2>Quick take</h2>{bullets_html}</div>"

    posts = load_posts()
    if not any(p.get("slug") == slug for p in posts):
        posts.append({
            "date": today,
            "slug": slug,
            "title": title,
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
    main()
