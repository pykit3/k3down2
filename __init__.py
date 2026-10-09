"""
k3down2 is utility to convert markdown segment into easy to transfer media such as images.
It depends on:

- pandoc to render markdown snippet to html, such as tables.
- graphviz to render graphviz to image.
- playwright (chromium) to render svg/html to png.
- mmdc to convert mermaid chart to svg. See: https://mermaid-js.github.io/mermaid/#
"""

__name__ = "k3down2"

from .down2 import (
    code_to_html,
    convert,
    download,
    graphviz_to_img,
    md_to_html,
    mdtable_to_barehtml,
    mermaid_to_svg,
    render_to_img,
    tex_to_img,
    tex_to_plain,
    tex_to_zhihu,
    tex_to_zhihu_compatible,
    tex_to_zhihu_url,
    web_to_img,
)

__all__ = [
    "code_to_html",
    "convert",
    "download",
    "graphviz_to_img",
    "md_to_html",
    "mdtable_to_barehtml",
    "mermaid_to_svg",
    "render_to_img",
    "tex_to_img",
    "tex_to_plain",
    "tex_to_zhihu",
    "tex_to_zhihu_compatible",
    "tex_to_zhihu_url",
    "web_to_img",
]


def __getattr__(name: str) -> str:
    # importlib.metadata takes about 20 ms to import, so it is loaded only
    # when __version__ is read
    if name != "__version__":
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    from importlib.metadata import version

    return version("k3down2")
