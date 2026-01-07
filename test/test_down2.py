import os
import re
import unittest

import k3proc
import k3ut
import skimage
import skimage.io
from skimage.metrics import structural_similarity as ssim

import k3down2

dd = k3ut.dd

this_base = os.path.dirname(__file__)


class TestTex(unittest.TestCase):
    def _clean(self):
        pass

    def setUp(self):
        self._clean()

    def tearDown(self):
        self._clean()

    def test_convert(self):
        d = "test/data/convert"
        for folder, to, opts in (
            (
                "code",
                "jpg",
                {},
            ),
            (
                "code",
                "png",
                {},
            ),
            (
                "code-500",
                "jpg",
                {"width": 500},
            ),
            (
                "code-nolang",
                "jpg",
                {},
            ),
            (
                "code-unicode",
                "jpg",
                {},
            ),
            (
                "md",
                "jpg",
                {},
            ),
            (
                "md",
                "png",
                {},
            ),
            (
                "mermaid",
                "jpg",
                {},
            ),
            (
                "mermaid",
                "png",
                {},
            ),
            (
                "graphviz",
                "jpg",
                {},
            ),
            (
                "graphviz",
                "png",
                {},
            ),
            (
                "table",
                "jpg",
                {},
            ),
            (
                "table",
                "png",
                {},
            ),
            (
                "tex_block",
                "jpg",
                {},
            ),
            (
                "tex_block",
                "png",
                {},
            ),
            (
                "tex_inline",
                "jpg",
                {},
            ),
            (
                "tex_inline",
                "png",
                {},
            ),
        ):
            frm = folder.split("-")[0]
            inp = fread(d, folder, "input")
            got = k3down2.convert(frm, inp, to, opt={"html": opts})

            wantpath = pjoin(d, folder, "want." + to)
            gotpath = pjoin(d, folder, "got." + to)

            fwrite(gotpath, got)

            sim = cmp_image(wantpath, gotpath)
            self.assertGreater(sim, 0.8)

            rm(gotpath)

    def test_tex_to_zhihu_compatible(self):
        tex = r"\{ q > 5, a <> 2 \}"
        want = r"\{ q \gt 5, a <\gt 2 \}"
        wanturl = "%5C%7B%20q%20%5Cgt%205%2C%20a%20%3C%5Cgt%202%20%5C%7D"
        got, goturl = k3down2.tex_to_zhihu_compatible(tex)
        self.assertEqual(want, got)
        self.assertEqual(wanturl, goturl)

    def test_tex_to_zhihu(self):
        big = r"""
X = \begin{bmatrix}
1      & x_2    & x_2^2 \\

\vdots & \vdots & \vdots \\

1      & x_n    & x_n^2
\end{bmatrix}
""".strip()
        cases = [
            (
                r"a = b",
                True,
                r'<img src="https://www.zhihu.com/equation?tex=a%20%3D%20b%5C%5C" alt="a = b\\" class="ee_img tr_noresize" eeimg="1">',
            ),
            (
                r"a = b",
                False,
                r'<img src="https://www.zhihu.com/equation?tex=a%20%3D%20b" alt="a = b" class="ee_img tr_noresize" eeimg="1">',
            ),
            (
                big,
                True,
                r'<img src="https://www.zhihu.com/equation?tex=X%20%3D%20%5Cbegin%7Bbmatrix%7D1%20%20%20%20%20%20%26%20x_2%20%20%20%20%26%20x_2%5E2%20%5C%5C%5Cvdots%20%26%20%5Cvdots%20%26%20%5Cvdots%20%5C%5C1%20%20%20%20%20%20%26%20x_n%20%20%20%20%26%20x_n%5E2%5Cend%7Bbmatrix%7D%5C%5C" alt="X = \begin{bmatrix}1      & x_2    & x_2^2 \\\vdots & \vdots & \vdots \\1      & x_n    & x_n^2\end{bmatrix}\\" class="ee_img tr_noresize" eeimg="1">',
            ),
            (
                big,
                False,
                r'<img src="https://www.zhihu.com/equation?tex=X%20%3D%20%5Cbegin%7Bbmatrix%7D1%20%20%20%20%20%20%26%20x_2%20%20%20%20%26%20x_2%5E2%20%5C%5C%5Cvdots%20%26%20%5Cvdots%20%26%20%5Cvdots%20%5C%5C1%20%20%20%20%20%20%26%20x_n%20%20%20%20%26%20x_n%5E2%5Cend%7Bbmatrix%7D" alt="X = \begin{bmatrix}1      & x_2    & x_2^2 \\\vdots & \vdots & \vdots \\1      & x_n    & x_n^2\end{bmatrix}" class="ee_img tr_noresize" eeimg="1">',
            ),
        ]

        for tex, block, want in cases:
            got = k3down2.tex_to_zhihu(tex, block)
            self.assertEqual(want, got)

    def test_tex_to_plain(self):
        case = [
            (r"_1", "₁"),
            (r"a_1 + b^2", "a₁ + b²"),
            (r"b^3 a_z pp", "b³ a_z pp"),
            (r"\mathbb{Q}^3", "ℚ³"),
            (r"\mathbb{Q}^{x+1}", "ℚˣ⁺¹"),
            (r"\sum_{1}^{x+1}(i^2)", "∑₁ˣ⁺¹(i²)"),
        ]

        for inp, want in case:
            got = k3down2.tex_to_plain(inp)
            self.assertEqual(want, got, inp)

            got = k3down2.convert("tex_inline", inp, "plain")
            self.assertEqual(want, got, inp)

    def test_tex_to_img(self):
        d = "test/data/tex_to_img_matrix"

        tex = r"""
X = \begin{bmatrix}
1      & x_2    & x_2^2 \\

\vdots & \vdots & \vdots \\

1      & x_n    & x_n^2
\end{bmatrix}
""".strip()

        for typ in ("jpg", "png"):
            wantfn = "want." + typ
            gotfn = "got." + typ
            rm(pjoin(d, gotfn))

            got = k3down2.tex_to_img(tex, False, typ)
            fwrite(d, gotfn, got)
            sim = cmp_image(pjoin(d, wantfn), pjoin(d, gotfn))
            self.assertGreater(sim, 0.8)

            rm(pjoin(d, gotfn))

    def test_tex_to_zhihu_url(self):
        big = r"""
X = \begin{bmatrix}
1      & x_2    & x_2^2 \\

\vdots & \vdots & \vdots \\

1      & x_n    & x_n^2
\end{bmatrix}
""".strip()
        cases = [
            (r"a = b", True, r"https://www.zhihu.com/equation?tex=a%20%3D%20b%5C%5C"),
            (r"a = b", False, r"https://www.zhihu.com/equation?tex=a%20%3D%20b"),
            (
                big,
                True,
                r"https://www.zhihu.com/equation?tex=X%20%3D%20%5Cbegin%7Bbmatrix%7D1%20%20%20%20%20%20%26%20x_2%20%20%20%20%26%20x_2%5E2%20%5C%5C%5Cvdots%20%26%20%5Cvdots%20%26%20%5Cvdots%20%5C%5C1%20%20%20%20%20%20%26%20x_n%20%20%20%20%26%20x_n%5E2%5Cend%7Bbmatrix%7D%5C%5C",
            ),
            (
                big,
                False,
                r"https://www.zhihu.com/equation?tex=X%20%3D%20%5Cbegin%7Bbmatrix%7D1%20%20%20%20%20%20%26%20x_2%20%20%20%20%26%20x_2%5E2%20%5C%5C%5Cvdots%20%26%20%5Cvdots%20%26%20%5Cvdots%20%5C%5C1%20%20%20%20%20%20%26%20x_n%20%20%20%20%26%20x_n%5E2%5Cend%7Bbmatrix%7D",
            ),
        ]

        for tex, block, want in cases:
            got = k3down2.tex_to_zhihu_url(tex, block)
            self.assertEqual(want, got)

    def test_web_to_png(self):
        d = "test/data/svg_to_png_matrix"

        for typ in [
            "png",
            "jpg",
        ]:
            wantfn = "want." + typ
            gotfn = "got." + typ

            rm(d, gotfn)
            data = k3down2.web_to_img(pjoin(d, "input.svg"), typ)
            fwrite(d, gotfn, data)

            sim = cmp_image(os.path.join(d, wantfn), os.path.join(d, gotfn))
            self.assertGreater(sim, 0.8)
            rm(d, gotfn)

    def test_render_to_img(self):
        d = "test/data/render_to_img"

        for frm, to, opts in [
            ("html", "png", {}),
            ("svg", "jpg", {}),
            ("html-code", "png", {}),
            ("html-code-500", "png", {"width": 500}),
            ("html-code-300", "png", {"width": 300}),
        ]:
            frm_typ = frm.split("-")[0]
            typ = to
            gotfn = "got." + typ

            inp = fread(d, frm, "input")

            data = k3down2.render_to_img(frm_typ, inp, to, **opts)
            fwrite(d, frm, gotfn, data)

            sim = cmp_image(os.path.join(d, frm, "want." + typ), os.path.join(d, frm, gotfn))

            self.assertGreater(sim, 0.8)

            rm(d, frm, gotfn)

    def test_download(self):
        url = "https://www.zhihu.com/equation?tex=a%20%3D%20b%5C%5C"

        data = k3down2.download(url)

        with open("test/data/ab.svg", "rb") as f:
            want = f.read()
        self.assertEqual(want, data)

    def test_mdtable_to_barehtml(self):
        md = r"""
| a   | b   | b   |b   |
| :-- | --: | :-: |--- |
| c `foo | bar`   | d   | d   |d   |
| e   | f   | f   |f   |
"""
        got = k3down2.mdtable_to_barehtml(md)
        want = r"""
<table>
<tr class="header">
<th style="text-align: left;">a</th>
<th style="text-align: right;">b</th>
<th style="text-align: center;">b</th>
<th>b</th>
</tr>
<tr class="odd">
<td style="text-align: left;">c <code>foo | bar</code></td>
<td style="text-align: right;">d</td>
<td style="text-align: center;">d</td>
<td>d</td>
</tr>
<tr class="even">
<td style="text-align: left;">e</td>
<td style="text-align: right;">f</td>
<td style="text-align: center;">f</td>
<td>f</td>
</tr>
</table>
""".strip()

        want = normalize_pandoc_output(want, got)

        self.assertEqual(want, got)

    def test_mdtable_to_barehtml_wild_table(self):
        """
        A table with wide column will cause pandoc to produce ``colgroup`` tag, which is not recognized by zhihu.
        Reported in:
        https://github.com/drmingdrmer/md2zhihu/issues/22

        Thus we have to set a very big rendering window to disable this behavior
            https://github.com/jgm/pandoc/issues/2574

        """

        md = r"""
| a   | b   |
| :-- | --: |
| yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy     | d   |
| e   | f   |
"""
        got = k3down2.mdtable_to_barehtml(md)
        want = r"""
<table>
<tr class="header">
<th style="text-align: left;">a</th>
<th style="text-align: right;">b</th>
</tr>
<tr class="odd">
<td style="text-align: left;">yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy yyyy</td>
<td style="text-align: right;">d</td>
</tr>
<tr class="even">
<td style="text-align: left;">e</td>
<td style="text-align: right;">f</td>
</tr>
</table>
""".strip()

        want = normalize_pandoc_output(want, got)

        self.assertEqual(want, got)

    def test_md_to_html(self):
        md = r"""
| a   | b   | b   |b   |
| :-- | --: | :-: |--- |
| c `foo | bar`   | d   | d   |d   |
| e   | f   | f   |f   |
"""
        got = k3down2.md_to_html(md)
        want = r"""
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
<table>
<thead>
<tr class="header">
<th style="text-align: left;">a</th>
<th style="text-align: right;">b</th>
<th style="text-align: center;">b</th>
<th>b</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;">c <code>foo | bar</code></td>
<td style="text-align: right;">d</td>
<td style="text-align: center;">d</td>
<td>d</td>
</tr>
<tr class="even">
<td style="text-align: left;">e</td>
<td style="text-align: right;">f</td>
<td style="text-align: center;">f</td>
<td>f</td>
</tr>
</tbody>
</table>
"""
        want = normalize_pandoc_output(want, got)

        self.assertEqual(want, got)

    def test_md_to_html_embed_image(self):
        # Render a markdown of a single table with a image in it.
        # By specifying the asset base url, it should be rendered correctly.

        md = r"""
| a   | b   | b   |b   |
| :-- | --: | :-: |--- |
| ![](foo.jpg)   | d   | d   |d   |
| e   | f   | f   |f   |
"""
        d = "test/data/md_to_html"
        gothtml = k3down2.md_to_html(md)

        data = k3down2.convert(
            "html",
            gothtml,
            "jpg",
            opt={"html": {"asset_base": os.path.abspath(d) + "/assets"}},
        )
        fwrite(d, "got.jpg", data)

        sim = cmp_image(os.path.join(d, "want.jpg"), os.path.join(d, "got.jpg"))
        self.assertGreater(sim, 0.8)


