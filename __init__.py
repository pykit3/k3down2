"""
k3down2 is utility to convert markdown segment into easy to transfer media sucha images.
It depends on:

- pandoc to render markdown snippet to html, such as tables.
- graphviz to render graphviz to image.
- google-chrome to render svg/html to png.
- imagemagick to process images.
- mmdc to convert mermaid chart to svg. See: https://mermaid-js.github.io/mermaid/#


"""

__version__ = "0.1.19"
__name__ = "k3down2"

from .down2 import convert

from .down2 import tex_to_zhihu
from .down2 import tex_to_zhihu_compatible
from .down2 import tex_to_zhihu_url
from .down2 import tex_to_plain
from .down2 import tex_to_img
from .down2 import web_to_img

from .down2 import render_to_img

from .down2 import download

from .down2 import mermaid_to_svg
from .down2 import graphviz_to_img

from .down2 import code_to_html

from .down2 import md_to_html
from .down2 import mdtable_to_barehtml
