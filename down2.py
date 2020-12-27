#!/usr/bin/env python
# coding: utf-8

import os
import tempfile
import logging
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pylatexenc.latex2text import LatexNodes2Text

import k3proc

#  from . import mistune


logger = logging.getLogger(__name__)

zhihu_equation_url_fmt = ('https://www.zhihu.com/equation'
                          '?tex={texurl}{align}'
                          )

zhihu_equation_fmt = ('<img src="https://www.zhihu.com/equation'
                      '?tex={texurl}{align}"'
                      ' alt="{tex}{altalign}"'
                      ' class="ee_img'
                      ' tr_noresize"'
                      ' eeimg="1">')


def tex_to_zhihu_url(tex, block):
    '''
    Convert tex source to a url linking to a svg on zhihu.
    www.zhihu.com/equation is a public api to render tex into svg.

    Args:
        tex(str): tex source

        block(bool): whether to render a block(center-aligned) equation or
            inline equation.

    Returns:
        string of a ``<img>`` tag.
    '''
    tex = re.sub(r'\n', '', tex)
    texurl = urllib.parse.quote(tex)

    if block:
        # zhihu use double back slash to center-align an equation.
        align = '%5C%5C'
    else:
        align = ''

    url = zhihu_equation_url_fmt.format(
        texurl=texurl,
        align=align,
    )

    return url


def tex_to_zhihu(tex, block):
    '''
    Convert tex source to a img tag link to a svg on zhihu.
    www.zhihu.com/equation is a public api to render tex into svg.

    Args:
        tex(str): tex source

        block(bool): whether to render a block(center-aligned) equation or
            inline equation.

    Returns:
        string of a ``<img>`` tag.
    '''

    tex = re.sub(r'\n', '', tex)
    texurl = urllib.parse.quote(tex)

    if block:
        # zhihu use double back slash to center-align an equation.
        align = '%5C%5C'
        altalign = '\\\\'
    else:
        align = ''
        altalign = ''

    url = zhihu_equation_fmt.format(
        tex=tex,
        texurl=texurl,
        align=align,
        altalign=altalign,
    )

    return url


superscripts = {
    "0": "⁰",
    "1": "¹",
    "2": "²",
    "3": "³",
    "4": "⁴",
    "5": "⁵",
    "6": "⁶",
    "7": "⁷",
    "8": "⁸",
    "9": "⁹",
    "a": "ᵃ",
    "b": "ᵇ",
    "c": "ᶜ",
    "d": "ᵈ",
    "e": "ᵉ",
    "f": "ᶠ",
    "g": "ᵍ",
    "h": "ʰ",
    "i": "ⁱ",
    "j": "ʲ",
    "k": "ᵏ",
    "l": "ˡ",
    "m": "ᵐ",
    "n": "ⁿ",
    "o": "ᵒ",
    "p": "ᵖ",
    "r": "ʳ",
    "s": "ˢ",
    "t": "ᵗ",
    "u": "ᵘ",
    "v": "ᵛ",
    "w": "ʷ",
    "x": "ˣ",
    "y": "ʸ",
    "z": "ᶻ",
    "A": "ᴬ",
    "B": "ᴮ",
    "D": "ᴰ",
    "E": "ᴱ",
    "G": "ᴳ",
    "H": "ᴴ",
    "I": "ᴵ",
    "J": "ᴶ",
    "K": "ᴷ",
    "L": "ᴸ",
    "M": "ᴹ",
    "N": "ᴺ",
    "O": "ᴼ",
    "P": "ᴾ",
    "R": "ᴿ",
    "T": "ᵀ",
    "U": "ᵁ",
    "V": "ⱽ",
    "W": "ᵂ",
    "+": "⁺",
    "-": "⁻",
    "=": "⁼",
    "(": "⁽",
    ")": "⁾",
}

