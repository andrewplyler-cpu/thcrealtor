import os
import re
import json
import random
import textwrap
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://plyler.realtor"
POSTS_JSON = "blog/posts/posts.json"
BLOG_INDEX = "blog.html"
SITEMAP = "sitemap.xml"

LAT = 36.2168
LON = -81.6746
HEADERS = {
  "User-Agent": "plyler-realtor-auto-blog (https://github.com/andrewplyler-cpu/thcrealtor)"
}

# ---------- helpers ----------

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

def get_weather_snapshot():
  try:
    points = requests.get(
      f"https://api.weather.gov/points/{LAT},{LON}",
      headers=HEADERS,
      timeout=15
    ).json()
    forecast_url = points["properties"]["forecast"]
    forecast = requests.get(forecast_url, headers=HEADERS, timeout=15).json()
    period = forecast["properties"]["periods"][0]
    return {
      "name": period.get("name", "Today"),
      "short_forecast": period.get("shortForecast", ""),
      "temp": f"{period.get('temperature', '?')}°{period.get('temperatureUnit', '')}",
      "wind": period.get("windSpeed", "") + " " + period.get("windDirection", "")
    }
  except Exception:
    return None

def seasonal_hook(dt_et: datetime) -> str:
  month = dt_et.month
  if month in (12, 1, 2):
    return "Winter is when you learn what a house is made of… ice, drainage, access, and heat."
  if month in (3, 4, 5):
    return "Spring is when mountain markets wake up fast… and you want your offers to be clean, clear, and quick."
  if month in (6, 7, 8):
    return "Summer brings more buyers and more optimism… the winners bring a plan."
  if month in (9, 10, 11):
    return "Fall is when views show off and smart buyers look for the right land with the right access."
  return "Life in the High Country rewards preparation and honest expectations."

def topic_pack(dt_et: datetime):
  choices = [
    ("Market Update", "High Country Market Pulse", [
      "What matters most this week: inventory, pricing, and which areas are getting the most calls.",
      "A good local strategy beats a national headline every time."
    ]),
    ("Investor Guide", "Second Homes and Rental Strategy", [
      "Not every mountain house is a good rental… and a good rental still has to match your lifestyle and budget.",
      "Get realistic about expenses, access, seasonality, and management."
    ]),
    ("Lifestyle", "Living in the NC High Country", [
      "Out here, people shop for lifestyle first… real estate is how you lock it in.",
      "If you like it up here, plan to protect your time with good systems and good contacts."
    ]),
    ("Seasonal Prep", "Buying in Mountain Weather", [
      "Weather changes the way you inspect property: roofs, roads, drainage, and practical maintenance.",
      "The right contractor relationships matter more than the right Instagram view."
    ]),
    ("Holiday + Local", "High Country Community Calendar", [
      "Local events tell you more about a community than any listing ever will.",
      "If you want to learn a market fast… go to the events."
    ])
  ]
  category, theme, bullets = random.choice(choices)

  titles = [
    f"NC High Country {theme}: Boone, Blowing Rock, Banner Elk",
    f"Watauga, Ashe, and Avery County {theme}",
    f"High Country Real Estate Notes: {theme}",
    f"Practical High Country Real Estate: {theme}"
  ]
  title = random.choice(titles)

  return category, title, bullets

def description_for(category: str) -> str:
  return f"{category}… High Country context and practical real estate guidance for Boone, Blowing Rock, Banner Elk, and the NC High Country."

# ---------- event scraping ----------

def scrape_boone_chamber(limit=5):
  url = "https://www.boonechamber.com/events"
  try:
    soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=20).text, "html.parser")
    text = soup.get_text("\n", strip=True)
    pattern = re.compile(
      r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d+\s+\n(.+?)\s+\n\d.*?Details",
      re.S
    )
    events = []
    for m in pattern.finditer(text):
      date = m.group(0).split("\n")[0].strip()
      title = m.group(2).strip()
      events.append({"title": title, "date": date, "source": "Boone Chamber", "url": url})
      if len(events) >= limit:
        break
    return events
  except Exception:
    return []

