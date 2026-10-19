#!/usr/bin/env python3
"""Print edition of the Apartment 14 dossier: a full-bleed cover, twelve A4-landscape pages and a back cover (fourteen in all, an even count for duplex binding) from index.html.

The live page is loaded in headless Chromium with window.__PRINT set, a print
stylesheet is added, and the sheets are re-cut into fixed 297 x 210 mm pages
(both plan views rendered statically). Plan PNGs are flattened onto the
panel colour first so the PDF carries no soft masks.
Run:  python3 tools/make_pdf.py [out.pdf]      (default apartment-14-heights-777.pdf)
"""
import asyncio, json, sys, tempfile
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parent.parent
PANEL = (246, 246, 244)  # --bg2, the plan panel
MM = 96 / 25.4

PRINT_CSS = r"""
@page{size:297mm 210mm;margin:0}
html,body{margin:0;padding:0;background:var(--bg)}
body{display:block}
html{scroll-behavior:auto}
.rail,.bar,.lb,.btns,.tabs,.tbtn,.railclose,.docs li.self,.legend{display:none!important}
.stick{position:static}
main{margin:0}
.pg{position:relative;width:297mm;height:210mm;padding:12mm 16mm 16mm;overflow:hidden;background:var(--bg);break-after:page;page-break-after:always}
.pg.band{background:var(--bg2)}
.pg:last-child{break-after:auto;page-break-after:auto}
.pg > *{max-width:none}
.pfoot{position:absolute;left:16mm;right:16mm;bottom:7.5mm;display:flex;justify-content:space-between;gap:6mm;font:500 6.8pt/1 var(--fb);letter-spacing:.22em;text-transform:uppercase;color:var(--ink3)}
.shead{margin-bottom:7mm;padding-bottom:3.2mm;gap:5mm}
.shead h2{font-size:8pt}
.shead .sno,.shead .smeta{font-size:6.6pt}
.title{font-size:24pt;margin-bottom:4mm;max-width:none}
.lede{font-size:10.5pt;line-height:1.5;margin-bottom:3.5mm;max-width:none}
.body{font-size:9pt;line-height:1.5;max-width:none;margin-bottom:.9em}
.cap{font-size:7.4pt;margin-top:3mm}
.sched div{font-size:8.2pt;line-height:1.4;padding:2mm 0;gap:4mm;grid-template-columns:30mm 1fr}
.sched dt{font-size:6.2pt;padding-top:1mm}
.two,.two.rev{grid-template-columns:1fr 1fr;gap:12mm}
/* front cover: full-bleed photograph, no running footer */
.pg.front{padding:0}
.pg.front .front{height:100%;min-height:0;padding:14mm 16mm}
.front .ftop,.front .fbot{font-size:7pt}
.front .ftitle{font-size:96pt}
.front .ftitle small{font-size:7.4pt;margin-bottom:6mm}
/* back cover: charcoal, built here (print only) */
.pg.back{padding:0;background:var(--ink)}
.backc{height:100%;display:flex;flex-direction:column;justify-content:space-between;padding:14mm 16mm;color:#f6f6f4;font:500 7pt/1.6 var(--fb);letter-spacing:.24em;text-transform:uppercase}
.backc .bt{display:flex;justify-content:space-between}
.backc .bm{text-align:center}
.backc .bm b{display:block;font:200 30pt/1 var(--fd);letter-spacing:-.01em;text-transform:none;margin:0 0 6mm}
.backc .bm i{display:block;width:14mm;height:.4mm;background:var(--acc2);margin:0 auto 6mm}
.backc .bb{display:grid;grid-template-columns:repeat(2,auto);justify-content:space-between;gap:6mm;color:rgba(246,246,244,.72)}
.backc .bb span b{display:block;color:#f6f6f4;font-weight:500;margin-bottom:1.5mm}
.front .cue{display:none}
/* welcome */
.pg.cover .stamp{font-size:6.8pt;margin-bottom:12mm}
.pg.cover .hero{grid-template-columns:1fr 1fr;gap:14mm;align-items:center}
.pg.cover .h1{font-size:36pt;margin-bottom:6mm}
.pg.cover .h1 small{font-size:7pt;margin-bottom:6mm}
.pg.cover .lede{font-size:10.5pt}
.pg.cover .figs{margin-top:10mm;padding-top:5mm;gap:6mm}
.pg.cover .figs .n{font-size:22pt}
.pg.cover .figs .n small{font-size:9pt}
.pg.cover .figs .l{font-size:6.4pt;margin-top:2mm}
.pg.cover .hv{aspect-ratio:auto;height:150mm}
/* building */
.sitebox{padding:6mm;border-radius:5mm}
.siteplan{aspect-ratio:auto;height:112mm}
.sitecap{font-size:8pt;min-height:0;margin-top:3mm;padding-top:2.5mm}
.sitecap i{font-size:6pt}
.legend{gap:2mm;margin-top:3mm}
.legend li{height:7.5mm;padding:0 3.5mm;font-size:7pt}
.sp-txt{font-size:1.25px}
.sp-txt.dim{font-size:1.1px}
.enc2{margin-top:0}
.frame.aer{aspect-ratio:auto;height:150mm}
/* residence */
.elev{padding:7mm;border-radius:5mm}
.moves{margin-top:0;gap:8mm}
.moves li{font-size:8.6pt;line-height:1.5;padding-top:3mm}
.moves b{font-size:12.5pt;margin-bottom:2mm}
.wide{margin-top:9mm}
.wide .frame{aspect-ratio:auto;height:110mm}
/* plans */
.planwrap{grid-template-columns:1fr 92mm;gap:9mm;align-items:start}
.plan.crop,.plan.full{max-width:none}
.plan.full{margin-top:6mm}
.ptag{font-size:6.4pt;top:-1.5mm}
.pzone{border-radius:3mm}
.planbox{padding:7mm;border-radius:5mm}
.plan{margin:0 auto}
.mk{display:none!important}  /* plans print clean; the lists name the rooms */
.planfoot{font-size:7.4pt;margin-top:3.5mm}
.pside h3{font-size:16pt}
.pside .rt{font-size:6.6pt}
.pside p{font-size:8.4pt;margin:3mm 0 4mm}
.homes{gap:5mm}
.homes h4{font-size:6.4pt;margin-bottom:1.5mm}
.rl li{font-size:7.8pt;padding:1.6mm 0;grid-template-columns:1fr}
.rl li i{display:none}
.levels{margin-top:6mm;padding-top:3.5mm;gap:6mm}
.levels .n{font-size:14pt}
.levels .l{font-size:6.4pt;margin-top:1.5mm}
.foot-note{font-size:7.6pt;margin-top:5mm}
/* materials */
.mats{grid-template-columns:repeat(3,1fr);gap:5mm;margin:6mm 0 0}
.mat{border-radius:4mm}
.mat .sw{aspect-ratio:16/7}
.mat .mt{padding:3.5mm 4mm 4mm}
.mat .mt i{font-size:6.2pt;margin-bottom:1.5mm}
.mat .mt b{font-size:10.5pt}
.mat .mt span{font-size:7.6pt}
.spec{gap:7mm 12mm}
.spec h4{font-size:13pt;margin-bottom:2.5mm}
.spec .sched div{font-size:7.8pt;padding:1.7mm 0;grid-template-columns:24mm 1fr}
/* views */
.gal{gap:3mm}
.gal.ga{grid-auto-rows:74mm}
.gal.gb{grid-auto-rows:80mm}
.gal figure{border-radius:3.5mm}
.gal figcaption{font-size:7pt;padding:8mm 3.5mm 3mm}
/* desk */
.desk{grid-template-columns:1fr 1fr;gap:14mm}
.acts{margin-top:6mm;gap:3mm}
.act{padding:3.5mm 4mm;grid-template-columns:10mm 1fr auto;gap:4mm;border-radius:3.5mm}
.act .ic{width:10mm;height:10mm}
.act .ic svg{width:4.5mm;height:4.5mm}
.act b{font-size:10.5pt}
.act span{font-size:7.8pt}
.act i{font-size:6.2pt}
.desk h4{font-size:13pt;margin-bottom:3mm}
.docs li{font-size:9pt;padding:3.5mm 0}
.docs li span{font-size:7.6pt}
.docs a,.docs em{font-size:6.2pt}
.docs a{padding:2.5mm 3.5mm}
.disc{margin-top:10mm;padding-top:4mm;font-size:7.4pt;max-width:none}
"""