subscripts = {
    "0": "₀",
    "1": "₁",
    "2": "₂",
    "3": "₃",
    "4": "₄",
    "5": "₅",
    "6": "₆",
    "7": "₇",
    "8": "₈",
    "9": "₉",
    "+": "₊",
    "-": "₋",
    "=": "₌",
    "(": "₍",
    ")": "₎",
    "b": "ᵦ",
    "g": "ᵧ",
    "a": "ₐ",
    "e": "ₑ",
    "i": "ᵢ",
    "j": "ⱼ",
    "o": "ₒ",
    "r": "ᵣ",
    "u": "ᵤ",
    "v": "ᵥ",
    "x": "ₓ",

}


def all_in(chars, cate):
    for c in chars:
        if c not in cate:
            return False
    return True


def tex_to_plain(tex):
    '''
    Try hard converting tex to unicode plain text.
    '''

    for reg, cate in (
            (r'_\{([^}]*?)\}', subscripts),
            (r'[\^]\{([^}]*?)\}', superscripts),
            (r'_(.)', subscripts),
            (r'[\^](.)', superscripts),
    ):
        pieces = []
        while True:
            match = re.search(reg, tex, flags=re.DOTALL | re.UNICODE)
            if match:
                chars = match.groups()[0]
                if all_in(chars, cate):
                    chars = [cate[x] for x in chars]
                else:
                    chars = tex[match.start():match.end()]
                pieces.append(tex[:match.start()])
                pieces.append(''.join(chars))
                tex = tex[match.end():]
            else:
                pieces.append(tex)
                break

        tex = ''.join(pieces)

    return LatexNodes2Text().latex_to_text(tex)


def tex_to_png(tex, block, outputfn=None):
    '''
    Alias of ``tex_to_img(tex, block, "png", outputfn=outputfn)``
    '''
    return tex_to_img(tex, block, "png", outputfn=outputfn)


def tex_to_jpg(tex, block, outputfn=None):
    '''
    Alias of ``tex_to_img(tex, block, "jpg", outputfn=outputfn)``
    '''
    return tex_to_img(tex, block, "jpg", outputfn=outputfn)


def tex_to_img(tex, block, typ, outputfn=None):
    '''
    Convert tex source to an image.

    Args:
        tex(str): tex source

        block(bool): whether to render a block(center-aligned) equation or
            inline equation.

        typ(str): output image type such as "png" or "jpg"

        outputfn(str): specifies the output path. By default it is None.

    Returns:
        bytes of png data.
    '''

    tmpfn = 'tex_to_png.svg'
    url = tex_to_zhihu_url(tex, block)
    download(url, outputfn=tmpfn)
    data = web_to_img(tmpfn, typ)
    if outputfn is not None:
        with open(outputfn, 'wb') as f:
            f.write(data)

    return data


def download(url, outputfn=None):
    '''
    Download content from ``url`` and return the responded data.
    If ``outputfn`` is specified, it also saves the data into ``outputfn``.

    Args:
        url(str): the url from which to download.

        outputfn(str): the output path to save the data. If it is None, do nothing.

    Returns:
        bytes of downloaded data.
    '''

    filedata = urllib.request.urlopen(url)
    datatowrite = filedata.read()

    if outputfn is not None:
        with open(outputfn, 'wb') as f:
            f.write(datatowrite)

    return datatowrite


def web_to_png(pagefn, cwd=None):
    '''
    Alias of ``web_to_img(pagefn, typ="png", cwd=cwd)``.
    '''

    return web_to_img(pagefn, "png", cwd=cwd)


def web_to_jpg(pagefn, cwd=None):
    '''
    Alias of ``web_to_img(pagefn, typ="jpg", cwd=cwd)``.
    '''

    return web_to_img(pagefn, "jpg", cwd=cwd)