def scrape_apptheatre(limit=5):
  url = "https://www.apptheatre.org/events-and-tickets"
  try:
    soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=20).text, "html.parser")
    events = []
    for h in soup.find_all(["h1", "h2", "h3", "h4"]):
      title = h.get_text(strip=True)
      if not title or len(title.split()) < 2:
        continue
      date_text = ""
      for sib in h.next_siblings:
        if getattr(sib, "name", None) and sib.name in ["ul", "ol", "p"]:
          date_text = sib.get_text(" ", strip=True)
          break
      events.append({"title": title, "date": date_text, "source": "Appalachian Theatre", "url": url})
      if len(events) >= limit:
        break
    return events
  except Exception:
    return []

def scrape_blowingrock(limit=5):
  url = "https://blowingrock.com/events/category/main/"
  try:
    soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=20).text, "html.parser")
    events = []
    for h in soup.find_all(["h3", "h4", "h5"]):
      title = h.get_text(strip=True)
      if not title or len(title.split()) < 2:
        continue
      date_text = ""
      for sib in h.previous_siblings:
        if isinstance(sib, str) and sib.strip():
          date_text = sib.strip()
          break
      events.append({"title": title, "date": date_text, "source": "Blowing Rock", "url": url})
      if len(events) >= limit:
        break
    return events
  except Exception:
    return []

def scrape_ashe_chamber(limit=5):
  url = "https://ashechamber.com/calendar.php"
  try:
    soup = BeautifulSoup(requests.get(url, headers=HEADERS, timeout=20).text, "html.parser")
    events = []
    for a in soup.find_all("a", href=True):
      href = a["href"]
      title = a.get_text(strip=True)
      if not title or len(title.split()) < 2:
        continue
      if "event" in href.lower() or "events" in href.lower():
        events.append({"title": title, "date": "", "source": "Ashe Chamber", "url": url})
        if len(events) >= limit:
          break
    return events
  except Exception:
    return []

def get_events(limit_total=12):
  events = []
  for scraper in [scrape_boone_chamber, scrape_apptheatre, scrape_blowingrock, scrape_ashe_chamber]:
    events.extend(scraper(limit=limit_total))
  seen = set()
  unique = []
  for e in events:
    key = e["title"].lower()
    if key in seen:
      continue
    seen.add(key)
    unique.append(e)
  return unique[:limit_total]

def events_html():
  events = get_events(limit_total=10)
  if not events:
    return "<p>No event scrape results today… but the High Country calendar never sleeps.</p>"
  items = []
  for e in events:
    date = f"{e['date']} · " if e['date'] else ""
    items.append(f"<li><strong>{e['title']}</strong> · {date}<em>{e['source']}</em></li>")
  return "<ul>" + "\n".join(items) + "</ul>"

# ---------- content generation ----------

def make_post_html(title, category, dt_et, weather, bullets, hook):
  weather_block = ""
  if weather:
    weather_block = textwrap.dedent(f"""
    <section>
      <h2>{weather['name']}: {weather['short_forecast']}</h2>
      <p><strong>Temp:</strong> {weather['temp']} · <strong>Wind:</strong> {weather['wind']}</p>
    </section>
    """)
  bullets_html = "\n".join(f"<li>{b}</li>" for b in bullets)
  events_block = events_html()

  body = f"""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title} | Andrew Plyler</title>
    <meta name="description" content="{title}. High Country real estate insights for Boone, Blowing Rock, Banner Elk, and beyond." />
    <link rel="canonical" href="{BASE_URL}/blog/{dt_et.date()}-{slugify(title)}/" />
    <link rel="stylesheet" href="/base.css" />
    <link rel="stylesheet" href="/style.css" />
  </head>
  <body>
    <main>
      <p><a href="/">Home</a> · <a href="/blog.html">Blog</a></p>

      <h1>{title}</h1>
      <p><em>{category} · {dt_et.strftime('%B %d, %Y')}</em></p>

      {weather_block}

      <section>
        <h2>Quick truth</h2>
        <p>{hook}</p>
        <ul>
          {bullets_html}
        </ul>
      </section>

      <section>
        <h2>Local events to keep you plugged into the market</h2>
        {events_block}
      </section>

      <section>
        <h2>Want a plan that fits the High Country</h2>
        <p>Buying or selling up here is simple… with the right local strategy. If you want a quick look at the best approach for Boone, Blowing Rock, Banner Elk, or anywhere in Watauga, Ashe, or Avery Counties… reach out.</p>
        <p><a href="/contact.html">Contact Andrew</a> · <a href="/services.html">Services</a> · <a href="/areas.html">Areas</a></p>
      </section>

      <footer>
        <p>© 2026 Andrew Plyler, REALTOR®/Broker. Equal Housing Opportunity.</p>
      </footer>
    </main>
  </body>
</html>
"""
  return textwrap.dedent(body).strip()

