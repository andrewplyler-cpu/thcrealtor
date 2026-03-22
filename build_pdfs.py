#!/usr/bin/env python3
"""Build all 4 High Country guide PDFs with updated 2026 data and local photos."""

import base64, os
from weasyprint import HTML, CSS

ASSETS = "/home/claude/thcrealtor/assets"
OUT    = "/home/claude/thcrealtor"

def img_b64(path):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    ext = path.rsplit(".", 1)[-1].lower()
    mime = "image/jpeg" if ext in ("jpg","jpeg") else "image/png"
    return f"data:{mime};base64,{data}"

stadium  = img_b64(f"{ASSETS}/C146C586-E8F9-4C77-917C-CC177B732567_1_105_c.jpeg")
mountain = img_b64(f"{ASSETS}/andrew-plyler-mountain.jpg")
headshot = img_b64(f"{ASSETS}/andrew-plyler-headshot.jpg")

BASE_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;0,700;1,400&family=Poppins:wght@300;400;500;600&display=swap');
* { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bark: #3B2F2F; --moss: #4A5240; --orange: #C0622A;
  --teal: #3D7A78; --cream: #F5F0E8; --mid: #8C7B6B;
}
body { font-family: 'Poppins', sans-serif; background: var(--cream); color: var(--bark); font-size: 10pt; }
.page { page-break-after: always; padding: 0; }
.page:last-child { page-break-after: auto; }

