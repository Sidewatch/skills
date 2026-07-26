# Sidewatch skill catalog

The curated list of agent-skill repositories shown in [Sidewatch](https://github.com/Sidewatch)'s
**Skills** pane, plus the job that keeps its star counts current.

`skills.json` also ships **inside the app**, so the pane works offline and with no network access
at all. This copy is an optional overlay: the app fetches it at most once a day, conditionally
(ETag), only if you turn *Check for catalog updates* on in Settings.

## Adding a skill

Open a PR editing `CURATED` in `refresh-skills.py`. Curation is a pull request, not a feed — the
list is small and hand-picked on purpose.

Sidewatch never installs a skill. It shows the install command in full and you run it yourself, in
your own terminal. A skill is executable instruction for an agent with filesystem access, so the
human stays in the loop by construction.

## How the numbers stay current

A scheduled workflow re-reads each repo's stars, description, licence and last push from the GitHub
API and commits the result. The app therefore fetches exactly **one** file and never calls the API
itself — unauthenticated that is 60 requests/hour, which a repo list would exhaust on first paint,
and a token would mean an account.

The script refuses to publish a partial catalog: if any repo fails to resolve, nothing is written,
so a bad run can't silently delete entries.

## Licence

MIT — see [LICENSE](LICENSE).
