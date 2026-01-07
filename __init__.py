"""
k3down2 is utility to convert markdown segment into easy to transfer media such as images.
It depends on:

- pandoc to render markdown snippet to html, such as tables.
- graphviz to render graphviz to image.
- google-chrome to render svg/html to png.
- imagemagick to process images.
- mmdc to convert mermaid chart to svg. See: https://mermaid-js.github.io/mermaid/#
"""

from importlib.metadata import version

__version__ = version("k3down2")
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