def make_blog_index(posts):
  cards = []
  for post in posts:
    cards.append(f"""
    <article>
      <p><em>{post['category']} · {post['date']}</em></p>
      <h2><a href="{post['url']}">{post['title']}</a></h2>
      <p>{post['description']}</p>
    </article>
    <hr />
    """)
  cards_html = "\n".join(cards)

  return textwrap.dedent(f"""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Blog & Insights | Andrew Plyler</title>
    <meta name="description" content="High Country real estate blog for Boone, Blowing Rock, Banner Elk, and the NC High Country." />
    <link rel="canonical" href="{BASE_URL}/blog.html" />
    <link rel="stylesheet" href="/base.css" />
    <link rel="stylesheet" href="/style.css" />
  </head>
  <body>
    <main>
      <p><a href="/">Home</a></p>
      <h1>Blog & Insights</h1>
      <p>Market updates, buying guides, and real-life High Country context for Boone, Blowing Rock, Banner Elk, Ashe County, Watauga County, and Avery County.</p>
      {cards_html}
    </main>
  </body>
</html>
""").strip()

def write_sitemap(posts):
  urls = [
    {"loc": f"{BASE_URL}/", "lastmod": datetime.now(ZoneInfo("UTC")).date().isoformat()},
    {"loc": f"{BASE_URL}/about.html", "lastmod": datetime.now(ZoneInfo("UTC")).date().isoformat()},
    {"loc": f"{BASE_URL}/areas.html", "lastmod": datetime.now(ZoneInfo("UTC")).date().isoformat()},
    {"loc": f"{BASE_URL}/services.html", "lastmod": datetime.now(ZoneInfo("UTC")).date().isoformat()},
    {"loc": f"{BASE_URL}/faq.html", "lastmod": datetime.now(ZoneInfo("UTC")).date().isoformat()},
    {"loc": f"{BASE_URL}/blog.html", "lastmod": datetime.now(ZoneInfo("UTC")).date().isoformat()},
    {"loc": f"{BASE_URL}/contact.html", "lastmod": datetime.now(ZoneInfo("UTC")).date().isoformat()},
  ]
  urls.extend({"loc": p["url"], "lastmod": p["date"]} for p in posts)

  lines = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>", "<urlset xmlns=\"https://www.sitemaps.org/schemas/sitemap/0.9\">"]
  for u in urls:
    lines.append("  <url>")
    lines.append(f"    <loc>{u['loc']}</loc>")
    {u['lastmod']}</lastmod}")
    lines.append("  </url>")
  lines.append("</urlset>")
  with open(SITEMAP, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

def main():
  dt_et = datetime.now(ZoneInfo("America/New_York"))
  category, title, bullets = topic_pack(dt_et)
  hook = seasonal_hook(dt_et)
  weather = get_weather_snapshot()

  slug = f"{dt_et.date()}-{slugify(title)}"
  post_dir = os.path.join("blog", slug)
  post_url = f"{BASE_URL}/blog/{slug}/"

  if os.path.exists(post_dir):
    print("Post already exists for today, skipping.")
    return

  posts = load_posts()

  post_html = make_post_html(title, category, dt_et, weather, bullets, hook)
  ensure_dir(post_dir)
  with open(os.path.join(post_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(post_html)

  posts.append({
    "date": dt_et.date().isoformat(),
    "slug": slug,
    "url": post_url,
    "title": title,
    "category": category,
    "description": description_for(category)
  })
  posts.sort(key=lambda p: p["date"], reverse=True)
  save_posts(posts)

  blog_index = make_blog_index(posts[:50])
  with open(BLOG_INDEX, "w", encoding="utf-8") as f:
    f.write(blog_index)

  write_sitemap(posts)


if __name__ == "__main__":
  main()
