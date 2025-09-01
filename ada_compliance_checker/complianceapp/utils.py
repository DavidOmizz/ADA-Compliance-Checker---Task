import re
from bs4 import BeautifulSoup
from html import escape
import webcolors


# Check for valid color formats
HEX_RE = re.compile(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})")
RGB_RE = re.compile(r"rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)")


NAMED_COLORS = {
'black': '#000000', 'white': '#ffffff', 'red': '#ff0000', 'green': '#008000',
'blue': '#0000ff', 'yellow': '#ffff00', 'gray': '#808080', 'grey': '#808080'
}

def normalize_hex(hex_or_short):
    h = hex_or_short.lstrip('#')
    if len(h) == 3:
        return ''.join([c*2 for c in h])
    return h


def hex_to_rgb(hexstr):
    h = normalize_hex(hexstr)
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def parse_color(token):
    # token = token.strip()
    # if not token:
    #     return None
    # m = HEX_RE.match(token)
    # if m:
    #     return hex_to_rgb(m.group(0))
    # m = RGB_RE.match(token)
    # if m:
    #     return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    # low = token.lower()
    # if low in NAMED_COLORS:
    #     return hex_to_rgb(NAMED_COLORS[low])
    # return None

    token = token.strip().lower()
    if not token:
        return None
    # Hex colors (#abc or #aabbcc)
    if HEX_RE.match(token):
        return hex_to_rgb(token)
    # RGB colors (rgb(255,0,0))
    m = RGB_RE.match(token)
    if m:
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    # Named colors (lightgreen, navy, etc.)
    try:
        rgb = webcolors.name_to_rgb(token)
        # print("DEBUG:", token, "->", rgb)
        return (rgb.red, rgb.green, rgb.blue)
    except ValueError:
        # print("DEBUG:", token, "->", rgb)
        return None


def relative_luminance(rgb):
    # rgb: tuple of ints 0-255
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
    # style string like 'color: lightgreen; background-color: green;'
    props = {}
    parts = style_str.split(';')
    for p in parts:
        if ':' in p:
            k,v = p.split(':',1)
            props[k.strip().lower()] = v.strip()
    fg = None
    bg = None
    if 'color' in props:
        fg = parse_color(props['color'])
    if 'background-color' in props:
        bg = parse_color(props['background-color'])
    return fg, bg

# def extract_inline_colors(style_str):
#     props = {}
#     parts = style_str.split(';')
#     for p in parts:
#         if ':' in p:
#             k,v = p.split(':',1)
#             props[k.strip().lower()] = v.strip().lower()  # 👈 normalize
#     fg = parse_color(props.get('color', ''))
#     bg = parse_color(props.get('background-color', ''))
#     return fg, bg



def css_selector_for(el):
    # simplified selector based on position
    path = []
    cur = el
    while cur and cur.name != '[document]':
        if not getattr(cur, 'name', None):
            break
        tag = cur.name
        # index among siblings of same tag
        parent = cur.parent
        if parent:
            same = [c for c in parent.find_all(cur.name, recursive=False)]
            if len(same) > 1:
                idx = same.index(cur) + 1
                path.append(f"{tag}:nth-of-type({idx})")
            else:
                path.append(tag)
        else:
            path.append(tag)
        cur = cur.parent
    return ' > '.join(reversed(path))


def snippet(el):
    return str(el)[:200]




def check_document(html):
    soup = BeautifulSoup(html, 'html.parser')
    issues = []

    # Check if lang attribute is present in <html> tag
    html_tag = soup.find('html')
    if html_tag is None or not html_tag.has_attr('lang') or not html_tag['lang'].strip():
        issues.append({
            'ruleId': 'DOC_LANG_MISSING',
            'message': "The document's primary language is not declared.",
            'element': 'html',
            'selector': css_selector_for(html_tag) if html_tag else 'html',
            'codeSnippet': snippet(html_tag) if html_tag else '<html>'
        })

    # Check if <title> tag is missing or empty
    title = soup.find('title')
    if title is None or not title.get_text(strip=True):
        issues.append({
            'ruleId': 'DOC_TITLE_MISSING',
            'message': 'Page is missing a non-empty <title> tag.',
            'element': 'title',
            'selector': css_selector_for(title) if title else 'head > title',
            'codeSnippet': snippet(title) if title else '<title>'
        })

    
    # IMG rules
    # Check <img> elements for missing alt attributes
    for img in soup.find_all('img'):
        if not img.has_attr('alt') or not img['alt'].strip():
            issues.append({
                'ruleId': 'IMG_ALT_MISSING',
                'message': 'Informative images should have a descriptive alt attribute.',
                'element': 'img',
                'selector': css_selector_for(img),
                'codeSnippet': snippet(img)
            })
        else:
            if len(img['alt']) > 120:
                issues.append({
                    'ruleId': 'IMG_ALT_LENGTH',
                    'message': 'alt text exceeds 120 characters (be concise).',
                    'element': 'img',
                    'selector': css_selector_for(img),
                    'codeSnippet': snippet(img)
                })

    # Link text
    # When <a> elements have generic text
    for a in soup.find_all('a'):
        text = (a.get_text() or '').strip().lower()
        if text in ('click here','here','read more'):
            issues.append({
                'ruleId': 'LINK_GENERIC_TEXT',
                'message': 'Link text should be descriptive; avoid generic phrases like "click here".',
                'element': 'a',
                'selector': css_selector_for(a),
                'codeSnippet': snippet(a)
            })

    
    # Headings
    # Check for multiple <h1> elements
    headings = []
    for i in range(1,7):
        for h in soup.find_all(f'h{i}'):
            headings.append((i,h))
    # Check multiple h1
    h1s = [h for lvl,h in headings if lvl==1]
    if len(h1s) > 1:
        for h in h1s:
            issues.append({
                'ruleId': 'HEADING_MULTIPLE_H1',
                'message': 'Page should have only one <h1>.',
                'element': 'h1',
                'selector': css_selector_for(h),
                'codeSnippet': snippet(h)
            })
    # Check order
    # Check heading order
    levels = [lvl for lvl,_ in headings]
    prev = 0
    for lvl,_ in headings:
        if prev and lvl > prev+1:
            issues.append({
                'ruleId': 'HEADING_ORDER',
                'message': f'Heading level skipped: previous {prev}, found {lvl}.',
                'element': f'h{lvl}',
                'selector': css_selector_for(_),
                'codeSnippet': snippet(_)
            })
        prev = lvl

    # Color contrast, I check inline styles on text-level elements
    # We'll check for elements that have a 'style' attribute containing color/background-color
    for tag in soup.find_all(True):
        style = tag.get('style')
        if not style:
            continue
        fg,bg = extract_inline_colors(style)
        if fg and bg:
            cr = contrast_ratio(fg,bg)
            # determine if text is large - approximate using tag name
            is_large = (tag.name in ('h1','h2'))
            threshold = 3.0 if is_large else 4.5
            if cr < threshold:
                issues.append({
                    'ruleId': 'COLOR_CONTRAST',
                    'message': f'Low contrast ratio: {cr:.2f}. Minimum expected is {threshold}.',
                    'element': tag.name,
                    'selector': css_selector_for(tag),
                    'codeSnippet': snippet(tag)
                })


    return issues