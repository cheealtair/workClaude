# Local AI Setup Notes

## Table of Contents

- [Chapter 1: LLM Models vs Hardware Comparisons](#chapter-1-llm-models-vs-hardware-comparisons)
  - [Hardware](#hardware)
  - [Models](#models)
  - [Model-to-Hardware Fit](#model-to-hardware-fit)
  - [Desktop-Optimised Models (RTX 3060 12GB)](#desktop-optimised-models-rtx-3060-12gb)
  - [Additional Recommended Models (Laptop)](#additional-recommended-models-laptop)
  - [Inference Engines](#inference-engines)
  - [Claude Code](#claude-code)
  - [Recommended Architecture](#recommended-architecture)
  - [Recommended Final Setup](#recommended-final-setup)
- [Chapter 2: Setting Up Claude Code](#chapter-2-setting-up-claude-code)
  - [What you need (and what you don't)](#what-you-need-and-what-you-dont)
  - [Why a Bash shell matters (and your options on Windows)](#why-a-bash-shell-matters-and-your-options-on-windows)
  - [Step 1: Set environment variables](#step-1-set-environment-variables)
  - [Step 2: Install Claude Code](#step-2-install-claude-code)
  - [Step 3: First run](#step-3-first-run)
- [Chapter 3: Local AI Stack Setup](#chapter-3-local-ai-stack-setup)
  - [llama.cpp Installation](#llamacpp-installation)
  - [LiteLLM Proxy Setup](#litellm-proxy-setup)
    - [Switching between local and cloud models](#switching-between-local-and-cloud-models)
  - [Agentic Alternatives for Local Models](#agentic-alternatives-for-local-models)
  - [Crush — Fully Local Agentic Stack](#crush----fully-local-agentic-stack)

---

## Chapter 1: LLM Models vs Hardware Comparisons

### Hardware

| Spec | Desktop | Laptop (HP ZBook Fury 16) |
|------|---------|---------------------------|
| CPU | — | Intel Core Ultra 9 |
| GPU | RTX 3060 | RTX PRO 4000 Blackwell |
| VRAM | 12GB | 16GB |
| System RAM | 32GB | 64GB |
| Assessment | Usable but not ideal | Strong local AI workstation |

---

### Models

| Model | Type | Total / Active Params | Q4_K_M Size | Strengths |
|-------|------|----------------------|-------------|-----------|
| Gemma 4 12B | Dense | 11.9B | ~7.6 GB | Fast, good daily assistant |
| Gemma 4 26B A4B (MoE) | MoE (8/128 experts) | 25.2B / 3.8B active | ~18 GB | Efficient MoE architecture |
| Gemma 4 31B | Dense | 30.7B | ~20 GB | Highest quality Gemma 4 |
| Qwen3 30B-A3B | MoE (8/128 experts) | 30B / 3.3B active | ~18.6 GB | Strong coding, document analysis, enterprise work |
| Qwen3-Coder 30B-A3B | MoE | 30B / 3.3B active | ~19 GB | Coding-focused, 256K context |
| Qwen3 32B | Dense | 32B | ~20 GB | Strong reasoning; 40% on Aider coding benchmark (best open local) |
| Qwen 3.5 9B | Dense (hybrid DeltaNet+Attention) | 9B | ~5.7 GB | Multimodal (text+image+video), 256K context, 201 languages |
| Devstral 24B | Dense | 24B | ~14 GB | Agentic coding; 46.8% SWE-Bench; beats DeepSeek-V3 671B on coding evals. Apache 2.0. |
| DeepSeek-R1 14B (distill) | Dense (distilled) | 14.8B | ~9 GB | Reasoning/math; distilled from full R1; MIT license |
| DeepSeek-R1 8B (distill) | Dense (distilled) | 8B | ~5 GB | Lightweight reasoning; fits comfortably in 12GB VRAM |

> **Note:** The original notes referenced "Gemma 4 27B" — this model does not exist. Gemma 4 ships as 12B, 26B (MoE), and 31B (Dense). "27B" is a Gemma 3 model.
> **Note:** DeepSeek-R1 full model (671B) is not locally runnable. Only the distilled variants (8B, 14B, 32B, 70B) are practical for local use.

---

### Model-to-Hardware Fit

| Model | Q4 Size | Desktop (RTX 3060 12GB VRAM, 32GB RAM) | Laptop (RTX PRO 4000 16GB VRAM, 64GB RAM) |
|-------|---------|---------------------------------------|------------------------------------------|
| Gemma 4 12B | ~7.6 GB | Fits in VRAM — runs well | Fits in VRAM — runs well |
| Gemma 4 26B (MoE) | ~18 GB | Too large for VRAM; slow with RAM offload on 32GB | Needs partial RAM offload (~2GB spill); usable |
| Gemma 4 31B (Dense) | ~20 GB | Won't run well — exceeds VRAM + limited RAM | Needs significant RAM offload; marginal |
| Qwen3 30B-A3B | ~18.6 GB | Too large for VRAM; tight on 32GB RAM | Needs partial RAM offload; usable — lower active params help |
| Qwen3-Coder 30B-A3B | ~19 GB | Too large for VRAM; tight on 32GB RAM | Needs partial RAM offload; usable |
| Qwen3 32B | ~20 GB | Too large for VRAM; tight on 32GB RAM | Needs partial RAM offload; usable |
| Devstral 24B | ~14 GB | Exceeds VRAM; usable with RAM offload (plenty of 32GB headroom) | Fits in VRAM — runs well |
| DeepSeek-R1 14B (distill) | ~9 GB | Fits in VRAM — runs well | Fits in VRAM — runs well |
| DeepSeek-R1 8B (distill) | ~5 GB | Fits in VRAM — runs well | Fits in VRAM — runs well |
| Qwen 3.5 9B | ~5.7 GB | Fits in VRAM — runs well | Fits in VRAM — runs well |

---

### Desktop-Optimised Models (RTX 3060 12GB)

These models fit comfortably in 12GB VRAM at Q4 quantization and run fully on-GPU without RAM offloading.

| Model | Q4 Size | Strengths | Ollama tag |
|-------|---------|-----------|------------|
| Gemma 4 12B | ~7.6 GB | Fast general assistant; strong daily tasks | `gemma4:12b` |
| Qwen 3.5 9B | ~5.7 GB | Multimodal (text+image+video), 256K context, 201 languages | `qwen3.5:9b` |
| DeepSeek-R1 8B (distill) | ~5 GB | Reasoning and math; MIT license | `deepseek-r1:8b` |
| DeepSeek-R1 14B (distill) | ~9 GB | Better reasoning; still fits in 12GB VRAM | `deepseek-r1:14b` |

For the desktop, avoid models larger than ~11GB Q4 unless you are comfortable with partial RAM offloading (-ngl flag in llama.cpp controls layer split). Devstral 24B (~14GB) spills ~2GB into RAM — still functional on 32GB system RAM but not fully GPU-resident.

---

### Additional Recommended Models (Laptop)

These models fit within 16GB VRAM at Q4 quantization without offloading.

| Model | Params | Q4 Size | Best For | Why Add |
|-------|--------|---------|----------|---------|
| Devstral 24B | 24B | ~14 GB | Coding, agentic tasks | Mistral's agentic coding model; 46.8% SWE-Bench (beats DeepSeek-V3 671B on coding evals); 128K context; Apache 2.0. Fits in 16GB VRAM. Ollama: `devstral:24b` |
| DeepSeek-R1 14B | 14.8B | ~9 GB | Reasoning, math, code | Distilled from full R1; adds dedicated reasoning capability. MIT license. Also fits in RTX 3060 12GB. Ollama: `deepseek-r1:14b` |
| Qwen3 32B | 32B | ~20 GB | Reasoning, coding | Dense model; 40% on Aider coding benchmark (best open local); needs partial RAM offload even on 16GB VRAM but 64GB system RAM gives plenty of headroom |
| Qwen 3.5 9B | 9B | ~5.7 GB | General + vision + reasoning | Multimodal (text+image+video), hybrid DeltaNet architecture, 256K native context (up to 1M). Apache 2.0. |

---

### Inference Engines

| Feature | Ollama | LM Studio | llama.cpp |
|---------|--------|-----------|-----------|
| Install ease | Simplest | Desktop GUI | Command line |
| API integration | Easy, works with Open WebUI | Less configurable | Most control |
| Performance | Slight overhead | Moderate | **Highest** |
| Memory efficiency | Good | Good | **Best** |
| Best for | Quick start | Experimentation | Power users |

**Recommendation:** Use llama.cpp for maximum performance.

---

### Claude Code

Default architecture:

```
Claude Code → Anthropic API → Claude Sonnet
```

By default Claude Code does NOT use Ollama, LM Studio, or llama.cpp. Local GPU is generally not used unless explicitly configured.

---

### Recommended Architecture

| Phase | Setup | Use Cases |
|-------|-------|-----------|
| Phase 1 — Separate | Claude Code (Sonnet) | Architecture, requirements, planning, reviews |
| Phase 1 — Separate | Local Qwen3 30B | Summaries, coding, refactoring, large document processing |
| Phase 2 — Integrated | Claude Code → LiteLLM → Claude Sonnet | Single interface routing to cloud model |
| Phase 2 — Integrated | Claude Code → LiteLLM → llama.cpp → Qwen3 | Single interface routing to local model |
| Fully local (Crush) | Crush → llama.cpp → any model | Agentic coding with zero cloud dependency; native llama.cpp integration |
| Fully local (Crush via proxy) | Crush → LiteLLM → llama.cpp → any model | Agentic coding with LiteLLM as the model router (switch models without reconfiguring Crush) |

---

### Recommended Final Setup

| Component | Choice |
|-----------|--------|
| Primary model | Qwen3 30B-A3B Q4_K_M (laptop) / Gemma 4 12B or DeepSeek-R1 14B (desktop) |
| Primary engine | llama.cpp |
| Planning & architecture | Claude Code with Claude Sonnet |
| Local coding assistant (cloud) | Aider → LiteLLM → Claude Sonnet |
| Local coding assistant (offline) | Crush → llama.cpp → Devstral 24B or Qwen3 30B |
| Local heavy work | Qwen3 30B-A3B (laptop) / DeepSeek-R1 14B (desktop) |
| Optional UI | Open WebUI |
| Avoid initially | Ollama, LM Studio (less control) |
| Avoid | OpenCode (archived September 2025) |

---

## Chapter 2: Setting Up Claude Code

Claude Code is an agentic coding assistant that runs in your terminal. It reads, writes, and executes commands across entire repos. At Siemens, it routes through the SDC LLM Gateway for corporate compliance.

### What you need (and what you don't)

**Required:**

| Requirement | Where to get it | Notes |
|---|---|---|
| Request **SDC LLM Gateway** subscription | `https://sdc.siemens.cloud/products/sdc-llm-gateway` → click **Get Access** → SDC Profile → Subscriptions → **Request Access** | Usually instant. API Key visible under Subscription Details |
| Generate **code.siemens.com** Personal Access Token | `https://code.siemens.com` → User Settings → Access Tokens → scopes `read_user` and `read_repository` | Instant. Token starts with `glpat-...` — save it locally |
| **A terminal** | Any terminal: PowerShell, CMD, Bash, Zsh | Claude Code is a CLI tool — it runs in whatever shell you have |
| **Internet connection** | — | Required for API calls to SDC LLM Gateway |
| **4 GB+ RAM** | — | Minimum system requirement |

**Not required:**

| Tool | Status | Notes |
|---|---|---|
| **VS Code** | Not needed | Claude Code is a standalone terminal tool. No IDE required. |
| **Git** | Optional but recommended | Useful for version control workflows. On Windows, Git for Windows also provides a Bash shell (see below). Claude Code works without it — it falls back to PowerShell. |
| **Git Bash** | Optional | One of several ways to get a Bash shell on Windows. See next section. |

> **Approval gating** — Claude Code is rolling out by business unit. Confirm your BU is approved on the SDC LLM Gateway product page at `https://sdc.siemens.cloud/products/sdc-llm-gateway` (look for "Current approved state for Claude Code Usage") before proceeding.

### Why a Bash shell matters (and your options on Windows)

Claude Code's internal tools generate shell commands. Many use Bash idioms — pipes, `grep`, `find`, `&&` chaining, `$VAR` syntax. A Bash shell means commands work identically across macOS, Linux, and Windows. Without one, Claude Code falls back to PowerShell, which works but has different syntax rules (no `&&` operator, `$env:VAR` instead of `$VAR`, backtick escaping instead of backslash).

On macOS and Linux, Bash/Zsh is already your default shell — no action needed. On Windows, you have several options:

| Option | What it is | Recommended? | Notes |
|---|---|---|---|
| **No Bash (PowerShell only)** | Use Claude Code with its PowerShell fallback | Works fine | Simplest setup. Claude Code adapts automatically. Minor syntax differences are handled for you. |
| **Git Bash** (via Git for Windows) | MSYS2-based Bash bundled with Git | Yes — if you want Git anyway | Lightweight (~300 MB). Most common choice. Set `CLAUDE_CODE_GIT_BASH_PATH` if not auto-detected. |
| **WSL2** (Windows Subsystem for Linux) | Full Linux kernel running inside Windows | Best overall | Install Claude Code *inside* WSL2 using the Linux installer. Native Linux environment — `apt`, `grep`, `find`, proper Bash, everything. Windows folders accessible at `/mnt/c/`, `/mnt/d/`, etc. |
| **MSYS2** (standalone) | The toolkit Git Bash is built on | Yes — for power users | Includes `pacman` package manager. Point `CLAUDE_CODE_GIT_BASH_PATH` to its `bash.exe`. |
| **Cygwin** | Older POSIX compatibility layer | Not recommended | Heavy, being superseded by WSL2 in most workflows. |
| **MobaXterm** | SSH/X11 client with embedded Cygwin | No | Its Bash is sandboxed inside MobaXterm — not exposed as a system shell for other tools to call. |

**Bottom line:** If you're on Windows and want the fullest experience, WSL2 is the strongest option. If you just want to get started quickly, PowerShell alone works — you won't hit a wall.

### Step 1: Set environment variables

#### macOS / Linux / WSL2

```bash
nano ~/.zshrc    # or ~/.bashrc if using Bash
```

Add at the bottom:

```bash
# Claude Code via SDC LLM Gateway
export ANTHROPIC_API_KEY="<your-sdc-gateway-api-key>"
export ANTHROPIC_BASE_URL="https://llm.sdc.siemens.cloud"
export ANTHROPIC_MODEL="claude-sonnet-4-6@default"
export CODE_SCAN_TOKEN="<your-code-siemens-PAT>"
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS="1"
```

Replace placeholders with your real values. Save (`Ctrl+O`, `Enter`, `Ctrl+X`). Reload:

```bash
source ~/.zshrc    # or source ~/.bashrc
```

Verify:

```bash
echo $ANTHROPIC_BASE_URL
echo $ANTHROPIC_MODEL
echo "API_KEY length: ${#ANTHROPIC_API_KEY}"
```

Should print the URL, model name, and a number around 64 (the key length).

#### Windows (PowerShell)

Allow custom profile scripts (one-time):

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Press `Y` when prompted. Create the profile file:

```powershell
New-Item -ItemType Directory -Path (Split-Path $PROFILE) -Force
New-Item -ItemType File -Path $PROFILE -Force
notepad $PROFILE
```

Notepad opens. Paste:

```powershell
# Claude Code via SDC LLM Gateway
$env:ANTHROPIC_API_KEY = "<your-sdc-gateway-api-key>"
$env:ANTHROPIC_BASE_URL = "https://llm.sdc.siemens.cloud"
$env:ANTHROPIC_MODEL = "claude-sonnet-4-6@default"
$env:CODE_SCAN_TOKEN = "<your-code-siemens-PAT>"
$env:CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS = "1"
```

Replace placeholders. Save (`Ctrl+S`), close Notepad. Load:

```powershell
. $PROFILE
```

Verify:

```powershell
echo $env:ANTHROPIC_BASE_URL
echo $env:ANTHROPIC_MODEL
```

> Do **not** set `ANTHROPIC_AUTH_TOKEN`. Only `ANTHROPIC_API_KEY`. Setting both triggers an "Auth conflict" warning.

### Step 2: Install Claude Code

Run **both** commands — the first installs Claude Code, the second pulls Siemens compliance settings. Without the second command, you are not compliant.

#### macOS / Linux / WSL2

```bash
curl -fsSL https://claude.ai/install.sh | bash
curl -fsSL https://dev-boost.code.siemens.io/managed-claude-code/post-install.sh | sh
```

#### Windows (PowerShell)

```powershell
irm https://claude.ai/install.ps1 | iex
irm https://dev-boost.code.siemens.io/managed-claude-code/post-install.ps1 | iex
```

Add the install directory to your User PATH if not already there:

```powershell
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";$env:USERPROFILE\.local\bin", "User")
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
```

**Optional — if you have Git Bash and want Claude Code to use it:**

```powershell
where.exe bash
```

If it returns a path like `C:\Program Files\Git\bin\bash.exe`, Claude Code will detect it automatically. If installed but not detected, set the env var `CLAUDE_CODE_GIT_BASH_PATH` to the correct path via Windows Settings → Environment Variables.

Verify the install:

```powershell
claude --version
```

**Installation footprint:**

| Component | Location | Size |
|---|---|---|
| CLI binary | `~\.local\bin\claude.exe` | ~218 MB |
| Config & sessions | `~\.claude\` | ~13 MB (grows with usage) |
| **Total** | | **~231 MB** |

### Step 3: First run

```bash
claude "say hello and tell me which model you are running"
```

You'll be prompted in sequence:

1. **"Detected a custom API key in your environment — Yes/No"** → pick **Yes** (default is "No (recommended)" — override it; the key is correct)
2. **Theme** → either is fine
3. **Folder trust** → trust the current folder if it's a project

You should see a response identifying **Claude Sonnet 4.6** (`claude-sonnet-4-6@default`). If it works — Claude Code is installed and routing through SDC Gateway.

---

## Chapter 3: Local AI Stack Setup

### llama.cpp Installation

#### Download

llama.cpp releases: https://github.com/ggml-org/llama.cpp/releases

Extract to: `C:\llama`

#### Model

Download `Qwen3-30B-A3B-Q4_K_M.gguf` and store in: `C:\models`

#### Start Server

```powershell
cd C:\llama

.\llama-server.exe `
  -m C:\models\Qwen3-30B-A3B-Q4_K_M.gguf `
  -ngl 999 `
  -c 32768
```

#### Built-in Web UI

llama-server includes a basic chat interface — no extra install required. Once the server is running, open `http://localhost:8080` in a browser to chat with the model directly. This is **not** the same as Open WebUI below.

#### GPU Monitoring

```powershell
nvidia-smi -l 1
```

#### Optional Open WebUI (separate project, requires Docker)

Open WebUI is a separate, standalone project with a richer interface (conversation history, model switching, user accounts, etc.). It connects to llama.cpp as a backend but requires Docker to run. Not related to the built-in llama-server UI above.

```powershell
docker run -d `
  -p 3000:8080 `
  --add-host=host.docker.internal:host-gateway `
  -v open-webui:/app/backend/data `
  ghcr.io/open-webui/open-webui:main
```

- URL: http://localhost:3000
- Endpoint: http://host.docker.internal:8080

---

### LiteLLM Proxy Setup

LiteLLM is a lightweight proxy that sits between clients (like Claude Code or Crush) and model backends (cloud APIs or local servers like llama.cpp). It exposes a single OpenAI-compatible endpoint, so you can switch between local and cloud models without reconfiguring each client.

#### Why use it

| Without LiteLLM | With LiteLLM |
|-----------------|--------------|
| Claude Code → Anthropic API (cloud only) | Claude Code → LiteLLM → Anthropic API |
| Separate client for local models | Claude Code → LiteLLM → llama.cpp → Qwen3 |
| Different config per model | One endpoint, multiple backends |

#### Install

```bash
pip install 'litellm[proxy]'
```

#### Environment variables (required)

Set these as **User environment variables** via Windows Settings → System → Advanced → Environment Variables:

| Variable | Value | Purpose |
|----------|-------|---------|
| `ANTHROPIC_API_KEY` | Your SDC LLM Gateway API key | Auth for cloud models |
| `ANTHROPIC_MODEL_LITELLM` | `anthropic/claude-opus-4-6@default` | Cloud model with LiteLLM provider prefix |

> LiteLLM's `os.environ/` syntax only works when the entire value comes from the env var — you cannot mix a prefix like `anthropic/` with `os.environ/VAR`. That's why `ANTHROPIC_MODEL_LITELLM` includes the `anthropic/` prefix.

#### Config file

The config file is at `litellm_config.yaml` in the workspace root:

```yaml
model_list:
  - model_name: local-qwen3
    litellm_params:
      model: openai/Qwen3-30B-A3B-Q4_K_M
      api_base: http://localhost:8080/v1
      api_key: not-needed

  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-sonnet-4-20250514
      api_key: os.environ/ANTHROPIC_API_KEY

  - model_name: claude-opus4_siemens
    litellm_params:
      model: os.environ/ANTHROPIC_MODEL_LITELLM
      api_key: os.environ/ANTHROPIC_API_KEY
```

| Model name | Routes to | Notes |
|---|---|---|
| `local-qwen3` | llama.cpp on localhost:8080 | Requires llama.cpp server running |
| `claude-sonnet` | Anthropic API (direct) | Currently unhealthy — model ID doesn't match Siemens proxy |
| `claude-opus4_siemens` | Anthropic via Siemens SDC Gateway | Working — uses `ANTHROPIC_MODEL_LITELLM` env var |

#### Starting from scratch

**Step 1 — Start llama.cpp server** (new terminal, leave it running):

```powershell
cd C:\llama
.\llama-server.exe -m C:\models\Qwen3-30B-A3B-Q4_K_M.gguf -ngl 999 -c 32768
```

Wait for `model loaded` message (~15-30 seconds while GPU loads the 17GB model).

**Step 2 — Start LiteLLM proxy** (new terminal, leave it running):

```powershell
$env:PYTHONIOENCODING = "utf-8"
litellm --config C:\d_drive\workKW\WorkClaude\litellm_config.yaml --port 4000
```

> The `PYTHONIOENCODING=utf-8` is required on Windows — LiteLLM's startup banner contains Unicode characters that crash under the default cp1252 encoding.

Wait for `Uvicorn running on http://0.0.0.0:4000`.

**Step 3 — Verify health:**

```bash
curl http://localhost:4000/health
```

**Step 4 — Test local model:**

```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-1234" \
  -d '{"model":"local-qwen3","messages":[{"role":"user","content":"Name three planets. One sentence only."}],"max_tokens":500}'
```

**Step 5 — Test cloud model (Siemens proxy):**

```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-1234" \
  -d '{"model":"claude-opus4_siemens","messages":[{"role":"user","content":"Name three planets. One sentence only."}],"max_tokens":100}'
```

> The `Authorization: Bearer sk-1234` is a dummy token — LiteLLM proxy doesn't enforce auth by default. The real API key is in the config/env var.

Test using Powershell (not curl):  
 $env:ANTHROPIC_API_KEY  
 $response = Invoke-RestMethod -Uri "http://localhost:4000/v1/chat/completions"   -Method POST   -Headers @{ "Authorization" = "Bearer sk-1234" }   -ContentType "application/json"   -Body '{"model":"claude-opus4_siemens","messages":[{"role":"user","content":"Name three planets. One sentence only."}],"max_tokens":1000}'

$response.choices[0].message.content   
>>> The three planets are Mercury, Venus, and Earth.  

If no results, then perhaps tokens was too short.

#### Switching between local and cloud models

Once both services are running, switch models by name in the request body:

```bash
# Local Qwen3
"model": "local-qwen3"

# Cloud Claude Opus via Siemens
"model": "claude-opus4_siemens"
```

#### Performance notes

- **Qwen3 thinking mode:** Qwen3 defaults to "thinking" mode — it spends tokens on internal reasoning (`reasoning_content`) before producing the visible answer (`content`). Set `max_tokens` to 300+ for simple questions, or the response may be all reasoning with an empty answer.
- **Generation speed:** ~10 tokens/sec on RTX PRO 4000
- **Prompt caching:** Working — repeat prompts are faster

#### Debugging

```bash
export LITELLM_LOG=DEBUG    # detailed logs
export LITELLM_LOG=INFO     # normal operation
```

#### Routing Claude Code through LiteLLM → llama.cpp

The useful case here is **Claude Code → LiteLLM → llama.cpp → Qwen3** — using a local model via Claude Code instead of the Siemens cloud. By default, Claude Code uses your Windows User env vars (`ANTHROPIC_BASE_URL`, `ANTHROPIC_MODEL`) and connects directly to the Siemens SDC proxy. To route through LiteLLM instead, override `ANTHROPIC_BASE_URL` in a terminal session (session-scoped — other terminals are unaffected):

```powershell
$env:ANTHROPIC_BASE_URL = "http://localhost:4000"
$env:ANTHROPIC_MODEL = "local-qwen3"
claude "say hello and tell me which model you are running"
```

> Do NOT override `ANTHROPIC_API_KEY`. Leave your real SDC key in place — Claude Code validates the key format on startup and rejects dummy values (prompts `/login`). LiteLLM ignores the incoming auth header and uses the real key from its own config only when routing to cloud models.

**Note on earlier friction testing (2026-06-14):** Prior notes recorded two 400 errors (`structured_outputs` and `system` role formatting) when testing Claude Code → LiteLLM → Siemens proxy. That was testing the wrong path — routing Claude Code through LiteLLM back to the cloud makes no sense; you'd just connect Claude Code directly to Siemens. The errors were Siemens org policy and LiteLLM/proxy interaction issues specific to that cloud route. Their behaviour against a local llama.cpp backend is untested and likely differs — llama.cpp is more permissive about message formatting, and `structured_outputs` policy restrictions don't apply locally.

---

### Agentic Alternatives for Local Models

Claude Code is purpose-built for Anthropic models. While it can route to local models via LiteLLM, the experience is rough. These tools talk natively to OpenAI-compatible endpoints like llama.cpp — no translation layer needed.

| Tool | Type | Best For | Notes |
|------|------|----------|-------|
| **Crush** | CLI TUI (Go) | Fully local agentic coding; Claude Code alternative | By Charmbracelet. Native `llamacpp` and `litellm` provider types — no translation layer. MCP support, LSP integration, auto-discovers models. FSL-1.1-MIT (free). **Recommended for fully local setup.** |
| **Aider** | CLI (like Claude Code) | Git-aware coding: edits, commits, multi-file refactors | Closest equivalent to Claude Code for local models. Very active open-source project. New `/context` command auto-selects relevant files. |
| **Cline** | VS Code extension | Agentic coding inside VS Code | Reads/writes files, runs terminal commands. Connects to llama.cpp directly. |
| **Continue** | VS Code / JetBrains extension | Chat + autocomplete + agentic features | IDE-integrated, supports multiple backends. |
| **Qwen-Agent** | Python library | Custom agentic workflows | Alibaba's own framework for Qwen. Deepest Qwen integration (thinking mode, tool use). |
| ~~**OpenCode**~~ | ~~CLI~~ | ~~Archived~~ | **Archived September 2025.** Do not use. Crush is its successor. |

#### Example: Aider with local Qwen3

```bash
pip install aider-chat
aider --openai-api-base http://localhost:8080/v1 --openai-api-key not-needed --model openai/Qwen3-30B-A3B-Q4_K_M
```

> **Reality check:** A 30B model (even a fast MoE like Qwen3-30B-A3B) is noticeably less capable than Claude Opus for complex multi-file refactors and large codebase reasoning. These tools shine for focused tasks — quick edits, single-file work, code generation — where the model size gap matters less.

---

### Crush — Fully Local Agentic Stack

#### Software Locations — Full Stack Reference

| Component | Location | Notes |
|-----------|-----------|-------|
| llama.cpp binaries | `C:\llama\` | Includes `llama-server.exe`, CUDA DLLs |
| Model files (.gguf) | `C:\models\` | One `.gguf` file per model |
| LiteLLM config | `C:\d_drive\workKW\WorkClaude\litellm_config.yaml` | Only needed for Path B (via LiteLLM) |
| Crush config (global) | `%LOCALAPPDATA%\crush\crush.json` | Windows global config |
| Crush config (per-project) | `.crush.json` in project root | Overrides global |
| Claude Code binary | `~\.local\bin\claude.exe` | ~218 MB |
| Claude Code config & sessions | `~\.claude\` | Grows with usage |
| llama.cpp server URL | `http://localhost:8080` | Default port |
| LiteLLM proxy URL | `http://localhost:4000` | Only when using Path B |

---

Crush is a terminal-based agentic coding assistant by Charmbracelet (the makers of Charm CLI tools). It is the successor to the archived OpenCode project. Go-based TUI; supports MCP servers; integrates with LSP for code intelligence.

License: FSL-1.1-MIT (free for personal and commercial use; source-available). Fully free stack when combined with llama.cpp and open-weight models.

#### Why Crush

- Native `llamacpp` provider type — connects to llama.cpp server directly with no LiteLLM proxy needed
- Also supports `litellm` provider type for when you want LiteLLM as a model router (switch models without reconfiguring Crush)
- Auto-discovers available models from the backend
- MCP support (connect to Graph Studio, filesystem, or any MCP server)
- LSP integration (code navigation, go-to-definition)

#### Install

**Windows (winget):**

```powershell
winget install charmbracelet.crush
```

**Windows / cross-platform (npm):**

```bash
npm install -g @charmland/crush
```

**Linux / WSL2:**

```bash
curl -fsSL https://charm.sh/install | bash
```

#### Config file locations

- Per-project: `.crush.json` in the project root
- Global (Windows): `%LOCALAPPDATA%\crush\crush.json`
- Global (Linux/WSL2): `~/.config/crush/crush.json`

#### Path A: Crush → llama.cpp (direct, recommended for local-only)

No LiteLLM needed. Crush speaks directly to the llama.cpp server.

`.crush.json`:

```json
{
  "providers": {
    "llamacpp": {
      "name": "llama.cpp",
      "base_url": "http://localhost:8080",
      "type": "llamacpp"
    }
  },
  "model": "llamacpp/Devstral-22B-Q4_K_M"
}
```

Start llama.cpp first (replace model name as needed):

```powershell
cd C:\llama
.\llama-server.exe -m C:\models\Devstral-22B-Q4_K_M.gguf -ngl 999 -c 32768
```

Then start Crush in your project folder:

```bash
crush
```

Crush auto-detects the running model from llama.cpp's `/v1/models` endpoint — you may not need to set `model` explicitly if only one is loaded.

#### Models for Path A — Desktop vs Laptop

llama.cpp loads one model at a time. Choose based on your machine.

**Models that run on both machines (fit in 12GB desktop VRAM):**

| Model | Q4 Size | Notes |
|---|---|---|
| Gemma 4 12B | ~7.6 GB | Fits both cleanly |
| DeepSeek-R1 14B | ~9 GB | Good reasoning + code; fits both |
| DeepSeek-R1 8B | ~5 GB | Lightest option |
| Qwen 3.5 9B | ~5.7 GB | Fits both |

Devstral 24B (~14GB) works on both but spills ~2GB into RAM on the desktop — functional but not fully GPU-resident.

#### Downloading GGUF Models

Yes — it is as simple as going to Hugging Face and downloading the `.gguf` file directly.

1. Go to [huggingface.co](https://huggingface.co) and search for the model
2. Look for a repo that provides GGUF quantized files — usually from **bartowski** or **lmstudio-community** (reliable quantizers)
3. Download the `Q4_K_M` variant — good balance of size and quality
4. Save to `C:\models\`

**Direct searches on HuggingFace for recommended models:**

| Model | HuggingFace repo to search |
|---|---|
| DeepSeek-R1 14B | `bartowski/DeepSeek-R1-Distill-Qwen-14B-GGUF` |
| DeepSeek-R1 8B | `bartowski/DeepSeek-R1-Distill-Qwen-8B-GGUF` |
| Gemma 4 12B | `bartowski/gemma-3-12b-it-GGUF` |
| Devstral 24B | `bartowski/Devstral-Small-2505-GGUF` |
| Qwen 3.5 9B | `bartowski/Qwen2.5-7B-Instruct-GGUF` |

Download only the single `.gguf` file — no other files needed for llama.cpp.

**To switch models:** stop the server, restart with a different `-m` flag, update `model` in `.crush.json` to match.

```powershell
# Desktop -- DeepSeek-R1 14B (fits in 12GB VRAM)
.\llama-server.exe -m C:\models\DeepSeek-R1-14B-Q4_K_M.gguf -ngl 999 -c 32768

# Laptop -- Devstral 24B (fits in 16GB VRAM)
.\llama-server.exe -m C:\models\Devstral-24B-Q4_K_M.gguf -ngl 999 -c 32768
```

Update `.crush.json` model field to match:

```json
"model": "llamacpp/DeepSeek-R1-14B-Q4_K_M"
```

Crush auto-detects from `/v1/models` — if only one model is loaded you may not need to set this explicitly.

#### Path B: Crush → LiteLLM → llama.cpp (use when you want model switching)

Useful when you run multiple models via LiteLLM and want to switch between them without changing Crush's config.

`.crush.json`:

```json
{
  "providers": {
    "litellm": {
      "name": "LiteLLM proxy",
      "base_url": "http://localhost:4000",
      "type": "litellm"
    }
  },
  "model": "litellm/local-qwen3"
}
```

The `model` value must match a `model_name` entry in your `litellm_config.yaml` (e.g. `local-qwen3` or `local-devstral`).

Full chain:

```
Crush → http://localhost:4000 (LiteLLM) → http://localhost:8080/v1 (llama.cpp) → model
```

All three components are free and open source. No cloud dependency.

#### Tool calling note

Crush's tool-calling reliability depends on the model's native function-calling support. Devstral 24B and Qwen3 30B both support tool calling — prefer these for agentic tasks. Smaller or older models may produce unreliable tool call JSON. This is the same caveat as Aider.

#### Crush vs Aider vs Claude Code

| | Crush | Aider | Claude Code |
|--|-------|-------|-------------|
| Interface | TUI (interactive) | CLI (command + session) | CLI (interactive) |
| Best model | Local llama.cpp | Local or cloud | Anthropic (Claude) |
| MCP support | Yes | No | Yes |
| Git integration | Yes | Yes (core feature) | Yes |
| Cost | Free | Free | Requires API key |
| Offline capable | Yes (Path A) | Yes | No |
