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
MANUAL_POSTS = [
    {
        "title":   "Moving to Boone NC: Complete High Country Relocation Guide",
        "slug":    "2026-03-20-moving-to-boone-nc-high-country-relocation-guide",
        "date":    "March 20, 2026",
        "excerpt": "Considering a move to the beautiful Blue Ridge Mountains? This comprehensive guide covers everything you need to know about relocating to Boone and the High Country region.",
        "image":   "https://assets.agentfire3.com/uploads/sites/1337/2024/04/Boone-NC-King-Street.jpg",
        "image_alt": "Downtown Boone in the NC High Country",
    },
    {
        "title":   "Is 2026 a Good Year to Buy a Mountain Home?",
        "slug":    "2026-03-01-is-2026-good-year-buy-mountain-home",
        "date":    "March 1, 2026",
        "excerpt": "Interest rates, inventory levels, and what I\u2019m seeing on the ground in Watauga, Avery, and Ashe counties this spring.",
        "image":   "https://assets.agentfire3.com/uploads/sites/1337/2024/04/Boone-NC-King-Street.jpg",
        "image_alt": "Downtown Boone NC High Country spring 2026",
    },
    {
        "title":   "Short-Term Rental Regulations in Watauga County: What Investors Need to Know",
        "slug":    "2026-02-15-str-regulations-watauga-county",
        "date":    "February 15, 2026",
        "excerpt": "A practical breakdown of STR zoning, permitting, and tax obligations for Airbnb investors in the Boone area.",
        "image":   "https://townofbannerelk.org/wp-content/uploads/2024/11/BannerElkPano1-1536x802.jpg",
        "image_alt": "Banner Elk mountain town in Avery County NC",
    },
    {
        "title":   "The Complete Guide to Buying Land in the NC High Country",
        "slug":    "2026-01-20-complete-guide-buying-land-nc-high-country",
        "date":    "January 20, 2026",
        "excerpt": "Topo, access, well and septic feasibility, zoning \u2014 everything you need to know before buying mountain acreage in Watauga, Avery, or Ashe County.",
        "image":   "https://b2290346.smushcdn.com/2290346/wp-content/uploads/2025/09/IMG_6222-scaled.jpeg?lossy=2&strip=1&webp=1",
        "image_alt": "Blowing Rock NC mountain village",
    },
    {
        "title":   "Well & Septic Due Diligence for NC Mountain Properties: The Complete Checklist",
        "slug":    "2026-02-09-well-septic-due-diligence-mountain-property-nc",
        "date":    "February 9, 2026",
        "excerpt": "Most mountain homes in the High Country run on well water and septic — not city utilities. Here's exactly what to test, what to ask, and what to walk away from.",
        "image":   "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1400&q=80&fit=crop",
        "image_alt": "Rural mountain property with well and wooded lot in the NC High Country",
    },
    {
        "title":   "The Leaf-Out Problem: Why Mountain Views Disappear in Summer",
        "slug":    "2026-02-13-mountain-views-leaf-out-problem-nc-high-country",
        "date":    "February 13, 2026",
        "excerpt": "That listing with stunning mountain views photographed in January may look very different come July. Here's what every High Country buyer needs to know about seasonal views.",
        "image":   "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1400&q=80&fit=crop",
        "image_alt": "Blue Ridge Mountains panoramic view from a high ridge in North Carolina",
    },
    {
        "title":   "Ashe County vs. Watauga County: A Land Buyer's Side-by-Side Comparison",
        "slug":    "2026-02-18-ashe-county-vs-watauga-county-land-comparison",
        "date":    "February 18, 2026",
        "excerpt": "Both counties sit in the NC High Country, but land prices, zoning, and character are very different. Here's what buyers need to know before they start looking.",
        "image":   "https://www.ashecountyrealestate.com/uploads/blog/images/legacy/2016-08-16-murals.jpg",
        "image_alt": "West Jefferson NC downtown murals — Ashe County's artsy mountain community",
    },
    {
        "title":   "Beech Mountain STR Investment: What the Ski Season Math Actually Looks Like",
        "slug":    "2026-02-23-beech-mountain-str-investment-ski-season-math",
        "date":    "February 23, 2026",
        "excerpt": "At 5,506 feet, Beech Mountain is the highest town east of the Mississippi — and one of the High Country's most interesting short-term rental investment markets. Here's an honest look at the numbers.",
        "image":   "https://www.visitboone.com/wp-content/uploads/listing-uploads/gallery/2023/02/beech-mountain-resort.jpg",
        "image_alt": "Beech Mountain Resort ski slopes in winter — the highest ski area in eastern North America",
    },
    {
        "title":   "High Country Weekend: What's Happening in Boone & the Mountains — March 7–9, 2026",
        "slug":    "2026-03-06-high-country-weekend-events-spring-march-2026",
        "date":    "March 6, 2026",
        "excerpt": "Ski season is winding down and spring is arriving in the mountains. Here's your weekly guide to what's happening across the NC High Country this weekend.",
        "image":   "https://assets.agentfire3.com/uploads/sites/1337/2024/04/Boone-NC-King-Street.jpg",
        "image_alt": "King Street in downtown Boone NC — the heart of High Country activity",
    },
]

