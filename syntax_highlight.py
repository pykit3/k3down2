from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Text, \
    Number, Operator, Punctuation, Literal


base00 = '#263238'
base01 = '#2e3c43'
base02 = '#314549'
base03 = '#546e7a'
base04 = '#b2ccd6'
base05 = '#eeffff'
base06 = '#eeffff'
base07 = '#ffffff'
base08 = '#f07178'
base09 = '#f78c6c'
base0a = '#ffcb6b'
base0b = '#c3e88d'
base0c = '#89ddff'
base0d = '#82aaff'
base0e = '#c792ea'
base0f = '#ff5370'


class Base16Style(Style):

    background_color = base00
    highlight_color = base02
    default_style = base05

    styles = {
        Text: base05,
        Error: base08,
        Comment: base03,
        Keyword: base0e,
        Keyword.Type: base0a,
        Keyword.Constant: base0d,
        Keyword.Namespace: base0d,
        Name: base05,
        Name.Builtin: base0a,
        Name.Function: base0d,
        Name.Class: base0d,
        Name.Decorator: base0e,
        Name.Exception: base08,
        Number: base09,
        Operator: base0d,
        Operator.Word: base0d,
        Punctuation: base05,
        Literal: base0b,
        String: base0b
    }


def escape(s, quote=True):
    s = s.replace("&", "&amp;")
    s = s.replace("<", "&lt;")
    s = s.replace(">", "&gt;")
    if quote:
        s = s.replace('"', "&quot;")
    return s


def code_to_html(text):

    lines = text.strip().split('\n')

    # extract code language: ```go
    lang = lines[0][3:].strip()
    text = '\n'.join(lines[1:-1])

    linenos = False
    style = Base16Style

    lineheight = "1.8"

    if lang == '':
        # For illustration text graph, use lower line height.
        # Becuase in such case it prefers an easy to read digram than a
        # comforable line height.
        lineheight = "1.3"

    prestyles = (r'line-height: {} !important;'
                 ' margin: 0 !important;'
                 ' padding: 1em;'
                 ' white-space: pre-wrap;'
                 ' background: {};'
                 ' color: {};').format(
                         lineheight,
                         style.background_color,
                         style.default_style,
                 )

    if lang == '':
        text = text.strip()
        return u'<pre style="%s"><code>%s</code></pre>\n' % (prestyles, escape(text))

    try:
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = HtmlFormatter(
            noclasses=True, linenos=linenos, style=style,
                prestyles=prestyles
        )
        code = highlight(text, lexer, formatter)
        if linenos:
            return '<div class="highlight-wrapper">%s</div>\n' % code
        return code
    except BaseException:
        return '<pre class="%s"><code>%s</code></pre>\n' % (
            lang, escape(text)
        )
