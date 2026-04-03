#!/usr/bin/env python3
"""
Auto Blog Post Generator for plyler.realtor / THCRealtor
Runs via GitHub Actions every Monday and Thursday.
Styles match the live site exactly — links base.css + style.css, same as all other pages.
"""

import os, json, re, anthropic
from datetime import date
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────────
SITE_NAME        = "The High Country Realtor"
SITE_URL         = "https://plyler.realtor"
AUTHOR_NAME      = "Andrew Plyler, REALTOR\u00ae"
AUTHOR_TITLE     = "Broker \u00b7 Blue Ridge Realty & Investments \u00b7 Boone, NC"
AUTHOR_PHONE     = "(770) 639-1233"
AUTHOR_PHONE_RAW = "+17706391233"
AUTHOR_EMAIL     = "aplyler@brri.net"
AUTHOR_BRAND_URL = "https://plyler.realtor"

BLOG_DIR         = Path("blog")
BLOG_INDEX_ROOT  = Path("blog.html")       # root-level blog listing (blog.html)
BLOG_INDEX_SUB   = BLOG_DIR / "index.html" # /blog/ URL listing (blog/index.html)

# ── Manually-curated posts (always shown, always first-checked) ────────────────
# These were added by hand and have no meta.json. We hardcode their metadata here
# so they always appear in the index. Add new manual posts to this list.
# ── Tag options: land | investment | market | relocation | local | selling
MANUAL_POSTS = [
    {
        "title":   "Moving to Boone NC: Complete High Country Relocation Guide",
        "slug":    "2026-03-20-moving-to-boone-nc-high-country-relocation-guide",
        "date":    "March 20, 2026",
        "tag":     "relocation",
        "excerpt": "Considering a move to the beautiful Blue Ridge Mountains? This comprehensive guide covers everything you need to know about relocating to Boone and the High Country region.",
        "image":   "https://assets.agentfire3.com/uploads/sites/1337/2024/04/Boone-NC-King-Street.jpg",
        "image_alt": "Downtown Boone in the NC High Country",
    },
    {
        "title":   "Is 2026 a Good Year to Buy a Mountain Home?",
        "slug":    "2026-03-01-is-2026-good-year-buy-mountain-home",
        "date":    "March 1, 2026",
        "tag":     "market",
        "excerpt": "Interest rates, inventory levels, and what I\u2019m seeing on the ground in Watauga, Avery, and Ashe counties this spring.",
        "image":   "/assets/blue_ridge_layers.jpg",
        "image_alt": "Layered Blue Ridge mountain ridgelines at dusk — NC High Country",
    },
    {
        "title":   "Short-Term Rental Regulations in Watauga County: What Investors Need to Know",
        "slug":    "2026-02-15-str-regulations-watauga-county",
        "date":    "February 15, 2026",
        "tag":     "investment",
        "excerpt": "A practical breakdown of STR zoning, permitting, and tax obligations for Airbnb investors in the Boone area.",
        "image":   "https://townofbannerelk.org/wp-content/uploads/2024/11/BannerElkPano1-1536x802.jpg",
        "image_alt": "Banner Elk mountain town in Avery County NC",
    },
    {
        "title":   "The Complete Guide to Buying Land in the NC High Country",
        "slug":    "2026-01-20-complete-guide-buying-land-nc-high-country",
        "date":    "January 20, 2026",
        "tag":     "land",
        "excerpt": "Topo, access, well and septic feasibility, zoning \u2014 everything you need to know before buying mountain acreage in Watauga, Avery, or Ashe County.",
        "image":   "/assets/sunset_road.jpg",
        "image_alt": "Sunset over a mountain road in the NC High Country",
    },
    {
        "title":   "Well & Septic Due Diligence for NC Mountain Properties: The Complete Checklist",
        "slug":    "2026-02-09-well-septic-due-diligence-mountain-property-nc",
        "date":    "February 9, 2026",
        "tag":     "land",
        "excerpt": "Most mountain homes in the High Country run on well water and septic — not city utilities. Here's exactly what to test, what to ask, and what to walk away from.",
        "image":   "/assets/rapids_bw.jpg",
        "image_alt": "Mountain creek rapids — water and septic are critical due diligence items for NC mountain properties",
    },
    {
        "title":   "The Leaf-Out Problem: Why Mountain Views Disappear in Summer",
        "slug":    "2026-02-13-mountain-views-leaf-out-problem-nc-high-country",
        "date":    "February 13, 2026",
        "tag":     "local",
        "excerpt": "That listing with stunning mountain views photographed in January may look very different come July. Here's what every High Country buyer needs to know about seasonal views.",
        "image":   "/assets/aerial_valley.png",
        "image_alt": "Aerial view of NC High Country valleys showing dense summer foliage",
    },
    {
        "title":   "Ashe County vs. Watauga County: A Land Buyer's Side-by-Side Comparison",
        "slug":    "2026-02-18-ashe-county-vs-watauga-county-land-comparison",
        "date":    "February 18, 2026",
        "tag":     "land",
        "excerpt": "Both counties sit in the NC High Country, but land prices, zoning, and character are very different. Here's what buyers need to know before they start looking.",
        "image":   "https://www.ashecountyrealestate.com/uploads/blog/images/legacy/2016-08-16-murals.jpg",
        "image_alt": "West Jefferson NC downtown murals — Ashe County's artsy mountain community",
    },
    {
        "title":   "Beech Mountain STR Investment: What the Ski Season Math Actually Looks Like",
        "slug":    "2026-02-23-beech-mountain-str-investment-ski-season-math",
        "date":    "February 23, 2026",
        "tag":     "investment",
        "excerpt": "At 5,506 feet, Beech Mountain is the highest town east of the Mississippi — and one of the High Country's most interesting short-term rental investment markets. Here's an honest look at the numbers.",
        "image":   "https://www.visitboone.com/wp-content/uploads/listing-uploads/gallery/2023/02/beech-mountain-resort.jpg",
        "image_alt": "Beech Mountain Resort ski slopes in winter — the highest ski area in eastern North America",
    },
    {
        "title":   "High Country Weekend: What's Happening in Boone & the Mountains — March 7–9, 2026",
        "slug":    "2026-03-06-high-country-weekend-events-spring-march-2026",
        "date":    "March 6, 2026",
        "tag":     "local",
        "excerpt": "Ski season is winding down and spring is arriving in the mountains. Here's your weekly guide to what's happening across the NC High Country this weekend.",
        "image":   "https://assets.agentfire3.com/uploads/sites/1337/2024/04/Boone-NC-King-Street.jpg",
        "image_alt": "King Street in downtown Boone NC — the heart of High Country activity",
    },
]