# ── Topic rotation ─────────────────────────────────────────────────────────────
TOPIC_CATEGORIES = [
    "High Country real estate market update (Boone, Blowing Rock, Banner Elk, West Jefferson)",
    "Appalachian State University student housing and investment opportunities near App State",
    "Buying land or mountain property in the High Country of NC",
    "Seasonal living in the Blue Ridge Mountains \u2013 current season, weather, what\u2019s happening now",
    "Upcoming events or festivals in Boone/High Country NC and their real estate appeal",
    "Relocation guide: moving to Boone NC or the High Country",
    "Second home and vacation property investment in the High Country",
    "Why families, retirees, and remote workers are choosing the High Country",
    "New construction, mountain cabins, and unique property types in Watauga/Ashe/Avery counties",
    "Holiday season in the High Country and its effect on the real estate market",
]

def get_topic():
    dow  = date.today().weekday()
    # Friday (4) = always a weekend events/calendar post
    if dow == 4:
        return "Weekend events calendar: what\'s happening in Boone and the NC High Country this weekend — festivals, outdoor activities, farmers markets, local events, ski conditions if applicable, and why this weekend is a great time to visit or explore the area as a potential buyer"
    week = date.today().isocalendar()[1]
    return TOPIC_CATEGORIES[(week * 3 + (0 if dow == 0 else 1)) % len(TOPIC_CATEGORIES)]

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
  <link rel="stylesheet" href="/style.css">"""

def shared_header(active_page="blog"):
    pages = [
        ("index.html","Home"), ("about.html","About"), ("areas.html","Areas"),
        ("services.html","Services"), ("blog.html","Blog"), ("contact.html","Contact"),
    ]
    links = ""
    for href, label in pages:
        page_id = href.replace(".html","")
        aria    = ' aria-current="page"' if page_id == active_page else ""
        links  += f'      <a href="/{href}"{aria}>{label}</a>\n'

    return f"""<a class="skip-link" href="#main">Skip to content</a>

<header class="site-header" role="banner">
  <div class="header-inner">
    <a href="/index.html" class="site-logo" aria-label="Andrew Plyler \u2014 Home">
      {SITE_LOGO_SVG}
      <span class="logo-text">
        <span class="logo-name">Andrew Plyler</span>
        <span class="logo-tag">The High Country Realtor</span>
      </span>
    </a>
    <nav class="main-nav" aria-label="Primary">
{links}      <a href="tel:{AUTHOR_PHONE_RAW}" class="nav-cta">Book a Call</a>
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
      <a href="/index.html" class="site-logo" aria-label="Andrew Plyler \u2014 Home" style="text-decoration:none;">
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
      <p>Born in Boone and rooted in the NC High Country. Helping buyers and sellers navigate mountain real estate with local knowledge and honest advice.</p>
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
        <li><a href="/about.html">About Andrew</a></li>
        <li><a href="/areas.html">Areas Served</a></li>
        <li><a href="/services.html">Services</a></li>
        <li><a href="/blog.html">Blog</a></li>
        <li><a href="/contact.html">Contact</a></li>
      </ul>
    </div>
    <div>
      <h4 class="footer-heading">Communities</h4>
      <ul class="footer-links" role="list">
        <li><a href="/areas.html">Boone</a></li>
        <li><a href="/areas.html">Blowing Rock</a></li>
        <li><a href="/areas.html">Banner Elk</a></li>
        <li><a href="/areas.html">Valle Crucis</a></li>
        <li><a href="/areas.html">Beech Mountain</a></li>
        <li><a href="/areas.html">West Jefferson</a></li>
      </ul>
    </div>
    <div>
      <h4 class="footer-heading">Contact</h4>
      <ul class="footer-links" role="list">
        <li><a href="tel:+17706391233">(770) 639-1233</a></li>
        <li><a href="tel:+18282638711">(828) 263-8711</a></li>
        <li><a href="mailto:{AUTHOR_EMAIL}">{AUTHOR_EMAIL}</a></li>
        <li>1129-1 Main St.<br>Blowing Rock, NC 28605</li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <p>&copy; {date.today().year} Andrew Plyler, REALTOR&reg;/Broker. Blue Ridge Realty &amp; Investments. All rights reserved. Equal Housing Opportunity.</p>
  </div>
