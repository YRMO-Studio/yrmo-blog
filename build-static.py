#!/usr/bin/env python3
"""
Build static HTML blog pages from JSON posts.
Generates individual HTML files for SEO indexing.
"""
import json
import os
import re
from datetime import datetime
from pathlib import Path

POSTS_DIR = Path(__file__).parent / "posts"
WEB_DIR = Path(os.path.expanduser("~/Projects/YRMO-Studio-WEB-Beta"))
BLOG_OUTPUT = WEB_DIR / "blog"
SITEMAP_PATH = WEB_DIR / "sitemap.xml"
DOMAIN = "https://yrmostudio.com"

def md_to_html(text):
    """Simple markdown to HTML converter."""
    lines = text.split('\n')
    html_parts = []
    in_list = False
    
    for line in lines:
        # Headings
        if line.startswith('### '):
            if in_list: html_parts.append('</ul>'); in_list = False
            html_parts.append(f'<h3>{escape_inline(line[4:])}</h3>')
            continue
        if line.startswith('## '):
            if in_list: html_parts.append('</ul>'); in_list = False
            html_parts.append(f'<h2>{escape_inline(line[3:])}</h2>')
            continue
        
        # HR
        if line.strip() == '---':
            if in_list: html_parts.append('</ul>'); in_list = False
            html_parts.append('<hr>')
            continue
        
        # List items
        if line.startswith('- '):
            if not in_list: html_parts.append('<ul>'); in_list = True
            html_parts.append(f'<li>{escape_inline(line[2:])}</li>')
            continue
        
        # Empty line
        if line.strip() == '':
            if in_list: html_parts.append('</ul>'); in_list = False
            continue
        
        # Paragraph
        if in_list: html_parts.append('</ul>'); in_list = False
        html_parts.append(f'<p>{escape_inline(line)}</p>')
    
    if in_list: html_parts.append('</ul>')
    return '\n      '.join(html_parts)

def escape_inline(text):
    """Process inline markdown (bold, italic, links)."""
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Links
    def link_replace(m):
        label, url = m.group(1), m.group(2)
        if re.match(r'^(https?:|mailto:|/|#)', url):
            return f'<a href="{url}" target="_blank" rel="noopener">{label}</a>'
        return label
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link_replace, text)
    return text

