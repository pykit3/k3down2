#!/usr/bin/env python
# coding: utf-8

import logging
import re
import urllib.request
import urllib.parse
import urllib.error
import urllib.request
import urllib.error
import urllib.parse
import sys

#  from . import mistune

import k3proc

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


def tex_to_png(tex, block, outputfn=None):
    '''
    Convert tex source to a png.

    Args:
        tex(str): tex source

        block(bool): whether to render a block(center-aligned) equation or
            inline equation.

        outputfn(str): specifies the output path. By default it is None.

    Returns:
        bytes of png data.
    '''

    tmpfn = 'tex_to_png.svg'
    url = tex_to_zhihu_url(tex, block)
    download(url, outputfn=tmpfn)
    data = web_to_png(tmpfn)
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
    Render a web page, which could be html, svg etc into png and save it locally.
    It uses a headless chrome to render the page.
    Requirement: Chrome, imagemagick

    Args:
        pagefn(string): path to a local file that can be rendered by chrome.

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

    # crop to visible area
    _, out, _ = k3proc.command_ex(
        "convert",
        "screenshot.png",
        "-trim",
        "+repage",
        "png:-",
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
