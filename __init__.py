"""
k3down2 is utility to convert markdown segment into easy to transfer media sucha images.
It depends on:

- pandoc to render markdown snippet to html, such as tables.
- google-chrome to render svg/html to png.
- imagemagick to process images.


"""

__version__ = "0.1.3"
__name__ = "k3down2"

from .down2 import tex_to_zhihu_url
from .down2 import tex_to_zhihu
from .down2 import tex_to_plain
from .down2 import tex_to_img
from .down2 import tex_to_jpg
from .down2 import tex_to_png
from .down2 import web_to_img
from .down2 import web_to_jpg
from .down2 import web_to_png
from .down2 import download
from .down2 import md_to_html
from .down2 import md_to_png
from .down2 import mdtable_to_barehtml