# ── Tag-based image pool — assets/blog/ (Wikimedia Commons, open license) ─────
IMAGE_POOL = {
    "market": [
        ("/assets/blog/boone-nc-king-street-winter.jpg", "King Street in Boone NC in winter — downtown High Country real estate market"),
        ("/assets/blog/blue-ridge-parkway-sunset.jpg", "Beautiful sunset along the Blue Ridge Parkway in North Carolina"),
        ("/assets/blog/appalachian-afterglow-blue-ridge.jpg", "Admiring the Blue Ridge Mountains in the afterglow at dusk"),
        ("/assets/blog/blue-ridge-autumn-overlook.jpg", "Autumn colors at Graveyard Fields overlook on the Blue Ridge Parkway NC"),
        ("/assets/blog/appalachian-state-sanford-mall-winter.jpg", "Sanford Mall at Appalachian State University in Boone NC in winter"),
        ("/assets/blog/appalachian-afterglow-blue-ridge.jpg", "Low-lying fog over the Appalachian Mountains — NC High Country morning"),
    ],
    "land": [
        ("/assets/blog/new-river-south-fork-todd-nc.jpg", "The South Fork of the New River in Todd NC — Ashe County waterfront land"),
        ("/assets/blog/new-river-double-shoals.jpg", "Double Shoals on the New River in Ashe County NC"),
        ("/assets/blog/linville-gorge-nc.jpg", "Linville Gorge in the NC High Country — dramatic mountain scenery"),
        ("/assets/blog/farmland-north-carolina.jpg", "Farmland in the NC mountains — rural High Country landscape"),
        ("/assets/blog/western-nc-mountain-sunset.jpg", "Mountain peak summit view in the NC High Country"),
        ("/assets/blog/foggy-appalachian-trail-overlook.jpg", "Foggy mountain view from an overlook in the NC High Country"),
        ("/assets/blog/new-river-autumn-ashe-county.jpg", "New River during autumn in New River State Park — Ashe County NC"),
    ],
    "investment": [
        ("/assets/blog/bass-lake-blowing-rock-fall.jpg", "Bass Lake in Blowing Rock NC with autumn foliage — investment area"),
        ("/assets/blog/moses-cone-estate-bass-lake.jpg", "Moses Cone Manor across Bass Lake — Blowing Rock NC investment property"),
        ("/assets/blog/grandfather-mountain-bridge.jpg", "The Mile High Swinging Bridge at Grandfather Mountain NC"),
        ("/assets/blog/appalachian-state-university-campus.jpg", "Aerial view of Appalachian State University campus — Boone NC"),
        ("https://www.visitboone.com/wp-content/uploads/listing-uploads/gallery/2023/02/beech-mountain-resort.jpg", "Beech Mountain Resort — short-term rental investment in NC High Country"),
        ("/assets/blog/blue-ridge-parkway-sunset.jpg", "Sunset along the Blue Ridge Parkway — NC mountain investment property"),
    ],
    "relocation": [
        ("/assets/blog/blue-ridge-parkway-smart-view.jpg", "Smart View overlook near the Blue Ridge Parkway — why people move to NC High Country"),
        ("/assets/blog/blue-ridge-mountains-north-carolina.jpg", "Blue Ridge Mountains in North Carolina — sweeping views for new residents"),
        ("/assets/blog/blue-ridge-mountains-north-carolina.jpg", "Family taking in the Blue Ridge Mountain scenery in North Carolina"),
        ("/assets/blog/rhododendron-blue-ridge-parkway.jpg", "Rosebay rhododendron blooming along the Blue Ridge Parkway in NC"),
        ("/assets/blog/moses-cone-estate-bass-lake.jpg", "Moses Cone Estate from Bass Lake — Blowing Rock NC lifestyle"),
        ("/assets/blog/new-river-autumn-ashe-county.jpg", "New River during autumn in Ashe County NC — High Country living"),
        ("/assets/blog/blue-ridge-parkway-smart-view.jpg", "Wisteria in bloom — spring in the NC mountains"),
    ],
    "local": [
        ("/assets/blog/blue-ridge-parkway-fall.jpg", "Fall foliage along the Blue Ridge Parkway in North Carolina"),
        ("/assets/blog/appalachian-fall-foliage-sugar-maples.jpg", "Colorful sugar maples in the Appalachian Mountains during fall foliage season"),
        ("/assets/blog/tweetsie-railroad-boone-nc.jpg", "Tweetsie Railroad amusement park between Boone and Blowing Rock NC"),
        ("/assets/blog/black-bear-north-carolina.jpg", "Black bear in North Carolina — wildlife in the High Country"),
        ("/assets/blog/rhododendron-blue-ridge-parkway.jpg", "Rhododendron blooming along the Blue Ridge Parkway in Deep Gap NC"),
        ("/assets/blog/mount-jefferson-north-carolina.jpg", "Mount Jefferson State Natural Area in Ashe County NC"),
        ("/assets/blog/appalachian-fall-foliage-sugar-maples.jpg", "Autumn leaf coloration and mountain views in the High Country"),
        ("/assets/blog/blue-ridge-autumn-overlook.jpg", "Autumn foliage at Graveyard Fields overlook, Blue Ridge Parkway NC"),
    ],
    "selling": [
        ("/assets/blog/western-nc-mountain-sunset.jpg", "Sunset view from a mountain road in western North Carolina"),
        ("/assets/blog/blue-ridge-parkway-sunset.jpg", "Beautiful sunset along the Blue Ridge Parkway — NC mountain property"),
        ("/assets/blog/blue-ridge-parkway-fall.jpg", "Blue Ridge Parkway fall foliage overlook — NC mountain home"),
        ("/assets/blog/appalachian-afterglow-blue-ridge.jpg", "Appalachian afterglow at sunset — the appeal of NC mountain real estate"),
        ("/assets/blog/blue-ridge-mountains-north-carolina.jpg", "Blue Ridge Mountains in North Carolina — selling mountain real estate"),
        ("/assets/blog/blue-ridge-parkway-autumn.jpg", "Autumn colors along the Blue Ridge Parkway — NC mountain homes for sale"),
    ],
}