</footer>"""

SHARED_JS = """
// Dark/light mode toggle
(function() {
  const toggle = document.querySelector('.theme-toggle');
  const html   = document.documentElement;
  const saved  = localStorage.getItem('theme');
  if (saved) html.setAttribute('data-theme', saved);
  if (toggle) {
    toggle.addEventListener('click', function() {
      const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
    });
  }
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

# ── AI content generation ──────────────────────────────────────────────────────
def generate_post():
    today_str = date.today().strftime("%B %d, %Y")
    prompt = f"""You are writing a blog post for Andrew Plyler, REALTOR\u00ae at Blue Ridge Realty & Investments in Boone, NC.
Andrew is a native of Boone with 40+ years of local knowledge, an App State grad, specializing in High Country real estate.

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

OUTPUT: respond ONLY with a JSON object (no markdown fences):
{{
  "title": "SEO title (60 chars max)",
  "meta_description": "155-char meta description with primary keyword",
  "slug": "url-friendly-slug",
  "focus_keyword": "primary SEO keyword phrase",
  "secondary_keywords": ["kw1","kw2","kw3"],
  "excerpt": "2-sentence plain-text excerpt for blog index card",
  "image_url": "a relevant publicly accessible image URL from townofbannerelk.org, visitboone.com, or use: https://assets.agentfire3.com/uploads/sites/1337/2024/04/Boone-NC-King-Street.jpg",
  "image_alt": "descriptive alt text for the image",
  "body_html": "full post body using only h2/p/ul/li/strong/em tags"
}}"""

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg    = client.messages.create(
        model="claude-sonnet-4-20250514", max_tokens=2000,
        messages=[{"role":"user","content":prompt}]
    )
    raw = msg.content[0].text.strip()
    raw = re.sub(r'```json\s*','',raw)
    raw = re.sub(r'```\s*','',raw)
    raw = re.sub(r'\s*```$','',raw)
    return json.loads(raw)

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

    img_html = ""
    if post.get("image_url"):
        img_html = f"""  <div class="image-band" style="aspect-ratio:21/8;">
    <img src="{post['image_url']}" alt="{post.get('image_alt','')}" loading="eager" />
  </div>"""

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
{head}
  <script type="application/ld+json">
{schema}
  </script>
  <style>{POST_CSS}</style>
</head>
<body>

{shared_header("blog")}

<main id="main">

  <div class="post-hero">
    <div class="container-narrow">
      <p class="section-label">High Country Real Estate</p>
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
        <p>{AUTHOR_TITLE}<br>Born &amp; raised in Boone &middot; App State alum &middot; 40+ years High Country expertise</p>
        <div class="author-cta">
          <a href="/contact.html" class="btn btn-primary">Get in Touch</a>
          <a href="tel:{AUTHOR_PHONE_RAW}" class="btn btn-outline">{AUTHOR_PHONE}</a>
        </div>
      </div>
    </div>

    <a href="/blog.html" class="back-link">&larr; Back to all posts</a>
  </div>

  <section class="cta-banner">
    <h2>Ready to Find Your Mountain Home?</h2>
    <p>Whether you&rsquo;re buying, selling, or just exploring &mdash; let&rsquo;s talk. No pressure, just honest mountain real estate advice.</p>
    <a href="/contact.html" class="btn btn-accent">Let&rsquo;s Get Started</a>
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
        cards += f"""      <a href="/blog/{p['slug']}/" class="blog-card fade-in">
{img_html}        <div class="blog-card-body">
          <span class="blog-card-date">{p['date']}</span>
          <h2 class="blog-card-title">{p['title']}</h2>
          <p class="blog-card-excerpt">{p['excerpt']}</p>
          <span class="blog-card-link">Read more &rarr;</span>
        </div>
      </a>\n"""

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
      <div class="grid-3">
{cards}
      </div>
    </div>
  </section>

  <section class="cta-banner">
    <h2>Ready to Find Your Mountain Home?</h2>
    <p>Whether you&rsquo;re buying, selling, or just exploring &mdash; let&rsquo;s talk. No pressure, just honest mountain real estate advice.</p>
    <a href="/contact.html" class="btn btn-accent">Let&rsquo;s Get Started</a>
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
    post     = generate_post()
    today    = date.today()
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
        "excerpt":   post["excerpt"],
        "image":     post.get("image_url", "https://assets.agentfire3.com/uploads/sites/1337/2024/04/Boone-NC-King-Street.jpg"),
        "image_alt": post.get("image_alt", post["title"]),
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
