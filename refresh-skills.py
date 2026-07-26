#!/usr/bin/env python3
"""Re-bake Resources/skills.json with current GitHub metadata.

The app fetches this ONE file. It never calls the GitHub API itself: unauthenticated API
access is 60 requests/hour per IP, so a per-repo fetch would burn the budget on first paint
and show zeros — and an API token would mean an account, which is the thing Sidewatch does
not want. Baking the numbers here moves that cost to CI, once a day, for everyone.

Curation lives in CURATED below: adding a skill is a pull request, not a feed.
"""
import json, os, subprocess, sys, datetime

CURATED = [
    # (repo, display name, category)
    ("anthropics/skills",                    "Anthropic Skills",                  "Collections"),
    ("obra/superpowers",                     "Superpowers",                       "Frameworks"),
    ("nextlevelbuilder/ui-ux-pro-max-skill", "UI/UX Pro Max",                     "Design"),
    ("ayghri/i-have-adhd",                   "I Have ADHD",                       "Output style"),
    ("UditAkhourii/adhd",                    "ADHD (tree-of-thought)",            "Reasoning"),
    ("ravila4/claude-adhd-skills",           "Claude ADHD Skills",                "Output style"),
    ("hesreallyhim/awesome-claude-code",     "Awesome Claude Code",               "Collections"),
    ("ComposioHQ/awesome-claude-skills",     "Awesome Claude Skills (Composio)",  "Collections"),
    ("travisvn/awesome-claude-skills",       "Awesome Claude Skills (travisvn)",  "Collections"),
    ("karanb192/awesome-claude-skills",      "Awesome Claude Skills (karanb192)", "Collections"),
]

def fetch(repo):
    r = subprocess.run(["gh", "api", f"repos/{repo}", "--jq",
                        '{s:.stargazers_count,d:.description,p:.pushed_at,l:.license.spdx_id}'],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"::warning::skipping {repo}: {r.stderr.strip()}", file=sys.stderr)
        return None
    return json.loads(r.stdout)

def main():
    skills = []
    for repo, name, category in CURATED:
        meta = fetch(repo)
        if meta is None:
            continue
        skills.append({
            "repo": repo,
            "name": name,
            "summary": (meta.get("d") or "").strip(),
            "category": category,
            # Clone into the PROJECT's skills dir, not the user's global one: a skill is
            # executable instruction for an agent, and scoping it to one repo keeps a trial
            # from silently applying everywhere.
            "install": f"git clone https://github.com/{repo} .claude/skills/{repo.split('/')[1]}",
            "stars": meta["s"],
            "updated": (meta.get("p") or "")[:10] or None,
            "license": meta.get("l"),
        })
    # A PARTIAL failure is just as bad as a total one: publishing a catalog with some entries
    # missing silently deletes them for every user on the next refresh. Only a complete run
    # may be published.
    if len(skills) != len(CURATED):
        missing = {repo for repo, _, _ in CURATED} - {s["repo"] for s in skills}
        print(f"::error::resolved {len(skills)}/{len(CURATED)} repos; refusing to publish a "
              f"partial catalog. Missing: {sorted(missing)}", file=sys.stderr)
        return 1
    out = {"version": 1,
           "generated": datetime.date.today().isoformat(),
           "skills": skills}
    path = os.path.join(os.path.dirname(__file__), "skills.json")
    with open(path, "w") as f:
        f.write(json.dumps(out, indent=2) + "\n")
    print(f"wrote {len(skills)} entries")
    return 0

if __name__ == "__main__":
    sys.exit(main())
