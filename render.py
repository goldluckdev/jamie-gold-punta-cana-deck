import os
from playwright.sync_api import sync_playwright

OUT = "/home/aiciv/state/edge-output/deck-punta-cana-contest-2026-09-12"
DECK = os.path.join(OUT, "deck-contest.html")
QADIR = os.path.join(OUT, "qa")
PDF = os.path.join(OUT, "PuntaCana-Contest-Deck-DRAFT.pdf")
os.makedirs(QADIR, exist_ok=True)
ARGS = ["--single-process", "--no-sandbox", "--disable-dev-shm-usage"]

with sync_playwright() as p:
    browser = p.chromium.launch(args=ARGS)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    page.goto("file://" + DECK, wait_until="networkidle", timeout=180000)
    page.wait_for_timeout(1500)
    n = page.eval_on_selector_all(".slide", "els => els.length")
    print("slides:", n)
    for idx in range(1, n + 1):
        el = page.query_selector(f".slide:nth-of-type({idx})")
        out = os.path.join(QADIR, f"slide-{idx:02d}.png")
        el.screenshot(path=out)
        print("wrote", out)
    page.pdf(path=PDF, width="1920px", height="1080px", print_background=True,
             margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
    print("PDF:", PDF)
    browser.close()
print("DONE")