def get_image_for_tag(tag, slug=""):
    pool = IMAGE_POOL.get(tag, IMAGE_POOL["market"])
    return pool[hash(slug) % len(pool)]

# ── Topic rotation ─────────────────────────────────────────────────────────────
# Evergreen topics — always relevant, rotated by week
EVERGREEN_TOPICS = [
    "High Country real estate market update — prices, inventory, and what buyers and sellers should know right now in Boone, Blowing Rock, Banner Elk, and West Jefferson",
    "Appalachian State University student housing: the buy-and-rent strategy for families of App State students",
    "Buying land or mountain property in the High Country of NC — what to check before you make an offer",
    "Relocation guide: why people are moving to Boone NC and the High Country — remote workers, retirees, and families",
    "Second home and vacation property investment in the High Country — what makes a mountain property a strong investment",
    "Why the High Country appeals to families, retirees, and remote workers — lifestyle, community, and real estate value",
    "New construction vs. existing homes in the NC High Country — what buyers need to know",
    "Selling a mountain home in the High Country — pricing strategy, timing, and what makes properties stand out",
    "Short-term rental investment in the High Country — honest analysis of STR potential in Watauga, Avery, and Ashe counties",
    "Buying a home near App State: what out-of-state families need to know about Boone NC real estate",
]

# Calendar-aware topics by month — only appears in the relevant window
CALENDAR_TOPICS = {
    # (month_start, month_end): topic
    (1, 2):  "Winter real estate in the High Country — why January and February are underrated months to buy a mountain home",
    (3, 3):  "Spring real estate season is arriving in the High Country — what buyers and sellers should do right now in March",
    (4, 5):  "Spring is peak season in the High Country — what buyers need to know about competing in a busy spring market",
    (6, 7):  "Summer in the Blue Ridge Mountains — why summer visitors become High Country buyers, and what they should know",
    (8, 8):  "Back-to-school season and App State move-in — student housing market update and what parents should know",
    (9, 9):  "Fall is coming to the High Country — why autumn is one of the best times to buy or sell mountain real estate",
    (10, 10): "Leaf season in the High Country — foliage, fall buyers, and what the real estate market looks like in October",
    (11, 11): "Thanksgiving and the holiday season approach — why serious buyers are still active and what sellers should know",
    (12, 12): "Year-end real estate in the High Country — December buyers are serious and motivated, here's what that means",
}

def get_recent_tags_and_topics(days=10):
    """Read the last N days of meta.json files and return recent titles/tags to avoid repeating."""
    recent = []
    if not BLOG_DIR.exists():
        return recent
    cutoff = date.today().toordinal() - days
    for d in BLOG_DIR.iterdir():
        if not d.is_dir():
            continue
        mf = d / "meta.json"
        if not mf.exists():
            continue
        # Parse date from slug prefix YYYY-MM-DD
        import re as _re
        m = _re.match(r'(\d{4}-\d{2}-\d{2})', d.name)
        if not m:
            continue
        try:
            post_date = date.fromisoformat(m.group(1))
        except ValueError:
            continue
        if post_date.toordinal() >= cutoff:
            try:
                meta = json.loads(mf.read_text())
                recent.append(meta.get("title", "").lower())
            except Exception:
                pass
    return recent

def get_topic():
    today = date.today()
    dow   = today.weekday()
    month = today.month
    week  = today.isocalendar()[1]

    # Friday = always a weekend events/local life post
    if dow == 4:
        return (
            f"Weekend events and things to do in Boone and the NC High Country — "
            f"what's happening this weekend in {today.strftime('%B %Y')}, "
            f"including outdoor activities, local events, dining, and why this is a great time to explore the area as a potential buyer or visitor"
        )

    # Check recent posts to avoid repeating the same calendar topic within the same week
    recent_titles = get_recent_tags_and_topics(days=8)

    # Check for a calendar-relevant topic this month
    for (m_start, m_end), topic in CALENDAR_TOPICS.items():
        if m_start <= month <= m_end:
            # Extract the first 4 meaningful words of the calendar topic as a fingerprint
            topic_words = [w.lower() for w in topic.split()[:6] if len(w) > 3]
            recently_used = any(
                any(word in title for word in topic_words)
                for title in recent_titles
            )
            if week % 2 == 1 and not recently_used:
                return topic
            # Fall through to evergreen if calendar topic was used recently

    # Fall back to evergreen rotation — offset by day-of-week so Mon/Wed/Fri get different topics
    dow_offset = {0: 0, 2: 1, 4: 2}.get(dow, 0)
    return EVERGREEN_TOPICS[(week + dow_offset) % len(EVERGREEN_TOPICS)]

def get_season():
    m = date.today().month
    if m in (12,1,2): return "winter"
    if m in (3,4,5):  return "spring"
    if m in (6,7,8):  return "summer"
    return "fall"

def get_holidays():
    today = date.today()
    all_h = {
        (1,1):"New Year\u2019s Day",(2,14):"Valentine\u2019s Day",(3,17):"St. Patrick\u2019s Day",
        (5,26):"Memorial Day weekend",(7,4):"Fourth of July",(9,1):"Labor Day weekend",
        (10,31):"Halloween",(11,27):"Thanksgiving",(12,25):"Christmas",(12,31):"New Year\u2019s Eve"
    }
    upcoming = []
    for (m,d),name in all_h.items():
        try:
            h = date(today.year, m, d)
        except ValueError:
            continue
        delta = (h - today).days
        if 0 <= delta <= 45:
            upcoming.append(f"{name} ({delta} days away)")
    return ", ".join(upcoming) if upcoming else "no major holidays in the next 45 days"

