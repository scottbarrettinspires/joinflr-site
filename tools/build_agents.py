#!/usr/bin/env python3
"""Builds a personal recruiting page for each active FLR agent in agents.json.

Pages are generated from the live index.html (the main joinflr.com page), so they
always match it. Run from the repo root:  python3 tools/build_agents.py
Output: agents/<slug>/index.html  (do not edit these by hand; they are rebuilt)
"""
import html, json, os, re, shutil, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SITE = "https://joinflr.com"
src = open("index.html", encoding="utf-8").read()
roster = json.load(open("agents.json", encoding="utf-8"))["agents"]
esc = lambda s: html.escape(s or "", quote=True)

def swap(h, old, new, count=1):
    if old not in h:
        sys.exit("Main page changed; anchor not found: " + old[:70])
    return h.replace(old, new, count)

def region(h, start, end_marker):
    a = h.index(start); b = h.index(end_marker, a) + len(end_marker)
    return a, b

def build(a):
    slug, name = a["slug"], a["name"]
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
        sys.exit("Bad slug: " + slug)
    first = name.split()[0]
    url = f"{SITE}/agents/{slug}/"
    h = src
    # ---- head ----
    h = re.sub(r"<title>.*?</title>", f"<title>{esc(name)} invites you to Florida Luxury Realty</title>", h, count=1, flags=re.S)
    h = re.sub(r'<meta name="description" content=".*?">', f'<meta name="description" content="{esc(name)} of Florida Luxury Realty invites you to learn about FLR: an AI Agent Partner, hands-on training, a custom back office and revenue share.">\n<meta name="robots" content="noindex,follow">', h, count=1)
    h = re.sub(r'<meta property="og:title" content=".*?">', f'<meta property="og:title" content="{esc(name)} invites you to Florida Luxury Realty">', h, count=1)
    h = h.replace('<meta property="og:url" content="https://joinflr.com/">', f'<meta property="og:url" content="{url}">')
    h = h.replace('<link rel="canonical" href="https://joinflr.com/">', f'<link rel="canonical" href="{url}">')
    h = h.replace('"url": "https://joinflr.com/"', f'"url": "{url}"')
    # ---- relative paths (page lives two folders deep) ----
    h = re.sub(r'(src|href)="(assets/|styles\.css|script\.js|new-agents/|future-agents/)', r'\1="../../\2', h)
    # ---- nav / audience band / footer ----
    h = re.sub(r'\s*<a class="menu-alt" href="[^"]*new-agents/">New licensees</a>', "", h, count=1)
    h = swap(h, '<a class="btn btn-teal btn-sm" href="#contact">Start a conversation</a>', '<a class="btn btn-teal btn-sm" href="#contact">Request information</a>')
    s, e = region(h, '<aside class="audience-band">', '</aside>'); h = h[:s] + h[e:]
    h = re.sub(r'\s*<a href="[^"]*new-agents/">New licensees</a>', "", h, count=1)
    h = re.sub(r'\s*<a href="[^"]*future-agents/">Studying for your license\?</a>', "", h, count=1)
    h = swap(h, '<a href="#contact">Start a conversation</a>\n    </div>\n  </div>\n  <div class="wrap legal">', '<a href="#contact">Request information</a>\n    </div>\n  </div>\n  <div class="wrap legal">')
    # ---- hero ----
    h = swap(h, 'For experienced agents &middot; Serving Florida since 1999', 'Serving Florida since 1999')
    h = swap(h, '<a class="btn btn-teal" href="#contact">Start a confidential conversation</a>\n      <a class="btn btn-ghost" href="#why">See what you get</a>',
             f'<a class="btn btn-teal" href="#contact">Request information</a>\n      <a class="btn btn-ghost" href="#intro">Meet {esc(first)}</a>')
    h = swap(h, '<li>Every conversation stays confidential</li>', f'<li>Introduced by {esc(name)}</li>')
    # ---- personal intro section (inserted right after hero) ----
    initials = "".join(w[0] for w in name.split()[:2]).upper()
    photo = a.get("photo") or ""
    if photo and os.path.exists(f"assets/agents/{photo}"):
        pic = f'<img class="ai-photo" src="../../assets/agents/{esc(photo)}" alt="{esc(name)}" width="500" height="500" loading="lazy">'
    else:
        pic = f'<span class="ai-photo ai-initials" aria-hidden="true">{esc(initials)}</span>'
    note = a.get("note") or ("It's when I choose to grow and partnered my business with Florida Luxury Realty that everything happened for me. "
                             "I want to share the same opportunity you could have for yourself. "
                             "I highly encourage you to take a few minutes for yourself to learn how Florida Luxury Realty would help your personal real estate business grow.")
    btns = ""
    if a.get("phone"):
        tel = re.sub(r"\D", "", a["phone"]); btns += f'<a class="btn btn-ghost" href="tel:+1{tel[-10:]}">Call {esc(first)}</a>'
    role = esc(a["role"]) if a.get("role") else ""
    role_html = f'<p class="ai-role">{role}</p>' if role else ""
    intro = f'''<section class="ai-sec" id="intro">
  <div class="wrap">
    <div class="ai-card reveal">
      {pic}
      <div class="ai-text">
        <h2 class="ai-name">{esc(name)}</h2>
        {role_html}
        <p>{esc(note)}</p>
        <p class="ai-help-h">Here is how FLR has helped my business flourish</p>
        <ul class="ai-help">
          <li><a class="aih aih-hynri" href="#hynri"><span class="aih-logo"><img src="../../assets/hynri-logo.png" alt="Hynri" width="731" height="215" loading="lazy"></span><b>My Own AI Agent Partner</b></a></li>
          <li><a class="aih aih-ls" href="#leadstream"><span class="aih-logo"><img src="../../assets/leadstream-logo.png" alt="LeadStream Systems" width="900" height="185" loading="lazy"></span><b>Generates and Nurtures Leads For Me</b></a></li>
          <li><a class="aih aih-sbi" href="#grow"><span class="aih-logo"><img src="../../assets/sbi-logo-light.png" alt="ScottBarrettInspires" width="900" height="266" loading="lazy"></span><b>Personal Coaching For Peak Success</b></a></li>
        </ul>
        {('<div class="ai-actions">' + btns + '</div>') if btns else ''}
      </div>
    </div>
  </div>
</section>

'''
    h = swap(h, '<section class="hero">', intro + '<section class="hero">')
    # move hero + "Production solves everything" band to sit just above the "Empowering agents" section
    hs = h.index('<section class="hero">')
    ws = h.index('<section class="section why-sec" id="why">')
    we = h.index('</section>', ws) + len('</section>')
    block = h[hs:we]
    h = h[:hs] + h[we:].lstrip("\n")
    ms = h.index('<section class="section mb-sec" id="service">')
    h = h[:ms] + block + "\n\n" + h[ms:]
    # ---- revenue share call to action (not a referral prompt for an outside agent) ----
    s, e = region(h, '<div class="rs-cta reveal">', 'Refer an agent</a>\n    </div>')
    h = h[:s] + f'''<div class="rs-cta reveal">
      <div>
        <h3>Ask about revenue share</h3>
        <p>Full terms are in the FLR agent policies and the Independent Contractor Agreement. Request information and we will walk you through them.</p>
      </div>
      <a class="btn btn-dark" href="#contact">Request information</a>
    </div>''' + h[e:]
    # ---- FAQ confidentiality answer: be upfront about the introduction record ----
    h = swap(h, '<p>Yes. We treat every inquiry as confidential, and Scott will reach out to you directly.</p>',
             f'<p>Yes. Scott will reach out to you directly. We note that {esc(name)} introduced you to FLR, and we do not share your information outside the brokerage.</p>')
    # ---- contact form ----
    h = swap(h, '<h2>Start a confidential conversation</h2>', '<h2>Request information</h2>')
    h = swap(h, '<form id="lead-form" class="form" novalidate>', f'<form id="lead-form" class="form" novalidate data-source="joinflr.com/agents/{slug}" data-subject="Information request from {esc(name)}\'s FLR page">\n      <input type="hidden" name="sponsor" value="{esc(name)}">\n      <input type="hidden" name="sponsor_slug" value="{slug}">')
    h = swap(h, '<div class="hp" aria-hidden="true">', f'<p class="muted ref-note">Your request goes to Scott Barrett, Managing Broker. We record that {esc(name)} introduced you to FLR.</p>\n      <div class="hp" aria-hidden="true">')
    h = swap(h, '<button class="btn btn-teal" type="submit">Send</button>', '<button class="btn btn-teal" type="submit">Send my request</button>')
    # ---- tracking context for script.js ----
    h = swap(h, '<script src="../../script.js', f'<script>window.FLR_REF={json.dumps({"slug": slug, "name": name})};</script>\n<script src="../../script.js')
    os.makedirs(f"agents/{slug}", exist_ok=True)
    open(f"agents/{slug}/index.html", "w", encoding="utf-8").write(h)
    return slug

# rebuild: remove folders for agents no longer in the roster
keep = {build(a) for a in roster}
for d in os.listdir("agents"):
    if os.path.isdir(f"agents/{d}") and d not in keep:
        shutil.rmtree(f"agents/{d}")
print("Built:", ", ".join(sorted(keep)))
