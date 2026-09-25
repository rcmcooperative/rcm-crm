# Local LLM Setup

This skill needs Ollama running locally with a Qwen3 model available, via a `claude-local` profile — the same pattern used for other local-only pipelines (e.g. the DHCL deidentification skill). If you've already set this up before, most of the early steps below are just confirmation checks; step 4 covers creating it from scratch if this is a genuinely new machine.

## 1. Install Ollama (if not already installed)

```bash
brew install ollama
```

Or download from https://ollama.com if you'd rather not use Homebrew.

## 2. Start the Ollama service

```bash
ollama serve
```

Leave this running in a terminal, or set it up as a background service if you'd rather not keep a terminal open (Ollama's installer usually offers to do this for you on macOS).

## 3. Confirm/pull a Qwen3 model

Check what you already have pulled first — you very likely already have a working model from setting up `claude-local` for other work:

```bash
ollama list
```

If nothing suitable is there yet:

```bash
ollama pull qwen3:8b
```

Whatever tag actually shows up in `ollama list` — a **general-purpose Qwen3 tag, e.g. `qwen3:8b`**, confirmed working. Do not use a coder-tuned tag (e.g. `qwen-coder-local`, `qwen2.5-coder`) — see "Notes on model choice and performance" below for why this matters, not just as a preference.

## 4. Set up the claude-local profile (one-time, if not already done)

**Skip this step if `~/.claude-local/settings.json` and the `claude-local` alias already exist on this machine** — check with `cat ~/.claude-local/settings.json` and `alias claude-local` first. If either comes back empty/not found, this step creates them from scratch.

Claude Code needs two fully separate config profiles, so a cloud session and a local session never fight over the same settings file:

1. **Create the local profile directory and its settings file:**

```bash
mkdir -p ~/.claude-local
```

