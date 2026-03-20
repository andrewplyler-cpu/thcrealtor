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
    css = """
    :root{--bg:#070A0F;--panel:#0F1625;--panel2:#0B1020;--text:#E5EAF5;--muted:#B6C3DE;--accent:#7CFFB2;--accent2:#43C6AC;--border:rgba(150,169,207,.18);--shadow:rgba(0,0,0,.35);}
    body{margin:0;background:radial-gradient(900px 400px at 15% 25%,rgba(124,255,178,.08),transparent),radial-gradient(900px 500px at 90% 10%,rgba(67,198,172,.06),transparent),linear-gradient(180deg,var(--bg),#04060A);color:var(--text);min-height:100vh;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;}
    a{color:var(--accent);text-decoration:none}
    a:hover{text-decoration:underline}
    .container{max-width:980px;margin:0 auto;padding:20px;}
    .hero{padding:20px 0 8px;border-bottom:1px solid var(--border);}
    .hero-title{margin:0;font-size:46px;letter-spacing:.02em;}
    .hero-intro{margin:10px 0 0;color:var(--muted);font-size:18px;line-height:1.4;max-width:760px;}
    .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px;margin-top:20px;}
    .card{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--border);border-radius:16px;box-shadow:0 18px 45px var(--shadow);padding:18px;}
    .card-meta{color:var(--muted);font-size:14px;display:flex;gap:8px;align-items:center;margin-bottom:10px}
    .pill{display:inline-flex;align-items:center;padding:5px 10px;border-radius:999px;border:1px solid var(--border);background:rgba(255,255,255,.04);color:var(--muted);font-weight:600;font-size:12px;}
    .dot{width:6px;height:6px;border-radius:99px;background:var(--accent);display:inline-block;margin-right:8px;box-shadow:0 0 0 4px rgba(124,255,178,.12)}
    .card-title{margin:0;font-size:20px;line-height:1.2}
    .card-preview{color:var(--muted);margin:10px 0 0;line-height:1.45}
    .footer{margin-top:26px;padding-top:16px;border-top:1px solid var(--border);color:var(--muted);font-size:13px}
    @media (prefers-color-scheme: light){
      :root{--bg:#F7F9FF;--panel:#FFFFFF;--panel2:#F7F8FE;--text:#16213D;--muted:#66799C;--border:rgba(10,20,40,.15);--shadow:rgba(8,15,30,.10);}
      .card{background:linear-gradient(180deg,var(--panel),var(--panel2));}
      .dot{box-shadow:0 0 0 4px rgba(67,198,172,.08)}
    }
    """.strip()
    ensure_dir(os.path.dirname(BLOG_CSS))
    with open(BLOG_CSS, "w", encoding="utf-8") as f:
        f.write(css)