# ── Shared HTML fragments ──────────────────────────────────────────────────────
SITE_LOGO_SVG = """<svg viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
        <path d="M20 4L4 28h10l6-10 6 10h10L20 4z" fill="currentColor" opacity="0.15"/>
        <path d="M20 8L8 26h7l5-8.5 5 8.5h7L20 8z" stroke="currentColor" stroke-width="1.5" fill="none"/>
        <path d="M14 26l3 6h6l3-6" stroke="currentColor" stroke-width="1.5" fill="none"/>
        <circle cx="20" cy="18" r="1.5" fill="currentColor" opacity="0.4"/>
      </svg>"""

def shared_head(title, description, canonical, keywords="", og_type="article", pub_date=""):
    og_article = f'\n  <meta property="article:published_time" content="{pub_date}">' if pub_date else ""
    kw_tag = f'\n  <meta name="keywords" content="{keywords}">' if keywords else ""
    return f"""  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{description}">{kw_tag}
  <meta name="author" content="{AUTHOR_NAME}">
  <meta name="robots" content="index, follow">
  <meta property="og:type" content="{og_type}">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical}">
  <meta property="og:site_name" content="{SITE_NAME}">{og_article}
  <link rel="canonical" href="{canonical}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cormorant:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500;1,600&family=Work+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/base.css">
  <link rel="stylesheet" href="/style.css">
  <script>
  // Apply theme before paint to avoid flash
  (function() {{
    var saved = localStorage.getItem('theme');
    var theme = saved || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', theme);
  }})();
  </script>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-VJT8L02CWS"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-VJT8L02CWS');
  </script>"""

def shared_header(active_page="blog"):
    pages = [
        ("","Home"), ("about","About"), ("areas","Areas"),
        ("services","Services"), ("faq","FAQ"), ("resources","Resources"),
        ("blog","Blog"), ("contact","Contact"),
    ]
    links = ""
    for href, label in pages:
        page_id = href.split("/")[-1] or "index"
        aria    = ' aria-current="page"' if page_id == active_page else ""
        href_val = "/" if href == "" else f"/{href}"
        links  += f'      <a href="{href_val}"{aria}>{label}</a>\n'

    return f"""<a class="skip-link" href="#main">Skip to content</a>

<header class="site-header" role="banner">
  <div class="header-inner">
    <a href="/" class="site-logo" aria-label="Andrew Plyler \u2014 Home">
      {SITE_LOGO_SVG}
      <span class="logo-text">
        <span class="logo-name">Andrew Plyler</span>
        <span class="logo-tag">The High Country Realtor</span>
      </span>
    </a>
    <nav class="main-nav" aria-label="Primary">
{links}      <a href="tel:{AUTHOR_PHONE_RAW}" class="nav-cta">Give me a holler!</a>
    </nav>
    <button class="theme-toggle" aria-label="Toggle dark mode" type="button">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
    </button>
    <button class="mobile-menu-btn" aria-label="Open menu" aria-expanded="false" type="button">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
    </button>
  </div>
</header>"""

def shared_footer():
    return f"""<footer class="site-footer" role="contentinfo">
  <div class="footer-grid">
    <div class="footer-brand">
      <a href="/" class="site-logo" aria-label="Andrew Plyler \u2014 Home" style="text-decoration:none;">
        <svg viewBox="0 0 40 40" width="36" height="36" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path d="M20 4L4 28h10l6-10 6 10h10L20 4z" fill="currentColor" opacity="0.15"/>
          <path d="M20 8L8 26h7l5-8.5 5 8.5h7L20 8z" stroke="currentColor" stroke-width="1.5" fill="none"/>
          <path d="M14 26l3 6h6l3-6" stroke="currentColor" stroke-width="1.5" fill="none"/>
        </svg>
        <span class="logo-text">
          <span class="logo-name">Andrew Plyler</span>
          <span class="logo-tag">The High Country Realtor</span>
        </span>
      </a>
      <p>Born in Boone, raised in Fayetteville, and rooted in the High Country for good. Helping buyers and sellers navigate mountain real estate with local knowledge and honest advice.</p>
      <div class="footer-social">
        <a href="https://www.instagram.com/thcrealtor" target="_blank" rel="noopener noreferrer" aria-label="Instagram"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="5"/><circle cx="17.5" cy="6.5" r="1.5" fill="currentColor" stroke="none"/></svg></a>
        <a href="https://www.facebook.com/THCRealtor" target="_blank" rel="noopener noreferrer" aria-label="Facebook"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z"/></svg></a>
        <a href="https://x.com/THCRealtor" target="_blank" rel="noopener noreferrer" aria-label="X (Twitter)"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg></a>
        <a href="https://www.linkedin.com/in/andrewplyler" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 8a6 6 0 016 6v7h-4v-7a2 2 0 00-4 0v7h-4v-7a6 6 0 016-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg></a>
      </div>
    </div>
    <div>
      <h4 class="footer-heading">Quick Links</h4>
      <ul class="footer-links" role="list">
        <li><a href="/about">About Andrew</a></li>
        <li><a href="/areas">Areas Served</a></li>
        <li><a href="/services">Services</a></li>
        <li><a href="/student-housing">College Housing</a></li>
        <li><a href="/resources">Resources</a></li>
        <li><a href="/faq">FAQ</a></li>
        <li><a href="/blog">Blog</a></li>
        <li><a href="/contact">Contact</a></li>
      </ul>
    </div>
    <div>
      <h4 class="footer-heading">Communities</h4>
      <ul class="footer-links" role="list">
        <li><a href="/areas">Boone</a></li>
        <li><a href="/areas">Blowing Rock</a></li>
        <li><a href="/areas">Banner Elk</a></li>
        <li><a href="/areas">Valle Crucis</a></li>
        <li><a href="/areas">Beech Mountain</a></li>
        <li><a href="/areas">West Jefferson</a></li>
      </ul>
    </div>
    <div>
      <h4 class="footer-heading">Contact</h4>
      <ul class="footer-links" role="list">
        <li><a href="tel:+17706391233">(770) 639-1233</a></li>
        <li><a href="mailto:{AUTHOR_EMAIL}">{AUTHOR_EMAIL}</a></li>
        <li>895 Blowing Rock Rd.<br>Boone, NC 28607</li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <p>&copy; {date.today().year} Andrew Plyler, REALTOR&reg;/Broker. Blue Ridge Realty &amp; Investments. All rights reserved. Equal Housing Opportunity.</p>
  </div>
</footer>"""

