#!/usr/bin/env python
# coding: utf-8

import os
import tempfile
import logging
import re
import sys
import json
import urllib.error
import urllib.parse
import urllib.request
from pylatexenc.latex2text import LatexNodes2Text

import k3proc
from .mime import mimetypes
from .syntax_highlight import code_to_html


logger = logging.getLogger(__name__)

zhihu_equation_url_fmt = "https://www.zhihu.com/equation?tex={texurl}{align}"

zhihu_equation_fmt = (
    '<img src="https://www.zhihu.com/equation'
    '?tex={texurl}{align}"'
    ' alt="{tex}{altalign}"'
    ' class="ee_img'
    ' tr_noresize"'
    ' eeimg="1">'
)


def convert(input_typ, input, output_typ, opt=None):
    conv = mappings[(input_typ, output_typ)]
    if callable(conv):
        kwargs = {}
        if opt is not None and input_typ in opt:
            kwargs = opt[input_typ]
        return conv(input, **kwargs)
    else:
        #  indirect convertion
        inp = convert(input_typ, input, conv, opt=opt)
        return convert(conv, inp, output_typ, opt=opt)


def tex_to_zhihu_compatible(tex):
    r"""
    Convert tex to zhihu compatible format.
    - ``>`` in img alt mess up the next escaped brace: ``\{ q > 1 \} --> \{ q > 1 }``.
    """

    tex = re.sub(r"\n", "", tex)
    tex = tex.replace(r">", r"\gt")
    texurl = urllib.parse.quote(tex)
    return tex, texurl


def tex_to_zhihu_url(tex, block):
    """
    Convert tex source to a url linking to a svg on zhihu.
    www.zhihu.com/equation is a public api to render tex into svg.

    Args:
        tex(str): tex source

        block(bool): whether to render a block(center-aligned) equation or
            inline equation.

    Returns:
        string of a ``<img>`` tag.
    """

    tex, texurl = tex_to_zhihu_compatible(tex)

    if block:
        # zhihu use double back slash to center-align an equation.
        align = "%5C%5C"
    else:
        align = ""

    url = zhihu_equation_url_fmt.format(
        texurl=texurl,
        align=align,
    )

    return url


def tex_to_zhihu(tex, block):
    """
    Convert tex source to a img tag link to a svg on zhihu.
    www.zhihu.com/equation is a public api to render tex into svg.

    Args:
        tex(str): tex source

        block(bool): whether to render a block(center-aligned) equation or
            inline equation.

    Returns:
        string of a ``<img>`` tag.
    """

    tex, texurl = tex_to_zhihu_compatible(tex)

    if block:
        # zhihu use double back slash to center-align an equation.
        align = "%5C%5C"
        altalign = "\\\\"
    else:
        align = ""
        altalign = ""

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
    """
    Try hard converting tex to unicode plain text.
    """

    for reg, cate in (
        (r"_\{([^}]*?)\}", subscripts),
        (r"[\^]\{([^}]*?)\}", superscripts),
        (r"_(.)", subscripts),
        (r"[\^](.)", superscripts),
    ):
        pieces = []
        while True:
            match = re.search(reg, tex, flags=re.DOTALL | re.UNICODE)
            if match:
                chars = match.groups()[0]
                if all_in(chars, cate):
                    chars = [cate[x] for x in chars]
                else:
                    chars = tex[match.start() : match.end()]
                pieces.append(tex[: match.start()])
                pieces.append("".join(chars))
                tex = tex[match.end() :]
            else:
                pieces.append(tex)
                break

        tex = "".join(pieces)

    return LatexNodes2Text().latex_to_text(tex)


def tex_to_img(tex, block, typ):
    """
    Convert tex source to an image.

    Args:
        tex(str): tex source

        block(bool): whether to render a block(center-aligned) equation or
            inline equation.

        typ(str): output image type such as "png" or "jpg"

    Returns:
        bytes of png data.
    """

    input_type = "tex_block"
    if not block:
        input_type = "tex_inline"
    return convert(input_type, tex, typ)


