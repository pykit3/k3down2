import os
import unittest
import hashlib
import k3down2

import k3ut

dd = k3ut.dd

this_base = os.path.dirname(__file__)


class TestTex(unittest.TestCase):


    def _clean(self):
        pass

    def setUp(self):
        self._clean()

    def tearDown(self):
        self._clean()

    def test_tex_to_zhihu(self):
        big = r'''
X = \begin{bmatrix}
1      & x_2    & x_2^2 \\

\vdots & \vdots & \vdots \\

1      & x_n    & x_n^2
\end{bmatrix}
'''.strip()
        cases = [
                (r'a = b', True,
                 r'<img src="https://www.zhihu.com/equation?tex=a%20%3D%20b%5C%5C" alt="a = b\\" class="ee_img tr_noresize" eeimg="1">'),
                (r'a = b', False,
                 r'<img src="https://www.zhihu.com/equation?tex=a%20%3D%20b" alt="a = b" class="ee_img tr_noresize" eeimg="1">'),
                (big, True,
                 r'<img src="https://www.zhihu.com/equation?tex=X%20%3D%20%5Cbegin%7Bbmatrix%7D1%20%20%20%20%20%20%26%20x_2%20%20%20%20%26%20x_2%5E2%20%5C%5C%5Cvdots%20%26%20%5Cvdots%20%26%20%5Cvdots%20%5C%5C1%20%20%20%20%20%20%26%20x_n%20%20%20%20%26%20x_n%5E2%5Cend%7Bbmatrix%7D%5C%5C" alt="X = \begin{bmatrix}1      & x_2    & x_2^2 \\\vdots & \vdots & \vdots \\1      & x_n    & x_n^2\end{bmatrix}\\" class="ee_img tr_noresize" eeimg="1">',
                ),
                (big, False,
                 r'<img src="https://www.zhihu.com/equation?tex=X%20%3D%20%5Cbegin%7Bbmatrix%7D1%20%20%20%20%20%20%26%20x_2%20%20%20%20%26%20x_2%5E2%20%5C%5C%5Cvdots%20%26%20%5Cvdots%20%26%20%5Cvdots%20%5C%5C1%20%20%20%20%20%20%26%20x_n%20%20%20%20%26%20x_n%5E2%5Cend%7Bbmatrix%7D" alt="X = \begin{bmatrix}1      & x_2    & x_2^2 \\\vdots & \vdots & \vdots \\1      & x_n    & x_n^2\end{bmatrix}" class="ee_img tr_noresize" eeimg="1">',
                ),
        ]

        for tex, block, want in cases:
            got = k3down2.tex_to_zhihu(tex, block)
            self.assertEqual(want, got)

    def test_tex_to_zhihu_url(self):
        big = r'''
X = \begin{bmatrix}
1      & x_2    & x_2^2 \\

\vdots & \vdots & \vdots \\

1      & x_n    & x_n^2
\end{bmatrix}
'''.strip()
        cases = [
                (r'a = b', True,
                 r'https://www.zhihu.com/equation?tex=a%20%3D%20b%5C%5C'),
                (r'a = b', False,
                 r'https://www.zhihu.com/equation?tex=a%20%3D%20b'),
                (big, True,
                 r'https://www.zhihu.com/equation?tex=X%20%3D%20%5Cbegin%7Bbmatrix%7D1%20%20%20%20%20%20%26%20x_2%20%20%20%20%26%20x_2%5E2%20%5C%5C%5Cvdots%20%26%20%5Cvdots%20%26%20%5Cvdots%20%5C%5C1%20%20%20%20%20%20%26%20x_n%20%20%20%20%26%20x_n%5E2%5Cend%7Bbmatrix%7D%5C%5C',
                ),
                (big, False,
                 r'https://www.zhihu.com/equation?tex=X%20%3D%20%5Cbegin%7Bbmatrix%7D1%20%20%20%20%20%20%26%20x_2%20%20%20%20%26%20x_2%5E2%20%5C%5C%5Cvdots%20%26%20%5Cvdots%20%26%20%5Cvdots%20%5C%5C1%20%20%20%20%20%20%26%20x_n%20%20%20%20%26%20x_n%5E2%5Cend%7Bbmatrix%7D',
                ),
        ]

        for tex, block, want in cases:
            got = k3down2.tex_to_zhihu_url(tex, block)
            self.assertEqual(want, got)

    def test_web_to_bng(self):

        if is_ci():
            return

        fn = 'matrix.svg'
        outfn = 'matrix.png'
        try:
            os.unlink('test/data/' + outfn)
        except OSError:
            pass

        #  just run, no check
        k3down2.web_to_png(fn, cwd='test/data')


    def test_download(self):
        url = 'https://www.zhihu.com/equation?tex=a%20%3D%20b%5C%5C'

        data = k3down2.download(url)

        with open('test/data/ab.svg', 'rb') as f:
            want = f.read()
        self.assertEqual(want, data)

        k3down2.download(url, outputfn='test/data/foo.svg')

        with open('test/data/foo.svg', 'rb') as f:
            got = f.read()
        self.assertEqual(want, got)

    def test_md_to_html(self):

        if is_ci():
            return

        md = r'''
| a   | b   | b   |b   |
| :-- | --: | :-: |--- |
| c `foo | bar`   | d   | d   |d   |
| e   | f   | f   |f   |
'''
        got = k3down2.md_to_html(md)
        want = r'''
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
'''
        self.assertEqual(want, got)

    def test_md_to_png(self):

        if is_ci():
            return

        md = r'''
| a   | b   | b   |b   |
| :-- | --: | :-: |--- |
| c `foo | bar`   | d   | d   |d   |
| e   | f   | f   |f   |
'''
        got = k3down2.md_to_png(md)
        with open('x.png', 'wb') as f:
            f.write(got)

def is_ci():
    # github ci
    return os.environ.get('CI') is not None
