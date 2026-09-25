# Local LLM Setup

**Currently not needed.** This skill's only LLM-dependent step (summarising channel discussion into Interaction notes) is parked pending a community conversation about the use of LLMs on their data — see `SKILL.md`'s "Parked features". The present pipeline is pure Python; nothing in it calls a model, local or hosted. This file is kept for when that step is reinstated, so the setup work isn't lost — don't act on it in the meantime.

---

This skill can run against Ollama with a Qwen3 model, via a `claude-local` profile — the same pattern used for other local-only pipelines on this machine (e.g. `crm-notes-extraction`, the DHCL deidentification skill). If you've set this up before for one of those, most of the steps below are just confirmation checks; step 4 covers creating it from scratch if this is a genuinely new machine.

**Why local at all for this skill specifically**: the Slack export this skill reads is currently scoped to public channels only (see `references/slack-export-format.md`), which is a lower-sensitivity input than the meeting notes `crm-notes-extraction` handles. Running locally isn't strictly forced by confidentiality the way it is for that skill — but it's still the more privacy-conscious default, consistent with how RCM Cooperative treats data generally, and costs nothing extra once the profile below exists. If a future version of this skill reads private-channel data (see the "Scope note" in `SKILL.md`), local execution stops being optional.

## 1. Install Ollama (if not already installed)

```bash
brew install ollama
```

Or download from https://ollama.com if you'd rather not use Homebrew.

## 2. Start the Ollama service

```bash
ollama serve
```

Leave this running in a terminal, or set it up as a background service (Ollama's macOS installer usually offers to do this for you).

## 3. Confirm/pull a Qwen3 model

Check what's already pulled first — likely already set up from other local pipelines on this machine:

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

**Part A — Ollama's own context window.** Ollama's default is only **4k tokens**, far too small for this skill (Claude Code's own system prompt and tool definitions alone use several thousand tokens, before `SKILL.md`, `.claude/skills/crm-slack-extraction/references/schema.md`, and a Slack export's channel message text are even added — a busy channel's day-files can add up quickly). If you're running Ollama as the menu-bar app (most likely, if you've never manually run `ollama serve` yourself):

1. Click the Ollama icon in the menu bar → **Settings**.
2. Find **Context length** and drag the slider up from 4k to at least **32k** — 64k if your machine handles it comfortably, and worth the higher end for this skill specifically if any target channel has a long message history.
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

From the `rcm-crm` repo root (so the skill at `.claude/skills/crm-slack-extraction/` is auto-discovered — see `references/how-to-run.md` for why this matters):

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

## 8. Sanity-check before trusting it on a real channel

This skill doesn't yet have an established ground-truth comparison the way `crm-notes-extraction` does (that skill can compare against note-sets already extracted via hosted Claude). Until a first trusted run exists to compare against, the practical substitute is: pick one small, already-familiar channel, read through its messages yourself first, and form your own view of who was active and what was discussed — then run the skill on that same channel and compare. Look specifically at:

- Did `people-participants` match the channel's actual membership (Step 1 of `SKILL.md` — this part is deterministic, so it should match exactly, not approximately)?
- Do the `lead-signals-<name>.csv` counts look plausible against your own read of who was most active?
- Did the Step 4 model-written summary accurately reflect what the channel discussed, without inventing detail or missing anything you'd consider central?
- Did it flag genuinely ambiguous cases (unmatched Slack users, unmapped channels) rather than guessing?

Once you're satisfied with one channel's output, that becomes your own baseline for judging future runs — worth keeping the compared channel's output on file for that purpose.

If accuracy is noticeably weaker than expected, that's plausibly the smaller local model rather than the pipeline — see below, and consider whether more fields should route to a flag rather than a guess for this particular model.

## Notes on model choice and performance

- **Use a general-purpose Qwen3 variant (e.g. `qwen3:8b`), not a coder-tuned one.** This was tested directly (on `crm-notes-extraction`, the first skill built on this pattern), not just theorised: `qwen-coder-local` (a `qwen2.5-coder` tag) reliably failed to produce a single working multi-step run — its tool calls came out as malformed JSON that Claude Code couldn't execute at all, printed as literal text instead of actually running. Switching to `qwen3:8b` immediately fixed it. If you only have a coder-tuned model pulled, pull a general-purpose Qwen3 tag before troubleshooting anything else.
- **Larger Qwen3 variants will generally do better** at the Step 4 summarisation task than smaller ones, at the cost of speed. Since a real run only needs to happen once per extraction, slower-but-more-thorough is usually the right tradeoff.
- **Even with a working model, don't expect it to independently plan the full pipeline.** Left to its own devices, a smaller model may skip straight to writing prose rather than running `parse_slack_export.py` first and following the CSV hand-off format. This is why `SKILL.md` spells out Steps 0–5 explicitly and in order — be explicit in your prompt (see `references/how-to-run.md`) rather than relying on a vague natural-language request.
- A channel with a long, busy message history may need chunking if the local model struggles to hold the whole thing in context for the Step 4 summary — not currently built into this skill's instructions; if you notice summary quality dropping on very active channels, that's a likely next thing to add.