def download(url):
    """
    Download content from ``url`` and return the responded data.
    If ``outputfn`` is specified, it also saves the data into ``outputfn``.

    Args:
        url(str): the url from which to download.

    Returns:
        bytes of downloaded data.
    """

    filedata = urllib.request.urlopen(url)
    datatowrite = filedata.read()
    return datatowrite


def web_to_img(pagefn, typ):
    """
    Render a web page, which could be html, svg etc into image.
    It uses a headless chrome to render the page.
    Requirement: Chrome, imagemagick

    Args:
        pagefn(string): path to a local file that can be rendered by chrome.

        typ(string): specify output image type such as "png", "jpg"

    Returns:
        bytes of the png data
    """

    intyp = pagefn.rsplit(".")[-1]
    page = fread(pagefn)
    return render_to_img(intyp, page, typ)


def render_to_img(mime, input, typ, width=1000, height=2000, asset_base=None):
    """
    Render content that is renderable in chrome to image.
    Such as html, svg etc into image.
    It uses a headless chrome to render the page.
    Requirement: Chrome, imagemagick

    Args:
        mime(str): a full mime type such as ``image/jpeg`` or a shortcut ``jpg``.

        input(str): content of the input, such as jpeg data or svg source file.

        typ(string): specifies output image type such as "png", "jpg"

        width(int): specifies the window width to render a page. Default 1000.

        height(int): specifies the window height to render a page. Default 2000.

        asset_base(str): specifies the path to assets dir. E.g. the image base path in a html page.

    Returns:
        bytes of the png data
    """

    if "html" in mime:
        input = (
            r'<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>'
            + input
        )

        # Only for html page we need to add asset_base url.
        if asset_base is not None:
            input = r'<base href="file://{}/">'.format(asset_base) + input

    m = mimetypes.get(mime) or mime

    # Use the input mime type as temp page suffix.
    suffix = mime

    # If the input ``mime`` is a full mime type such as `application/xhtml+xml`,
    # convert it back to file suffix.
    for k, v in mimetypes.items():
        if v == m:
            suffix = k
            break

    chrome = "google-chrome"
    if sys.platform == "darwin":
        # mac
        chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    with tempfile.TemporaryDirectory() as tdir:
        # Write page content into a temp file.
        # Since chrome does not recoganize the `<base>` tag encoded in a
        # data-uri.
        fn = os.path.join(tdir, "xxx." + suffix)
        flags = "w"
        if isinstance(input, bytes):
            flags = "wb"
        with open(fn, flags) as f:
            f.write(input)

        k3proc.command_ex(
            chrome,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--screenshot",
            "--window-size={},{}".format(width, height),
            "--default-background-color=00000000",
            "--force-device-scale-factor=2",
            "--disable-web-security",
            "--disable-features=VizDisplayCompositor",
            fn,
            cwd=tdir,
        )

        if typ == "png":
            moreargs = []
        else:
            # flatten alpha channel
            moreargs = ["-background", "white", "-flatten", "-alpha", "off"]

        # crop to visible area
        _, out, _ = k3proc.command_ex(
            "convert",
            pjoin(tdir, "screenshot.png"),
            "-trim",
            "+repage",
            *moreargs,
            typ + ":-",
            text=False,
        )

    return out


html_style = """
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
"""


def md_to_html(md):
    """
    Build markdown source into html.

    Args:
        md(str): markdown source.

    Returns:
        str of html
    """

    _, html, _ = k3proc.command_ex(
        "pandoc",
        "-f",
        "markdown",
        "-t",
        "html",
        input=md,
    )

    return html_style + html


