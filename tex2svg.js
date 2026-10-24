// Render the TeX read from stdin to a standalone SVG on stdout, with MathJax 3.
// Usage: node tex2svg.js block|inline < tex
// For bad TeX, it writes the message of MathJax to stderr and exits 1.
const fs = require("fs");
const { mathjax } = require("mathjax-full/js/mathjax.js");
const { TeX } = require("mathjax-full/js/input/tex.js");
const { SVG } = require("mathjax-full/js/output/svg.js");
const { liteAdaptor } = require("mathjax-full/js/adaptors/liteAdaptor.js");
const { RegisterHTMLHandler } = require("mathjax-full/js/handlers/html.js");
const { AllPackages } = require("mathjax-full/js/input/tex/AllPackages.js");

const mode = process.argv[2];
if (mode !== "block" && mode !== "inline") {
  process.stderr.write("usage: node tex2svg.js block|inline < tex\n");
  process.exit(2);
}

const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const doc = mathjax.document("", {
  // noundefined and noerrors would draw bad TeX in red instead of failing.
  InputJax: new TeX({ packages: AllPackages.filter((p) => p !== "noundefined" && p !== "noerrors") }),
  // "local" puts the glyphs in the <defs> of the SVG, so that the SVG stands alone.
  OutputJax: new SVG({ fontCache: "local" }),
});

const tex = fs.readFileSync(0, "utf8");
const node = doc.convert(tex, { display: mode === "block" });
const svg = adaptor.innerHTML(node);
const error = svg.match(/data-mjx-error="([^"]*)"/);
if (error) {
  process.stderr.write(error[1] + "\n");
  process.exit(1);
}
process.stdout.write(svg);