# Re-cuts the sheets into pages: originals are moved, sheet headers are cloned.
PRINT_JS = r"""
(() => {
  const $ = (s, r) => (r || document).querySelector(s);
  const MM = 96 / 25.4, FOOT = 'Apartment 14 at Heights 777 · Prepared for Horizon Growth Limited by Wrace International · Private';
  const main = $('main'), pages = [];
  const take = (s) => { const n = $(s); if (!n) throw new Error('missing ' + s); return n; };
  const head = {}; ['building', 'residence', 'plans', 'materials', 'views', 'desk'].forEach(id => { head[id] = take('#' + id + ' .shead'); });
  const H = (id) => head[id].cloneNode(true);
  const page = (cls, nodes) => { const d = document.createElement('section'); d.className = 'pg ' + cls; nodes.forEach(n => d.appendChild(n)); pages.push(d); };
  /* both plan views, each a static clone of the explorer sized to a page height */
  const plans = {};
  ['unit', 'floor'].forEach(v => { window.__renderPlan(v); plans[v] = $('.planwrap').cloneNode(true); });
  const sizePlan = (wrap, hmm) => { const plan = $('.plan', wrap), img = $('img', plan); const w = +img.getAttribute('width'), h = +img.getAttribute('height'), px = hmm * MM; plan.style.height = px + 'px'; plan.style.width = (px * w / h) + 'px'; img.style.width = '100%'; img.style.height = '100%'; };
  sizePlan(plans.unit, 112); sizePlan(plans.floor, 84);
  /* screen-only wording */
  const lede = take('#plans .lede'); lede.textContent = lede.textContent.replace(' Hover a number, or a room in the list.', '');
  const fn = take('#plans .foot-note'); fn.textContent = fn.textContent.replace('; the numbered markers sit where the rooms are labelled on the sheet', '');
  const sc = take('#sitecap'); sc.innerHTML = sc.innerHTML.replace(' · hover any part of the plot', '');
  page('cover', [take('#welcome .stamp'), take('#welcome .hero')]);
  page('band', [H('building'), take('#building .two')]);
  page('band', [H('building'), take('#building .enc2')]);
  page('', [H('residence'), take('#residence .two')]);
  page('', [H('residence'), take('#residence .moves'), take('#residence .wide')]);
  page('', [H('plans'), take('#plans .title'), take('#plans .lede'), plans.unit]);
  page('', [H('plans'), plans.floor, fn]);
  page('band', [H('materials'), take('#materials .title'), take('#materials .lede'), take('#materials .mats')]);
  page('band', [H('materials'), take('#materials .spec')]);
  /* views over two pages: the two large views, then the other five */
  const gal = take('#views .gal'), gb = gal.cloneNode(false); gal.classList.add('ga'); gb.classList.add('gb'); [...gal.children].slice(2).forEach(f => gb.appendChild(f));
  page('band', [H('views'), take('#views .title'), gal]);
  page('band', [H('views'), gb]);
  page('', [H('desk'), take('#desk .desk'), take('#desk .disc')]);
  page('front', [take('#front')]); pages.unshift(pages.pop());
  const back = document.createElement('div'); back.className = 'backc';
  back.innerHTML = '<div class="bt"><span>Wrace International</span><span>Issue 01 · October 2026 · Private</span></div>'
    + '<div class="bm"><b>Apartment 14</b><i></i><span>Heights 777 · Fifth floor · Plot 777, CAD Zone A07 · Parakou Street, Wuse II, Abuja</span></div>'
    + '<div class="bb"><span><b>Office</b>The District by Wrace, 83 Close Adetokunbo Ademola Cres, Abuja</span><span><b>Email</b>wraceinternational@gmail.com</span></div>';
  page('back', [back]);
  pages.slice(1, -1).forEach((p, i, rest) => { const f = document.createElement('div'); f.className = 'pfoot'; f.innerHTML = '<span>' + FOOT + '</span><span>' + String(i + 1).padStart(2, '0') + ' / ' + String(rest.length).padStart(2, '0') + '</span>'; p.appendChild(f); });
  main.innerHTML = ''; pages.forEach(p => main.appendChild(p));
  return pages.length;
})()
"""