SHARED_JS = """
// Dark/light mode toggle — respects OS preference, manual override saved to localStorage
(function() {
  const toggle = document.querySelector('.theme-toggle');
  const html   = document.documentElement;
  if (toggle) {
    toggle.addEventListener('click', function() {
      const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
    });
  }
  // Keep in sync if user changes OS preference while page is open
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
    if (!localStorage.getItem('theme')) {
      html.setAttribute('data-theme', e.matches ? 'dark' : 'light');
    }
  });
})();

// Mobile menu
(function() {
  const btn = document.querySelector('.mobile-menu-btn');
  const nav = document.querySelector('.main-nav');
  if (btn && nav) {
    btn.addEventListener('click', function() {
      const open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open);
    });
  }
})();

// Scroll-aware header
(function() {
  const header = document.querySelector('.site-header');
  if (!header) return;
  window.addEventListener('scroll', function() {
    header.classList.toggle('scrolled', window.scrollY > 20);
  }, { passive: true });
})();
"""

POST_CSS = """
  .post-hero {
    padding: clamp(4rem, 10vw, 6rem) var(--space-4) clamp(2rem, 5vw, 3rem);
    background: var(--color-surface-offset);
    border-bottom: 1px solid var(--color-divider);
  }
  .post-hero .container-narrow { max-width: 800px; }
  .post-hero h1 {
    font-family: var(--font-display);
    font-size: var(--text-2xl);
    font-weight: 500;
    letter-spacing: -0.02em;
    line-height: 1.2;
    margin-bottom: var(--space-5);
    color: var(--color-text);
  }
  .post-meta {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: var(--space-3);
    font-size: var(--text-sm);
    color: var(--color-text-muted);
  }
  .post-meta-dot { opacity: 0.4; }
  .post-layout {
    max-width: 800px;
    margin: 0 auto;
    padding: clamp(var(--space-12), 6vw, var(--space-20)) var(--space-4);
  }
  .post-body { font-size: var(--text-base); line-height: 1.8; color: var(--color-text); }
  .post-body h2 {
    font-family: var(--font-display);
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--color-text);
    margin: clamp(var(--space-8), 4vw, var(--space-12)) 0 var(--space-4);
    line-height: 1.3;
  }
  .post-body p   { margin-bottom: var(--space-6); max-width: 72ch; }
  .post-body ul, .post-body ol { margin: 0 0 var(--space-6) var(--space-8); }
  .post-body li  { margin-bottom: var(--space-2); font-size: var(--text-base); }
  .post-body strong { font-weight: 600; color: var(--color-text); }
  .post-body em     { font-style: italic; color: var(--color-accent); }
  .author-card {
    display: flex;
    gap: var(--space-6);
    align-items: flex-start;
    background: var(--color-surface);
    border: 1px solid oklch(from var(--color-text) l c h / 0.08);
    border-radius: var(--radius-lg);
    padding: var(--space-8);
    margin-top: clamp(var(--space-12), 6vw, var(--space-16));
  }
  @media (max-width: 600px) { .author-card { flex-direction: column; } }
  .author-avatar {
    width: 72px; height: 72px;
    border-radius: var(--radius-full);
    background: var(--color-primary);
    flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-family: var(--font-display);
    font-size: var(--text-xl);
    color: var(--color-text-inverse);
    font-weight: 600;
  }
  .author-info h3 {
    font-family: var(--font-display);
    font-size: var(--text-lg);
    font-weight: 600;
    color: var(--color-text);
    margin-bottom: var(--space-1);
  }
  .author-info p {
    font-size: var(--text-sm);
    color: var(--color-text-muted);
    line-height: 1.6;
    margin-bottom: var(--space-5);
    max-width: 52ch;
  }
  .author-cta { display: flex; gap: var(--space-3); flex-wrap: wrap; }
  .back-link {
    display: inline-flex;
    align-items: center;
    gap: var(--space-2);
    margin-top: var(--space-10);
    font-size: var(--text-sm);
    font-weight: 600;
    color: var(--color-primary);
    text-decoration: none;
  }
  .back-link:hover { color: var(--color-primary-hover); }
  .blog-index-hero {
    padding: clamp(var(--space-16), 10vw, var(--space-24)) var(--space-4) clamp(var(--space-8), 5vw, var(--space-12));
    background: var(--color-surface-offset);
    border-bottom: 1px solid var(--color-divider);
  }
"""


# ── Tag display metadata ───────────────────────────────────────────────────────
TAG_META = {
    "land":       {"label": "Land",            "color": "#8B4A1A", "bg": "#F5EDE8", "css": "tag-land"},
    "investment": {"label": "Investment & STR", "color": "#3D7A78", "bg": "#E8F5F4", "css": "tag-investment"},
    "market":     {"label": "Market",           "color": "#C0622A", "bg": "#FFF0E8", "css": "tag-market"},
    "relocation": {"label": "Relocation",       "color": "#4A5240", "bg": "#E8F0E8", "css": "tag-relocation"},
    "local":      {"label": "Local Life",       "color": "#6B5A4A", "bg": "#F0EBE8", "css": "tag-local"},
    "selling":    {"label": "Selling",          "color": "#1A3B5C", "bg": "#E8EFF5", "css": "tag-selling"},
}