def generate_post_html(post):
    """Generate a full static HTML page for a blog post."""
    body_html = md_to_html(post.get('body', ''))
    title = post['title']
    desc = post['description']
    slug = post['slug']
    date = post['date']
    read_time = post.get('readTime', '5 min')
    author = post.get('author', 'YRMO Studio')
    tags = post.get('tags', [])
    
    tags_html = ''.join(f'<span class="tag">{t}</span>' for t in tags)
    
    return f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} — YRMO Studio</title>
  <meta name="description" content="{desc}">
  <meta name="author" content="{author}">
  <link rel="canonical" href="{DOMAIN}/blog/{slug}">
  
  <!-- Open Graph -->
  <meta property="og:type" content="article">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{DOMAIN}/blog/{slug}">
  <meta property="og:site_name" content="YRMO Studio">
  <meta property="article:published_time" content="{date}T00:00:00+01:00">
  <meta property="article:author" content="{author}">
  
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  
  <!-- JSON-LD Structured Data -->
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "BlogPosting",
    "headline": "{title}",
    "description": "{desc}",
    "datePublished": "{date}T00:00:00+01:00",
    "author": {{
      "@type": "Organization",
      "name": "YRMO Studio",
      "url": "{DOMAIN}"
    }},
    "publisher": {{
      "@type": "Organization",
      "name": "YRMO Studio",
      "url": "{DOMAIN}"
    }},
    "mainEntityOfPage": {{
      "@type": "WebPage",
      "@id": "{DOMAIN}/blog/{slug}"
    }}
  }}
  </script>
  
  <link rel="icon" href="../public/favicon.ico" type="image/x-icon">
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #050607;
      --text: #e8e8e8;
      --dim: #a0a0a0;
      --accent: #ACDD81;
      --forest: #1A552D;
      --font-display: 'Space Grotesk', sans-serif;
      --font-body: 'Inter', sans-serif;
    }}
    *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: var(--font-body);
      line-height: 1.8;
      min-height: 100vh;
    }}
    .nav {{
      position: fixed; top: 0; left: 0; right: 0; z-index: 100;
      padding: 20px 48px;
      display: flex; align-items: center; justify-content: space-between;
      background: rgba(5,6,7,0.92); backdrop-filter: blur(20px);
      border-bottom: 1px solid rgba(255,255,255,0.04);
    }}
    .nav__logo {{ height: 48px; }}
    .nav__links {{ display: flex; gap: 32px; list-style: none; }}
    .nav__links a {{ color: var(--dim); text-decoration: none; font-size: 0.95rem; transition: color 0.2s; }}
    .nav__links a:hover {{ color: var(--accent); }}
    
    .article {{
      max-width: 740px;
      margin: 0 auto;
      padding: 140px 24px 80px;
    }}
    .article__back {{
      display: inline-flex; align-items: center; gap: 8px;
      color: var(--accent); text-decoration: none; font-size: 0.9rem;
      margin-bottom: 40px; opacity: 0.8;
    }}
    .article__back:hover {{ opacity: 1; }}
    .article__meta {{
      color: var(--dim); font-size: 0.85rem; margin-bottom: 12px;
    }}
    .article__title {{
      font-family: var(--font-display);
      font-size: 2.4rem; font-weight: 700; line-height: 1.2;
      margin-bottom: 16px;
    }}
    .article__desc {{
      font-size: 1.15rem; color: var(--dim); line-height: 1.6;
      margin-bottom: 12px;
    }}
    .article__tags {{
      display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 40px;
    }}
    .tag {{
      background: rgba(172,221,129,0.08); color: var(--accent);
      padding: 4px 12px; border-radius: 20px; font-size: 0.78rem;
    }}
    .article__body h2 {{
      font-family: var(--font-display);
      font-size: 1.6rem; font-weight: 600; margin: 48px 0 16px;
      color: var(--text);
    }}
    .article__body h3 {{
      font-family: var(--font-display);
      font-size: 1.25rem; font-weight: 600; margin: 32px 0 12px;
    }}
    .article__body p {{
      margin-bottom: 16px; color: rgba(232,232,232,0.88);
    }}
    .article__body ul {{
      margin: 0 0 16px 24px;
    }}
    .article__body li {{
      margin-bottom: 8px; color: rgba(232,232,232,0.88);
    }}
    .article__body hr {{
      border: none; border-top: 1px solid rgba(255,255,255,0.06);
      margin: 40px 0;
    }}
    .article__body strong {{ color: var(--text); }}
    .article__body a {{ color: var(--accent); text-decoration: underline; }}
    
    .cta-box {{
      background: rgba(172,221,129,0.06);
      border: 1px solid rgba(172,221,129,0.15);
      border-radius: 12px; padding: 32px; margin-top: 48px;
      text-align: center;
    }}
    .cta-box h3 {{ font-family: var(--font-display); margin-bottom: 12px; }}
    .cta-box p {{ color: var(--dim); margin-bottom: 20px; }}
    .cta-btn {{
      display: inline-block; background: var(--accent); color: #050607;
      padding: 12px 32px; border-radius: 8px; text-decoration: none;
      font-weight: 600; font-size: 0.95rem;
    }}
    .cta-btn:hover {{ opacity: 0.9; }}
    
    @media (max-width: 768px) {{
      .nav {{ padding: 16px 20px; }}
      .article {{ padding: 100px 16px 60px; }}
      .article__title {{ font-size: 1.8rem; }}
    }}
  </style>
</head>
<body>
  <nav class="nav">
    <a href="/"><img src="../Wolf%20Logo.png" alt="YRMO Studio" class="nav__logo"></a>
    <ul class="nav__links">
      <li><a href="/">Inicio</a></li>
      <li><a href="/blog">Blog</a></li>
      <li><a href="/#contacto">Contacto</a></li>
    </ul>
  </nav>

  <article class="article">
    <a href="/blog" class="article__back">← Volver al blog</a>
    <div class="article__meta">{date} · {read_time} · {author}</div>
    <h1 class="article__title">{title}</h1>
    <p class="article__desc">{desc}</p>
    <div class="article__tags">{tags_html}</div>
    <div class="article__body">
      {body_html}
    </div>
    
    <div class="cta-box">
      <h3>¿Quieres tu propio agente IA?</h3>
      <p>Setup profesional, formación 1:1 y soporte continuo. Todo en español.</p>
      <a href="/#contacto" class="cta-btn">Hablar con YRMO Studio</a>
    </div>
  </article>