def mdtable_to_barehtml(md):
    """
    Build markdown table into html without style.

    Args:
        md(str): markdown source.

    Returns:
        str of html
    """

    # A table with wide column will cause pandoc to produce ``colgroup`` tag, which is not recognized by zhihu.
    # Reported in:
    #      https://github.com/drmingdrmer/md2zhihu/issues/22
    #
    # Thus we have to set a very big rendering window to disable this behavior
    #      https://github.com/jgm/pandoc/issues/2574

    _, html, _ = k3proc.command_ex(
        "pandoc",
        "-f",
        "markdown",
        "-t",
        "html",
        "--column",
        "100000",
        input=md,
    )
    lines = html.strip().split("\n")
    lines = [
        x for x in lines if x not in ("<thead>", "</thead>", "<tbody>", "</tbody>")
    ]

    return "\n".join(lines)


def mermaid_to_svg(mmd):
    """
    Render mermaid to svg.
    See: https://mermaid-js.github.io/mermaid/#

    Requires:
        npm install @mermaid-js/mermaid-cli
    """

    with tempfile.TemporaryDirectory() as tdir:
        output_path = os.path.join(tdir, "mmd.svg")

        puppeteer_config = {
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
            ]
        }

        config_file_path = os.path.join(tdir, "config.json")
        with open(config_file_path, "w") as f:
            f.write(json.dumps(puppeteer_config))

        k3proc.command_ex(
            "npm",
            "exec",
            "--",
            "mmdc",
            "-o",
            output_path,
            "--puppeteerConfigFile",
            config_file_path,
            input=mmd,
        )
        return fread(output_path)


def graphviz_to_img(gv, typ):
    """
    Render graphviz to svg.

    Requires:
        brew install graphviz
    """

    _, out, _ = k3proc.command_ex(
        "dot",
        "-T" + typ,
        input=to_bytes(gv),
        text=False,
    )
    return out


def to_bytes(s):
    if isinstance(s, bytes):
        return s
    return bytes(s, "utf-8")


def pjoin(*p):
    return os.path.join(*p)


def fread(*p):
    with open(os.path.join(*p), "r") as f:
        return f.read()


mappings = {
    ("md", "html"): md_to_html,
    ("md", "jpg"): "html",
    ("md", "png"): "html",
    ("html", "jpg"): lambda x, **kwargs: render_to_img("html", x, "jpg", **kwargs),
    ("html", "png"): lambda x, **kwargs: render_to_img("html", x, "png", **kwargs),
    # markdown table
    ("table", "html"): mdtable_to_barehtml,
    ("table", "jpg"): "html",
    ("table", "png"): "html",
    ("mermaid", "svg"): mermaid_to_svg,
    ("mermaid", "jpg"): "svg",
    ("mermaid", "png"): "svg",
    ("graphviz", "svg"): lambda x: graphviz_to_img(x, "svg"),
    ("graphviz", "jpg"): lambda x: graphviz_to_img(x, "jpg"),
    ("graphviz", "png"): lambda x: graphviz_to_img(x, "png"),
    ("tex_block", "url"): lambda x: tex_to_zhihu_url(x, True),
    ("tex_inline", "url"): lambda x: tex_to_zhihu_url(x, False),
    ("tex_block", "imgtag"): lambda x: tex_to_zhihu(x, True),
    ("tex_inline", "imgtag"): lambda x: tex_to_zhihu(x, False),
    ("url", "jpg"): download,
    ("url", "png"): download,
    ("url", "svg"): download,
    ("url", "html"): download,
    ("tex_block", "jpg"): "svg",
    ("tex_inline", "jpg"): "svg",
    ("tex_block", "png"): "svg",
    ("tex_inline", "png"): "svg",
    ("tex_block", "svg"): "url",
    ("tex_inline", "svg"): "url",
    ("tex_inline", "plain"): tex_to_plain,
    ("svg", "jpg"): lambda x: render_to_img("svg", x, "jpg"),
    ("svg", "png"): lambda x: render_to_img("svg", x, "png"),
    ("code", "html"): code_to_html,
    ("code", "jpg"): "html",
    ("code", "png"): "html",
}