Then create `~/.claude-local/settings.json` with:

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "ollama",
    "ANTHROPIC_BASE_URL": "http://localhost:11434",
    "CLAUDE_CODE_ATTRIBUTION_HEADER": "0"
  },
  "model": "qwen3:8b",
  "theme": "dark"
}
```

Change `"model"` if you're using a different general-purpose Qwen3 tag than `qwen3:8b` — but do not set this to a coder-tuned tag (see "Notes on model choice and performance" at the end of this document).

2. **Make sure `~/.claude/settings.json` (the default, cloud profile) stays clean** — no `env` block, so it's never accidentally routed to Ollama:

```json
{
  "model": "claude-sonnet-4-6",
  "theme": "dark"
}
```

3. **Add both aliases to `~/.zshrc`:**

```bash
alias claude-cloud='claude --model claude-sonnet-4-6'
alias claude-local='CLAUDE_CONFIG_DIR=~/.claude-local claude'
```

4. Open a **brand-new terminal window** (or `source ~/.zshrc`) so the aliases actually exist in your shell.

**Known gotcha**: an active conda environment can inject `ANTHROPIC_BASE_URL`/`ANTHROPIC_AUTH_TOKEN` via its own activation scripts, silently routing what you thought was a cloud session to local Ollama even with a clean `settings.json`. If `/status` (see step 7) ever shows an unexpected base URL, run `conda deactivate` and check again before assuming a `settings.json` problem.

## 5. Fix the context window (one-time setup)

This is a two-part fix — both parts are needed, because Ollama and Claude Code each have their own, independent idea of how much context is available, and by default they disagree badly.

**Part A — Ollama's own context window.** Ollama's default is only **4k tokens**, far too small for this skill (Claude Code's own system prompt and tool definitions alone use several thousand tokens, before `SKILL.md`, `.claude/skills/crm-notes-extraction/references/schema.md`, and the notes file are even added). If you're running Ollama as the menu-bar app (most likely, if you've never manually run `ollama serve` yourself):

1. Click the Ollama icon in the menu bar → **Settings**.
2. Find **Context length** and drag the slider up from 4k to at least **32k** — 64k if your machine handles it comfortably.
3. Quit and reopen the app (or just confirm the setting stuck after a normal reopen — this has been confirmed to persist).

**Part B — Claude Code's assumed context window.** Separately, Claude Code doesn't recognise local model names like `qwen3:8b` (it only has built-in knowledge of Anthropic's own models), so by default it *assumes* a 200k window for any unrecognised model — which doesn't match what Ollama is actually providing, and produces a warning like:

> "qwen3:8b" is not a model this version of Claude Code recognizes, so auto-compact will keep this session within 200k tokens...

Fix this by setting `CLAUDE_CODE_MAX_CONTEXT_TOKENS` to match whatever you set in Part A, on the same `claude-local` alias definition in `~/.zshrc`:

```bash
# Local Qwen session
alias claude-local='CLAUDE_CONFIG_DIR=~/.claude-local CLAUDE_CODE_MAX_CONTEXT_TOKENS=32768 claude'
```

(`32768` = 32k, matching the Ollama slider above — keep these two numbers in agreement if you ever change one.)

**Important**: editing `~/.zshrc` alone doesn't apply the change to a terminal window that's already open. Either open a **brand-new terminal window**, or run `source ~/.zshrc` in your current one, before launching `claude-local` again. You'll know it worked because the "not a model this version recognizes" warning stops appearing at startup.

## 6. Open claude-local

From the `rcm-crm` repo root (so the skill at `.claude/skills/crm-notes-extraction/` is auto-discovered — see `.claude/skills/crm-notes-extraction/references/how-to-run.md` for why this matters):

```bash
cd <path-to-rcm-crm-repo>
claude-local
```

The remaining check below is run from inside that session.

## 7. Verify you're actually running locally

From inside your `claude-local` session:

```
/status
```

This reports which model is actually backing the session — confirm it shows your local Ollama model (e.g. `qwen3:8b` or whatever general-purpose Qwen3 tag you pulled in step 3), not a hosted Claude model, and **not a coder-tuned tag** — see "Notes on model choice and performance" below. This is a direct readout from Claude Code's own config, not something routed through the model's reasoning, so it's a more reliable check than asking the model a question about itself.

## 8. Sanity-check before trusting it on real notes

*(Adapted from the dhcl-deidentification skill's equivalent step — that version ran against synthetic participant files with a ground-truth answer key; this skill doesn't have an equivalent fixture yet.)*

Before running this skill against real, possibly-confidential meeting notes, it's worth doing a first run against a note-set you've already extracted with Claude (in a hosted chat) and comparing outputs side by side — e.g. re-run the Superbloom or CRUK-Manchester-ELNs note-sets, since both have a known-good extraction to compare against. Look specifically at:
- Did it correctly limit People to attendees only (not everyone mentioned in discussion)?
- Did it flag fields it couldn't determine, rather than guessing?
- Did it get the picklist values (`org-type`, `project-status`, `interaction-type`, `interaction-status`) right, including the exact spelling/casing from `.claude/skills/crm-notes-extraction/references/schema.md`?

If accuracy is noticeably weaker than the hosted-chat extractions, that's expected for a smaller local model — see the note on model choice below, and consider whether more fields should route to a flag rather than a guess for this particular model.

## Notes on model choice and performance

- **Use a general-purpose Qwen3 variant (e.g. `qwen3:8b`), not a coder-tuned one.** This was tested directly, not just theorised: `qwen-coder-local` (a `qwen2.5-coder` tag) reliably failed to produce a single working multi-step run — its tool calls came out as malformed JSON that Claude Code couldn't execute at all, printed as literal text instead of actually running. This matches a documented pattern from Qwen-coder models generally with Claude Code's local-model bridge, not something specific to this skill. Switching to `qwen3:8b` immediately fixed it — tool calls executed correctly and the model worked through multiple steps. If you only have a coder-tuned model pulled, pull a general-purpose Qwen3 tag before troubleshooting anything else.
- **Larger Qwen3 variants will generally do better at this extraction task** than smaller ones, at the cost of speed. Since a real notes file only needs to run once per extraction (not interactively), slower-but-more-thorough is usually the right tradeoff.
- **Even with a working model, don't expect it to independently plan "I need to write a Python script to build this xlsx."** In testing, `qwen3:8b` executed tool calls correctly but, left to its own devices, produced a shallow copy-paste of the notes rather than a genuinely structured extraction. That's why Step 4/5 of `SKILL.md` now split the task in two: the model produces a flat, fact-by-fact CSV describing what it found (deliberately as simple a format as possible — one line per fact, nothing to align or nest), and a deterministic script (`.claude/skills/crm-notes-extraction/scripts/build_workbook.py`) handles all the actual xlsx construction, formatting, and schema validation. Don't ask the model to build the xlsx directly. (An earlier version of this hand-off used nested JSON, then a wide CSV row per entity — both were found to be error-prone for a smaller model to reproduce correctly; the long/tidy fact-per-line format removes that failure mode by giving the model nothing to count or align.)
- Long note files with several meetings may need chunking if the local model struggles to hold the whole file in context while extracting carefully — not currently built into this skill's instructions, so if you notice extraction quality dropping on longer files, that's a likely next thing to add.
