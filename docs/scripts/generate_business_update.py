#!/usr/bin/env python3
import os, argparse, json, datetime, re

def load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def append_markdown(path, block):
    with open(path, "a", encoding="utf-8") as f:
        f.write("\n\n" + block + "\n")

def heuristic(diff):
    points, impact, breaking = [], [], False

    # Gratisversand-Schwelle erkennen
    old = re.search(r"^-\s*FREE_SHIPPING_THRESHOLD\s*=\s*([0-9.]+)", diff, re.M)
    new = re.search(r"^\+\s*FREE_SHIPPING_THRESHOLD\s*=\s*([0-9.]+)", diff, re.M)
    if new:
        n = float(new.group(1))
        if old and old.group(1) != new.group(1):
            o = float(old.group(1))
            direction = "lowered" if n < o else "increased"
            points.append(f"Free-shipping threshold {direction} from €{o:.2f} to €{n:.2f}.")
            impact.append("May affect conversion rate and shipping costs.")
        else:
            points.append(f"Free-shipping threshold set to €{n:.2f}.")

    # Mitglieder-Rabatt erkennen
    if re.search(r"calculate_discount\(.+is_member", diff):
        points.append("Introduced member-specific discount.")
        impact.append("Improves loyalty value; affects checkout messaging.")
    if re.search(r"\b0\.8\b", diff):
        points.append("Members receive 20% discount.")
    if re.search(r"\b0\.9\b", diff):
        points.append("Non-members retain 10% discount.")

    if not points:
        points.append("Minor internal changes; no obvious business impact.")
        impact.append("No user-visible change detected.")

    return {
        "summary": " ".join(points),
        "impact":  " ".join(impact),
        "breaking_change": breaking,
        "affected_endpoints": []
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--diff-file", required=True)
    ap.add_argument("--business-md", default="docs/business_updates.md")
    ap.add_argument("--proposals_json", default="docs/proposals.json")
    ap.add_argument("--pr_url", default="")
    ap.add_argument("--pr_number", default="")
    ap.add_argument("--pr_comment_out", default="pr_comment.md")
    args = ap.parse_args()

    diff = load_text(args.diff_file)
    data = heuristic(diff)  # <- hier könnte später optional ein LLM aufgerufen werden

    ts = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    md_block = f"""### Business Update – {ts}

**What changed**  
{data['summary']}

**Impact**  
{data['impact']}

**Risk**  
{"⚠️ Breaking change" if data["breaking_change"] else "No breaking change"}
"""

    # 1) Doku ergänzen (dieser Commit geht in einen separaten Docs-PR)
    append_markdown(args.business_md, md_block)

    # 2) proposals.json (für Lovable Dashboard) – aktuellen Vorschlag anhängen
    proposals = []
    if os.path.exists(args.proposals_json):
        try:
            proposals = json.loads(load_text(args.proposals_json))
        except Exception:
            proposals = []

    proposals.append({
        "summary": data["summary"],
        "impact": data["impact"],
        "breaking_change": data["breaking_change"],
        "affected_endpoints": data.get("affected_endpoints", []),
        "pr_html_url": args.pr_url,
        "docs_pr_html_url": "",   # wird nach dem Erstellen des Docs-PRs ergänzt
        "pr_number": args.pr_number
    })
    save_json(args.proposals_json, proposals)

    # 3) PR-Kommentartext erzeugen (wird im Original-PR gepostet)
    pr_comment = f"""🤖 **Business doc suggestion based on code diff**

**What changed**  
{data['summary']}

**Impact**  
{data['impact']}

**Risk**  
{"⚠️ Breaking change" if data["breaking_change"] else "No breaking change"}

**Docs will be proposed in a separate PR.**
"""
    with open(args.pr_comment_out, "w", encoding="utf-8") as f:
        f.write(pr_comment)

    print("OK")

if __name__ == "__main__":
    main()