def tag_badge_html(tag, inline=False):
    """Return a styled tag badge. inline=True for post pages, False for cards."""
    t = TAG_META.get(tag, TAG_META["market"])
    if inline:
        return (
            f'<span style="display:inline-block;font-size:0.68rem;font-weight:700;'
            f'letter-spacing:0.12em;text-transform:uppercase;padding:0.22rem 0.65rem;'
            f'border-radius:3px;background:{t["bg"]};color:{t["color"]};'
            f'margin-bottom:0.6rem;">{t["label"]}</span>'
        )
    return f'<span class="blog-card-tag {t["css"]}">{t["label"]}</span>'

# ── AI content generation ──────────────────────────────────────────────────────
def generate_post():
    today_str = date.today().strftime("%B %d, %Y")
    prompt = f"""You are writing a blog post for Andrew Plyler, REALTOR\u00ae at Blue Ridge Realty & Investments in Boone, NC.
Andrew was born in Boone, grew up in Fayetteville, and graduated from App State in 2002. His family has had a home in Valle Crucis since 1978. In 2020, turning 40 and facing a cancelled camp season due to Covid, he decided to plant his roots in the High Country for good and switch careers to real estate. He is a REALTOR®/Broker, specializing in High Country real estate.

TODAY: {today_str} | SEASON: {get_season()} | UPCOMING: {get_holidays()}
TOPIC: {get_topic()}

Write a complete, high-quality blog post optimized for Google SEO and AI search engines (ChatGPT, Perplexity, Claude).
Naturally include keywords: "Boone NC real estate", "High Country REALTOR", "buy a home in Boone NC", "Appalachian State housing", "mountain property NC".

REQUIREMENTS:
- 700\u20131,000 words of body content
- Tone: mix of warm local expert AND professional market insight (vary by topic)
- 3\u20135 H2 subheadings
- At least one specific local detail (street, neighborhood, landmark, event)
- End with a soft CTA to contact Andrew Plyler
- Do NOT fabricate MLS statistics \u2014 use descriptive language for market conditions
- Do NOT use the word "nestled"
- ALWAYS use the Oxford comma in all lists

OUTPUT: respond ONLY with a JSON object (no markdown fences):
{{
  "title": "SEO title (60 chars max)",
  "meta_description": "155-char meta description with primary keyword",
  "slug": "url-friendly-slug",
  "focus_keyword": "primary SEO keyword phrase",
  "secondary_keywords": ["kw1","kw2","kw3"],
  "excerpt": "2-sentence plain-text excerpt for blog index card",
  "image_url": "leave blank — image is assigned automatically from assets/blog/ library based on tag",
  "image_alt": "descriptive alt text for the image",
  "tag": "one of: land | investment | market | relocation | local | selling",
  "body_html": "full post body using only h2/p/ul/li/strong/em tags — NO attributes on any tags, plain tags only (e.g. <h2> not <h2 class=something>)"
}}

TAGGING RULES:
- land: buying land, perc tests, well/septic, mountain due diligence, lots/acreage
- investment: STR, Airbnb, VRBO, rental income, cap rate, investor analysis
- market: price trends, inventory, interest rates, market conditions
- relocation: moving to Boone, second homes, retirement, lifestyle
- local: events, weekend guides, seasonal living, local knowledge
- selling: listing strategy, pricing, seller tips, how to sell mountain property
"""

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg    = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=3000,
        messages=[{"role":"user","content":prompt}]
    )
    raw = msg.content[0].text.strip()
    raw = re.sub(r'```json\s*','',raw)
    raw = re.sub(r'```\s*','',raw)
    raw = re.sub(r'\s*```$','',raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        try:
            from json_repair import repair_json
            return json.loads(repair_json(raw))
        except Exception:
            _m = re.search("[{].*[}]", raw, re.DOTALL)
            return json.loads(_m.group(0) if _m else raw)

# ── HTML builders ──────────────────────────────────────────────────────────────
def build_post_html(post, pub_date, slug):
    iso  = date.today().isoformat()
    kws  = ", ".join(post.get("secondary_keywords", []))
    canonical = f"{SITE_URL}/blog/{slug}/"

    schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post["title"],
        "description": post["meta_description"],
        "author": {"@type":"Person","name":AUTHOR_NAME,"url":AUTHOR_BRAND_URL},
        "publisher": {"@type":"Organization","name":SITE_NAME,"url":SITE_URL},
        "datePublished": iso,
        "dateModified": iso,
        "mainEntityOfPage": canonical,
        "keywords": post["focus_keyword"] + ", " + kws
    }, indent=2)

    head = shared_head(
        title       = f"{post['title']} | {SITE_NAME}",
        description = post['meta_description'],
        canonical   = canonical,
        keywords    = f"{post['focus_keyword']}, {kws}",
        og_type     = "article",
        pub_date    = iso,
    )

    # Always resolve an image — use image_url if AI provided one, otherwise pull from pool
    resolved_image     = post.get("image_url") or get_image_for_tag(post.get("tag", "market"), slug)[0]
    resolved_image_alt = post.get("image_alt") or get_image_for_tag(post.get("tag", "market"), slug)[1]
    img_html = f"""  <div class="image-band" style="aspect-ratio:21/8;">
    <img src="{resolved_image}" alt="{resolved_image_alt}" loading="eager" />
  </div>"""

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
{head}
  <script type="application/ld+json">
{schema}
  </script>
  <style>{POST_CSS}
