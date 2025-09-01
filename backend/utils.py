import re
import webcolors
from bs4 import BeautifulSoup

HEX_RE = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})")
RGB_RE = re.compile(r"rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)")

def normalize_hex(hex_or_short):
    h = hex_or_short.lstrip('#')
    if len(h) == 3:
        return ''.join([c*2 for c in h])
    return h

def hex_to_rgb(hexstr):
    h = normalize_hex(hexstr)
    return tuple(int(h[i:i+2], 16) for i in (0,2,4))

def parse_color(token):
    token = token.strip().lower()
    if not token:
        return None
    if HEX_RE.match(token):
        return hex_to_rgb(token)
    m = RGB_RE.match(token)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    try:
        rgb = webcolors.name_to_rgb(token)
        return (rgb.red, rgb.green, rgb.blue)
    except ValueError:
        return None

def relative_luminance(rgb):
    def channel(c):
        c = c/255.0
        return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055) ** 2.4
    r,g,b = rgb
    return 0.2126*channel(r) + 0.7152*channel(g) + 0.0722*channel(b)

def contrast_ratio(rgb1, rgb2):
    l1 = relative_luminance(rgb1)
    l2 = relative_luminance(rgb2)
    lighter = max(l1,l2)
    darker = min(l1,l2)
    return (lighter + 0.05) / (darker + 0.05)

def extract_inline_colors(style_str):
    props = {}
    parts = style_str.split(';')
    for p in parts:
        if ':' in p:
            k,v = p.split(':',1)
            props[k.strip().lower()] = v.strip().lower()
    fg = parse_color(props.get('color',''))
    bg = parse_color(props.get('background-color',''))
    return fg,bg

def css_selector_for(el):
    path = []
    cur = el
    while cur and getattr(cur, 'name', None) != '[document]':
        tag = cur.name
        parent = cur.parent
        if parent:
            same = [c for c in parent.find_all(cur.name, recursive=False)]
            if len(same) > 1:
                idx = same.index(cur)+1
                path.append(f"{tag}:nth-of-type({idx})")
            else:
                path.append(tag)
        else:
            path.append(tag)
        cur = parent
    return ' > '.join(reversed(path))

def snippet(el):
    return str(el)[:200]

def check_document(html):
    soup = BeautifulSoup(html, "html.parser")
    issues = []

    # Check if <html> tag is missing or empty
    html_tag = soup.find("html")
    if html_tag is None or not html_tag.has_attr("lang") or not html_tag["lang"].strip():
        issues.append({
            "ruleId": "DOC_LANG_MISSING",
            "message": "The document's primary language is not declared.",
            "element": "html",
            "selector": css_selector_for(html_tag) if html_tag else "html",
            "codeSnippet": snippet(html_tag) if html_tag else "<html>"
        })

    # Check if <title> tag is missing or empty
    title = soup.find("title")
    if title is None or not title.get_text(strip=True):
        issues.append({
            "ruleId": "DOC_TITLE_MISSING",
            "message": "Page is missing a non-empty <title> tag.",
            "element": "title",
            "selector": css_selector_for(title) if title else "head > title",
            "codeSnippet": snippet(title) if title else "<title>"
        })

    # When ALT is missing
    for img in soup.find_all("img"):
        if not img.has_attr("alt") or not img["alt"].strip():
            issues.append({
                "ruleId": "IMG_ALT_MISSING",
                "message": "Informative images should have a descriptive alt attribute.",
                "element": "img",
                "selector": css_selector_for(img),
                "codeSnippet": snippet(img)
            })

    # When link text is generic
    for a in soup.find_all("a"):
        text = (a.get_text() or "").strip().lower()
        if text in ("click here", "here", "read more"):
            issues.append({
                "ruleId": "LINK_GENERIC_TEXT",
                "message": "Link text should be descriptive; avoid generic phrases like 'click here'.",
                "element": "a",
                "selector": css_selector_for(a),
                "codeSnippet": snippet(a)
            })

    # Check multiple <h1> elements
    h1s = soup.find_all("h1")
    if len(h1s) > 1:
        for h in h1s:
            issues.append({
                "ruleId": "HEADING_MULTIPLE_H1",
                "message": "Page should have only one <h1>.",
                "element": "h1",
                "selector": css_selector_for(h),
                "codeSnippet": snippet(h)
            })

    # Check heading order
    headings = []
    for i in range(1,7):
        for h in soup.find_all(f"h{i}"):
            headings.append((i,h))
    prev = 0
    for lvl,h in headings:
        if prev and lvl > prev+1:
            issues.append({
                "ruleId": "HEADING_ORDER",
                "message": f"Heading level skipped: previous {prev}, found {lvl}.",
                "element": f"h{lvl}",
                "selector": css_selector_for(h),
                "codeSnippet": snippet(h)
            })
        prev = lvl

    # Check color contrast
    for tag in soup.find_all(True):
        style = tag.get("style")
        if not style: 
            continue
        fg,bg = extract_inline_colors(style)
        if fg and bg:
            cr = contrast_ratio(fg,bg)
            is_large = (tag.name in ("h1","h2"))
            threshold = 3.0 if is_large else 4.5
            if cr < threshold:
                issues.append({
                    "ruleId": "COLOR_CONTRAST",
                    "message": f"Low contrast ratio: {cr:.2f}. Minimum expected is {threshold}.",
                    "element": tag.name,
                    "selector": css_selector_for(tag),
                    "codeSnippet": snippet(tag)
                })

    return issues
