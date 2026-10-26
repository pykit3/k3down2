import functools
import http.server
import io
import os
import re
import threading
import unittest
from unittest import mock

import k3proc
import k3ut
import numpy
import skimage
import skimage.io
from PIL import Image
from playwright.sync_api import BrowserType
from playwright.sync_api import Error as PlaywrightError
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
            self.assertGreater(sim, 0.75)

            rm(gotpath)

    def test_tex_to_zhihu_compatible(self):
        tex = r"\{ q > 5, a <> 2 \}"
        want = r"\{ q \gt 5, a <\gt 2 \}"
        wanturl = "%5C%7B%20q%20%5Cgt%205%2C%20a%20%3C%5Cgt%202%20%5C%7D"
        got, goturl = k3down2.tex_to_zhihu_compatible(tex)
        self.assertEqual(want, got)
        self.assertEqual(wanturl, goturl)

    def test_tex_to_zhihu_compatible_preserves_escaped_gt(self):
        cases = [
            # already-escaped \> should not become \\gt
            (r"a \> b", r"a \> b"),
            # arrow -> should not become -\gt
            (r"a -> b", r"a -\gt b"),
            # standalone > still replaced
            (r"x > 1", r"x \gt 1"),
            # multiple unescaped >
            (r"a > b > c", r"a \gt b \gt c"),
        ]
        for tex, want in cases:
            got, _ = k3down2.tex_to_zhihu_compatible(tex)
            self.assertEqual(want, got, tex)

    def test_tex_to_zhihu_compatible_gt_before_letter(self):
        cases = [
            # A letter right after \gt would form an undefined command such as \gty.
            (r"x>y", (r"x\gt y", "x%5Cgt%20y")),
            (r"a>b>c", (r"a\gt b\gt c", "a%5Cgt%20b%5Cgt%20c")),
            # A digit ends a command name, so it needs no space.
            (r"x>1", (r"x\gt1", "x%5Cgt1")),
        ]
        for tex, want in cases:
            got = k3down2.tex_to_zhihu_compatible(tex)
            self.assertEqual(want, got, tex)

    def test_tex_to_zhihu_compatible_newline(self):
        # TeX reads a line end as a space; deleting it would form the undefined command \cdotx.
        tex = "a \\cdot\nx"
        want = (r"a \cdot x", "a%20%5Ccdot%20x")
        got = k3down2.tex_to_zhihu_compatible(tex)
        self.assertEqual(want, got)

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
                r'<img src="https://www.zhihu.com/equation?tex=X%20%3D%20%5Cbegin%7Bbmatrix%7D%201%20%20%20%20%20%20%26%20x_2%20%20%20%20%26%20x_2%5E2%20%5C%5C%20%20%5Cvdots%20%26%20%5Cvdots%20%26%20%5Cvdots%20%5C%5C%20%201%20%20%20%20%20%20%26%20x_n%20%20%20%20%26%20x_n%5E2%20%5Cend%7Bbmatrix%7D%5C%5C" alt="X = \begin{bmatrix} 1      &amp; x_2    &amp; x_2^2 \\  \vdots &amp; \vdots &amp; \vdots \\  1      &amp; x_n    &amp; x_n^2 \end{bmatrix}\\" class="ee_img tr_noresize" eeimg="1">',
            ),
            (
                big,
                False,
                r'<img src="https://www.zhihu.com/equation?tex=X%20%3D%20%5Cbegin%7Bbmatrix%7D%201%20%20%20%20%20%20%26%20x_2%20%20%20%20%26%20x_2%5E2%20%5C%5C%20%20%5Cvdots%20%26%20%5Cvdots%20%26%20%5Cvdots%20%5C%5C%20%201%20%20%20%20%20%20%26%20x_n%20%20%20%20%26%20x_n%5E2%20%5Cend%7Bbmatrix%7D" alt="X = \begin{bmatrix} 1      &amp; x_2    &amp; x_2^2 \\  \vdots &amp; \vdots &amp; \vdots \\  1      &amp; x_n    &amp; x_n^2 \end{bmatrix}" class="ee_img tr_noresize" eeimg="1">',
            ),
        ]

        for tex, block, want in cases:
            got = k3down2.tex_to_zhihu(tex, block)
            self.assertEqual(want, got)

    def test_tex_to_zhihu_escapes_alt(self):
        cases = [
            # A raw quote would end the alt attribute and turn the rest of the tex into attributes.
            (
                r'\text{"a"} title="x"',
                r'<img src="https://www.zhihu.com/equation?tex=%5Ctext%7B%22a%22%7D%20title%3D%22x%22" alt="\text{&quot;a&quot;} title=&quot;x&quot;" class="ee_img tr_noresize" eeimg="1">',
            ),
            (
                r"f'(x)",
                r'<img src="https://www.zhihu.com/equation?tex=f%27%28x%29" alt="f&#x27;(x)" class="ee_img tr_noresize" eeimg="1">',
            ),
            (
                r"\text{&copy} a & b",
                r'<img src="https://www.zhihu.com/equation?tex=%5Ctext%7B%26copy%7D%20a%20%26%20b" alt="\text{&amp;copy} a &amp; b" class="ee_img tr_noresize" eeimg="1">',
            ),
            (
                r"a < b",
                r'<img src="https://www.zhihu.com/equation?tex=a%20%3C%20b" alt="a &lt; b" class="ee_img tr_noresize" eeimg="1">',
            ),
        ]

        for tex, want in cases:
            got = k3down2.tex_to_zhihu(tex, False)
            self.assertEqual(want, got, tex)

    def test_tex_to_plain(self):
        case = [
            (r"_1", "₁"),
            (r"a_1 + b^2", "a₁ + b²"),
            (r"b^3 a_z pp", "b³ a_z pp"),
            (r"\mathbb{Q}^3", "ℚ³"),
            (r"\mathbb{Q}^{x+1}", "ℚˣ⁺¹"),
            (r"\sum_{1}^{x+1}(i^2)", "∑₁ˣ⁺¹(i²)"),
            (r"a\_b", "a_b"),
            (r"a\_{b}", "a_b"),
            (r"a\\_1", "a\n₁"),
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
            self.assertGreater(sim, 0.75)

            rm(pjoin(d, gotfn))

    def test_tex_to_svg(self):
        # A display formula puts the limits of a sum below and above it, and an inline formula beside it.
        tex = r"\sum_{i=1}^{n} i"

        for name, block in (("block", True), ("inline", False)):
            got = k3down2.tex_to_svg(tex, block)

            with open(f"test/data/tex_to_svg/{name}.svg") as f:
                want = f.read()
            self.assertEqual(want, got, name)

    def test_tex_to_svg_bad_tex(self):
        with self.assertRaises(k3proc.CalledProcessError) as ctx:
            k3down2.tex_to_svg(r"a \foo b", False)

        self.assertEqual([r"Undefined control sequence \foo"], ctx.exception.err)

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
                r"https://www.zhihu.com/equation?tex=X%20%3D%20%5Cbegin%7Bbmatrix%7D%201%20%20%20%20%20%20%26%20x_2%20%20%20%20%26%20x_2%5E2%20%5C%5C%20%20%5Cvdots%20%26%20%5Cvdots%20%26%20%5Cvdots%20%5C%5C%20%201%20%20%20%20%20%20%26%20x_n%20%20%20%20%26%20x_n%5E2%20%5Cend%7Bbmatrix%7D%5C%5C",
            ),
            (
                big,
                False,
                r"https://www.zhihu.com/equation?tex=X%20%3D%20%5Cbegin%7Bbmatrix%7D%201%20%20%20%20%20%20%26%20x_2%20%20%20%20%26%20x_2%5E2%20%5C%5C%20%20%5Cvdots%20%26%20%5Cvdots%20%26%20%5Cvdots%20%5C%5C%20%201%20%20%20%20%20%20%26%20x_n%20%20%20%20%26%20x_n%5E2%20%5Cend%7Bbmatrix%7D",
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
            self.assertGreater(sim, 0.75)
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

            self.assertGreater(sim, 0.75)

            rm(d, frm, gotfn)

    def test_render_to_img_bytes_html(self):
        d = "test/data/render_to_img/html"
        inp = fread(d, "input").encode("utf-8")

        data = k3down2.render_to_img("html", inp, "png")
        fwrite(d, "got.png", data)

        sim = cmp_image(os.path.join(d, "want.png"), os.path.join(d, "got.png"))
        self.assertGreater(sim, 0.75)

        rm(d, "got.png")

    def test_render_to_img_wider_than_viewport(self):
        # The div starts at the 8px margin of the body and ends past the 1000px viewport.
        inp = '<div style="width: 1200px; height: 10px; background: black"></div>'

        data = k3down2.render_to_img("html", inp, "png", width=1000)

        # The screenshot is taken at 2 device pixels per CSS pixel, and the trim leaves only the div.
        got = Image.open(io.BytesIO(data))
        self.assertEqual((2400, 20), got.size)

    def test_render_to_img_closes_page_on_error(self):
        page = mock.Mock()
        page.goto.side_effect = RuntimeError("goto failed")
        browser = mock.Mock()
        browser.new_page.return_value = page

        with mock.patch.object(k3down2.down2, "_get_browser", return_value=browser), self.assertRaises(RuntimeError):
            k3down2.render_to_img("svg", "<svg/>", "png")

        page.close.assert_called_once_with()

    def test_render_to_img_retries_failed_capture(self):
        buf = io.BytesIO()
        Image.new("RGBA", (2, 1), (255, 0, 0, 255)).save(buf, format="PNG")
        png = buf.getvalue()
        failure = PlaywrightError(
            "Page.screenshot: Protocol error (Page.captureScreenshot): Unable to capture screenshot"
        )

        page = mock.Mock()
        # The page is 0px wide and high, so render_to_img() keeps the viewport.
        page.evaluate.return_value = 0
        page.screenshot.side_effect = [failure, failure, png]
        browser = mock.Mock()
        browser.new_page.return_value = page

        with mock.patch.object(k3down2.down2, "_get_browser", return_value=browser):
            data = k3down2.render_to_img("html", "<p>x</p>", "png")

        self.assertEqual(3, page.screenshot.call_count)
        got = Image.open(io.BytesIO(data))
        self.assertEqual((255, 0, 0, 255), got.getpixel((0, 0)))

    def test_render_to_img_raises_failed_screenshot(self):
        capture_failure = PlaywrightError(
            "Page.screenshot: Protocol error (Page.captureScreenshot): Unable to capture screenshot"
        )
        timeout = PlaywrightError("Page.screenshot: Timeout 30000ms exceeded.")

        # The results of the screenshots, and how many render_to_img() takes before it raises the last result.
        cases = (
            ([capture_failure, capture_failure, capture_failure], 3),
            ([timeout], 1),
        )

        for results, want_calls in cases:
            page = mock.Mock()
            page.evaluate.return_value = 0
            page.screenshot.side_effect = results
            browser = mock.Mock()
            browser.new_page.return_value = page

            with (
                mock.patch.object(k3down2.down2, "_get_browser", return_value=browser),
                self.assertRaises(PlaywrightError) as ctx,
            ):
                k3down2.render_to_img("html", "<p>x</p>", "png")

            self.assertIs(results[-1], ctx.exception)
            self.assertEqual(want_calls, page.screenshot.call_count)

    def test_get_browser_after_launch_failure(self):
        errors = [RuntimeError("launch failed")]
        launch = BrowserType.launch

        def launch_or_fail(browser_type, *args, **kwargs):
            if errors:
                raise errors.pop()
            return launch(browser_type, *args, **kwargs)

        # Start without a browser, so that _get_browser() starts Playwright and launches Chromium.
        k3down2.down2._shutdown_browser()

        with mock.patch.object(BrowserType, "launch", launch_or_fail):
            with self.assertRaisesRegex(RuntimeError, "launch failed"):
                k3down2.down2._get_browser()

            # A Playwright left running by the failed launch makes this call raise.
            browser = k3down2.down2._get_browser()

        self.assertTrue(browser.is_connected())

    def test_trim_and_convert(self):
        def png(size, bg, pixels):
            img = Image.new("RGBA", size, bg)
            for xy, color in pixels:
                img.putpixel(xy, color)

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()

        cases = (
            ("opaque", png((10, 10), (255, 255, 255, 255), [((5, 5), (0, 0, 0, 255))]), (0, 0, 0, 255)),
            ("transparent", png((10, 10), (0, 0, 0, 0), [((2, 3), (255, 0, 0, 255))]), (255, 0, 0, 255)),
            (
                "invisible color is not content",
                png((10, 10), (0, 0, 0, 0), [((2, 3), (255, 0, 0, 255)), ((8, 8), (255, 255, 255, 0))]),
                (255, 0, 0, 255),
            ),
        )

        for name, data, pixel in cases:
            got = Image.open(io.BytesIO(k3down2.down2._trim_and_convert(data, "png")))
            self.assertEqual((1, 1), got.size, name)
            self.assertEqual(pixel, got.getpixel((0, 0)), name)

    def test_download(self):
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory="test/data")
        with http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler) as server:
            thread = threading.Thread(target=server.serve_forever)
            thread.start()
            try:
                port = server.server_address[1]
                data = k3down2.download(f"http://127.0.0.1:{port}/ab.svg")
            finally:
                server.shutdown()
                thread.join()

        with open("test/data/ab.svg", "rb") as f:
            want = f.read()
        self.assertEqual(want, data)

    def test_download_closes_response_on_error(self):
        resp = mock.MagicMock()
        resp.__enter__.return_value = resp
        resp.read.side_effect = TimeoutError("read timed out")

        with (
            mock.patch("urllib.request.urlopen", return_value=resp) as urlopen,
            self.assertRaises(TimeoutError),
        ):
            k3down2.download("https://example.com/a.svg")

        urlopen.assert_called_once_with("https://example.com/a.svg", timeout=30)
        resp.__exit__.assert_called_once()

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
        self.assertGreater(sim, 0.75)

        rm(d, "got.jpg")


