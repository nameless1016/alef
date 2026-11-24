"""Icons drawn with CSS masks.

`st.html` strips inline <svg>, and relying on an icon font proved unreliable,
so each icon is a plain <span class="a-ic a-ic-NAME"> whose shape comes from a
data-URI mask defined in CSS (see `css()`, injected by utils.ui.inject_css).
The icon takes the text colour (currentColor).
"""
from urllib.parse import quote

_BODIES = {
    "logo": "<path d='M12 3 4 20.5l8-4.2 8 4.2z'/>",
    "sparkle": "<path d='M12 3c.6 4.6 2.4 6.4 9 9-6.6 2.6-8.4 4.4-9 9-.6-4.6-2.4-6.4-9-9 6.6-2.6 8.4-4.4 9-9z'/>",
    "chevron-down": "<path d='m6 9 6 6 6-6'/>",
    "chevron-right": "<path d='m9 6 6 6-6 6'/>",
    "folder": "<path d='M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/>",
    "clock": "<circle cx='12' cy='12' r='9'/><path d='M12 7v5l3 2'/>",
    "calendar": "<rect x='3.5' y='5' width='17' height='15' rx='1.5'/><path d='M3.5 10h17M8 3v4M16 3v4'/>",
    "check": "<path d='m5 12.5 4.5 4.5L19 7.5'/>",
    "branch": "<circle cx='6' cy='5' r='2'/><circle cx='6' cy='19' r='2'/><circle cx='18' cy='8' r='2'/><path d='M6 7v10M18 10c0 4-6 3-12 7'/>",
    "file": "<path d='M6 3h8l5 5v13H6z'/><path d='M14 3v5h5'/>",
}


def css() -> str:
    rules = [".a-ic{display:inline-block;flex:none;vertical-align:middle;background-color:currentColor;"
             "-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat}"]
    for name, body in _BODIES.items():
        svg = ("<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' "
               f"stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'>{body}</svg>")
        rules.append(f'.a-ic-{name}{{--ic:url("data:image/svg+xml,{quote(svg, safe="/:=,;()\' ")}")}}')
    return "\n".join(rules)


def _ic(name: str, size: int) -> str:
    return f'<span class="a-ic a-ic-{name}" style="width:{size}px;height:{size}px" aria-hidden="true"></span>'


def logo(size: int = 16) -> str: return _ic("logo", size)
def sparkle(size: int = 14) -> str: return _ic("sparkle", size)
def chevron_down(size: int = 12) -> str: return _ic("chevron-down", size)
def chevron_right(size: int = 12) -> str: return _ic("chevron-right", size)
def folder(size: int = 14) -> str: return _ic("folder", size)
def clock(size: int = 12) -> str: return _ic("clock", size)
def calendar(size: int = 12) -> str: return _ic("calendar", size)
def check(size: int = 12) -> str: return _ic("check", size)
def branch(size: int = 12) -> str: return _ic("branch", size)
def file(size: int = 13) -> str: return _ic("file", size)
