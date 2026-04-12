#!/usr/bin/env python3
"""Build script for Yu Feng's academic homepage.
Edit JSON files in data/ then run: python3 build.py
"""
import json
import os
from collections import defaultdict

def load_json(filename):
    with open(os.path.join('data', filename)) as f:
        return json.load(f)


def build_education(education):
    items = []
    for ed in education:
        items.append(f'''
            <div class="edu-item">
                <i class="fa-solid fa-graduation-cap"></i>
                <div>
                    <div class="edu-degree">{ed["degree"]}, {ed["year"]}</div>
                    <div class="edu-institution">{ed["institution"]}</div>
                </div>
            </div>''')
    return '\n'.join(items)


def build_interests(interests):
    items = []
    for interest in interests:
        items.append(f'<li>{interest}</li>')
    return '\n                  '.join(items)


def build_students(students):
    cards = []
    for s in students:
        if s.get('url') and s['url'] != '#':
            name_html = f'<a href="{s["url"]}" target="_blank" rel="noopener">{s["name"]}</a>'
        elif s.get('url') == '#':
            name_html = s['name']
        else:
            name_html = s['name']
        cards.append(f'''
          <div class="student-card">
            <div class="student-name">{name_html}</div>
            <div class="student-role">{s["role"]}</div>
          </div>''')
    return '\n'.join(cards)


def build_publications(pubs):
    by_year = defaultdict(list)
    for p in pubs:
        by_year[p['year']].append(p)

    html_parts = []
    for year in sorted(by_year.keys(), reverse=True):
        html_parts.append(f'''
        <div class="pub-year-group">
          <div class="pub-year-header">{year}</div>''')

        for p in by_year[year]:
            award_badge = ''
            if p.get('award'):
                award_badge = f'<span class="award-badge"><i class="fa-solid fa-trophy"></i> {p["award"]}</span>'

            if p.get('url') and p['url'] != '#':
                pdf_link = f'<a href="{p["url"]}" class="pub-link" target="_blank" rel="noopener"><i class="fa-solid fa-file-pdf"></i> PDF</a>'
            else:
                pdf_link = ''

            html_parts.append(f'''
          <div class="pub-item">
            <div class="pub-title">{p["title"]}</div>
            <div class="pub-authors">{p["authors"]}</div>
            <div class="pub-venue">
              <span class="venue-name">{p["venue"]}, {p["year"]}</span>
              {award_badge}
            </div>
            <div class="pub-links">{pdf_link}</div>
          </div>''')

        html_parts.append('        </div>')

    return '\n'.join(html_parts)


def build_awards(awards):
    items = []
    for a in awards:
        items.append(f'<li>{a}</li>')
    return '\n              '.join(items)


def build_service(service):
    pc = service['program_committee'] if isinstance(service['program_committee'], str) else ', '.join(service['program_committee'])
    er = service['external_review'] if isinstance(service['external_review'], str) else ', '.join(service['external_review'])
    return f'''
            <div class="service-block">
              <h3>Program Committee</h3>
              <p>{pc}</p>
            </div>
            <div class="service-block">
              <h3>External Review</h3>
              <p>{er}</p>
            </div>'''


def build_jsonld_person(profile):
    """Build JSON-LD structured data for the Person schema."""
    import json as _json
    person = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": profile["name"],
        "alternateName": profile["name_cn"],
        "jobTitle": profile["title"],
        "url": "https://fredfeng.github.io/",
        "email": f'mailto:{profile["email"]}',
        "image": "https://fredfeng.github.io/img/me.jpg",
        "affiliation": {
            "@type": "Organization",
            "name": profile["university"],
            "department": {
                "@type": "Organization",
                "name": profile["department"]
            },
            "url": profile["university_url"]
        },
        "sameAs": [
            profile["scholar"],
            profile["github"],
            profile["twitter"]
        ],
        "alumniOf": [
            {
                "@type": "CollegeOrUniversity",
                "name": "University of Texas at Austin"
            },
            {
                "@type": "CollegeOrUniversity",
                "name": "Beihang University"
            }
        ],
        "knowsAbout": profile["interests"],
        "description": f'{profile["name"]} is an {profile["title"].lower()} in {profile["department"]} at {profile["university"]}. Research focuses on programming languages, formal verification, security, program synthesis, zero-knowledge proofs, and AI agent safety.'
    }
    return _json.dumps(person, indent=2)


