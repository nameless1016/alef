"""Inline SVG icons (stroke = currentColor)."""


def _svg(body: str, size: int = 14, sw: float = 1.6) -> str:
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{body}</svg>')


def logo(size: int = 16) -> str:
    return _svg('<path d="M12 3 4 20.5l8-4.2 8 4.2z"/>', size, 1.8)


def sparkle(size: int = 14) -> str:
    return _svg('<path d="M12 3c.6 4.6 2.4 6.4 9 9-6.6 2.6-8.4 4.4-9 9-.6-4.6-2.4-6.4-9-9 6.6-2.6 8.4-4.4 9-9z"/>', size)


def chevron_down(size: int = 12) -> str:
    return _svg('<path d="m6 9 6 6 6-6"/>', size)


def chevron_right(size: int = 12) -> str:
    return _svg('<path d="m9 6 6 6-6 6"/>', size)


def folder(size: int = 14) -> str:
    return _svg('<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>', size)


def clock(size: int = 12) -> str:
    return _svg('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>', size)


def calendar(size: int = 12) -> str:
    return _svg('<rect x="3.5" y="5" width="17" height="15" rx="1.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/>', size)


def check(size: int = 12) -> str:
    return _svg('<path d="m5 12.5 4.5 4.5L19 7.5"/>', size, 2)


def branch(size: int = 12) -> str:
    return _svg('<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="8" r="2"/><path d="M6 7v10M18 10c0 4-6 3-12 7"/>', size)


def file(size: int = 13) -> str:
    return _svg('<path d="M6 3h8l5 5v13H6z"/><path d="M14 3v5h5"/>', size)