.blog-card-tag {{ display:inline-block;font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;padding:0.2rem 0.6rem;border-radius:3px;margin-bottom:0.4rem; }}
.tag-relocation {{ background:#E8F0E8;color:#4A5240; }}
.tag-market     {{ background:#FFF0E8;color:#C0622A; }}
.tag-investment {{ background:#E8F5F4;color:#3D7A78; }}
.tag-land       {{ background:#F5EDE8;color:#8B4A1A; }}
.tag-local      {{ background:#F0EBE8;color:#6B5A4A; }}
.tag-selling    {{ background:#E8EFF5;color:#1A3B5C; }}
.tag-filter-btn {{ background:white;border:1px solid #D5CCC0;color:#5A4A3A;padding:0.35rem 0.9rem;border-radius:99px;font-size:0.8rem;font-weight:600;cursor:pointer;transition:all 0.18s;font-family:inherit; }}
.tag-filter-btn:hover,.tag-filter-btn.active {{ background:#3B2F2F;color:white;border-color:#3B2F2F; }}
.blog-card.hidden {{ display:none !important; }}
.blog-filter-bar {{ display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:2rem; }}
.filter-btn {{ background:white;border:1px solid #D5CCC0;color:#5A4A3A;padding:0.35rem 0.9rem;border-radius:99px;font-size:0.8rem;font-weight:600;cursor:pointer;transition:all 0.18s;font-family:inherit; }}
.filter-btn:hover,.filter-btn.active {{ background:#3B2F2F;color:white;border-color:#3B2F2F; }}
  </style>
  <script>
function filterPosts(tag) {{
  document.querySelectorAll('.tag-filter-btn').forEach(function(b){{b.classList.toggle('active',b.dataset.filter===tag);}});
  var v=0;
  document.querySelectorAll('.blog-card[data-tag]').forEach(function(c){{var m=tag==='all'||c.dataset.tag===tag;c.classList.toggle('hidden',!m);if(m)v++;}});
  var n=document.getElementById('no-results');if(n)n.style.display=v===0?'block':'none';
}}
  </script>
  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-VJT8L02CWS"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-VJT8L02CWS');
  </script>
</head>
<body>

{shared_header("blog")}

<main id="main">

  <div class="post-hero">
    <div class="container-narrow">
      <p class="section-label">High Country Real Estate</p>
      {tag_badge_html(post.get('tag', 'market'), inline=True)}
      <h1>{post['title']}</h1>
      <div class="post-meta">
        <span>{AUTHOR_NAME}</span>
        <span class="post-meta-dot">&middot;</span>
        <span>{pub_date}</span>
        <span class="post-meta-dot">&middot;</span>
        <span>Boone, NC</span>
      </div>
    </div>
  </div>

{img_html}

  <div class="post-layout">
    <article class="post-body" itemscope itemtype="https://schema.org/BlogPosting">
      <meta itemprop="headline"      content="{post['title']}">
      <meta itemprop="datePublished" content="{iso}">
      <meta itemprop="author"        content="{AUTHOR_NAME}">
      {post['body_html']}
    </article>

    <div class="author-card">
      <div class="author-avatar">AP</div>
      <div class="author-info">
        <h3>{AUTHOR_NAME}</h3>
        <p>{AUTHOR_TITLE}<br>Born in Boone &middot; App State alum &middot; Roots planted firmly in the High Country</p>
        <div class="author-cta">
          <a href="/contact" class="btn btn-primary">Get in Touch</a>
          <a href="tel:{AUTHOR_PHONE_RAW}" class="btn btn-outline">Give me a holler!</a>
        </div>
      </div>
    </div>

    <a href="/blog" class="back-link">&larr; Back to all posts</a>
  </div>

  <section class="cta-banner">
    <h2>Ready to Find Your Mountain Home?</h2>
    <p>Whether you&rsquo;re buying, selling, or just exploring &mdash; let&rsquo;s talk. No pressure, just honest mountain real estate advice.</p>
    <a href="/contact" class="btn btn-accent">Let&rsquo;s Get Started</a>
  </section>

</main>

{shared_footer()}

<script>{SHARED_JS}</script>
</body>
</html>"""

def build_index_html(all_posts):
    """Build the blog listing page. all_posts is a list of dicts sorted newest-first."""
    cards = ""
    for p in all_posts:
        img_html = ""
        if p.get("image"):
            img_html = f'''        <div class="blog-card-img">
          <img src="{p['image']}" alt="{p.get('image_alt', p['title'])}" loading="lazy" />
        </div>\n'''
        tag   = p.get("tag", "market")
        badge = tag_badge_html(tag)
        cards += (
            f'      <a href="/blog/{p["slug"]}/" class="blog-card fade-in" data-tag="{tag}">\n'
            f'{img_html}'
            f'        <div class="blog-card-body">\n'
            f'          {badge}<br/><span class="blog-card-date">{p["date"]}</span>\n'
            f'          <h2 class="blog-card-title">{p["title"]}</h2>\n'
            f'          <p class="blog-card-excerpt">{p["excerpt"]}</p>\n'
            f'          <span class="blog-card-link">Read more &rarr;</span>\n'
            f'        </div>\n'
            f'      </a>\n'
        )

    if not cards.strip():
        cards = '<p style="text-align:center;color:var(--color-text-muted);padding:var(--space-16) 0;font-style:italic;grid-column:1/-1;">Posts coming soon. Check back Monday!</p>'

    head = shared_head(
        title       = f"Blog | {SITE_NAME}",
        description = f"Local insights on Boone NC real estate, mountain living, App State housing, events, and more from Andrew Plyler, REALTOR\u00ae.",
        canonical   = f"{SITE_URL}/blog/",
        og_type     = "website",
    )

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
{head}
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Blog",
    "name": "The High Country Realtor Blog",
    "url": "{SITE_URL}/blog/",
    "description": "Real estate insights, mountain living tips, and High Country NC market updates from Andrew Plyler, REALTOR\u00ae",
    "author": {{
      "@type": "Person",
      "name": "{AUTHOR_NAME}",
      "url": "{AUTHOR_BRAND_URL}"
    }}
  }}
  </script>
  <style>{POST_CSS}</style>
</head>
<body>

{shared_header("blog")}

<main id="main">

  <div class="blog-index-hero">
    <div class="container">
      <p class="section-label">From the Blog</p>
      <h1 class="section-title">Mountain market insights &amp; local knowledge.</h1>
      <p class="section-desc">Real estate tips, seasonal guides, and High Country living from a Boone native.</p>
    </div>
  </div>

  <section class="section">
    <div class="container">
      <div class="blog-filter-bar">
        <button class="filter-btn active" data-filter="all">All Posts</button>
        <button class="filter-btn" data-filter="market">Market</button>
        <button class="filter-btn" data-filter="land">Land</button>
        <button class="filter-btn" data-filter="investment">Investment &amp; STR</button>
        <button class="filter-btn" data-filter="relocation">Relocation</button>
        <button class="filter-btn" data-filter="local">Local Life</button>
        <button class="filter-btn" data-filter="selling">Selling</button>
      </div>
      <div class="grid-3" id="blogGrid">
{cards}
      </div>
    </div>
  </section>
  <script>
  (function(){{
    var btns=document.querySelectorAll(".filter-btn");
    var cards=document.querySelectorAll("#blogGrid .blog-card");
    btns.forEach(function(btn){{
      btn.addEventListener("click",function(){{
        btns.forEach(function(b){{b.classList.remove("active");}});
        btn.classList.add("active");
        var f=btn.getAttribute("data-filter");
        cards.forEach(function(card){{
          card.style.display=(f==="all"||card.getAttribute("data-tag")===f)?"":"none";
        }});
      }});
    }});
  }})();
  </script>

  <section class="cta-banner">
    <h2>Ready to Find Your Mountain Home?</h2>
    <p>Whether you&rsquo;re buying, selling, or just exploring &mdash; let&rsquo;s talk. No pressure, just honest mountain real estate advice.</p>
    <a href="/contact" class="btn btn-accent">Let&rsquo;s Get Started</a>
  </section>

</main>

{shared_footer()}

<script>{SHARED_JS}</script>
</body>
</html>"""

# ── Collect all post metadata ──────────────────────────────────────────────────
def collect_all_meta():
    """
    Merge MANUAL_POSTS (hardcoded) with auto-generated posts (from meta.json files).
    Manual posts take precedence if a slug matches. Result sorted newest-first.
    """
    manual_slugs = {p["slug"] for p in MANUAL_POSTS}
    auto_posts = []

    if BLOG_DIR.exists():
        for d in BLOG_DIR.iterdir():
            if not d.is_dir():
                continue
            if d.name in manual_slugs:
                continue  # manual post owns this slug
            mf = d / "meta.json"
            if mf.exists():
                try:
                    meta = json.loads(mf.read_text())
                    # Ensure image fields exist (older posts may not have them)
                    meta.setdefault("image", "https://assets.agentfire3.com/uploads/sites/1337/2024/04/Boone-NC-King-Street.jpg")
                    meta.setdefault("image_alt", meta.get("title", "High Country Real Estate"))
                    meta.setdefault("tag", "market")  # fallback tag for older posts
                    auto_posts.append(meta)
                except Exception:
                    pass

    all_posts = list(MANUAL_POSTS) + auto_posts

    # Sort newest-first by slug (slug starts with YYYY-MM-DD)
    def sort_key(p):
        match = re.match(r'(\d{4}-\d{2}-\d{2})', p.get("slug", ""))
        return match.group(1) if match else "0000-00-00"

    all_posts.sort(key=sort_key, reverse=True)
    return all_posts

# ── Main ───────────────────────────────────────────────────────────────────────
def update_sitemap(slug, pub_date_iso):
    """Add the new blog post to sitemap.xml."""
    SITEMAP = Path("sitemap.xml")
    if not SITEMAP.exists():
        return
    content = SITEMAP.read_text()
    new_url = f"""  <url><loc>https://plyler.realtor/blog/{slug}/</loc><lastmod>{pub_date_iso}</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>"""
    if slug not in content:
        content = content.replace('</urlset>', f'{new_url}\n</urlset>')
        SITEMAP.write_text(content)
        print(f"  \u2713 Sitemap \u2192 added {slug}")

def main():
    print("\U0001f3d4  Generating High Country blog post...")

    today        = date.today()
    today_prefix = today.isoformat()
    existing     = [d for d in BLOG_DIR.iterdir() if d.is_dir() and d.name.startswith(today_prefix)]
    if existing:
        print(f"  \u26a0\ufe0f  Post for {today_prefix} already exists ({existing[0].name}) — skipping.")
        all_meta   = collect_all_meta()
        index_html = build_index_html(all_meta)
        BLOG_INDEX_ROOT.write_text(index_html, encoding="utf-8")
        BLOG_INDEX_SUB.write_text(index_html, encoding="utf-8")
        print(f"  \u2713 Index rebuilt ({len(all_meta)} posts)")
        return

    post     = generate_post()
    pub_date = today.strftime("%B %d, %Y")
    slug     = re.sub(r'[^a-z0-9-]', '-', post["slug"].lower())
    slug     = re.sub(r'-+', '-', slug).strip('-')
    slug     = f"{today.isoformat()}-{slug}"

    # Write new post
    post_dir = BLOG_DIR / slug
    post_dir.mkdir(parents=True, exist_ok=True)
    (post_dir / "index.html").write_text(
        build_post_html(post, pub_date, slug), encoding="utf-8"
    )
    print(f"  \u2713 Post \u2192 blog/{slug}/index.html")

    # Save meta.json so future runs pick it up
    (post_dir / "meta.json").write_text(json.dumps({
        "title":     post["title"],
        "slug":      slug,
        "date":      pub_date,
        "tag":       post.get("tag", "market"),
        "excerpt":   post["excerpt"],
        "image":     post.get("image_url") or get_image_for_tag(post.get("tag","market"), slug)[0],
        "image_alt": post.get("image_alt") or get_image_for_tag(post.get("tag","market"), slug)[1],
    }, indent=2), encoding="utf-8")

    # Rebuild both index files
    update_sitemap(slug, today.isoformat())
    all_meta = collect_all_meta()
    index_html = build_index_html(all_meta)

    BLOG_INDEX_ROOT.write_text(index_html, encoding="utf-8")
    print(f"  \u2713 Index \u2192 blog.html ({len(all_meta)} posts total)")

    BLOG_INDEX_SUB.write_text(index_html, encoding="utf-8")
    print(f"  \u2713 Index \u2192 blog/index.html ({len(all_meta)} posts total)")

    print("\u2705 Done!")

if __name__ == "__main__":
    main()