def flatten_plans(tmp: Path) -> dict:
    out = {}
    for p in sorted((ROOT / "assets").glob("plan-*.png")):
        im = Image.open(p).convert("RGBA")
        bg = Image.new("RGB", im.size, PANEL)
        bg.paste(im, mask=im.split()[3])
        f = tmp / p.name
        bg.save(f, "PNG", optimize=True)
        out["assets/" + p.name] = f.as_uri()
    return out


async def main(out: Path):
    tmp = Path(tempfile.mkdtemp(prefix="apt14print-"))
    assets = flatten_plans(tmp)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": round(297 * MM), "height": round(210 * MM)})
        await pg.add_init_script("window.__PRINT=true;window.__assets=" + json.dumps(assets) + ";")
        await pg.goto((ROOT / "index.html").as_uri())
        await pg.add_style_tag(content=PRINT_CSS)
        n = await pg.evaluate(PRINT_JS)
        await pg.emulate_media(media="print")
        await pg.evaluate("document.fonts.ready")
        # lazy images never load off-screen: make every image eager, then wait (bounded) for them
        await pg.evaluate("[...document.images].forEach(i => { i.loading = 'eager'; })")
        await pg.evaluate("Promise.race([new Promise(r => setTimeout(r, 15000)), Promise.all([...document.images].map(i => i.complete ? 1 : new Promise(r => { i.onload = i.onerror = r; })))])")
        await pg.wait_for_timeout(400)
        await pg.pdf(path=str(out), width="297mm", height="210mm", print_background=True, prefer_css_page_size=True,
                     margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        await b.close()
    print(out, n, "pages,", out.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    asyncio.run(main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "apartment-14-heights-777.pdf"))