def build_jsonld_publications(pubs):
    """Build JSON-LD structured data for recent publications as ScholarlyArticle items."""
    import json as _json
    articles = []
    for p in pubs[:10]:
        article = {
            "@context": "https://schema.org",
            "@type": "ScholarlyArticle",
            "name": p["title"],
            "author": [{"@type": "Person", "name": a.strip()} for a in p["authors"].split(",")],
            "datePublished": str(p["year"]),
            "isPartOf": {
                "@type": "PublicationEvent",
                "name": p["venue"]
            }
        }
        if p.get("url") and p["url"] != "#":
            url = p["url"]
            if url.startswith("/"):
                url = "https://fredfeng.github.io" + url
            article["url"] = url
        if p.get("award"):
            article["award"] = p["award"]
        articles.append(article)
    return _json.dumps(articles, indent=2)


def build():
    profile = load_json('profile.json')
    students = load_json('students.json')
    pubs = load_json('publications.json')
    awards = load_json('awards.json')
    service = load_json('service.json')

    education_html = build_education(profile['education'])
    interests_html = build_interests(profile['interests'])
    students_html = build_students(students)
    pubs_html = build_publications(pubs)
    awards_html = build_awards(awards['awards'])
    service_html = build_service(service)
    jsonld_person = build_jsonld_person(profile)
    jsonld_pubs = build_jsonld_publications(pubs)

    # Build keywords from interests
    keywords = ", ".join(profile["interests"]) + ", formal verification, smart contracts, DeFi security, zero-knowledge proofs, compiler, UC Santa Barbara, UCSB, computer science"

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{profile["name"]} ({profile["name_cn"]}) - {profile["title"]} of {profile["department"]} at {profile["university"]}. Research in programming languages, formal verification, security, program synthesis, zero-knowledge proofs, and AI agent safety.">
  <meta name="author" content="{profile["name"]}">
  <meta name="keywords" content="{keywords}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="https://fredfeng.github.io/">

  <meta property="og:site_name" content="{profile["name"]} ({profile["name_cn"]})">
  <meta property="og:url" content="https://fredfeng.github.io/">
  <meta property="og:title" content="{profile["name"]} ({profile["name_cn"]})">
  <meta property="og:description" content="{profile["title"]} of {profile["department"]} at {profile["university"]}. Research in programming languages, formal verification, security, and AI agent safety.">
  <meta property="og:locale" content="en-us">
  <meta property="og:type" content="website">
  <meta property="og:image" content="https://fredfeng.github.io/img/me.jpg">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:site" content="@captain8299">
  <meta name="twitter:creator" content="@captain8299">
  <meta name="twitter:title" content="{profile["name"]} ({profile["name_cn"]}) - {profile["title"]}, {profile["university"]}">
  <meta name="twitter:description" content="{profile["title"]} of {profile["department"]} at {profile["university"]}. Research in programming languages, formal verification, security, and AI agent safety.">
  <meta name="twitter:image" content="https://fredfeng.github.io/img/me.jpg">

  <script type="application/ld+json">
{jsonld_person}
  </script>
  <script type="application/ld+json">
{jsonld_pubs}
  </script>

  <title>{profile["name"]} ({profile["name_cn"]})</title>

  <link rel="icon" type="image/png" href="/img/icon.png">
  <link rel="apple-touch-icon" type="image/png" href="/img/icon.png">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" integrity="sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl+Vegovlnee1c9QX4TctnWMn13TZye+giMm8e2LwA==" crossorigin="anonymous" referrerpolicy="no-referrer">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/academicons/1.9.4/css/academicons.min.css" integrity="sha512-IW0nhlW5MgNydsXJO40En2EoCkTTjZhI3yuODrZIc8cQ4h1XcF53PsqDHa09NqnkXuIe0Oiyyj171BqZFwISBw==" crossorigin="anonymous" referrerpolicy="no-referrer">

  <style>
    :root {{
      --color-bg: #ffffff;
      --color-bg-alt: #f8f9fa;
      --color-navy: #1a1a2e;
      --color-navy-light: #16213e;
      --color-accent: #2ecc71;
      --color-accent-dark: #27ae60;
      --color-text: #2c3e50;
      --color-text-light: #636e72;
      --color-text-muted: #95a5a6;
      --color-border: #e8ecef;
      --color-card-bg: #ffffff;
      --font-main: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      --max-width: 1100px;
      --nav-height: 64px;
      --section-padding: 5rem 0;
      --transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    *, *::before, *::after {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}

    html {{
      scroll-behavior: smooth;
      scroll-padding-top: var(--nav-height);
    }}

    body {{
      font-family: var(--font-main);
      color: var(--color-text);
      background: var(--color-bg);
      line-height: 1.7;
      font-size: 16px;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }}

    /* ---- Navigation ---- */
    .nav {{
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: var(--nav-height);
      background: rgba(26, 26, 46, 0.95);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      z-index: 1000;
      border-bottom: 1px solid rgba(255,255,255,0.08);
    }}

    .nav-inner {{
      max-width: var(--max-width);
      margin: 0 auto;
      padding: 0 2rem;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .nav-brand {{
      color: #fff;
      text-decoration: none;
      font-weight: 600;
      font-size: 1.1rem;
      letter-spacing: -0.02em;
    }}

    .nav-links {{
      display: flex;
      gap: 0.25rem;
      list-style: none;
    }}

    .nav-links a {{
      color: rgba(255,255,255,0.75);
      text-decoration: none;
      font-size: 0.9rem;
      font-weight: 500;
      padding: 0.5rem 1rem;
      border-radius: 8px;
      transition: var(--transition);
    }}

    .nav-links a:hover {{
      color: #fff;
      background: rgba(255,255,255,0.1);
    }}

    .hamburger {{
      display: none;
      background: none;
      border: none;
      cursor: pointer;
      padding: 0.5rem;
      flex-direction: column;
      gap: 5px;
    }}

    .hamburger span {{
      display: block;
      width: 22px;
      height: 2px;
      background: #fff;
      border-radius: 2px;
      transition: var(--transition);
    }}

    /* ---- Hero ---- */
    .hero {{
      background: linear-gradient(135deg, var(--color-navy) 0%, var(--color-navy-light) 100%);
      padding: 8rem 2rem 5rem;
      margin-top: var(--nav-height);
    }}

    .hero-inner {{
      max-width: var(--max-width);
      margin: 0 auto;
      display: grid;
      grid-template-columns: 260px 1fr;
      gap: 4rem;
      align-items: start;
    }}

    .hero-photo {{
      width: 220px;
      height: 220px;
      border-radius: 50%;
      object-fit: cover;
      border: 4px solid rgba(255,255,255,0.15);
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }}

    .hero-profile {{
      text-align: center;
    }}

    .hero-name {{
      color: #fff;
      font-size: 2.4rem;
      font-weight: 700;
      letter-spacing: -0.03em;
      margin-bottom: 0.5rem;
      line-height: 1.2;
    }}

    .hero-title {{
      color: var(--color-accent);
      font-size: 1.15rem;
      font-weight: 500;
      margin-bottom: 0.25rem;
    }}

    .hero-affiliation {{
      color: rgba(255,255,255,0.7);
      font-size: 1rem;
    }}

    .hero-affiliation a {{
      color: rgba(255,255,255,0.85);
      text-decoration: none;
      border-bottom: 1px solid rgba(255,255,255,0.3);
      transition: var(--transition);
    }}

    .hero-affiliation a:hover {{
      color: #fff;
      border-color: var(--color-accent);
    }}

    .hero-social {{
      display: flex;
      justify-content: center;
      gap: 1rem;
      margin-top: 1.5rem;
    }}

    .hero-social a {{
      display: flex;
      align-items: center;
      justify-content: center;
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background: rgba(255,255,255,0.1);
      color: rgba(255,255,255,0.8);
      font-size: 1.2rem;
      text-decoration: none;
      transition: var(--transition);
    }}

    .hero-social a:hover {{
      background: var(--color-accent);
      color: #fff;
      transform: translateY(-2px);
    }}

    .hero-content {{
      color: rgba(255,255,255,0.85);
      font-size: 1.02rem;
      line-height: 1.8;
    }}

    .hero-content p {{
      margin-bottom: 1rem;
    }}

    .hero-content a {{
      color: var(--color-accent);
      text-decoration: none;
      border-bottom: 1px solid transparent;
      transition: var(--transition);
    }}

    .hero-content a:hover {{
      border-color: var(--color-accent);
    }}

    .hero-details {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2rem;
      margin-top: 2rem;
      padding-top: 2rem;
      border-top: 1px solid rgba(255,255,255,0.1);
    }}

    .hero-details h3 {{
      color: rgba(255,255,255,0.5);
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      margin-bottom: 0.75rem;
    }}

    .hero-details ul {{
      list-style: none;
    }}

    .hero-details li {{
      color: rgba(255,255,255,0.8);
      font-size: 0.95rem;
      padding: 0.2rem 0;
    }}

    .edu-item {{
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
      margin-bottom: 0.75rem;
    }}

    .edu-item i {{
      color: var(--color-accent);
      margin-top: 0.2rem;
      font-size: 0.9rem;
    }}

    .edu-degree {{
      color: rgba(255,255,255,0.9);
      font-size: 0.95rem;
      font-weight: 500;
    }}

    .edu-institution {{
      color: rgba(255,255,255,0.55);
      font-size: 0.85rem;
    }}

    /* ---- Sections ---- */
    .section {{
      padding: var(--section-padding);
    }}

    .section-alt {{
      background: var(--color-bg-alt);
    }}

    .container {{
      max-width: var(--max-width);
      margin: 0 auto;
      padding: 0 2rem;
    }}

    .section-header {{
      margin-bottom: 3rem;
    }}

    .section-header h2 {{
      font-size: 2rem;
      font-weight: 700;
      letter-spacing: -0.03em;
      color: var(--color-navy);
      margin-bottom: 0.5rem;
    }}

    .section-header p {{
      color: var(--color-text-light);
      font-size: 1.05rem;
    }}

    .section-line {{
      width: 48px;
      height: 3px;
      background: var(--color-accent);
      border-radius: 2px;
      margin-top: 0.75rem;
    }}

    /* ---- Students ---- */
    .students-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
      gap: 1.25rem;
    }}

    .student-card {{
      background: var(--color-card-bg);
      border: 1px solid var(--color-border);
      border-radius: 12px;
      padding: 1.5rem;
      transition: var(--transition);
    }}

    .student-card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 8px 30px rgba(0,0,0,0.08);
      border-color: var(--color-accent);
    }}

    .student-name {{
      font-weight: 600;
      font-size: 1rem;
      margin-bottom: 0.25rem;
    }}

    .student-name a {{
      color: var(--color-text);
      text-decoration: none;
      transition: var(--transition);
    }}

    .student-name a:hover {{
      color: var(--color-accent-dark);
    }}

    .student-role {{
      color: var(--color-text-muted);
      font-size: 0.85rem;
      font-weight: 500;
    }}

    /* ---- Publications ---- */
    .pub-year-group {{
      margin-bottom: 2.5rem;
    }}

    .pub-year-header {{
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--color-navy);
      letter-spacing: -0.02em;
      margin-bottom: 1rem;
      padding-bottom: 0.5rem;
      border-bottom: 2px solid var(--color-border);
    }}

    .pub-item {{
      padding: 1.25rem 0;
      border-bottom: 1px solid var(--color-border);
    }}

    .pub-item:last-child {{
      border-bottom: none;
    }}

    .pub-title {{
      font-weight: 600;
      font-size: 1.02rem;
      color: var(--color-text);
      line-height: 1.5;
      margin-bottom: 0.35rem;
    }}

    .pub-authors {{
      color: var(--color-text-light);
      font-size: 0.9rem;
      margin-bottom: 0.35rem;
    }}

    .pub-venue {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex-wrap: wrap;
    }}

    .venue-name {{
      color: var(--color-text-muted);
      font-size: 0.9rem;
      font-weight: 500;
    }}

    .award-badge {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      background: linear-gradient(135deg, #fff3cd, #ffeeba);
      color: #856404;
      font-size: 0.78rem;
      font-weight: 600;
      padding: 0.2rem 0.65rem;
      border-radius: 20px;
      border: 1px solid #ffc107;
    }}

    .award-badge i {{
      font-size: 0.7rem;
    }}

    .pub-links {{
      margin-top: 0.5rem;
    }}

    .pub-link {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      color: var(--color-accent-dark);
      text-decoration: none;
      font-size: 0.85rem;
      font-weight: 600;
      padding: 0.3rem 0.75rem;
      border: 1.5px solid var(--color-accent);
      border-radius: 6px;
      transition: var(--transition);
    }}

    .pub-link:hover {{
      background: var(--color-accent);
      color: #fff;
    }}

    /* ---- Awards ---- */
    .awards-list {{
      list-style: none;
    }}

    .awards-list li {{
      padding: 0.85rem 0 0.85rem 1.5rem;
      border-left: 3px solid var(--color-accent);
      margin-bottom: 0.5rem;
      font-size: 0.98rem;
      color: var(--color-text);
      transition: var(--transition);
      background: transparent;
      border-radius: 0 8px 8px 0;
    }}

    .awards-list li:hover {{
      background: rgba(46, 204, 113, 0.05);
      padding-left: 2rem;
    }}

    /* ---- Service ---- */
    .service-block {{
      margin-bottom: 2rem;
    }}

    .service-block h3 {{
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--color-navy);
      margin-bottom: 0.75rem;
    }}

    .service-block p {{
      color: var(--color-text-light);
      font-size: 0.95rem;
      line-height: 1.8;
    }}

    /* ---- Contact ---- */
    .contact-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1.5rem;
    }}

    .contact-item {{
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 1.25rem;
      border-radius: 12px;
      background: var(--color-card-bg);
      border: 1px solid var(--color-border);
      transition: var(--transition);
    }}

    .contact-item:hover {{
      border-color: var(--color-accent);
      box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    }}

    .contact-icon {{
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: rgba(46, 204, 113, 0.1);
      color: var(--color-accent-dark);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      flex-shrink: 0;
    }}

    .contact-label {{
      font-size: 0.8rem;
      color: var(--color-text-muted);
      font-weight: 500;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}

    .contact-value {{
      font-size: 0.95rem;
      font-weight: 500;
      color: var(--color-text);
    }}

    .contact-value a {{
      color: var(--color-text);
      text-decoration: none;
      transition: var(--transition);
    }}

    .contact-value a:hover {{
      color: var(--color-accent-dark);
    }}

    /* ---- Footer ---- */
    .footer {{
      background: var(--color-navy);
      color: rgba(255,255,255,0.5);
      text-align: center;
      padding: 2.5rem 2rem;
      font-size: 0.85rem;
    }}

    .footer a {{
      color: rgba(255,255,255,0.7);
      text-decoration: none;
      transition: var(--transition);
    }}

    .footer a:hover {{
      color: var(--color-accent);
    }}

    /* ---- Scroll animations ---- */
    .fade-in {{
      opacity: 1;
      transform: translateY(0);
      transition: opacity 0.6s ease, transform 0.6s ease;
    }}

    .fade-in.hidden {{
      opacity: 0;
      transform: translateY(20px);
    }}

    .fade-in.visible {{
      opacity: 1;
      transform: translateY(0);
    }}

    /* ---- Responsive ---- */
    @media (max-width: 768px) {{
      .hero-inner {{
        grid-template-columns: 1fr;
        gap: 2rem;
        text-align: center;
      }}

      .hero-profile {{
        display: flex;
        flex-direction: column;
        align-items: center;
      }}

      .hero-photo {{
        width: 160px;
        height: 160px;
      }}

      .hero-details {{
        grid-template-columns: 1fr;
        gap: 1.5rem;
      }}

      .hero-name {{
        font-size: 1.8rem;
      }}

      .hero {{
        padding: 6rem 1.5rem 3rem;
      }}

      .nav-links {{
        position: fixed;
        top: var(--nav-height);
        left: 0;
        right: 0;
        background: rgba(26, 26, 46, 0.98);
        backdrop-filter: blur(20px);
        flex-direction: column;
        padding: 1rem;
        gap: 0;
        transform: translateY(-100%);
        opacity: 0;
        pointer-events: none;
        transition: var(--transition);
      }}

      .nav-links.open {{
        transform: translateY(0);
        opacity: 1;
        pointer-events: auto;
      }}

      .nav-links a {{
        padding: 0.75rem 1rem;
        font-size: 1rem;
      }}

      .hamburger {{
        display: flex;
      }}

      .hamburger.active span:nth-child(1) {{
        transform: rotate(45deg) translate(5px, 5px);
      }}

      .hamburger.active span:nth-child(2) {{
        opacity: 0;
      }}

      .hamburger.active span:nth-child(3) {{
        transform: rotate(-45deg) translate(5px, -5px);
      }}

      .section {{
        padding: 3rem 0;
      }}

      .section-header h2 {{
        font-size: 1.6rem;
      }}

      .container {{
        padding: 0 1.25rem;
      }}

      .students-grid {{
        grid-template-columns: 1fr 1fr;
      }}

      .contact-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    @media (max-width: 480px) {{
      .students-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>

  <!-- Navigation -->
  <nav class="nav" role="navigation" aria-label="Main navigation">
    <div class="nav-inner">
      <a href="#" class="nav-brand">{profile["name"]} ({profile["name_cn"]})</a>
      <ul class="nav-links" id="navLinks">
        <li><a href="#about">Home</a></li>
        <li><a href="#students">Students</a></li>
        <li><a href="#publications">Publications</a></li>
        <li><a href="#awards">Awards</a></li>
        <li><a href="#service">Service</a></li>
        <li><a href="#contact">Contact</a></li>
      </ul>
      <button class="hamburger" id="hamburger" aria-label="Toggle navigation">
        <span></span>
        <span></span>
        <span></span>
      </button>
    </div>
  </nav>

  <main>
  <!-- Hero / About -->
  <section class="hero" id="about" aria-label="About Yu Feng">
    <div class="hero-inner">
      <div class="hero-profile">
        <img src="{profile["photo"]}" alt="{profile["name"]}" class="hero-photo">
        <h1 class="hero-name">{profile["name"]}</h1>
        <p class="hero-title">{profile["title"]}</p>
        <p class="hero-affiliation">
          <a href="{profile["university_url"]}" target="_blank" rel="noopener">{profile["university"]}</a>
        </p>
        <div class="hero-social">
          <a href="mailto:{profile["email"]}" aria-label="Email"><i class="fa-solid fa-envelope"></i></a>
          <a href="{profile["scholar"]}" target="_blank" rel="noopener" aria-label="Google Scholar"><i class="ai ai-google-scholar"></i></a>
          <a href="{profile["github"]}" target="_blank" rel="noopener" aria-label="GitHub"><i class="fa-brands fa-github"></i></a>
          <a href="{profile["twitter"]}" target="_blank" rel="noopener" aria-label="X / Twitter"><i class="fa-brands fa-x-twitter"></i></a>
        </div>
      </div>
      <div class="hero-content">
        <p>{profile["bio"]}</p>
        <p>{profile["research"]}</p>
        {"<p>" + profile["recruiting"] + "</p>" if profile.get("recruiting") else ""}
        <div class="hero-details">
          <div>
            <h3>Research Interests</h3>
            <ul>
              {interests_html}
            </ul>
          </div>
          <div>
            <h3>Education</h3>
            {education_html}
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Students -->
  <section class="section" id="students" aria-label="Students">
    <div class="container">
      <div class="section-header fade-in">
        <h2>Students</h2>
        <div class="section-line"></div>
      </div>
      <div class="students-grid fade-in">
        {students_html}
      </div>
    </div>
  </section>

  <!-- Publications -->
  <section class="section section-alt" id="publications" aria-label="Publications">
    <div class="container">
      <div class="section-header fade-in">
        <h2>Publications</h2>
        <div class="section-line"></div>
      </div>
      <div class="fade-in">
        {pubs_html}
      </div>
    </div>
  </section>

  <!-- Awards -->
  <section class="section" id="awards" aria-label="Awards and Grants">
    <div class="container">
      <div class="section-header fade-in">
        <h2>Awards &amp; Grants</h2>
        <div class="section-line"></div>
      </div>
      <ul class="awards-list fade-in">
        {awards_html}
      </ul>
    </div>
  </section>

  <!-- Service -->
  <section class="section section-alt" id="service" aria-label="Professional Service">
    <div class="container">
      <div class="section-header fade-in">
        <h2>Service</h2>
        <div class="section-line"></div>
      </div>
      <div class="fade-in">
        {service_html}
      </div>
    </div>
  </section>

  <!-- Contact -->
  <section class="section" id="contact" aria-label="Contact Information">
    <div class="container">
      <div class="section-header fade-in">
        <h2>Contact</h2>
        <div class="section-line"></div>
      </div>
      <div class="contact-grid fade-in">
        <div class="contact-item">
          <div class="contact-icon"><i class="fa-solid fa-envelope"></i></div>
          <div>
            <div class="contact-label">Email</div>
            <div class="contact-value"><a href="mailto:{profile["email"]}">{profile["email"]}</a></div>
          </div>
        </div>
        <div class="contact-item">
          <div class="contact-icon"><i class="fa-solid fa-location-dot"></i></div>
          <div>
            <div class="contact-label">Office</div>
            <div class="contact-value">{profile["office"]}</div>
          </div>
        </div>
        <div class="contact-item">
          <div class="contact-icon"><i class="fa-brands fa-github"></i></div>
          <div>
            <div class="contact-label">GitHub</div>
            <div class="contact-value"><a href="{profile["github"]}" target="_blank" rel="noopener">fredfeng</a></div>
          </div>
        </div>
        <div class="contact-item">
          <div class="contact-icon"><i class="fa-brands fa-x-twitter"></i></div>
          <div>
            <div class="contact-label">X / Twitter</div>
            <div class="contact-value"><a href="{profile["twitter"]}" target="_blank" rel="noopener">@captain8299</a></div>
          </div>
        </div>
      </div>
    </div>
  </section>

  </main>

  <!-- Footer -->
  <footer class="footer" role="contentinfo">
    <p>&copy; 2025 {profile["name"]}. {profile["university"]}.</p>
  </footer>

  <script>
    // Mobile menu toggle
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.getElementById('navLinks');

    hamburger.addEventListener('click', () => {{
      hamburger.classList.toggle('active');
      navLinks.classList.toggle('open');
    }});

    // Close mobile menu on link click
    navLinks.querySelectorAll('a').forEach(link => {{
      link.addEventListener('click', () => {{
        hamburger.classList.remove('active');
        navLinks.classList.remove('open');
      }});
    }});

    // Scroll-triggered fade-in: hide elements first, then reveal on scroll
    const fadeEls = document.querySelectorAll('.fade-in');
    fadeEls.forEach(el => el.classList.add('hidden'));

    const observer = new IntersectionObserver((entries) => {{
      entries.forEach(entry => {{
        if (entry.isIntersecting) {{
          entry.target.classList.remove('hidden');
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }}
      }});
    }}, {{ threshold: 0.05, rootMargin: '0px 0px 50px 0px' }});

    // Delay observer setup so above-fold elements render immediately
    requestAnimationFrame(() => {{
      fadeEls.forEach(el => {{
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight) {{
          el.classList.remove('hidden');
          el.classList.add('visible');
        }} else {{
          observer.observe(el);
        }}
      }});
    }});
  </script>

</body>
</html>'''

    with open('index.html', 'w') as f:
        f.write(html)

    print(f'Built index.html successfully ({len(pubs)} publications, {len(students)} students).')


if __name__ == '__main__':
    build()