/* COVER */
.cover {
  background: linear-gradient(160deg, var(--bark) 0%, #2C2020 55%, var(--moss) 100%);
  min-height: 100vh; padding: 3rem 2.5rem 2rem;
  display: flex; flex-direction: column; justify-content: flex-end;
  position: relative; overflow: hidden;
}
.cover-photo {
  position: absolute; inset: 0;
  background-size: cover; background-position: center;
  opacity: 0.28;
}
.cover-logo { font-size: 0.65rem; font-weight: 600; letter-spacing: 0.2em; color: var(--orange); text-transform: uppercase; position: relative; margin-bottom: 0.4rem; }
.cover-tag { font-size: 0.62rem; font-weight: 500; letter-spacing: 0.15em; color: rgba(255,255,255,0.55); text-transform: uppercase; position: relative; margin-bottom: 0.75rem; }
.cover h1 { font-family: 'Lora', serif; font-size: 2.4rem; color: white; line-height: 1.2; position: relative; margin-bottom: 0.75rem; }
.cover-sub { font-size: 0.85rem; color: rgba(255,255,255,0.65); font-weight: 300; position: relative; max-width: 480px; line-height: 1.6; margin-bottom: 2rem; }
.cover-contact { position: relative; border-top: 1px solid rgba(255,255,255,0.15); padding-top: 1.2rem; }
.cover-contact p { font-size: 0.72rem; color: rgba(255,255,255,0.6); line-height: 1.7; font-weight: 300; }
.cover-contact strong { color: rgba(255,255,255,0.9); font-weight: 600; }

/* INNER PAGE */
.inner { padding: 2.5rem 2.5rem 2rem; min-height: 100vh; }
.inner-header { border-bottom: 2px solid var(--cream); padding-bottom: 0.6rem; margin-bottom: 1.5rem; display: flex; justify-content: space-between; align-items: center; }
.inner-header .brand { font-size: 0.6rem; font-weight: 600; letter-spacing: 0.15em; color: var(--orange); text-transform: uppercase; }
.inner-header .pg { font-size: 0.6rem; color: var(--mid); }

h2 { font-family: 'Lora', serif; font-size: 1.4rem; color: var(--bark); margin-bottom: 0.75rem; margin-top: 1.5rem; }
h2:first-child { margin-top: 0; }
h3 { font-family: 'Lora', serif; font-size: 1rem; color: var(--bark); margin: 1rem 0 0.4rem; }
p { line-height: 1.65; margin-bottom: 0.65rem; font-size: 0.88rem; color: #4A3A3A; }
ul { margin: 0.5rem 0 0.75rem 1.2rem; }
li { font-size: 0.88rem; line-height: 1.6; color: #4A3A3A; margin-bottom: 0.25rem; }
strong { color: var(--bark); }

.eyebrow { font-size: 0.6rem; font-weight: 600; letter-spacing: 0.18em; color: var(--orange); text-transform: uppercase; margin-bottom: 0.3rem; }

/* CALLOUT */
.callout { background: white; border-left: 3px solid var(--teal); padding: 1rem 1.2rem; margin: 1.2rem 0; border-radius: 0 4px 4px 0; }
.callout p { margin: 0; font-size: 0.85rem; color: var(--bark); font-style: italic; }

/* STATS ROW */
.stats { display: flex; gap: 1rem; margin: 1.2rem 0; }
.stat { flex: 1; background: white; border: 1px solid #E8E0D5; border-radius: 5px; padding: 0.85rem 1rem; text-align: center; }
.stat-num { font-family: 'Lora', serif; font-size: 1.3rem; color: var(--orange); font-weight: 700; }
.stat-label { font-size: 0.65rem; color: var(--mid); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.2rem; }

/* TABLE */
table { width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.82rem; }
th { background: var(--bark); color: white; padding: 0.5rem 0.75rem; text-align: left; font-weight: 500; font-size: 0.75rem; }
td { padding: 0.5rem 0.75rem; border-bottom: 1px solid #E8E0D5; }
tr:nth-child(even) td { background: #FAF6EF; }

/* PHOTO */
.photo-block { margin: 1.2rem 0; border-radius: 5px; overflow: hidden; }
.photo-block img { width: 100%; display: block; }
.photo-caption { font-size: 0.65rem; color: var(--mid); padding: 0.4rem 0.5rem; background: white; border: 1px solid #E8E0D5; border-top: none; }

/* AGENT CARD */
.agent-card { background: var(--bark); color: white; padding: 1.5rem; border-radius: 5px; margin-top: 1.5rem; display: flex; gap: 1.2rem; align-items: center; }
.agent-photo { width: 72px; height: 72px; border-radius: 50%; overflow: hidden; flex-shrink: 0; border: 2px solid var(--orange); }
.agent-photo img { width: 100%; height: 100%; object-fit: cover; }
.agent-info p { color: rgba(255,255,255,0.75); font-size: 0.78rem; margin: 0; line-height: 1.6; }
.agent-info strong { color: white; font-size: 0.9rem; }
.agent-name { font-family: 'Lora', serif; font-size: 1rem; color: white; margin-bottom: 0.3rem; }

.footer-strip { background: var(--bark); color: rgba(255,255,255,0.55); font-size: 0.6rem; padding: 0.5rem 2.5rem; text-align: center; margin-top: 2rem; }

/* Accent colors */
.accent-teal { color: var(--teal); }
.accent-orange { color: var(--orange); }
.accent-moss { color: var(--moss); }
"""

# ─────────────────────────────────────────────
# GUIDE 1: STUDENT HOUSING PLAYBOOK
# ─────────────────────────────────────────────
html_student = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"/>
<style>{BASE_CSS}</style></head><body>

<!-- COVER -->
<div class="page cover">
  <div class="cover-photo" style="background-image:url('{stadium}')"></div>
  <div class="cover-logo">plyler.realtor</div>
  <div class="cover-tag">A Complete Guide for Students &amp; Parents</div>
  <h1>Boone Student<br/>Housing Playbook</h1>
  <p class="cover-sub">Everything App State families need to rent smart, live well, and invest wisely in the High Country.</p>
  <div class="cover-contact">
    <p><strong>Andrew Plyler, REALTOR®/Broker</strong><br/>
    770.639.1233 · aplyler@brri.net · plyler.realtor<br/>
    Blue Ridge Realty &amp; Investments · Boone, NC 28607</p>
  </div>
</div>

<!-- PAGE 2 -->
<div class="page inner">
  <div class="inner-header"><span class="brand">plyler.realtor · Student Housing Playbook</span><span class="pg">Page 2</span></div>
  <h2>Welcome to the High Country</h2>
  <p>Finding the right place to live near App State is one of the most important — and stressful — decisions a student or parent can make. Boone's rental market moves fast, inventory is tight, and demand from 21,000+ students keeps pressure on every available unit.</p>
  <p>This playbook gives you a clear, step-by-step framework to find, evaluate, and secure the right housing — whether you're a first-year student, a junior looking for more independence, or a parent considering buying investment property near campus.</p>

  <div class="stats">
    <div class="stat"><div class="stat-num">21,000+</div><div class="stat-label">Enrolled Students</div></div>
    <div class="stat"><div class="stat-num">$1,000–$1,400</div><div class="stat-label">Avg. Rent Per Room/Mo</div></div>
    <div class="stat"><div class="stat-num">13 Free</div><div class="stat-label">AppalCART Routes</div></div>
    <div class="stat"><div class="stat-num">Yes</div><div class="stat-label">Walk-to-Campus Options</div></div>
  </div>

  <h2>Chapter 1: Understanding the Boone Rental Market</h2>
  <h3>The App State Effect</h3>
  <p>With over 21,000 students enrolled, Appalachian State University drives nearly every aspect of Boone's housing market. Demand consistently outpaces supply, which means students who wait until spring to look for fall housing are already late. The best properties — close to campus, in safe neighborhoods, on a bus route — sign leases in January and February for the following August.</p>

  <h3>2026 Rental Market: What You'll Pay Per Room</h3>
  <p>Boone rents have risen steadily. As of early 2026, <strong>per-bedroom rents near App State range from $1,000 to $1,400/month</strong>, depending on proximity to campus, amenities, and property condition. Budget accordingly:</p>

  <table>
    <tr><th>Property Type</th><th>Typical Rent/Bedroom</th><th>Notes</th></tr>
    <tr><td>3–5 BR house near campus</td><td>$1,050–$1,255/mo per BR</td><td>Highest demand; sign early</td></tr>
    <tr><td>1 BR apartment (solo)</td><td>$1,050–$1,819/mo</td><td>Limited supply near campus</td></tr>
    <tr><td>2 BR shared (per person)</td><td>$900–$1,100/mo per BR</td><td>Good value with right roommate</td></tr>
    <tr><td>Luxury student community</td><td>$1,200–$1,400/mo per BR</td><td>e.g., The Standard at Boone</td></tr>
    <tr><td>On AppalCART route (off-campus)</td><td>$1,000–$1,200/mo per BR</td><td>More options, strong value</td></tr>
  </table>

  <div class="callout"><p>Pro Tip: Set up alerts on Zillow, Apartments.com, and Facebook Marketplace using Boone, NC as your search area. Properties within a half-mile of campus rent within days of listing.</p></div>

  <h3>When to Start Your Search</h3>
  <ul>
    <li><strong>October–November:</strong> Landlords begin advertising for next year. Good time to assess neighborhoods.</li>
    <li><strong>December–January:</strong> Peak signing season. Best units are claimed quickly.</li>
    <li><strong>February–March:</strong> Secondary inventory appears as some deals fall through.</li>
    <li><strong>April–May:</strong> Slim pickings — mainly sublets and last-minute listings.</li>
  </ul>
</div>

<!-- PAGE 3 -->
<div class="page inner">
  <div class="inner-header"><span class="brand">plyler.realtor · Student Housing Playbook</span><span class="pg">Page 3</span></div>

  <div class="photo-block">
    <img src="{stadium}" alt="Kidd Brewer Stadium aerial, Boone NC"/>
    <div class="photo-caption">Kidd Brewer Stadium and Appalachian State University campus — surrounded by the Blue Ridge Mountains.</div>
  </div>

  <h2>Chapter 2: Neighborhoods &amp; Locations</h2>
  <p>Boone is a compact mountain town, but location matters enormously — especially in winter when snow and ice make driving steep mountain roads challenging.</p>

  <h3>Near-Campus Options (Walking Distance)</h3>
  <ul>
    <li><strong>Rivers Street / Stadium Drive:</strong> Dense student corridor, high walkability, mix of older homes and newer apartments.</li>
    <li><strong>Faculty Street / Deerfield:</strong> Quieter residential streets, 10–20 min walk to most buildings.</li>
    <li><strong>Downtown Boone (King Street area):</strong> Vibrant, walkable, access to restaurants and shops — slightly pricier at $1,300–$1,800/mo for a 1BR.</li>
  </ul>

  <h3>Bus-Route Communities (AppalCART)</h3>
  <p>AppalCART operates 13 fare-free routes serving the App State campus and surrounding Boone community. Living on a bus route opens up more affordable options further from campus without sacrificing accessibility.</p>
  <ul>
    <li>All routes are fare-free — no cost to ride any time.</li>
    <li>Routes serve Walmart, Watauga Medical Center, and major shopping corridors.</li>
    <li>Check appstate.edu/transportation for current route maps and schedules.</li>
  </ul>

  <h2>Chapter 3: What to Look for in a Lease</h2>
  <p>North Carolina landlord-tenant law provides strong protections — but only if you read your lease carefully before signing.</p>

  <table>
    <tr><th>Lease Item</th><th>What to Know</th></tr>
    <tr><td>Lease Term</td><td>Most Boone student leases run August 1 – July 31. Match to your academic plans.</td></tr>
    <tr><td>Security Deposit</td><td>NC law caps at 2 months' rent. Get itemized move-in documentation.</td></tr>
    <tr><td>Subletting Policy</td><td>Study abroad or co-op? Many leases prohibit subletting.</td></tr>
    <tr><td>Pet Policy</td><td>Clearly stated pet fees and restrictions. Unauthorized pets can cost your deposit.</td></tr>
    <tr><td>Utilities Included</td><td>Know exactly what's included — internet, water, trash, electric, gas.</td></tr>
    <tr><td>Snow/Ice Responsibility</td><td>Some leases require tenants to clear walks. In Boone winters, this matters.</td></tr>
    <tr><td>Early Termination</td><td>Know the exit clause and any buyout costs.</td></tr>
  </table>

  <div class="callout"><p>Always photograph every room, every wall, and every appliance on move-in day and email photos to your landlord within 24 hours. This single step prevents most security deposit disputes.</p></div>
</div>

<!-- PAGE 4 -->
<div class="page inner">
  <div class="inner-header"><span class="brand">plyler.realtor · Student Housing Playbook</span><span class="pg">Page 4</span></div>

  <h2>Chapter 4: Budgeting for Off-Campus Life</h2>
  <p>Off-campus living often costs more than students initially plan. Use this budget framework as a starting point — actual costs will vary.</p>

  <div class="stats">
    <div class="stat"><div class="stat-num">$1,000–$1,400</div><div class="stat-label">Rent (per BR, 2026)</div></div>
    <div class="stat"><div class="stat-num">$100–$180</div><div class="stat-label">Utilities/mo</div></div>
    <div class="stat"><div class="stat-num">$200–$300</div><div class="stat-label">Groceries/mo</div></div>
    <div class="stat"><div class="stat-num">$0</div><div class="stat-label">AppalCART Bus</div></div>
  </div>

  <h3>Cost-Saving Strategies</h3>
  <ul>
    <li>Split a 3–4 BR house with roommates — per-person cost drops significantly even at today's rates.</li>
    <li>Use AppalCART free bus routes — eliminate car expenses entirely.</li>
    <li>Buy groceries at the Boone Walmart or Food Lion rather than convenience stores.</li>
    <li>Look for utilities-included rentals, especially if usage is unpredictable.</li>
  </ul>

  <h2>Chapter 5: For Parents — Should You Buy Instead of Rent?</h2>
  <p>Many App State parents run the numbers and realize that buying a condo or small house near campus can cost less per month than renting — while building equity and creating a potential income property after graduation. With per-bedroom rents now exceeding $1,000/month, the math has never been more compelling.</p>

  <h3>The Case for Buying</h3>
  <ul>
    <li>Your child's rent payments build YOUR equity instead of a landlord's.</li>
    <li>Roommate rent at $1,000–$1,200/bedroom can offset most or all of your mortgage payment.</li>
    <li>Boone property values have appreciated consistently due to constrained supply.</li>
    <li>Post-graduation, the property becomes a long-term rental or vacation asset.</li>
  </ul>

  <h3>What to Consider</h3>
  <ul>
    <li>Buy-and-hold works best for a 4+ year horizon — account for closing costs.</li>
    <li>HOA rules matter — check short-term rental restrictions before buying.</li>
    <li>Work with a local agent who knows the student rental market intimately.</li>
  </ul>

  <div class="callout"><p>I've helped dozens of App State families buy near campus. Call me to run the rent-vs-buy numbers for your specific situation — it's often a clearer decision than families expect.</p></div>

  <div class="agent-card">
    <div class="agent-photo"><img src="{mountain}" alt="Andrew Plyler"/></div>
    <div class="agent-info">
      <div class="agent-name">Andrew Plyler</div>
      <p>REALTOR®/Broker · Blue Ridge Realty &amp; Investments<br/>
      Born &amp; raised in Boone · 40+ years High Country experience<br/>
      App State connected · Community-first approach<br/>
      <strong>770.639.1233 · aplyler@brri.net · plyler.realtor</strong></p>
    </div>
  </div>
</div>

<div class="footer-strip">Andrew Plyler, REALTOR®/Broker · Blue Ridge Realty &amp; Investments · Boone, NC 28607 · 770.639.1233 · aplyler@brri.net · plyler.realtor · © 2026</div>
</body></html>"""

# ─────────────────────────────────────────────
# GUIDE 2: INVESTMENT PROPERTY GUIDE
# ─────────────────────────────────────────────
html_investment = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"/>
<style>{BASE_CSS}</style></head><body>

<div class="page cover">
  <div class="cover-photo" style="background-image:url('{mountain}')"></div>
  <div class="cover-logo">plyler.realtor</div>
  <div class="cover-tag">Boone · Banner Elk · Blowing Rock · Valle Crucis</div>
  <h1>High Country<br/>Investment Property<br/>Guide</h1>
  <p class="cover-sub">A local investor's framework for buying, renting, and building wealth in the NC mountains.</p>
  <div class="cover-contact">
    <p><strong>Andrew Plyler, REALTOR®/Broker</strong><br/>
    770.639.1233 · aplyler@brri.net · plyler.realtor<br/>
    Blue Ridge Realty &amp; Investments · Boone, NC 28607</p>
  </div>
</div>

<div class="page inner">
  <div class="inner-header"><span class="brand">plyler.realtor · Investment Property Guide</span><span class="pg">Page 2</span></div>
  <h2>Why Invest in the High Country?</h2>
  <p>The North Carolina High Country offers a rare combination of strong rental demand, constrained land supply, four-season appeal, and sustained long-term appreciation. Whether your goal is steady rental income, short-term vacation rentals, or long-term equity growth, this market rewards patient, locally-informed investors.</p>

  <div class="stats">
    <div class="stat"><div class="stat-num">21,000+</div><div class="stat-label">App State Students</div></div>
    <div class="stat"><div class="stat-num">3 Nearby</div><div class="stat-label">Ski Resorts</div></div>
    <div class="stat"><div class="stat-num">$1,000–$1,400</div><div class="stat-label">Per BR/Mo (2026)</div></div>
    <div class="stat"><div class="stat-num">3,300+ ft</div><div class="stat-label">Elevation</div></div>
  </div>

  <h2>Three Investment Profiles</h2>

  <h3>Profile 1: Student Rental Near App State</h3>
  <p>Boone's university market creates predictable, year-round demand. Houses and condos within walking distance or on AppalCART bus routes command premium rents and low vacancy rates. With per-bedroom rents now ranging <strong>$1,000–$1,400/month in 2026</strong>, multi-bedroom properties rented by the room offer compelling per-square-foot returns.</p>
  <ul>
    <li>Best property types: 3–5 BR houses, townhomes, condos near campus</li>
    <li>Average gross rent yield: 7–10% depending on proximity and condition</li>
    <li>A 4BR house at $1,100/BR generates $4,400/month gross revenue</li>
    <li>Leases typically run August–July aligned with academic calendar</li>
    <li>Relatively low maintenance compared to vacation rentals</li>
  </ul>

  <h3>Profile 2: Short-Term Vacation Rental (STR)</h3>
  <p>The High Country draws visitors year-round: skiers in winter, leaf-peepers in fall, hikers in summer, and families escaping heat in spring. Properties near ski areas or with mountain views command strong nightly rates on Airbnb and VRBO.</p>
  <ul>
    <li>Peak seasons: October (fall color), December–March (ski season), June–August (summer escape)</li>
    <li>Verify STR regulations before buying — rules vary by municipality and HOA</li>
    <li>Professional management typically runs 20–30% of gross revenue</li>
    <li>Furnished properties require higher upfront investment but command better rates</li>
  </ul>

  <h3>Profile 3: Long-Term Appreciation Play</h3>
  <p>Land and property in the High Country face natural supply constraints: mountains don't allow unlimited development. Buyers seeking long-term appreciation often focus on acreage, view lots, and properties in communities with strict building covenants that preserve value.</p>
  <ul>
    <li>Blowing Rock and Banner Elk corridors historically show strongest appreciation</li>
    <li>Creekfront and ridgeline properties carry premiums that compound over time</li>
    <li>Limited developable land creates structural floor under prices</li>
  </ul>
</div>

<div class="page inner">
  <div class="inner-header"><span class="brand">plyler.realtor · Investment Property Guide</span><span class="pg">Page 3</span></div>

  <div class="photo-block">
    <img src="{stadium}" alt="App State campus aerial view"/>
    <div class="photo-caption">Appalachian State University — the engine of Boone's rental market — surrounded by Blue Ridge fall color.</div>
  </div>

  <h2>Due Diligence: What to Check Before You Buy</h2>
  <table>
    <tr><th>Item</th><th>Why It Matters</th></tr>
    <tr><td>Zoning</td><td>Confirm residential, STR, and rental permissions with Town of Boone or Watauga County planning.</td></tr>
    <tr><td>Septic/Well</td><td>Many mountain properties are on private well and septic — inspect both carefully.</td></tr>
    <tr><td>HOA Rules</td><td>Some communities prohibit short-term rentals or limit rental terms. Read covenants thoroughly.</td></tr>
    <tr><td>Flood/Slope</td><td>Check FEMA flood maps and slope stability, especially for creek-adjacent or steep-lot properties.</td></tr>
    <tr><td>Seasonal Access</td><td>Verify year-round road access. Some private roads become impassable in winter.</td></tr>
    <tr><td>Insurance</td><td>Mountain properties may require separate wind/hail riders. Budget accordingly.</td></tr>
    <tr><td>Cap Rate</td><td>Calculate net operating income ÷ purchase price. Target 6%+ for residential rental.</td></tr>
  </table>

  <div class="callout"><p>The most common mistake I see High Country investors make is buying based on vacation experience rather than investment fundamentals. I help clients separate emotional appeal from sound numbers.</p></div>

  <h2>Financing High Country Investment Properties</h2>
  <ul>
    <li><strong>Conventional investment loans:</strong> Typically require 20–25% down; rates 0.5–1% above primary home rates.</li>
    <li><strong>Vacation home loans:</strong> If you occupy 14+ days/year, you may qualify for second-home financing (better terms).</li>
    <li><strong>DSCR loans:</strong> Debt Service Coverage Ratio loans qualify based on rental income — ideal for STR investors.</li>
    <li><strong>Local lenders:</strong> Community banks in Boone often have more flexibility on mountain properties than national lenders.</li>
    <li><strong>1031 Exchange:</strong> Selling another investment property? Defer capital gains by exchanging into High Country real estate.</li>
  </ul>

  <div class="agent-card">
    <div class="agent-photo"><img src="{mountain}" alt="Andrew Plyler"/></div>
    <div class="agent-info">
      <div class="agent-name">Andrew Plyler</div>
      <p>REALTOR®/Broker · Blue Ridge Realty &amp; Investments<br/>
      Born &amp; raised in Boone · 40+ years High Country experience<br/>
      <strong>770.639.1233 · aplyler@brri.net · plyler.realtor</strong></p>
    </div>
  </div>
</div>

<div class="footer-strip">Andrew Plyler, REALTOR®/Broker · Blue Ridge Realty &amp; Investments · Boone, NC · For informational purposes only. Not legal or financial advice. © 2026</div>
</body></html>"""

# ─────────────────────────────────────────────
# GUIDE 3: BUYING LAND
# ─────────────────────────────────────────────
html_land = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"/>
<style>{BASE_CSS}</style></head><body>

<div class="page cover">
  <div class="cover-photo" style="background-image:url('{mountain}')"></div>
  <div class="cover-logo">plyler.realtor</div>
  <div class="cover-tag">Lots · Acreage · Mountain Retreats · Building Sites</div>
  <h1>Buying Land in<br/>the High Country</h1>
  <p class="cover-sub">Your complete guide to finding, evaluating, and purchasing mountain land in western NC.</p>
  <div class="cover-contact">
    <p><strong>Andrew Plyler, REALTOR®/Broker</strong><br/>
    770.639.1233 · aplyler@brri.net · plyler.realtor<br/>
    Blue Ridge Realty &amp; Investments · Boone, NC 28607</p>
  </div>
</div>

<div class="page inner">
  <div class="inner-header"><span class="brand">plyler.realtor · Buying Land in the High Country</span><span class="pg">Page 2</span></div>
  <h2>Why Land in the High Country?</h2>
  <p>There is something irreplaceable about owning a piece of the North Carolina mountains. Whether you're dreaming of building your forever home on a ridgeline, securing a family retreat near Boone, or holding raw acreage as a long-term investment, High Country land offers natural beauty, constrained supply, and enduring value that few markets can match.</p>

  <div class="stats">
    <div class="stat"><div class="stat-num">3,000–5,500 ft</div><div class="stat-label">Avg. Elevation</div></div>
    <div class="stat"><div class="stat-num">Constrained</div><div class="stat-label">Land Supply</div></div>
    <div class="stat"><div class="stat-num">Critical</div><div class="stat-label">4-Season Access</div></div>
    <div class="stat"><div class="stat-num">Custom &amp; Modular</div><div class="stat-label">Build Options</div></div>
  </div>

  <h2>Types of Land Available</h2>

  <h3>Raw/Undeveloped Acreage</h3>
  <p>Large tracts with no improvements — no utilities, no road, no clearing. Typically the most affordable per-acre price, but requiring the most due diligence. Best for buyers with a long time horizon or those seeking privacy and seclusion.</p>

  <h3>Platted Subdivision Lots</h3>
  <p>Lots within a planned community — usually with roads, sometimes with utilities stubbed in. Many mountain subdivisions have architectural covenants governing structure size, appearance, and permitted uses. Easier to finance and build on, but less flexibility.</p>

  <h3>Cleared/Ready-to-Build Sites</h3>
  <p>Lots that have been cleared, perc-tested (for septic), and sometimes permitted. These command a premium but significantly reduce the time and risk between purchase and breaking ground.</p>

  <h2>Critical Due Diligence: Mountains Are Different</h2>
  <p>Mountain land due diligence is substantially more complex than buying a residential lot in a flat suburban market. These are the non-negotiable items every buyer must investigate:</p>

  <table>
    <tr><th>Item</th><th>Why It Matters</th></tr>
    <tr><td>Perc Test</td><td>Required for septic approval. The most common deal-killer in mountain land. Test before you close.</td></tr>
    <tr><td>Well Feasibility</td><td>If no public water, a well study or neighbor data tells you what depth (and cost) to expect.</td></tr>
    <tr><td>Road/Access</td><td>Is access via public road, easement, or private road? Get access rights in writing — always.</td></tr>
    <tr><td>Slope &amp; Buildability</td><td>Steep slopes over 30% limit building sites and increase foundation costs dramatically.</td></tr>
    <tr><td>Flood Zone</td><td>FEMA maps cover creek bottoms. Mountain creeks flood. Check FIRM maps for the parcel.</td></tr>
    <tr><td>Utilities</td><td>Electric, internet, gas — what's available at the road? Running power uphill gets expensive.</td></tr>
    <tr><td>Zoning</td><td>Watauga County and municipal zoning dictates what you can build and how. Verify permitted uses.</td></tr>
    <tr><td>Timber/Mineral Rights</td><td>Some parcels have severed timber or mineral rights. Confirm what you're actually buying.</td></tr>
    <tr><td>Covenants/Restrictions</td><td>Subdivision docs may restrict structure size, materials, rental use, or livestock.</td></tr>
  </table>

  <div class="callout"><p>I've seen buyers fall in love with a mountain view and skip the perc test. Don't. A beautiful 10-acre parcel without buildable land or septic approval is a very expensive problem.</p></div>
</div>

<div class="page inner">
  <div class="inner-header"><span class="brand">plyler.realtor · Buying Land in the High Country</span><span class="pg">Page 3</span></div>

  <div class="photo-block">
    <img src="{stadium}" alt="High Country aerial view"/>
    <div class="photo-caption">The Blue Ridge Mountains from above — constrained topography means every buildable parcel holds enduring value.</div>
  </div>

  <h2>The Buying Process: Step by Step</h2>
  <ul>
    <li><strong>Step 1 — Define your goal:</strong> Primary home site, vacation retreat, investment hold, or farming? Goal shapes your search criteria.</li>
    <li><strong>Step 2 — Set your budget including development costs:</strong> Land price is just the start. Add road, well, septic, clearing, and utilities.</li>
    <li><strong>Step 3 — Find a local agent:</strong> Mountain land requires local expertise. Roads, easements, and access issues require someone who knows the territory.</li>
    <li><strong>Step 4 — Conduct layered due diligence:</strong> Survey, perc test, soil study, flood check, covenant review — in that order.</li>
    <li><strong>Step 5 — Negotiate with contingencies:</strong> Perc test and survey contingencies are standard in NC land contracts and protect you.</li>
    <li><strong>Step 6 — Close and plan:</strong> After closing, work with Watauga County planning on permits, setbacks, and your build timeline.</li>
  </ul>

  <h2>Financing Land: What to Know</h2>
  <ul>
    <li><strong>Raw land loans:</strong> Typically 30–50% down, 10–15 year terms, higher rates. Fewer lenders offer them.</li>
    <li><strong>Improved land/lot loans:</strong> Better terms with utilities and road access — some lenders treat these like construction loans.</li>
    <li><strong>Construction-to-permanent loans:</strong> If you plan to build soon, a single close C-to-P loan covers land + construction.</li>
    <li><strong>Cash buyers:</strong> Common in the High Country land market — cash offers on land are competitive and close faster.</li>
    <li><strong>Seller financing:</strong> Some landowners in western NC will carry a note, especially on larger or more remote parcels.</li>
  </ul>

  <div class="agent-card">
    <div class="agent-photo"><img src="{mountain}" alt="Andrew Plyler"/></div>
    <div class="agent-info">
      <div class="agent-name">Andrew Plyler</div>
      <p>REALTOR®/Broker · Blue Ridge Realty &amp; Investments<br/>
      Born &amp; raised in Boone · 40+ years of local land knowledge<br/>
      I know which roads wash out, which hollows flood, and which views are worth every penny.<br/>
      <strong>770.639.1233 · aplyler@brri.net · plyler.realtor</strong></p>
    </div>
  </div>
</div>

<div class="footer-strip">Andrew Plyler, REALTOR®/Broker · Blue Ridge Realty &amp; Investments · Boone, NC · Always consult licensed surveyors, engineers, and legal professionals before purchasing land. © 2026</div>
</body></html>"""

# ─────────────────────────────────────────────
# GUIDE 4: WELCOME TO THE HIGH COUNTRY
# ─────────────────────────────────────────────
html_relocation = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"/>
<style>{BASE_CSS}</style></head><body>

<div class="page cover">
  <div class="cover-photo" style="background-image:url('{stadium}')"></div>
  <div class="cover-logo">plyler.realtor</div>
  <div class="cover-tag">Boone · Blowing Rock · Banner Elk · Valle Crucis · West Jefferson</div>
  <h1>Welcome to the<br/>High Country</h1>
  <p class="cover-sub">Your guide to relocating, retiring, or buying a second home in the NC mountains.</p>
  <div class="cover-contact">
    <p><strong>Andrew Plyler, REALTOR®/Broker</strong><br/>
    770.639.1233 · aplyler@brri.net · plyler.realtor<br/>
    Blue Ridge Realty &amp; Investments · Boone, NC 28607</p>
  </div>
</div>

<div class="page inner">
  <div class="inner-header"><span class="brand">plyler.realtor · Welcome to the High Country</span><span class="pg">Page 2</span></div>
  <h2>A Place Like No Other</h2>
  <p>The North Carolina High Country sits at the top of the southern Appalachians — a region of cool summers, brilliant falls, snowy winters, and wildflower springs. It is one of the few places in the Southeast where you can trade the heat and congestion of the piedmont or coast for mountain air, a genuine downtown, world-class outdoor recreation, and a community that has maintained its character through decades of growth.</p>

  <div class="stats">
    <div class="stat"><div class="stat-num">~75°F avg</div><div class="stat-label">Summer High</div></div>
    <div class="stat"><div class="stat-num">3,300 ft</div><div class="stat-label">Boone Elevation</div></div>
    <div class="stat"><div class="stat-num">~2 hrs</div><div class="stat-label">To Charlotte</div></div>
    <div class="stat"><div class="stat-num">~1.5 hrs</div><div class="stat-label">To Asheville</div></div>
  </div>

  <h2>The Communities of the High Country</h2>

  <h3>Boone</h3>
  <p>The commercial and cultural hub of the High Country. Home to Appalachian State University, a vibrant King Street downtown with independent restaurants and shops, Watauga Medical Center, and easy access to all mountain corridors. Year-round population ~20,000 with a college-town energy. Median home prices have risen to <strong>$350K–$600K+</strong> for quality single-family homes as of 2025–2026.</p>

  <h3>Blowing Rock</h3>
  <p>A refined mountain village with a historic Main Street, upscale dining, art galleries, and the Blowing Rock attraction. Known for its luxury second-home market and well-preserved small-town character. One of the most desirable addresses in the High Country. Properties range from $500K to $2M+.</p>

  <h3>Banner Elk &amp; Beech Mountain</h3>
  <p>Ski country. Banner Elk anchors the Sugar Mountain and Beech Mountain ski resort corridor, making it a four-season recreation destination. Strong vacation rental market. Beech Mountain (5,506 ft elevation) is the highest incorporated town east of the Rockies.</p>

  <h3>Valle Crucis &amp; West Jefferson</h3>
  <p>Agricultural and artisan communities in the Watauga and New River valleys. Slower pace, larger properties, and lower price points. Famous for the Mast General Store (Valle Crucis) and a thriving arts scene (West Jefferson).</p>

  <h2>The Four-Season Lifestyle</h2>
  <table>
    <tr><th>Season</th><th>What to Expect</th></tr>
    <tr><td>Spring</td><td>Wildflowers, trout fishing, waterfall hikes. Rhododendron blooms in June. Real estate season begins.</td></tr>
    <tr><td>Summer</td><td>Cool 70s when the piedmont swelters. Hiking, cycling, outdoor music. Peak relocation inquiry season.</td></tr>
    <tr><td>Fall</td><td>World-class color. Blue Ridge Parkway drives. Apple festivals. The reason most people fall in love with the region.</td></tr>
    <tr><td>Winter</td><td>Snow and ski season. Cozy mountain towns. Lower market inventory — can be a buyer's advantage.</td></tr>
  </table>
</div>

<div class="page inner">
  <div class="inner-header"><span class="brand">plyler.realtor · Welcome to the High Country</span><span class="pg">Page 3</span></div>

  <div class="photo-block">
    <img src="{stadium}" alt="Boone NC aerial view"/>
    <div class="photo-caption">Boone, NC — nestled in the Blue Ridge Mountains. The only city of its size in America surrounded by this much natural beauty.</div>
  </div>

  <h2>Outdoor Recreation at Your Doorstep</h2>
  <ul>
    <li><strong>Blue Ridge Parkway:</strong> America's most visited national park unit — miles of it run through the High Country.</li>
    <li><strong>Hiking:</strong> Hundreds of trails in Pisgah, Jefferson, and Nantahala National Forests within an hour's drive.</li>
    <li><strong>Skiing:</strong> Beech Mountain, Sugar Mountain, and App Ski Mountain — three resorts within 30 minutes of Boone.</li>
    <li><strong>Trout fishing:</strong> The New River and Watauga River systems are designated blue-ribbon trout waters.</li>
    <li><strong>Mountain biking:</strong> Pisgah trails are internationally recognized; local trails accessible from Boone.</li>
  </ul>

  <h2>Buying a Home or Second Home Here</h2>
  <p>The High Country real estate market has tightened considerably since 2020, with remote work migration and second-home demand pushing prices upward. Inventory remains constrained by mountain geography.</p>

  <h3>2025–2026 Market Conditions</h3>
  <ul>
    <li>Median home prices in Boone: <strong>$350K–$600K+</strong> for quality single-family homes</li>
    <li>Blowing Rock and Banner Elk luxury properties: <strong>$500K to $2M+</strong></li>
    <li>Land and older fixer properties still offer value for buyers willing to invest in improvements</li>
    <li>Multiple offer situations are common on desirable properties at any price point</li>
  </ul>

  <h2>Practical Living Information</h2>
  <table>
    <tr><th>Category</th><th>Details</th></tr>
    <tr><td>Healthcare</td><td>Watauga Medical Center (Boone) — full-service hospital. Specialists in Boone or via telemedicine.</td></tr>
    <tr><td>Grocery &amp; Shopping</td><td>Walmart, Lowe's Foods, and a growing local food scene. Specialty goods via Asheville or online.</td></tr>
    <tr><td>Airport Access</td><td>Tri-Cities (TRI) ~1 hr; Charlotte (CLT) ~2 hrs; Asheville (AVL) ~1.5 hrs.</td></tr>
    <tr><td>Internet</td><td>Fiber and high-speed internet available in Boone proper; more variable in rural/mountain areas.</td></tr>
    <tr><td>Schools</td><td>Watauga County Schools; App State dual enrollment; several private options in the region.</td></tr>
    <tr><td>Climate Note</td><td>Boone averages ~30 inches of snow per year. 4WD or AWD vehicle highly recommended.</td></tr>
  </table>

  <div class="agent-card">
    <div class="agent-photo"><img src="{mountain}" alt="Andrew Plyler"/></div>
    <div class="agent-info">
      <div class="agent-name">Andrew Plyler</div>
      <p>REALTOR®/Broker · Blue Ridge Realty &amp; Investments<br/>
      Born in Boone, raised in this community, watching it grow and change for 40+ years.<br/>
      There's no substitute for that kind of local knowledge when you're making a major life decision.<br/>
      <strong>770.639.1233 · aplyler@brri.net · plyler.realtor</strong></p>
    </div>
  </div>
</div>

<div class="footer-strip">Andrew Plyler, REALTOR®/Broker · Blue Ridge Realty &amp; Investments · Boone, NC · Market data is approximate and subject to change. © 2026</div>
</body></html>"""

# ─────────────────────────────────────────────
# BUILD ALL 4 PDFs
# ─────────────────────────────────────────────
guides = [
    ("guide_student_housing.pdf", html_student),
    ("guide_investment.pdf",      html_investment),
    ("guide_land.pdf",            html_land),
    ("guide_relocation.pdf",      html_relocation),
]

for filename, html in guides:
    out_path = f"{OUT}/{filename}"
    print(f"Building {filename}...")
    HTML(string=html).write_pdf(
        out_path,
        stylesheets=[CSS(string="@page { size: letter; margin: 0; }")]
    )
    size = os.path.getsize(out_path)
    print(f"  ✓ {filename} — {size:,} bytes")

print("\nAll 4 PDFs built successfully.")