</body>
</html>'''


def md_file_to_json(md_path):
    """Convert a markdown blog post to the JSON format used by the repo."""
    with open(md_path, 'r') as f:
        content = f.read()
    
    # Extract title (first # line)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else md_path.stem
    
    # Extract description (line with **Resumen:** or first paragraph after ---)
    desc_match = re.search(r'\*\*Resumen:\*\*\s*(.+)', content)
    if not desc_match:
        desc_match = re.search(r'^---\s*\n\n(.+?)$', content, re.MULTILINE)
    desc = desc_match.group(1) if desc_match else title
    
    # Generate slug from filename
    slug = md_path.stem
    
    # Extract tags from content or filename
    tags = []
    if 'openclaw' in content.lower(): tags.append('openclaw')
    if 'negocio' in content.lower() or 'empresa' in content.lower(): tags.append('negocio')
    if 'tutorial' in content.lower() or 'guía' in content.lower() or 'paso' in content.lower(): tags.append('tutorial')
    if 'seguridad' in content.lower(): tags.append('seguridad')
    if 'pyme' in content.lower() or 'autónomo' in content.lower(): tags.append('pymes')
    if 'coste' in content.lower() or 'precio' in content.lower(): tags.append('costes')
    if not tags: tags.append('ia')
    
    # Body: everything after the first --- separator (skip frontmatter)
    body_parts = content.split('---', 2)
    if len(body_parts) >= 3:
        body = body_parts[2].strip()
    elif len(body_parts) >= 2:
        body = body_parts[1].strip()
    else:
        body = content
    
    # Remove the title line from body
    body = re.sub(r'^#\s+.+\n*', '', body).strip()
    # Remove author/date lines
    body = re.sub(r'^\*Por .+\*\n*', '', body).strip()
    body = re.sub(r'^\*\*Resumen:\*\*.*\n*', '', body).strip()
    if body.startswith('---'):
        body = body[3:].strip()
    
    # Estimate read time
    word_count = len(body.split())
    read_time = f"{max(3, word_count // 200)} min"
    
    return {
        "slug": slug,
        "title": title,
        "description": desc[:200],
        "date": "2026-03-08",
        "author": "YRMO Studio",
        "tags": tags[:5],
        "readTime": read_time,
        "image": None,
        "body": body
    }


def update_sitemap(posts):
    """Update sitemap.xml with blog post URLs."""
    sitemap_entries = [
        f'''  <url>
    <loc>{DOMAIN}/</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>''',
        f'''  <url>
    <loc>{DOMAIN}/blog</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.9</priority>
  </url>'''
    ]
    
    for post in sorted(posts, key=lambda p: p['date'], reverse=True):
        sitemap_entries.append(f'''  <url>
    <loc>{DOMAIN}/blog/{post['slug']}</loc>
    <lastmod>{post['date']}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>''')
    
    sitemap = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(sitemap_entries)}
</urlset>'''
    
    with open(SITEMAP_PATH, 'w') as f:
        f.write(sitemap)
    print(f"  Updated sitemap.xml with {len(posts)} blog posts")


def main():
    # 1. Load existing JSON posts
    all_posts = []
    for json_file in sorted(POSTS_DIR.glob("*.json")):
        if json_file.name == "index.json":
            continue
        with open(json_file) as f:
            post = json.load(f)
            all_posts.append(post)
            print(f"  Loaded: {post['slug']}")
    
    # 2. Convert markdown posts from output/blog/
    md_blog_dir = Path(os.path.expanduser("~/.openclaw/workspace/output/blog"))
    existing_slugs = {p['slug'] for p in all_posts}
    
    if md_blog_dir.exists():
        for md_file in sorted(md_blog_dir.glob("*.md")):
            slug = md_file.stem
            if slug in existing_slugs:
                print(f"  Skip (exists): {slug}")
                continue
            try:
                post = md_file_to_json(md_file)
                all_posts.append(post)
                
                # Save JSON to repo
                json_name = f"{post['date']}-{post['slug']}.json"
                json_path = POSTS_DIR / json_name
                with open(json_path, 'w') as f:
                    json.dump(post, f, ensure_ascii=False, indent=2)
                print(f"  Converted: {slug}")
            except Exception as e:
                print(f"  ERROR converting {slug}: {e}")
    
    # 3. Update index.json
    index_data = {
        "posts": sorted(
            [{"slug": p["slug"], "title": p["title"], "description": p["description"],
              "date": p["date"], "tags": p["tags"], "readTime": p["readTime"]}
             for p in all_posts],
            key=lambda x: x["date"],
            reverse=True
        )
    }
    with open(POSTS_DIR / "index.json", 'w') as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    print(f"  Updated index.json: {len(all_posts)} posts")
    
    # 4. Generate static HTML pages
    BLOG_OUTPUT.mkdir(exist_ok=True)
    
    # Create blog/index.html that redirects to /blog
    with open(BLOG_OUTPUT / "index.html", 'w') as f:
        f.write(f'<meta http-equiv="refresh" content="0;url=/blog">')
    
    for post in all_posts:
        slug_dir = BLOG_OUTPUT / post['slug']
        slug_dir.mkdir(exist_ok=True)
        html = generate_post_html(post)
        with open(slug_dir / "index.html", 'w') as f:
            f.write(html)
        print(f"  Generated HTML: /blog/{post['slug']}/")
    
    # 5. Update sitemap
    update_sitemap(all_posts)
    
    print(f"\nDone! {len(all_posts)} posts generated as static HTML.")
    print(f"Output: {BLOG_OUTPUT}/")


if __name__ == "__main__":
    main()