def normalize_pandoc_output(want, got):
    #  pandoc may output different style html:
    #  '<tab[25 chars]n<th style="text-align: left;">a</th>\n<th sty[427 chars]ble>' !=
    #  '<tab[25 chars]n<th align="left">a</th>\n<th align="right">b<[310 chars]ble>'

    if 'align="' in got:
        want = re.sub(r'style="text-align: (left|right|center);"', r'align="\1"', want)
    return want


def cmp_image(want, got):
    da = skimage.io.imread(want)
    db = skimage.io.imread(got)

    if da.shape != db.shape:
        k3proc.command_ex(
            "convert",
            # height then width
            "-resize",
            "%dx%d!" % (da.shape[1], da.shape[0]),
            got,
            got,
        )
        db = skimage.io.imread(got)

    # fix different channel issues.
    if len(da.shape) == 3 and da.shape[2] == 4:
        # remove alpha channel, keep rgb
        da = da[:, :, :3]
    if len(db.shape) == 3 and db.shape[2] == 4:
        # remove alpha channel, keep rgb
        db = db[:, :, :3]

    img1 = skimage.img_as_int(da)
    img2 = skimage.img_as_int(db)

    print("img1:-------------", want)
    print(img1.shape)
    print("img2:-------------", got)
    print(img2.shape)

    # shape is in form: (170, 270, 4): 4 channels
    #              or:  (170, 270):    1 channel

    if len(img1.shape) == 2:
        p = ssim(img1, img2)
    else:
        # channel_axis=2 specifies img.shape[2] specifies the number of channels
        p = ssim(img1, img2, channel_axis=2)

    print("similarity(want/got):", want, got, p)
    return p


def pjoin(*p):
    return os.path.join(*p)


def rm(*p):
    try:
        os.unlink(os.path.join(*p))
    except OSError:
        pass


def fread(*p):
    with open(os.path.join(*p), "r") as f:
        return f.read()


def fwrite(*p):
    cont = p[-1]
    p = p[:-1]
    with open(os.path.join(*p), "wb") as f:
        f.write(cont)


def is_ci():
    # github ci
    return os.environ.get("CI") is not None
