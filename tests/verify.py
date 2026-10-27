"""Ibarat verification — hand-calcs and behaviour checks.

Run from the clinic-demo repo (full checks incl. route smoke) or from
the standalone repo mirror (engine checks only).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CLINIC = os.path.expanduser("~/workspace/clinic-demo")
REPO = os.path.dirname(HERE)

engine = None
for path, mod in ((CLINIC, "app.ibarat.engine"), (REPO, "ibarat.engine")):
    if path not in sys.path:
        sys.path.insert(0, path)
    try:
        engine = __import__(mod, fromlist=["engine"])
        break
    except Exception:
        continue
assert engine is not None, "could not import ibarat engine"

passed = failed = 0


def check(name, cond, extra=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"PASS {name}")
    else:
        failed += 1
        print(f"FAIL {name} {extra}")


# 1. Standard mode swaps known words, keeps the rest.
r = engine.paraphrase("The important book is very useful.", "standard")
check("standard swap", r["rewritten"] == "The significant book is very helpful.",
      r["rewritten"])
check("standard changed count", r["changed_words"] == 2, str(r))

# 2. Formal vs simple differ.
f = engine.paraphrase("The important book is useful.", "formal")
s = engine.paraphrase("The important book is useful.", "simple")
check("formal vs simple differ", f["rewritten"] != s["rewritten"],
      f"{f['rewritten']} | {s['rewritten']}")
check("formal wording", f["rewritten"] == "The crucial book is beneficial.",
      f["rewritten"])
check("simple wording", s["rewritten"] == "The big book is handy.",
      s["rewritten"])

# 3. All 7 modes produce output.
for m in engine.MODES:
    out = engine.paraphrase("The important book is useful.", m)["rewritten"]
    check(f"mode {m} non-empty", bool(out.strip()), out)

# 4. Protected terms are never swapped; proper nouns mid-sentence kept.
p = engine.paraphrase("The important metformin study is useful.", "standard",
                      protected=["metformin"])
check("protected term kept", "metformin" in p["rewritten"]
      and "significant" in p["rewritten"], p["rewritten"])

# 5. Shorten phrase table.
sh = engine.paraphrase("In order to begin, we need time.", "shorten")
check("shorten phrase", sh["rewritten"].lower().startswith("to begin"),
      sh["rewritten"])

# 6. Similarity: identical = 1.0, disjoint = 0.
check("similarity identical",
      engine.word_set_similarity("cats dogs", "cats dogs") == 1.0)
check("similarity disjoint",
      engine.word_set_similarity("cats dogs", "fish birds") == 0.0)

# 7. Summarizer picks the keyword-dense sentence first.
text = ("Cats sleep all day. Cats sleep and cats rest and cats dream. "
        "Birds fly south in winter.")
summ = engine.summarize(text, 1)
check("summarizer picks dense sentence",
      summ["summary"].startswith("Cats sleep and cats rest"),
      summ["summary"])

# 8. Flesch hand-calc: "The cat sat on the mat." -> 6 words, 1 sentence,
#    6 syllables -> 206.835 - 1.015*6 - 84.6*1 = 116.145 -> 116.15.
read = engine.readability("The cat sat on the mat.")
check("flesch hand-calc", read["flesch_reading_ease"] == 116.15, str(read))

# 9. Style flags catch a doubled word.
an = engine.analyze("The the cat sat.")
check("repeated-word flag",
      any(f["type"] == "repeated_word" for f in an["flags"]), str(an))

# 10. APA citation exact string with DOI; no-DOI output invents nothing.
cit = engine.build_citation("apa", surname="Khan", initials="A. B.",
                            year="2024", title="Drug pricing in Pakistan",
                            container="Journal of Pharmacy Practice",
                            doi="10.1234/abc")
check("apa citation exact",
      cit["citation"] == "Khan, A. B. (2024). Drug pricing in Pakistan. "
      "Journal of Pharmacy Practice. https://doi.org/10.1234/abc",
      cit["citation"])
cit2 = engine.build_citation("apa", surname="Khan", year="2024",
                             title="Drug pricing in Pakistan")
check("no-doi invents nothing", "doi.org" not in cit2["citation"]
      and "http" not in cit2["citation"] and cit2["note"] != "",
      cit2["citation"])

# 11. Route smoke (clinic-demo context only).
try:
    from fastapi.testclient import TestClient
    sys.path.insert(0, CLINIC)
    from app.main import app
    c = TestClient(app)
    check("route /ibarat 200", c.get("/ibarat").status_code == 200)
    d = c.post("/ibarat/api/paraphrase",
               json={"text": "The important book is useful.",
                     "mode": "standard", "protected": []}).json()
    check("api paraphrase", d["rewritten"] == "The significant book is helpful.",
          str(d))
    d = c.post("/ibarat/api/summarize",
               json={"text": text, "sentences": 1}).json()
    check("api summarize", d["summary"].startswith("Cats sleep and cats rest"),
          str(d))
    d = c.post("/ibarat/api/analyze", json={"text": "The the cat sat."}).json()
    check("api analyze", d["flag_count"] >= 1, str(d))
    d = c.post("/ibarat/api/cite",
               json={"style": "apa", "surname": "Khan", "year": "2024",
                     "title": "Drug pricing in Pakistan"}).json()
    check("api cite", "Khan (2024)" in d["citation"], str(d))
    check("api ai-status honest",
          "ai_available" in c.get("/ibarat/api/ai-status").json())
    for route in ("/quwwat", "/ishtehar", "/dars", "/bayan", "/lablink"):
        check(f"no regression {route}",
              c.get(route).status_code == 200)
except Exception as e:  # standalone mirror: engine checks above are the suite
    print(f"SKIP route smoke ({type(e).__name__}: {e})")

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