def web_to_img(pagefn, typ, cwd=None):
    '''
    Render a web page, which could be html, svg etc into image.
    It uses a headless chrome to render the page.
    Requirement: Chrome, imagemagick

    Args:
        pagefn(string): path to a local file that can be rendered by chrome.

        typ(string): specify output image type such as "png", "jpg"

        cwd(string): path to the working dir. By default it is None.

    Returns:
        bytes of the png data
    '''

    chrome = 'google-chrome'
    if sys.platform == 'darwin':
        # mac
        chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    k3proc.command_ex(
        chrome,
        "--headless",
        "--screenshot",
        "--window-size=1000,2000",
        "--default-background-color=0",
        pagefn,
        cwd=cwd,
    )

    if typ == 'png':
        moreargs = []
    else:
        # flatten alpha channel
        moreargs = ['-background', 'white', '-flatten', '-alpha', 'off']

    # crop to visible area
    _, out, _ = k3proc.command_ex(
        "convert",
        "screenshot.png",
        "-trim",
        "+repage",
        *moreargs,
        typ + ":-",
        text=False,
        cwd=cwd,
    )

    return out


html_style = '''
<style type="text/css" media="screen">
    table {
        display: block;
        margin-bottom: 1em;
        width: fit-content;
        font-family: -apple-system,BlinkMacSystemFont,"Roboto","Segoe UI","Helvetica Neue","Lucida Grande",Arial,sans-serif;
        font-size: .75em;
        border-collapse: collapse;
        overflow-x: auto;
    }

    thead {
        background-color: #f2f3f3;
        border-bottom: 2px solid #b6b6b6;
    }

    th {
        padding: 0.5em;
        font-weight: bold;
        text-align: left;
    }

    td {
        padding: 0.5em;
        border-bottom: 1px solid #ddd;
    }

    tr,
    td,
    th {
        vertical-align: middle;
    }
    pre.highlight {
        margin: 0;
        padding: 1em;
        background: #263238;
        color: #eff;
        font-size: 1.5em;
        font-family: "SFMono-Regular",Consolas,"Liberation Mono",Menlo,Courier,"PingFang SC", "Microsoft YaHei",monospace;
    }
</style>
'''


def md_to_html(md):
    '''
    Build markdown source into html.

    Args:
        md(str): markdown source.

    Returns:
        str of html
    '''

    _, html, _ = k3proc.command_ex(
        "pandoc",
        "-f", "markdown",
        "-t", "html",
        input=md,
    )

    return html_style + html


def md_to_png(md):
    '''
    Build markdown source into html screenshot in png.

    Args:
        md(str): markdown source.

    Returns:
        bytes of png data.
    '''

    html = md_to_html(md)

    fn = 'x.html'
    with open(fn, 'w') as f:
        f.write(html)

    return web_to_png(fn)


def mdtable_to_barehtml(md):
    '''
    Build markdown table into html without style.

    Args:
        md(str): markdown source.

    Returns:
        str of html
    '''

    _, html, _ = k3proc.command_ex(
        "pandoc",
        "-f", "markdown",
        "-t", "html",
        input=md,
    )
    lines = html.strip().split('\n')
    lines = [x for x in lines
             if x not in ('<thead>', '</thead>', '<tbody>', '</tbody>')
             ]

    return '\n'.join(lines)


def mermaid_to_svg(mmd, outputfn):
    """
    Render mermaid to svg.
    See: https://mermaid-js.github.io/mermaid/#

    Requires:
        npm install @mermaid-js/mermaid-cli
    """

    k3proc.command_ex(
        "mmdc",
        "-o", outputfn,
        input=mmd,
    )


def mermaid_to_img(mmd, typ, cwd=None):
    """
    Render mermaid to image.
    """

    with tempfile.TemporaryDirectory() as tdir:
        p = os.path.join(tdir, "mmd.svg")
        mermaid_to_svg(mmd, p)
        return web_to_img(p, typ, cwd=cwd)


def mermaid_to_jpg(mmd, cwd=None):
    """
    Alias to mermaid_to_img(mmd, "jpg", cwd=cwd)
    """
    return mermaid_to_img(mmd, 'jpg', cwd=cwd)


def mermaid_to_png(mmd, cwd=None):
    """
    Alias to mermaid_to_img(mmd, "png", cwd=cwd)
    """
    return mermaid_to_img(mmd, 'png', cwd=cwd)
