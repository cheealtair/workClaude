---
title: "Local AI Setup Notes"
subtitle: "A guide to setting up local LLM inference and agentic workflows"
author: "chee"
date: "2026-08-16"
subject: "Local AI setup, Claude Code, llama.cpp, Crush"
lang: "en"
numbersections: true
colorlinks: true
linkcolor: blue
titlepage: true
titlepage-color: "108000"
titlepage-text-color: "FFFFFF"
titlepage-rule-color: "66BF66"
fontsize: 11pt
geometry: "margin=2.5cm"
---

# Local AI Setup Notes

<!-- START TOC -->

- [Chapter 1: LLM Models vs Hardware Comparisons](#chapter-1-llm-models-vs-hardware-comparisons)
  - [[DATA] 1.1 Hardware Specifications](#[data]-11-hardware-specifications)
  - [[DATA] 1.2 Models Overview](#[data]-12-models-overview)
  - [[INTEGRATION] 1.3 Model-to-Hardware Fit](#[integration]-13-model-to-hardware-fit)
  - [[RECOMMENDATION] 1.4 Desktop-Optimised Models (RTX 3060 12GB)](#[recommendation]-14-desktop-optimised-models-rtx-3060-12gb)
  - [[RECOMMENDATION] 1.5 Additional Recommended Models (Laptop)](#[recommendation]-15-additional-recommended-models-laptop)
  - [[INTEGRATION] 1.6 Inference Engines](#[integration]-16-inference-engines)
  - [[INTEGRATION] 1.7 Claude Code Integration](#[integration]-17-claude-code-integration)
  - [[ARCHITECTURE] 1.8 Recommended Architecture](#[architecture]-18-recommended-architecture)
  - [[RECOMMENDATION] 1.9 Recommended Final Setup](#[recommendation]-19-recommended-final-setup)
- [Chapter 2: Setting Up Claude Code](#chapter-2-setting-up-claude-code)
  - [[REQUIREMENTS] 2.1 What You Need (and What You Don't)](#[requirements]-21-what-you-need-and-what-you-dont)
  - [[INTEGRATION] 2.2 Why a Bash Shell Matters (and Your Options on Windows)](#[integration]-22-why-a-bash-shell-matters-and-your-options-on-windows)
  - [[CONFIG] 2.3 Step 1: Set Environment Variables](#[config]-23-step-1-set-environment-variables)
  - [[INSTALL] 2.4 Step 2: Install Claude Code](#[install]-24-step-2-install-claude-code)
  - [[USAGE] 2.5 Step 3: First Run](#[usage]-25-step-3-first-run)
- [Chapter 3: Local AI Stack Setup](#chapter-3-local-ai-stack-setup)
  - [[INSTALL] 3.1 llama.cpp Installation](#[install]-31-llamacpp-installation)
  - [[INTEGRATION] 3.2 LiteLLM Proxy Setup](#[integration]-32-litellm-proxy-setup)
  - [[ALTERNATIVES] 3.3 Agentic Alternatives for Local Models](#[alternatives]-33-agentic-alternatives-for-local-models)
  - [[INSTALL] 3.4 Crush — Fully Local Agentic Stack](#[install]-34-crush---fully-local-agentic-stack)

<!-- END TOC -->

## Chapter 1: LLM Models vs Hardware Comparisons

This chapter provides a comprehensive overview of local LLM models and their compatibility with different hardware configurations. It covers model specifications, performance characteristics, inference engines, and recommendations for both desktop and laptop setups. The goal is to help you choose the right models and tools for your specific hardware constraints while maximizing performance and usability.

### [DATA] 1.1 Hardware Specifications

This section documents the hardware configurations used for testing and development. Two systems were evaluated: a desktop workstation and a high-end laptop.

| Spec | Desktop | Laptop (HP ZBook Fury 16) |
|------|---------|---------------------------|
| CPU | — | Intel Core Ultra 9 |
| GPU | RTX 3060 | RTX PRO 4000 Blackwell |
| VRAM | 12GB | 16GB |
| System RAM | 32GB | 64GB |
| Assessment | Usable but not ideal | Strong local AI workstation *(defined)*

### [DATA] 1.2 Models Overview

This table lists all models discussed in this guide, their architecture types, parameter counts, and key strengths. All sizes are at Q4_K_M quantization unless otherwise noted.

| Model | Type | Total / Active Params | Q4_K_M Size | Strengths |
|-------|------|----------------------|-------------|-----------|
| Gemma 4 12B | Dense | 11.9B | ~7.6 GB | Fast, good daily assistant *(defined)* |
| Gemma 4 26B A4B (MoE) | MoE (8/128 experts) | 25.2B / 3.8B active | ~18 GB | Efficient MoE architecture *(defined)* |
| Gemma 4 31B | Dense | 30.7B | ~20 GB | Highest quality Gemma 4 *(defined)* |
| Qwen3 30B-A3B | MoE (8/128 experts) | 30B / 3.3B active | ~18.6 GB | Strong coding, document analysis, enterprise work *(defined)* |
| Qwen3-Coder 30B-A3B | MoE | 30B / 3.3B active | ~19 GB | Coding-focused, 256K context *(defined)* |
| Qwen3 32B | Dense | 32B | ~20 GB | Strong reasoning; 40% on Aider coding benchmark (best open local) *(defined)* |
| Qwen 3.5 9B | Dense (hybrid DeltaNet+Attention) | 9B | ~5.7 GB | Multimodal (text+image+video), 256K context, 201 languages *(defined)* |
| Devstral 24B | Dense | 24B | ~14 GB | Agentic coding; 46.8% SWE-Bench; beats DeepSeek-V3 671B on coding evals. Apache 2.0. *(defined)* |
| DeepSeek-R1 14B (distill) | Dense (distilled) | 14.8B | ~9 GB | Reasoning/math; distilled from full R1; MIT license *(defined)* |
| DeepSeek-R1 8B (distill) | Dense (distilled) | 8B | ~5 GB | Lightweight reasoning; fits comfortably in 12GB VRAM *(defined)* |

**Important Notes:**

- The original notes referenced "Gemma 4 27B" — this model does not exist. Gemma 4 ships as 12B, 26B (MoE), and 31B (Dense). "27B" is a Gemma 3 model.
- DeepSeek-R1 full model (671B) is not locally runnable. Only the distilled variants (8B, 14B, 32B, 70B) are practical for local use.

### [INTEGRATION] 1.3 Model-to-Hardware Fit

This matrix shows how each model performs on the two hardware configurations. VRAM-resident models run faster and more efficiently than those requiring RAM offload.

| Model | Q4 Size | Desktop (RTX 3060 12GB VRAM, 32GB RAM) | Laptop (RTX PRO 4000 16GB VRAM, 64GB RAM) |
|-------|---------|---------------------------------------|------------------------------------------|
| Gemma 4 12B | ~7.6 GB | Fits in VRAM — runs well *(defined)* | Fits in VRAM — runs well *(defined)* |
| Gemma 4 26B (MoE) | ~18 GB | Too large for VRAM; slow with RAM offload on 32GB | Needs partial RAM offload (~2GB spill); usable *(in-progress)* |
| Gemma 4 31B (Dense) | ~20 GB | Won't run well — exceeds VRAM + limited RAM | Needs significant RAM offload; marginal *(pending)* |
| Qwen3 30B-A3B | ~18.6 GB | Too large for VRAM; tight on 32GB RAM | Needs partial RAM offload; usable — lower active params help *(in-progress)* |
| Qwen3-Coder 30B-A3B | ~19 GB | Too large for VRAM; tight on 32GB RAM | Needs partial RAM offload; usable *(in-progress)* |
| Qwen3 32B | ~20 GB | Too large for VRAM; tight on 32GB RAM | Needs partial RAM offload; usable *(in-progress)* |
| Devstral 24B | ~14 GB | Exceeds VRAM; usable with RAM offload (plenty of 32GB headroom) | Fits in VRAM — runs well *(defined)* |
| DeepSeek-R1 14B (distill) | ~9 GB | Fits in VRAM — runs well *(defined)* | Fits in VRAM — runs well *(defined)* |
| DeepSeek-R1 8B (distill) | ~5 GB | Fits in VRAM — runs well *(defined)* | Fits in VRAM — runs well *(defined)* |
| Qwen 3.5 9B | ~5.7 GB | Fits in VRAM — runs well *(defined)* | Fits in VRAM — runs well *(defined)* |

### [RECOMMENDATION] 1.4 Desktop-Optimised Models (RTX 3060 12GB)

These models fit comfortably in 12GB VRAM at Q4 quantization and run fully on-GPU without RAM offloading, providing optimal performance for desktop use.

| Model | Q4 Size | Strengths | Ollama tag |
|-------|---------|-----------|------------|
| Gemma 4 12B | ~7.6 GB | Fast general assistant; strong daily tasks | `gemma4:12b` *(defined)* |
| Qwen 3.5 9B | ~5.7 GB | Multimodal (text+image+video), 256K context, 201 languages | `qwen3.5:9b` *(defined)* |
| DeepSeek-R1 8B (distill) | ~5 GB | Reasoning and math; MIT license | `deepseek-r1:8b` *(defined)* |
| DeepSeek-R1 14B (distill) | ~9 GB | Better reasoning; still fits in 12GB VRAM | `deepseek-r1:14b` *(defined)* |

For the desktop, avoid models larger than ~11GB Q4 unless you are comfortable with partial RAM offloading. The `-ngl` flag in llama.cpp controls layer split between GPU and CPU. Devstral 24B (~14GB) spills approximately 2GB into RAM — still functional on 32GB system RAM but not fully GPU-resident.

### [RECOMMENDATION] 1.5 Additional Recommended Models (Laptop)

These models fit within 16GB VRAM at Q4 quantization without offloading, making them ideal for the laptop configuration.

| Model | Params | Q4 Size | Best For | Why Add |
|-------|--------|---------|----------|---------|
| Devstral 24B | 24B | ~14 GB | Coding, agentic tasks | Mistral's agentic coding model; 46.8% SWE-Bench (beats DeepSeek-V3 671B on coding evals); 128K context; Apache 2.0. Fits in 16GB VRAM. Ollama: `devstral:24b` *(defined)* |
| DeepSeek-R1 14B | 14.8B | ~9 GB | Reasoning, math, code | Distilled from full R1; adds dedicated reasoning capability. MIT license. Also fits in RTX 3060 12GB. Ollama: `deepseek-r1:14b` *(defined)* |
| Qwen3 32B | 32B | ~20 GB | Reasoning, coding | Dense model; 40% on Aider coding benchmark (best open local); needs partial RAM offload even on 16GB VRAM but 64GB system RAM gives plenty of headroom *(in-progress)* |
| Qwen 3.5 9B | 9B | ~5.7 GB | General + vision + reasoning | Multimodal (text+image+video), hybrid DeltaNet architecture, 256K native context (up to 1M). Apache 2.0. *(defined)* |

### [INTEGRATION] 1.6 Inference Engines

Comparison of popular inference engines for running local LLMs:

| Feature | Ollama | LM Studio | llama.cpp |
|---------|--------|-----------|-----------|
| Install ease | Simplest | Desktop GUI | Command line *(defined)* |
| API integration | Easy, works with Open WebUI | Less configurable | Most control *(defined)* |
| Performance | Slight overhead | Moderate | **Highest** *(defined)* |
| Memory efficiency | Good | Good | **Best** *(defined)* |
| Best for | Quick start | Experimentation | Power users *(defined)* |

**Recommendation:** Use llama.cpp for maximum performance and memory efficiency.

### [INTEGRATION] 1.7 Claude Code Integration

By default, Claude Code routes through the Anthropic API to access Claude Sonnet models. Local GPU inference is generally not used unless explicitly configured via environment variables or LiteLLM proxy.

Default architecture:
```
Claude Code → Anthropic API → Claude Sonnet
```

### [ARCHITECTURE] 1.8 Recommended Architecture

This table outlines four deployment phases with increasing levels of integration between cloud and local models.

| Phase | Setup | Use Cases |
|-------|-------|-----------|
| Phase 1 — Separate | Claude Code (Sonnet) | Architecture, requirements, planning, reviews *(defined)* |
| Phase 1 — Separate | Local Qwen3 30B | Summaries, coding, refactoring, large document processing *(defined)* |
| Phase 2 — Integrated | Claude Code → LiteLLM → Claude Sonnet | Single interface routing to cloud model *(pending)* |
| Phase 2 — Integrated | Claude Code → LiteLLM → llama.cpp → Qwen3 | Single interface routing to local model *(pending)* |
| Fully local (Crush) | Crush → llama.cpp → any model | Agentic coding with zero cloud dependency; native llama.cpp integration *(defined)* |
| Fully local (Crush via proxy) | Crush → LiteLLM → llama.cpp → any model | Agentic coding with LiteLLM as the model router (switch models without reconfiguring Crush) *(pending)* |

### [RECOMMENDATION] 1.9 Recommended Final Setup

This is the recommended configuration for a balanced setup leveraging both cloud and local capabilities:

| Component | Choice |
|-----------|--------|
| Primary model | Qwen3 30B-A3B Q4_K_M (laptop) / Gemma 4 12B or DeepSeek-R1 14B (desktop) *(defined)* |
| Primary engine | llama.cpp *(defined)* |
| Planning & architecture | Claude Code with Claude Sonnet *(defined)* |
| Local coding assistant (cloud) | Aider → LiteLLM → Claude Sonnet *(pending)* |
| Local coding assistant (offline) | Crush → llama.cpp → Devstral 24B or Qwen3 30B *(defined)* |
| Local heavy work | Qwen3 30B-A3B (laptop) / DeepSeek-R1 14B (desktop) *(defined)* |
| Optional UI | Open WebUI *(pending)* |
| Avoid initially | Ollama, LM Studio (less control) *(pending)* |
| Avoid | OpenCode (archived September 2025) *(validated)* |

\newpage

## Chapter 2: Setting Up Claude Code

\newpage

Claude Code is an agentic coding assistant that runs in your terminal. It reads, writes, and executes commands across entire repositories. At [YOUR_ORG], it routes through the [Corporate LLM Gateway] for corporate compliance. This chapter provides step-by-step instructions for installation and configuration.

### [REQUIREMENTS] 2.1 What You Need (and What You Don't)

The following table lists required versus optional dependencies for Claude Code setup:

**Required Dependencies:**

| Requirement | Where to get it | Notes |
|---|---|---|
| Request **[Corporate LLM Gateway]** subscription | `[YOUR_ORG_URL]/products/[gateway-name]` → click **Get Access** → [Profile] → Subscriptions → **Request Access** | Usually instant. API Key visible under Subscription Details *(defined)* |
| Generate **[dev-platform].[YOUR_ORG].com** Personal Access Token | `https://[dev-platform].[YOUR_ORG].com` → User Settings → Access Tokens → scopes `read_user` and `read_repository` | Instant. Token starts with `glpat-...` — save it locally *(defined)* |
| **A terminal** | Any terminal: PowerShell, CMD, Bash, Zsh | Claude Code is a CLI tool — it runs in whatever shell you have *(defined)* |
| **Internet connection** | — | Required for API calls to [Corporate LLM Gateway] *(defined)* |
| **4 GB+ RAM** | — | Minimum system requirement *(defined)* |

**Optional Dependencies:**

| Tool | Status | Notes |
|---|---|---|
| **VS Code** | Not needed | Claude Code is a standalone terminal tool. No IDE required. *(validated)* |
| **Git** | Optional but recommended | Useful for version control workflows. On Windows, Git for Windows also provides a Bash shell (see below). Claude Code works without it — it falls back to PowerShell. *(pending)* |
| **Git Bash** | Optional | One of several ways to get a Bash shell on Windows. See next section. *(pending)* |

> **Approval gating** — Claude Code is rolling out by business unit. Confirm your BU is approved on the [Corporate LLM Gateway] product page at `[YOUR_ORG_URL]/products/[gateway-name]` (look for "Current approved state for Claude Code Usage") before proceeding.

### [INTEGRATION] 2.2 Why a Bash Shell Matters (and Your Options on Windows)

Claude Code's internal tools generate shell commands that use Bash idioms — pipes, `grep`, `find`, `&&` chaining, `$VAR` syntax. A Bash shell means commands work identically across macOS, Linux, and Windows. Without one, Claude Code falls back to PowerShell, which works but has different syntax rules: no `&&` operator, `$env:VAR` instead of `$VAR`, backtick escaping instead of backslash.

On macOS and Linux, Bash/Zsh is already your default shell — no action needed. On Windows, you have several options:

| Option | What it is | Recommended? | Notes |
|---|---|---|---|
| **No Bash (PowerShell only)** | Use Claude Code with its PowerShell fallback | Works fine | Simplest setup. Claude Code adapts automatically. Minor syntax differences are handled for you. *(validated)* |
| **Git Bash** (via Git for Windows) | MSYS2-based Bash bundled with Git | Yes — if you want Git anyway | Lightweight (~300 MB). Most common choice. Set `CLAUDE_CODE_GIT_BASH_PATH` if not auto-detected. *(pending)* |
| **WSL2** (Windows Subsystem for Linux) | Full Linux kernel running inside Windows | Best overall | Install Claude Code *inside* WSL2 using the Linux installer. Native Linux environment — `apt`, `grep`, `find`, proper Bash, everything. Windows folders accessible at `/mnt/c/`, `/mnt/d/`, etc. *(recommended)* |
| **MSYS2** (standalone) | The toolkit Git Bash is built on | Yes — for power users | Includes `pacman` package manager. Point `CLAUDE_CODE_GIT_BASH_PATH` to its `bash.exe`. *(pending)* |
| **Cygwin** | Older POSIX compatibility layer | Not recommended | Heavy, being superseded by WSL2 in most workflows. *(avoid)* |
| **MobaXterm** | SSH/X11 client with embedded Cygwin | No | Its Bash is sandboxed inside MobaXterm — not exposed as a system shell for other tools to call. *(avoid)* |

**Bottom line:** If you're on Windows and want the fullest experience, WSL2 is the strongest option. If you just want to get started quickly, PowerShell alone works — you won't hit a wall.

### [CONFIG] 2.3 Set Environment Variables

#### macOS / Linux / WSL2

Open your shell configuration file and add the following environment variables:

```bash
nano ~/.zshrc    # or ~/.bashrc if using Bash
```

Add at the bottom of the file:

```bash
# Claude Code via [Corporate LLM Gateway]
export ANTHROPIC_API_KEY="<[YOUR_ORG]-gateway-api-key>"
export ANTHROPIC_BASE_URL="[YOUR_ORG_URL]"
export ANTHROPIC_MODEL="claude-sonnet-4-6@default"
export CODE_SCAN_TOKEN="<[YOUR_ORG]-PAT>"
export CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS="1"
```

Replace placeholders with your real values. Save (`Ctrl+O`, `Enter`, `Ctrl+X`). Reload the shell:

```bash
source ~/.zshrc    # or source ~/.bashrc
```

Verify the variables are set correctly:

```bash
echo $ANTHROPIC_BASE_URL
echo $ANTHROPIC_MODEL
echo "API_KEY length: ${#ANTHROPIC_API_KEY}"
```

This should print the URL, model name, and a number around 64 (the key length).

#### Windows (PowerShell)

First, allow custom profile scripts (one-time):

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Press `Y` when prompted. Then create the profile file:

```powershell
New-Item -ItemType Directory -Path (Split-Path $PROFILE) -Force
New-Item -ItemType File -Path $PROFILE -Force
notepad $PROFILE
```

Notepad opens. Paste the following content:

```powershell
# Claude Code via [Corporate LLM Gateway]
$env:ANTHROPIC_API_KEY = "<[YOUR_ORG]-gateway-api-key>"
$env:ANTHROPIC_BASE_URL = "[YOUR_ORG_URL]"
$env:ANTHROPIC_MODEL = "claude-sonnet-4-6@default"
$env:CODE_SCAN_TOKEN = "<[YOUR_ORG]-PAT>"
$env:CLAUDE_CODE_DISABLE_EXPERIMENTAL_BETAS = "1"
```

Replace placeholders with your actual values. Save (`Ctrl+S`), close Notepad. Load the profile:

```powershell
. $PROFILE
```

Verify the variables are set:

```powershell
echo $env:ANTHROPIC_BASE_URL
echo $env:ANTHROPIC_MODEL
```

> **Important:** Do **not** set `ANTHROPIC_AUTH_TOKEN`. Only `ANTHROPIC_API_KEY` is required. Setting both triggers an "Auth conflict" warning.

### [INSTALL] 2.4 Install Claude Code

Run both commands — the first installs Claude Code, and the second pulls [your org] platform settings. Without the second command, you are not compliant with corporate requirements.

#### macOS / Linux / WSL2

```bash
curl -fsSL https://claude.ai/install.sh | bash
curl -fsSL https://[devops].[YOUR_ORG].io/managed-claude-code/post-install.sh | sh
```

#### Windows (PowerShell)

```powershell
irm https://claude.ai/install.ps1 | iex
irm https://[devops].[YOUR_ORG].io/managed-claude-code/post-install.ps1 | iex
```

Add the install directory to your User PATH if not already there:

```powershell
[Environment]::SetEnvironmentVariable("Path", [Environment]::GetEnvironmentVariable("Path", "User") + ";$env:USERPROFILE\.local\bin", "User")
$env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
```

**Optional — if you have Git Bash and want Claude Code to use it:**

Find the Git Bash executable:

```powershell
where.exe bash
```

If it returns a path like `C:\Program Files\Git\bin\bash.exe`, Claude Code will detect it automatically. If installed but not detected, set the env var `CLAUDE_CODE_GIT_BASH_PATH` to the correct path via Windows Settings → Environment Variables.

Verify the installation:

```powershell
claude --version
```

**Installation footprint:**

| Component | Location | Size |
|---|---|---|
| CLI binary | `~\.local\bin\claude.exe` | ~218 MB |
| Config & sessions | `~\.claude\` | ~13 MB (grows with usage) |
| **Total** | — | **~231 MB** |

### [USAGE] 2.5 First Run

Execute the following command to start using Claude Code:

```bash
claude "say hello and tell me which model you are running"
```

You'll be prompted in sequence:

1. **"Detected a custom API key in your environment — Yes/No"** → pick **Yes** (default is "No (recommended)" — override it; the key is correct)
2. **Theme** → either option is fine
3. **Folder trust** → trust the current folder if it's a project

You should see a response identifying **Claude Sonnet 4.6** (`claude-sonnet-4-6@default`). If it works — Claude Code is installed and routing through [Corporate LLM Gateway].

\newpage

## Chapter 3: Local AI Stack Setup

\newpage

This chapter covers the installation and configuration of local AI inference tools, including llama.cpp, LiteLLM proxy, and agentic alternatives like Crush and Aider. It provides complete setup instructions for both direct llama.cpp integration and model routing via LiteLLM.

### [INSTALL] 3.1 llama.cpp Installation

#### Download

Obtain the latest llama.cpp binaries from the official releases page:

https://github.com/ggml-org/llama.cpp/releases

Extract to: `C:\llama`

#### Model

Download a GGUF quantized model (e.g., `Qwen3-30B-A3B-Q4_K_M.gguf`) and store in: `C:\models`

#### Start Server

Navigate to the llama directory and start the server with full GPU offloading:

```powershell
cd C:\llama

.\llama-server.exe `
  -m C:\models\Qwen3-30B-A3B-Q4_K_M.gguf `
  -ngl 999 `
  -c 32768
```

The `-ngl 999` flag requests all layers be offloaded to GPU. The `-c 32768` sets context window size to 32K tokens.

#### Built-in Web UI

llama-server includes a basic chat interface — no extra install required. Once the server is running, open `http://localhost:8080` in a browser to chat with the model directly. This is **not** the same as Open WebUI discussed later.

#### GPU Monitoring

Monitor GPU usage while running llama.cpp:

```powershell
nvidia-smi -l 1
```

This updates the NVIDIA-SMI display every second.

#### Optional Open WebUI (separate project, requires Docker)

Open WebUI is a separate, standalone project with a richer interface including conversation history, model switching, user accounts, and more. It connects to llama.cpp as a backend but requires Docker to run. Not related to the built-in llama-server UI above.

```powershell
docker run -d `
  -p 3000:8080 `
  --add-host=host.docker.internal:host-gateway `
  -v open-webui:/app/backend/data `
  ghcr.io/open-webui/open-webui:main
```

- URL: http://localhost:3000
- Endpoint: http://host.docker.internal:8080

### [INTEGRATION] 3.2 LiteLLM Proxy Setup

LiteLLM is a lightweight proxy that sits between clients (like Claude Code or Crush) and model backends (cloud APIs or local servers like llama.cpp). It exposes a single OpenAI-compatible endpoint, so you can switch between local and cloud models without reconfiguring each client.

#### Why Use It

| Without LiteLLM | With LiteLLM |
|-----------------|--------------|
| Claude Code → Anthropic API (cloud only) | Claude Code → LiteLLM → Anthropic API |
| Separate client for local models | Claude Code → LiteLLM → llama.cpp → Qwen3 |
| Different config per model | One endpoint, multiple backends |

#### Install

Install the LiteLLM package with proxy support:

```bash
pip install 'litellm[proxy]'
```

#### Environment Variables (required)

Set these as **User environment variables** via Windows Settings → System → Advanced → Environment Variables:

| Variable | Value | Purpose |
|----------|-------|---------|
| `ANTHROPIC_API_KEY` | Your [Corporate LLM Gateway] API key | Auth for cloud models *(defined)* |
| `ANTHROPIC_MODEL_LITELLM` | `anthropic/claude-opus-4-6@default` | Cloud model with LiteLLM provider prefix *(defined)* |

> **Note:** LiteLLM's `os.environ/` syntax only works when the entire value comes from the env var — you cannot mix a prefix like `anthropic/` with `os.environ/VAR`. That's why `ANTHROPIC_MODEL_LITELLM` includes the `anthropic/` prefix.

#### Config File

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

  - model_name: [org]-opus
    litellm_params:
      model: os.environ/ANTHROPIC_MODEL_LITELLM
      api_key: os.environ/ANTHROPIC_API_KEY
```

| Model name | Routes to | Notes |
|---|---|---|
| `local-qwen3` | llama.cpp on localhost:8080 | Requires llama.cpp server running *(defined)* |
| `claude-sonnet` | Anthropic API (direct) | Currently unhealthy — model ID doesn't match [Corporate LLM Gateway] *(pending)* |
| `[org]-opus` | [Corporate LLM Gateway] | Working — uses `ANTHROPIC_MODEL_LITELLM` env var *(validated)* |

#### Starting from Scratch

Follow these steps to set up the complete local AI stack:

**Step 1 — Start llama.cpp server** (new terminal, leave it running):

```powershell
cd C:\llama
.\llama-server.exe -m C:\models\Qwen3-30B-A3B-Q4_K_M.gguf -ngl 999 -c 32768
```

Wait for `model loaded` message (~15-30 seconds while GPU loads the ~17GB model).

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
curl http://localhost:4000/v1/chat/completions `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer sk-1234" `
  -d '{"model":"local-qwen3","messages":[{"role":"user","content":"Name three planets. One sentence only."}],"max_tokens":500}'
```

**Step 5 — Test cloud model ([Corporate LLM Gateway]):**

```bash
curl http://localhost:4000/v1/chat/completions `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer sk-1234" `
  -d '{"model":"[org]-opus","messages":[{"role":"user","content":"Name three planets. One sentence only."}],"max_tokens":100}'
```

> The `Authorization: Bearer sk-1234` is a dummy token — LiteLLM proxy doesn't enforce auth by default. The real API key is in the config/env var.

Test using PowerShell (not curl):

```powershell
$env:ANTHROPIC_API_KEY  
$response = Invoke-RestMethod -Uri "http://localhost:4000/v1/chat/completions"   -Method POST   -Headers @{ "Authorization" = "Bearer sk-1234" }   -ContentType "application/json"   -Body '{"model":"[org]-opus","messages":[{"role":"user","content":"Name three planets. One sentence only."}],"max_tokens":1000}'
$response.choices[0].message.content   
```

Expected output: `The three planets are Mercury, Venus, and Earth.`

If no results appear, the token may have been too short.

#### Switching Between Local and Cloud Models

Once both services are running, switch models by name in the request body:

```bash
# Local Qwen3
"model": "local-qwen3"

# Cloud [model]
"model": "[org]-opus"
```

#### Performance Notes

- **Qwen3 thinking mode:** Qwen3 defaults to "thinking" mode — it spends tokens on internal reasoning (`reasoning_content`) before producing the visible answer (`content`). Set `max_tokens` to 300+ for simple questions, or the response may be all reasoning with an empty answer.
- **Generation speed:** ~10 tokens/sec on RTX PRO 4000
- **Prompt caching:** Working — repeat prompts are faster

#### Debugging

Set logging level for LiteLLM:

```bash
export LITELLM_LOG=DEBUG    # detailed logs
export LITELLM_LOG=INFO     # normal operation
```

#### Routing Claude Code through LiteLLM → llama.cpp

The useful case here is **Claude Code → LiteLLM → llama.cpp → Qwen3** — using a local model via Claude Code instead of the [your org] cloud. By default, Claude Code uses your Windows User env vars (`ANTHROPIC_BASE_URL`, `ANTHROPIC_MODEL`) and connects directly to the [Corporate LLM Gateway]. To route through LiteLLM instead, override `ANTHROPIC_BASE_URL` in a terminal session (session-scoped — other terminals are unaffected):

```powershell
$env:ANTHROPIC_BASE_URL = "http://localhost:4000"
$env:ANTHROPIC_MODEL = "local-qwen3"
claude "say hello and tell me which model you are running"
```

> **Important:** Do NOT override `ANTHROPIC_API_KEY`. Leave your real [Corporate LLM Gateway] key in place — Claude Code validates the key format on startup and rejects dummy values (prompts `/login`). LiteLLM ignores the incoming auth header and uses the real key from its own config only when routing to cloud models.

**Note on earlier friction testing (2026-06-14):** Prior notes recorded two 400 errors (`structured_outputs` and `system` role formatting) when testing Claude Code → LiteLLM → [Corporate LLM Gateway]. That was testing the wrong path — routing Claude Code through a corporate proxy back to the cloud makes no sense; you'd just connect Claude Code directly to [Corporate LLM Gateway]. The errors were [your org] policy and LiteLLM/proxy interaction issues specific to that cloud route. Their behaviour against a local llama.cpp backend is untested and likely differs — llama.cpp is more permissive about message formatting, and `structured_outputs` policy restrictions don't apply locally.

### [ALTERNATIVES] 3.3 Agentic Alternatives for Local Models

Claude Code is purpose-built for Anthropic models. While it can route to local models via LiteLLM, the experience is rough. These tools talk natively to OpenAI-compatible endpoints like llama.cpp — no translation layer needed.

| Tool | Type | Best For | Notes |
|------|------|----------|-------|
| **Crush** | CLI TUI (Go) | Fully local agentic coding; Claude Code alternative | By Charmbracelet. Native `llamacpp` and `litellm` provider types — no translation layer. MCP support, LSP integration, auto-discovers models. FSL-1.1-MIT (free). **Recommended for fully local setup** *(recommended)* |
| **Aider** | CLI (like Claude Code) | Git-aware coding: edits, commits, multi-file refactors | Closest equivalent to Claude Code for local models. Very active open-source project. New `/context` command auto-selects relevant files *(defined)* |
| **Cline** | VS Code extension | Agentic coding inside VS Code | Reads/writes files, runs terminal commands. Connects to llama.cpp directly *(pending)* |
| **Continue** | VS Code / JetBrains extension | Chat + autocomplete + agentic features | IDE-integrated, supports multiple backends *(pending)* |
| **Qwen-Agent** | Python library | Custom agentic workflows | Alibaba's own framework for Qwen. Deepest Qwen integration (thinking mode, tool use) *(pending)* |
| ~~**OpenCode**~~ | ~~CLI~~ | ~~Archived~~ | **Archived September 2025.** Do not use. Crush is its successor *(validated)* |

#### Example: Aider with Local Qwen3

```bash
pip install aider-chat
aider --openai-api-base http://localhost:8080/v1 --openai-api-key not-needed --model openai/Qwen3-30B-A3B-Q4_K_M
```

> **Reality check:** A 30B model (even a fast MoE like Qwen3-30B-A3B) is noticeably less capable than Claude Opus for complex multi-file refactors and large codebase reasoning. These tools shine for focused tasks — quick edits, single-file work, code generation — where the model size gap matters less.

### [INSTALL] 3.4 Crush — Fully Local Agentic Stack

#### Software Locations — Full Stack Reference

This table documents all software locations in the full stack setup:

| Component | Location | Notes |
|-----------|----------|-------|
| llama.cpp binaries | `C:\llama\` | Includes `llama-server.exe`, CUDA DLLs *(defined)* |
| Model files (.gguf) | `C:\models\` | One `.gguf` file per model *(defined)* |
| LiteLLM config | `C:\d_drive\workKW\WorkClaude\litellm_config.yaml` | Only needed for Path B (via LiteLLM) *(pending)* |
| Crush config (global) | `%LOCALAPPDATA%\crush\crush.json` | Windows global config *(defined)* |
| Crush config (per-project) | `.crush.json` in project root | Overrides global *(pending)* |
| Claude Code binary | `~\.local\bin\claude.exe` | ~218 MB *(defined)* |
| Claude Code config & sessions | `~\.claude\` | Grows with usage *(defined)* |
| llama.cpp server URL | `http://localhost:8080` | Default port *(defined)* |
| LiteLLM proxy URL | `http://localhost:4000` | Only when using Path B *(pending)* |

Crush is a terminal-based agentic coding assistant by Charmbracelet (the makers of Charm CLI tools). It is the successor to the archived OpenCode project. Go-based TUI; supports MCP servers; integrates with LSP for code intelligence.

License: FSL-1.1-MIT (free for personal and commercial use; source-available). Fully free stack when combined with llama.cpp and open-weight models.

#### Why Crush

- Native `llamacpp` provider type — connects to llama.cpp server directly with no LiteLLM proxy needed *(defined)*
- Also supports `litellm` provider type for when you want LiteLLM as a model router (switch models without reconfiguring Crush) *(pending)*
- Auto-discovers available models from the backend *(defined)*
- MCP support (connect to Graph Studio, filesystem, or any MCP server) *(pending)*
- LSP integration (code navigation, go-to-definition) *(pending)*

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

#### Config File Locations

Config files can be stored in multiple locations:

- Per-project: `.crush.json` in the project root *(defined)*
- Global (Windows): `%LOCALAPPDATA%\crush\crush.json` *(defined)*
- Global (Linux/WSL2): `~/.config/crush/crush.json` *(pending)*

#### Path A: Crush → llama.cpp (direct, recommended for local-only)

No LiteLLM needed. Crush speaks directly to the llama.cpp server. This is the recommended approach for fully offline setups.

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

llama.cpp loads one model at a time. Choose based on your machine configuration:

**Models that run on both machines (fit in 12GB desktop VRAM):**

| Model | Q4 Size | Notes |
|---|---|---|
| Gemma 4 12B | ~7.6 GB | Fits both cleanly *(defined)* |
| DeepSeek-R1 14B | ~9 GB | Good reasoning + code; fits both *(defined)* |
| DeepSeek-R1 8B | ~5 GB | Lightest option *(defined)* |
| Qwen 3.5 9B | ~5.7 GB | Fits both *(defined)* |

Devstral 24B (~14GB) works on both but spills approximately 2GB into RAM on the desktop — functional but not fully GPU-resident.

#### Downloading GGUF Models

Yes — it is as simple as going to Hugging Face and downloading the `.gguf` file directly:

1. Go to [huggingface.co](https://huggingface.co) and search for the model
2. Look for a repo that provides GGUF quantized files — usually from **bartowski** or **lmstudio-community** (reliable quantizers)
3. Download the `Q4_K_M` variant — good balance of size and quality
4. Save to `C:\models\`

**Direct searches on HuggingFace for recommended models:**

| Model | HuggingFace repo to search |
|---|---|
| DeepSeek-R1 14B | `bartowski/DeepSeek-R1-Distill-Qwen-14B-GGUF` *(defined)* |
| DeepSeek-R1 8B | `bartowski/DeepSeek-R1-Distill-Qwen-8B-GGUF` *(defined)* |
| Gemma 4 12B | `bartowski/gemma-3-12b-it-GGUF` *(defined)* |
| Devstral 24B | `bartowski/Devstral-Small-2505-GGUF` *(defined)* |
| Qwen 3.5 9B | `bartowski/Qwen2.5-7B-Instruct-GGUF` *(defined)* |

Download only the single `.gguf` file — no other files needed for llama.cpp.

**To switch models:** stop the server, restart with a different `-m` flag, update `model` in `.crush.json` to match:

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

#### Tool Calling Note

Crush's tool-calling reliability depends on the model's native function-calling support. Devstral 24B and Qwen3 30B both support tool calling — prefer these for agentic tasks. Smaller or older models may produce unreliable tool call JSON. This is the same caveat as Aider.

#### Crush vs Aider vs Claude Code

| Feature | Crush | Aider | Claude Code |
|---|-------|--------|-------------|
| Interface | TUI (interactive) | CLI (command + session) | CLI (interactive) |
| Best model | Local llama.cpp | Local or cloud | Anthropic (Claude) |
| MCP support | Yes | No | Yes |
| Git integration | Yes | Yes (core feature) | Yes |
| Cost | Free | Free | Requires API key |
| Offline capable | Yes (Path A) | Yes | No |