def normalize_pandoc_output(want, got):
    #  pandoc may output different style html:
    #  '<tab[25 chars]n<th style="text-align: left;">a</th>\n<th sty[427 chars]ble>' !=
    #  '<tab[25 chars]n<th align="left">a</th>\n<th align="right">b<[310 chars]ble>'

    if 'align="' in got:
        want = re.sub(r'style="text-align: (left|right|center);"', r'align="\1"', want)
    return want


def cmp_image(want, got):
    from PIL import Image as PILImage

    want_img = open_on_white(want)
    got_img = open_on_white(got)

    # Resize got to match want dimensions if they differ
    if want_img.size != got_img.size:
        got_img = got_img.resize(want_img.size, PILImage.LANCZOS)

    da = numpy.array(want_img)
    db = numpy.array(got_img)

    img1 = skimage.img_as_int(da)
    img2 = skimage.img_as_int(db)

    print("img1:-------------", want)
    print(img1.shape)
    print("img2:-------------", got)
    print(img2.shape)

    p = ssim(img1, img2, channel_axis=2)

    print("similarity(want/got):", want, got, p)
    return p


def open_on_white(path):
    # Paste the image on white, as a page shows it. convert("RGB") alone keeps the color stored in a transparent
    # pixel, and the transparent PNG goldens store black there, the color of their text.
    img = Image.open(path)
    rgba = img.convert("RGBA")
    white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    on_white = Image.alpha_composite(white, rgba)
    return on_white.convert("RGB")


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