def make_post_html(title, category, dt_et):
    date_str = dt_et.strftime("%B %d, %Y")
    body = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>{title} | Andrew Plyler</title>
        <meta name="description" content="{title}. High Country real estate context for Boone, Blowing Rock, Banner Elk, Ashe, Watauga, and Avery Counties." />
        <link rel="canonical" href="{BASE_URL}/blog/{dt_et.date()}-{slugify(title)}/" />
        <link rel="stylesheet" href="/base.css" />
        <link rel="stylesheet" href="/style.css" />
        <link rel="stylesheet" href="/blog/blog.css" />
      </head>
      <body>
        <div class="container">
          <div style="margin-bottom:18px"><a href="/">Home</a> · <a href="/blog">Blog</a></div>

          <h1 style="margin:0;font-size:44px">{title}</h1>
          <p style="margin:8px 0 18px;color:var(--muted)"><span class="pill"><span class="dot"></span>{category}</span> · {date_str}</p>

          <p style="color:var(--muted);line-height:1.55">This is a quick High Country perspective that cuts through fluff and focuses on what matters up here: lifestyle fit, smart timing, and practical choices.</p>

          <h2 style="margin:28px 0 10px">What to focus on</h2>
          <ul style="color:var(--muted);line-height:1.6">
            <li>Think like a local: access, seasons, maintenance.</li>
            <li>Use clean offers and realistic expectations… not wishful thinking.</li>
            <li>Pick the right area for your lifestyle and your future plans.</li>
          </ul>

          <section style="margin-top:24px;padding:18px;border:1px solid var(--border);border-radius:16px;background:rgba(255,255,255,.03)">
            <h2 style="margin:0">Need a quick plan</h2>
            <p style="color:var(--muted);margin:10px 0 0">If you want help navigating Boone, Blowing Rock, Banner Elk, or anywhere in Watauga, Ashe, or Avery Counties… reach out and I’ll make it simple.</p>
            <p style="margin:10px 0 0"><a href="/contact">Contact Andrew</a> · <a href="/services">Services</a> · <a href="/areas">Areas</a></p>
          </section>

          <div class="footer">© 2026 Andrew Plyler, REALTOR®/Broker.</div>
        </div>
      </body>
    </html>
    """.strip()
    return body


def make_blog_index(posts):
    cards = []
    for p in posts:
        cards.append(f"""
      <article class="card">
        <div class="card-meta"><span class="pill"><span class="dot"></span>{p['category']}</span> · {p['date']}</div>
        <h2 class="card-title"><a href="{p['url']}">{p['title']}</a></h2>
        <p class="card-preview">{p['description']}</p>
      </article>""")

    cards_html = "\n".join(cards)

    html = f"""
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Blog & Insights | Andrew Plyler</title>
        <meta name="description" content="High Country real estate blog: Boone, Blowing Rock, Banner Elk, Ashe, Watauga, and Avery Counties." />
        <link rel="canonical" href="{BASE_URL}/blog" />
        <link rel="stylesheet" href="/base.css" />
        <link rel="stylesheet" href="/style.css" />
        <link rel="stylesheet" href="/blog/blog.css" />
      </head>
      <body>
        <div class="container">
          <div style="margin-bottom:18px"><a href="/">Home</a></div>
          <header class="hero">
            <h1 class="hero-title">Blog & Insights</h1>
            <p class="hero-intro">Market updates, buying guides, and honest takes on life and real estate in the NC High Country… new post twice per week.</p>
          </header>

          <div class="grid">
            {cards_html}
          </div>

          <div class="footer">© 2026 Andrew Plyler, REALTOR®/Broker.</div>
        </div>
      </body>
    </html>
    """.strip()
    return html


def main():
    dt_et = datetime.now(ZoneInfo("America/New_York"))

    posts = load_posts()

    topics = [
        ("Lifestyle", "Blowing Rock, Banner Elk, and Boone – a Practical Snapshot", "High Country context for Boone, Blowing Rock, Banner Elk, Ashe, Watauga, and Avery Counties."),
        ("Seasonal", "Buying a Mountain Home in Spring", "Spring buyers show up fast… be ready before the first showing."),
        ("Market", "High Country Market Notes", "A short take on what actually moves the needle up here."),
    ]

    category, title, description = random.choice(topics)
    slug = f"{dt_et.date()}-{slugify(title)}"

    # Only create a new post folder when we actually have new content for today
    if not any(p.get("slug") == slug for p in posts):
        post_dir = os.path.join("blog", slug)
        ensure_dir(post_dir)
        with open(os.path.join(post_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(make_post_html(title, category, dt_et))

        posts.append({
            "date": dt_et.date().isoformat(),
            "slug": slug,
            "url": f"{BASE_URL}/blog/{slug}/",
            "title": title,
            "category": category,
            "description": description,
        })

    posts.sort(key=lambda p: p["date"], reverse=True)
    save_posts(posts)

    write_blog_css()

    html = make_blog_index(posts)
    ensure_dir(os.path.dirname(BLOG_INDEX))
    with open(BLOG_INDEX, "w", encoding="utf-8") as f:
        f.write(html)
    with open(BLOG_HTML_ROOT, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    main()
