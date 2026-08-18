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
  - [[DATA] 1.1 Hardware Specifications](#data-11-hardware-specifications)
  - [[DATA] 1.2 Models Overview](#data-12-models-overview)
  - [[INTEGRATION] 1.3 Model-to-Hardware Fit](#integration-13-model-to-hardware-fit)
  - [[RECOMMENDATION] 1.4 Desktop-Optimised Models (RTX 3060 12GB)](#recommendation-14-desktop-optimised-models-rtx-3060-12gb)
  - [[RECOMMENDATION] 1.5 Additional Recommended Models (Laptop)](#recommendation-15-additional-recommended-models-laptop)
  - [[INTEGRATION] 1.6 Inference Engines](#integration-16-inference-engines)
  - [[INTEGRATION] 1.7 Claude Code Integration](#integration-17-claude-code-integration)
  - [[ARCHITECTURE] 1.8 Recommended Architecture](#architecture-18-recommended-architecture)
  - [[RECOMMENDATION] 1.9 Recommended Final Setup](#recommendation-19-recommended-final-setup)
- [Chapter 2: Setting Up Claude Code](#chapter-2-setting-up-claude-code)
  - [[REQUIREMENTS] 2.1 What You Need (and What You Don't)](#requirements-21-what-you-need-and-what-you-dont)
  - [[INTEGRATION] 2.2 Why a Bash Shell Matters (and Your Options on Windows)](#integration-22-why-a-bash-shell-matters-and-your-options-on-windows)
  - [[CONFIG] 2.3 Step 1: Set Environment Variables](#config-23-step-1-set-environment-variables)
  - [[INSTALL] 2.4 Step 2: Install Claude Code](#install-24-step-2-install-claude-code)
  - [[USAGE] 2.5 Step 3: First Run](#usage-25-step-3-first-run)
- [Chapter 3: Local AI Stack Setup](#chapter-3-local-ai-stack-setup)
  - [[INSTALL] 3.1 llama.cpp Installation](#install-31-llamacpp-installation)
    - [3.1.1 Claude Code -> LiteLLM -> llama.cpp -> Qwen3.5](#311--claude-code---litellm---llamacpp---qwen35)
  - [[INTEGRATION] 3.2 LiteLLM Proxy Setup](#integration-32-litellm-proxy-setup)
    - [3.2.1 Install LiteLLM](#321-install-litellm)
    - [3.2.2 Use separate API keys for each hop](#322-use-separate-api-keys-for-each-hop)
    - [3.2.3 Create the LiteLLM configuration file](#323-create-the-litellm-configuration-file)
  - [[TESTING] 3.3 Testing in Windows](#testing-33-testing-in-windows)
  - [3.4 Testing Claude Code -> LiteLLM -> llama.cpp -> Qwen3.5](#34--testing-claude-code---litellm---llamacpp---qwen35)
    - [3.4.1 Set environment variables for testing](#341-set-environment-variables-for-testing)
    - [3.4.2 Testing without Claude Code](#342-testing-without-claude-code)
    - [3.4.3 Testing with Claude Code](#343-testing-with-claude-code)
    - [3.4.4 Success checklist](#344-success-checklist)
  - [3.5 Final Configurations](#35-final-configurations)
    - [3.5.1 Only after everything works -- update `.bashrc`](#351-only-after-everything-works----update-bashrc)
    - [3.5.2 Do not enable Qwen thinking yet](#352-do-not-enable-qwen-thinking-yet)
    - [3.5.3 Fallback only if LiteLLM fails](#353-fallback-only-if-litellm-fails)
    - [3.5.4 Final architecture](#354-final-architecture)
    - [3.5.5 Changing context size](#355-changing-context-size)
- [Chapter 4: Agentic Alternatives for Local Models](#chapter-4-agentic-alternatives-for-local-models)
- [Chapter 5: Crush — Fully Local Agentic Stack](#chapter-5-crush--fully-local-agentic-stack)
  - [[INSTALL] 5.1 Software Locations — Full Stack Reference](#install-51-software-locations--full-stack-reference)
  - [5.2 Why Crush](#52-why-crush)
  - [5.3 Install](#53-install)
  - [5.4 Config File Locations](#54-config-file-locations)
  - [5.5 Path A: Crush → llama.cpp](#55-path-a-crush--llamacpp)
  - [5.6 Models for Path A — Desktop vs Laptop](#56-models-for-path-a--desktop-vs-laptop)
  - [5.7 Downloading GGUF Models](#57-downloading-gguf-models)
  - [5.8 Path B: Crush → LiteLLM → llama.cpp](#58-path-b-crush--litellm--llamacpp)
  - [5.9 Tool Calling Note](#59-tool-calling-note)
  - [5.10 Crush vs Aider vs Claude Code](#510-crush-vs-aider-vs-claude-code)

<!-- END TOC -->

## Chapter 1: LLM Models vs Hardware Comparisons

This chapter provides a comprehensive overview of local LLM models and their compatibility with different hardware configurations. It covers model specifications, performance characteristics, inference engines, and recommendations for both desktop and laptop setups. The goal is to help you choose the right models and tools for your specific hardware constraints while maximizing performance and usability.

### [DATA] 1.1 Hardware Specifications

This section documents the hardware configurations used for testing and development. Two systems were evaluated: a desktop workstation and a high-end laptop.

| Spec | Desktop | Laptop (HP ZBook Fury 16) |
|------|---------|---------------------------|
| CPU | AMD Ryzen 5 5600X 6-Core | Intel Core Ultra 9 |
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
| Gemma 3 12B IT Q4_K_M | Dense (IT) | 12B | ~7 GB | Mature general-purpose; writing, summarisation, reasoning, multilingual, vision, function calling, structured output, long context *(defined)* |
| Qwen3 30B-A3B | MoE (8/128 experts) | 30B / 3.3B active | ~18.6 GB | Strong coding, document analysis, enterprise work *(defined)* |
| Qwen3-Coder 30B-A3B | MoE | 30B / 3.3B active | ~19 GB | Coding-focused, 256K context *(defined)* |
| Qwen3 32B | Dense | 32B | ~20 GB | Strong reasoning; 40% on Aider coding benchmark (best open local) *(defined)* |
| Qwen 3.5 9B Q5_K_M | Dense (hybrid DeltaNet+Attention) | 9B | ~6.6 GB | **Default model**; Multimodal (text+image+video), 256K context, 201 languages; coding, reasoning, agents, React/Node dev, Python, Linux admin, tool calling *(defined)* |
| Qwen 3.5 9B Q6_K | Dense (hybrid DeltaNet+Attention) | 9B | ~7.7 GB | **Higher-fidelity quantisation**; same model as Q5_K_M but slightly less quantisation loss; use for benchmarking or when maximum Qwen3.5 quality is preferred over VRAM/context headroom *(defined)* |
| Qwen3 8B Q5_K_M | Dense | 8B | ~5.9 GB | **Fast model**; established Qwen series; leaves more VRAM headroom (~6GB) for KV cache and longer contexts; quick coding questions, shell commands, simple code generation *(defined)* |
| Devstral 24B | Dense | 24B | ~14 GB | Agentic coding; 46.8% SWE-Bench; beats DeepSeek-V3 671B on coding evals. Apache 2.0. *(defined)* |
| DeepSeek-R1 14B (distill) | Dense (distilled) | 14.8B | ~9 GB | Reasoning/math; distilled from full R1; MIT license *(defined)* |
| DeepSeek-R1 8B (distill) | Dense (distilled) | 8B | ~5 GB | Lightweight reasoning; fits comfortably in 12GB VRAM *(defined)* |

**Important Notes:**

- The original notes referenced "Gemma 4 27B" — this model does not exist. Gemma 4 ships as 12B, 26B (MoE), and 31B (Dense). "27B" is a Gemma 3 model.
- DeepSeek-R1 full model (671B) is not locally runnable. Only the distilled variants (8B, 14B, 32B, 70B) are practical for local use.
- **Qwen 3.5 9B** is available in two quantizations: Q5_K_M (~6.6 GB, recommended default) and Q6_K (~7.7 GB, higher fidelity). Q5_K_M is the better practical choice on a 12GB RTX 3060 for everyday use; Q6_K is useful for benchmarking or when maximum quality is preferred.
- **Gemma 3 12B IT** is the predecessor to Gemma 4 and serves as a mature, stable general-purpose backup model with strong support for vision, function calling, structured output, and long context.

### [INTEGRATION] 1.3 Model-to-Hardware Fit

This matrix shows how each model performs on the two hardware configurations. VRAM-resident models run faster and more efficiently than those requiring RAM offload.

| Model | Q4/Q5/Q6 Size | Desktop (RTX 3060 12GB VRAM, 32GB RAM) | Laptop (RTX PRO 4000 16GB VRAM, 64GB RAM) |
|-------|---------------|---------------------------------------|------------------------------------------|
| Gemma 4 12B | ~7.6 GB | Fits in VRAM — runs well *(defined)* | Fits in VRAM — runs well *(defined)* |
| Gemma 3 12B IT Q4_K_M | ~7 GB | Fits in VRAM — runs well; stable general-purpose backup *(defined)* | Fits in VRAM — runs well *(defined)* |
| Gemma 4 26B (MoE) | ~18 GB | Too large for VRAM; slow with RAM offload on 32GB | Needs partial RAM offload (~2GB spill); usable *(in-progress)* |
| Gemma 4 31B (Dense) | ~20 GB | Won't run well — exceeds VRAM + limited RAM | Needs significant RAM offload; marginal *(pending)* |
| Qwen3 30B-A3B | ~18.6 GB | Too large for VRAM; tight on 32GB RAM | Needs partial RAM offload; usable — lower active params help *(in-progress)* |
| Qwen3-Coder 30B-A3B | ~19 GB | Too large for VRAM; tight on 32GB RAM | Needs partial RAM offload; usable *(in-progress)* |
| Qwen3 32B | ~20 GB | Too large for VRAM; tight on 32GB RAM | Needs partial RAM offload; usable *(in-progress)* |
| Devstral 24B | ~14 GB | Exceeds VRAM; usable with RAM offload (plenty of 32GB headroom) | Fits in VRAM — runs well *(defined)* |
| DeepSeek-R1 14B (distill) | ~9 GB | Fits in VRAM — runs well *(defined)* | Fits in VRAM — runs well *(defined)* |
| DeepSeek-R1 8B (distill) | ~5 GB | Fits in VRAM — runs well *(defined)* | Fits in VRAM — runs well *(defined)* |
| Qwen 3.5 9B Q5_K_M | ~6.6 GB | Fits in VRAM — **recommended default**; excellent for coding, reasoning, agents *(defined)* | Fits in VRAM — runs well; leaves ~5GB headroom *(defined)* |
| Qwen 3.5 9B Q6_K | ~7.7 GB | Fits in VRAM — higher fidelity; slightly less VRAM headroom *(defined)* | Fits in VRAM — for benchmarking or maximum quality needs *(defined)* |
| Qwen3 8B Q5_K_M | ~5.9 GB | **Fits comfortably**; leaves ~6GB VRAM headroom for longer contexts and KV cache *(defined)* | Fits in VRAM with significant headroom; fastest option *(defined)* |

### [RECOMMENDATION] 1.4 Desktop-Optimised Models (RTX 3060 12GB)

These models fit comfortably in 12GB VRAM at Q4/Q5 quantization and run fully on-GPU without RAM offloading, providing optimal performance for desktop use.

| Model | Quantisation | Size | Strengths | Ollama tag |
|-------|--------------|------|-----------|------------|
| **Qwen 3.5 9B Q5_K_M** | Q5_K_M | ~6.6 GB | **Default model**; coding, reasoning, agents, React/Node dev, Python, Linux admin, tool calling, general questions | `qwen3.5:9b` *(defined)* |
| Gemma 4 12B | Q4_K_M | ~7.6 GB | Fast general assistant; strong daily tasks; good multimodal support | `gemma4:12b` *(defined)* |
| Qwen3 8B Q5_K_M | Q5_K_M | ~5.9 GB | **Fastest**; established Qwen series; leaves ~6GB VRAM headroom for KV cache and longer contexts; quick coding questions, shell commands, simple code generation | `qwen3:8b` *(defined)* |
| DeepSeek-R1 8B (distill) | Q4_K_M | ~5 GB | Reasoning and math; MIT license; lightest option | `deepseek-r1:8b` *(defined)* |
| DeepSeek-R1 14B (distill) | Q4_K_M | ~9 GB | Better reasoning; still fits in 12GB VRAM | `deepseek-r1:14b` *(defined)* |

For the desktop, avoid models larger than ~11GB Q4 unless you are comfortable with partial RAM offloading. The `-ngl` flag in llama.cpp controls layer split between GPU and CPU. Devstral 24B (~14GB) spills approximately 2GB into RAM — still functional on 32GB system RAM but not fully GPU-resident.

**Qwen 3.5 9B Quantisation Note:** The Q5_K_M version (~6.6 GB) is the recommended default for everyday use. The Q6_K version (~7.7 GB) offers slightly higher fidelity with less quantisation loss but uses more VRAM. On a 12GB RTX 3060, Q5_K_M is generally the better practical choice, leaving more headroom for context and KV cache.

### [RECOMMENDATION] 1.5 Additional Recommended Models (Laptop)

These models fit within 16GB VRAM at Q4/Q5 quantization without offloading, making them ideal for the laptop configuration.

| Model | Params | Quantisation | Size | Best For | Why Add |
|-------|--------|--------------|------|----------|---------|
| Devstral 24B | 24B | Q4_K_M | ~14 GB | Coding, agentic tasks | Mistral's agentic coding model; 46.8% SWE-Bench (beats DeepSeek-V3 671B on coding evals); 128K context; Apache 2.0. Fits in 16GB VRAM. Ollama: `devstral:24b` *(defined)* |
| Qwen3 8B Q5_K_M | 8B | Q5_K_M | ~5.9 GB | Fast coding, shell commands, quick questions | Leaves significant VRAM headroom (~10GB) for longer contexts and KV cache; fastest option on laptop. Ollama: `qwen3:8b` *(defined)* |
| DeepSeek-R1 14B | 14.8B | Q4_K_M | ~9 GB | Reasoning, math, code | Distilled from full R1; adds dedicated reasoning capability. MIT license. Also fits in RTX 3060 12GB. Ollama: `deepseek-r1:14b` *(defined)* |
| Qwen 3.5 9B Q5_K_M | 9B | Q5_K_M | ~6.6 GB | **Default**; General + vision + reasoning + agents | Multimodal (text+image+video), hybrid DeltaNet architecture, 256K native context (up to 1M). Apache 2.0. Excellent balance of quality and speed. Ollama: `qwen3.5:9b` *(defined)* |
| Qwen 3.5 9B Q6_K | 9B | Q6_K | ~7.7 GB | Higher-fidelity generations, benchmarking | Same model as Q5_K_M but with less quantisation loss; use when maximum Qwen3.5 quality is preferred over VRAM headroom. Ollama: `qwen3.5:9b` *(defined)* |
| Gemma 4 12B | 12B | Q4_K_M | ~7.6 GB | Harder reasoning, complex documents, multimodal experiments | Stronger general reasoning than Qwen3.5; handles images/audio well. Good for comparison experiments. Ollama: `gemma4:12b` *(defined)* |
| Gemma 3 12B IT Q4_K_M | 12B | Q4_K_M | ~7 GB | Writing, summarisation, stable backup | Mature general-purpose model with support for vision, function calling, structured output, long context, and multilingual workloads. Ollama: `gemma3:12b-it` *(defined)* |
| Qwen3 32B | 32B | Q4_K_M | ~20 GB | Reasoning, coding (needs RAM offload) | Dense model; 40% on Aider coding benchmark (best open local); needs partial RAM offload but 64GB system RAM gives plenty of headroom *(in-progress)* |

### [INTEGRATION] 1.6 Inference Engines

Comparison of popular inference engines for running local LLMs:

| Feature | Ollama | LM Studio | llama.cpp |
|---------|--------|-----------|-----------|
| Install ease | Simplest | Desktop GUI | Command line *(defined)* |
| API integration | Easy, works with Open WebUI | Less configurable | Most control *(defined)* |
| Performance | Slight overhead | Moderate | **Highest** *(defined)* |
| Memory efficiency | Good | Good | **Best** *(defined)* |
| Best for | Quick start | Experimentation | Power users *(defined)* |

**Quantisation Notes:** llama.cpp supports multiple quantization schemes. Q4_K_M offers the best balance of size and quality (~4-bit). Q5_K_M provides slightly higher fidelity at the cost of ~1GB more VRAM. Q6_K is even higher quality but may exceed VRAM on smaller GPUs. For a 12GB RTX 3060, Q5_K_M for Qwen3.5 9B and Q4_K_M for Gemma 4 12B are recommended defaults.

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

| Component | Choice | Notes |
|-----------|--------|-------|
| Primary model | Qwen 3.5 9B Q5_K_M (Desktop / Laptop) | **Default for everyday coding**; Qwen 3.5 9B for general AI work, Qwen3 8B for fast tasks with more context headroom *(defined)* |
| Primary engine | llama.cpp *(defined)* | Use `-ngl 999` for full GPU offloading; supports multiple quantizations *(Q4_K_M, Q5_K_M, Q6_K)* |
| Planning & architecture | Claude Code with Claude Sonnet *(defined)* | For complex planning and requirements gathering |
| Local coding assistant (cloud) | Aider → LiteLLM → Claude Sonnet *(pending)* | For tasks requiring cloud model capabilities |
| Local coding assistant (offline) | Crush → llama.cpp → Devstral 24B or Qwen3 30B-A3B *(defined)* | For agentic workflows without cloud dependency |
| Alternative multimodal model | Gemma 4 12B Q4_K_M | Harder reasoning, complex documents, image/audio understanding *(defined)* |
| Stable backup model | Gemma 3 12B IT Q4_K_M | Mature general-purpose; writing, summarisation, multilingual tasks *(defined)* |
| Fast lightweight model | Qwen3 8B Q5_K_M | Quick coding questions, shell commands, leaves more VRAM for context *(defined)* |
| Higher-fidelity option | Qwen 3.5 9B Q6_K | When maximum quality is preferred over speed/VRAM headroom *(defined)* |
| Local heavy work | Qwen3 30B-A3B (laptop) / DeepSeek-R1 14B (desktop) | Document analysis, reasoning, math; fits in VRAM on both *(defined)* |
| Optional UI | Open WebUI *(pending)* | Richer interface with conversation history and model switching |
| Avoid initially | Ollama, LM Studio (less control) *(pending)* | Use llama.cpp for best performance and memory efficiency |
| Avoid | OpenCode (archived September 2025) *(validated)* | Crush is its successor |

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

This chapter covers the installation and configuration of local AI inference tools, including llama.cpp and the LiteLLM proxy. It provides complete setup instructions for both direct llama.cpp integration and model routing via LiteLLM.

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



#### 3.1.1  Claude Code -> LiteLLM -> llama.cpp -> Qwen3.5


Use Claude Code with a local Qwen3.5 model running in `llama.cpp`, while avoiding the direct Claude Code -> `llama.cpp` Anthropic `/v1/messages` compatibility issue that produced:

```
Jinja Exception: System message must be at the beginning.
```

The recommended architecture is:
```
Claude Code
    | Anthropic /v1/messages (port 4000)
    v
LiteLLM Proxy
    | translates Anthropic -> OpenAI Chat Completions (port 8080)
    v
llama-server /v1/chat/completions
    v
Qwen3.5-9B-Q5_K_M.gguf  (RTX 3060 12 GB)
```

The key idea is that Claude Code talks Anthropic format to LiteLLM, while LiteLLM talks OpenAI-compatible `/v1/chat/completions` to `llama.cpp`. This bypasses the problematic direct Claude Code -> `llama.cpp` Anthropic request handling.



**Key decisions**

**1. Two separate API keys.**
`ANTHROPIC_AUTH_TOKEN` authenticates Claude Code to LiteLLM. `LOCAL_LLAMA_API_KEY` authenticates LiteLLM to llama.cpp. These must not be conflated.

**2. Critical LiteLLM setting.**
`use_chat_completions_url_for_anthropic_messages: true` is the linchpin. Without it, LiteLLM forwards Anthropic-format requests directly to llama.cpp, reproducing the original Jinja error.

**3. Thinking disabled initially.**
`--reasoning off --reasoning-budget 0` is required at the start. Qwen3 exhibited looping behaviour in this environment when thinking was enabled. Enable reasoning only after the full tool chain is proven stable.

**4. Four verification gates before launching Claude Code.**
Direct llama.cpp test -> LiteLLM model discovery -> Anthropic-format request through LiteLLM -> token counting. Do not skip ahead.

**5. Bashrc update is deferred.**
Environment variables are set manually in the terminal first. Persist to `.bashrc` only after the full manual test environment is verified.

---

** Start llama.cpp in a stable non-thinking configuration **

For the initial Claude Code integration, disable Qwen thinking. First prove that API translation and tool calling work reliably. Thinking can be reintroduced later.

Run:

```bash
~/llama.cpp/build/bin/llama-server \
  -m ~/models/gguf/Qwen3.5-9B-Q5_K_M.gguf \
  --alias qwen-local \
  -ngl 99 \
  -fa on \
  -ctk q8_0 \
  -ctv q8_0 \
  -c 262144 \
  --jinja \
  --chat-template-kwargs '{"enable_thinking":false}' \
  --host 127.0.0.1 \
  --port 8080 \
  --reasoning off \
  --reasoning-budget 0 \
  --temp 0.7 \
  --top-p 0.8 \
  --top-k 20 \
  --min-p 0.0 \
  --presence-penalty 1.5 \
  --repeat-penalty 1.0 \
  --api-key local-llm \
  -lv 4
```

The outer single quotes in `--chat-template-kwargs '{"enable_thinking":false}'` are shell quoting. The JSON property name is inside double quotes. `-ngl 99` is retained because it is already working on the RTX 3060 system. It is unrelated to the Jinja/API issue.

**Context size** - Find out the max context of the specific model. For example the Qwen3.5-9B-Q5_K_M.gguf model is 262144 for max context. Possible sizes are:  -c 65536 ,  -c 262144 , -c 131072  

Note the ctk and ctv controls the context of key value.

The important integration options are:

```text
--alias qwen-local
--jinja
--reasoning off
--reasoning-budget 0
--api-key local-llm
```

The LiteLLM design depends on `llama.cpp`'s `/v1/chat/completions` endpoint, not `/v1/messages`. Test it directly:

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer local-llm" \
  -d '{
    "model": "qwen-local",
    "max_tokens": 100,
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Reply with only the word hello."}
    ]
  }'
```

Expected result: an OpenAI-compatible response containing `hello`. Do not continue until this test passes.

**Aside**:
As mentioned in the beginning of the section, there has even been a llama.cpp issue specifically involving Claude Code + Qwen3.5 through /v1/messages, including conversion problems with thinking content.
Hence we use LiteLLM to fixing/bypassing the chat-template incompatibility—most likely using a translation layer such as LiteLLM/Claude Code Router rather than Claude Code ? /v1/messages directly.

The two tests below may pass, yet Qwen can still be incompatible between Claude Code and llama.cpp
```bash
curl http://127.0.0.1:8080/v1/models \
  -H "x-api-key: local-llm"

curl http://127.0.0.1:8080/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: local-llm" \
  -d '{
    "model": "qwen-local",
    "max_tokens": 100,
    "system": "You are a helpful assistant.",
    "messages": [
      {
        "role": "user",
        "content": "Reply with only the word hello."
      }
    ]
  }'
```


### [INTEGRATION] 3.2 LiteLLM Proxy Setup

LiteLLM is a lightweight proxy that sits between clients (like Claude Code or Crush) and model backends (cloud APIs or local servers like llama.cpp). It exposes a single OpenAI-compatible endpoint, so you can switch between local and cloud models without reconfiguring each client.

#### Why Use It

| Without LiteLLM | With LiteLLM |
|-----------------|--------------|
| Claude Code → Anthropic API (cloud only) | Claude Code → LiteLLM → Anthropic API |
| Separate client for local models | Claude Code → LiteLLM → llama.cpp → Qwen3 |
| Different config per model | One endpoint, multiple backends |


#### 3.2.1 Install LiteLLM

Check whether `uv` is installed, then install the LiteLLM proxy:

```bash
uv --version
sudo snap install astral-uv --classic   # if need to install
#uv tool install 'litellm[proxy]'
uv tool install "litellm[proxy]"   --with "fastapi>=0.136.3,<0.140"   --force
litellm --version
```

Using `uv tool install` keeps LiteLLM isolated from the current Conda `(base)` Python environment.

Or using pip:  
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



#### 3.2.2 Use separate API keys for each hop

```
Claude Code -- LiteLLM key  --> LiteLLM
LiteLLM     -- local-llm key --> llama.cpp
```

The existing llama.cpp key is `local-llm`. Generate a LiteLLM master key:

```bash
echo "sk-$(openssl rand -hex 24)"
```

This produces a key in the format `sk-b48d8e...`. Save the generated key. In the examples below it is represented as `sk-YOUR-LITELLM-KEY`. It will be defined in .bashrc for LITELLM_MASTER_KEY

---

#### 3.2.3 Create the LiteLLM configuration file

```bash
mkdir -p ~/.config/litellm
nano ~/.config/litellm/config.yaml
```

Use this configuration:

```yaml
model_list:
  - model_name: qwen-local
    litellm_params:
      model: openai/qwen-local
      api_base: http://127.0.0.1:8080/v1
      api_key: os.environ/LOCAL_LLAMA_API_KEY
    model_info:
      supports_function_calling: true

litellm_settings:
  drop_params: true
  modify_params: true
  use_chat_completions_url_for_anthropic_messages: true

general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
```

### What each important setting does

`model_name: qwen-local` is the model name Claude Code will request from LiteLLM. (See `alias` option where llama-server is run)

`model: openai/qwen-local` -- the `openai/` prefix tells LiteLLM to treat the backend as an OpenAI-compatible provider.

`api_base: http://127.0.0.1:8080/v1` points LiteLLM to the local `llama-server` OpenAI-compatible API.

`api_key: os.environ/LOCAL_LLAMA_API_KEY` -- LiteLLM reads the llama.cpp API key from an environment variable instead of storing it directly in YAML.

`supports_function_calling: true` tells LiteLLM the local model/backend should be treated as capable of tool/function calling.

`use_chat_completions_url_for_anthropic_messages: true` is critical. Claude Code sends Anthropic `/v1/messages` requests to LiteLLM. This setting tells LiteLLM to translate those requests through Chat Completions rather than forwarding them as Anthropic messages to `llama.cpp`.

The resulting flow should be:

```text
Claude Code /v1/messages
        ↓
LiteLLM translation
        ↓
llama.cpp /v1/chat/completions
```

#### `drop_params` and `modify_params`

`drop_params: true` and `modify_params: true` allow LiteLLM to discard unsupported parameters and normalise request structures when translating Claude-style requests for the local OpenAI-compatible backend.


**WARNING**
 LiteLLM does not behave like a well-disciplined Starfleet officer. It does not automatically search standard Linux
 directories such as /etc/litellm/ or ~/.config/litellm/. You must tell it where to look — explicitly.   
Example:  litellm --config my_llm_config .....


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




### [TESTING] 3.3 Testing in Windows

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

\newpage





### 3.4  Testing Claude Code -> LiteLLM -> llama.cpp -> Qwen3.5

#### 3.4.1 Set environment variables for testing

Initially, set these manually in the terminal rather than immediately modifying `.bashrc`.

```bash
export LOCAL_LLAMA_API_KEY="local-llm"
export LITELLM_MASTER_KEY="sk-YOUR-LITELLM-KEY"

export ANTHROPIC_BASE_URL="http://127.0.0.1:4000"
export ANTHROPIC_AUTH_TOKEN="$LITELLM_MASTER_KEY"

unset ANTHROPIC_API_KEY

export ANTHROPIC_CUSTOM_MODEL_OPTION="qwen-local"
export ANTHROPIC_CUSTOM_MODEL_OPTION_NAME="Qwen 3.5 9B Local"

export CLAUDE_CODE_MAX_CONTEXT_TOKENS="16384"
unset CLAUDE_CODE_DISABLE_UNKNOWN_MODEL_WINDOW_ENFORCEMENT

export ANTHROPIC_DEFAULT_HAIKU_MODEL="qwen-local"
export CLAUDE_CODE_SUBAGENT_MODEL="inherit"
```

Important changes when using LiteLLM in between Llama.cpp and Claude Code setup:

- `ANTHROPIC_BASE_URL="http://127.0.0.1:4000"` -- Claude Code now talks to LiteLLM on port 4000, not directly to llama.cpp on port 8080.
- `ANTHROPIC_AUTH_TOKEN` is used for Claude Code -> LiteLLM authentication.
- `unset ANTHROPIC_API_KEY` removes the old direct llama.cpp Claude key variable.
- `LOCAL_LLAMA_API_KEY="local-llm"` is the llama.cpp key, now stored separately and used internally by LiteLLM.


As an alternative to `.bashrc`, Claude Code-specific variables (excluding secret credentials) can be set in `~/.claude/settings.json`. Settings defined there take precedence over `.bashrc`.

```json
{
  "model": "qwen-local",
  "env": {
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:4000",
    "ANTHROPIC_CUSTOM_MODEL_OPTION": "qwen-local",
    "ANTHROPIC_CUSTOM_MODEL_OPTION_NAME": "Qwen 3.5 9B Local",
    "CLAUDE_CODE_MAX_CONTEXT_TOKENS": "262144",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "qwen-local",
    "CLAUDE_CODE_SUBAGENT_MODEL": "inherit"
  }
}
```

Keep `LITELLM_MASTER_KEY` and `LOCAL_LLAMA_API_KEY` in `.bashrc` only — do not store credentials in `settings.json`.

---

#### 3.4.2 Testing without Claude Code

Start LiteLLM

In a separate terminal, run:

```bash
litellm \
  --config ~/.config/litellm/config.yaml \
  --host 127.0.0.1 \
  --port 4000 \
  --detailed_debug
```

Verify both servers are listening:

```bash
ss -ltnp | grep -E ':(4000|8080)\b'
```

Expected: `127.0.0.1:4000` (LiteLLM) and `127.0.0.1:8080` (llama.cpp).
---

Verification test A -- LiteLLM model discovery

```bash
curl http://127.0.0.1:4000/v1/models \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY"
```

Expected result should contain `qwen-local`. If it does not appear, stop and fix the LiteLLM model configuration before proceeding.
---

Verification test B -- Anthropic request through LiteLLM

```bash
curl http://127.0.0.1:4000/v1/messages \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-local",
    "max_tokens": 100,
    "system": "You are a helpful assistant.",
    "messages": [{"role": "user", "content": "Reply with only the word hello."}]
  }'
```

Expected response: `hello`. This confirms that LiteLLM is successfully accepting Anthropic-compatible requests.

---

Verification test C -- confirm LiteLLM is not using llama.cpp `/v1/messages`

Watch the `llama-server` trace output while running the LiteLLM `/v1/messages` test. The llama.cpp log should show a request equivalent to:

```text
POST /v1/chat/completions
```

It should not show:

```text
POST /v1/messages
```

This is one of the most important checks in the entire setup.

Success means the path is genuinely:

```text
Claude/Anthropic request
        ↓
LiteLLM
        ↓
OpenAI Chat Completions
        ↓
llama.cpp
```

rather than simply forwarding the problematic Anthropic request directly to llama.cpp.

---

Verification test D -- token counting

```bash
curl http://127.0.0.1:4000/v1/messages/count_tokens \
  -H "Authorization: Bearer $LITELLM_MASTER_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen-local",
    "system": "You are a helpful assistant.",
    "messages": [{"role": "user", "content": "hello"}]
  }'
```

Expected result: a response containing an `input_tokens` value. This is useful because Claude Code may use token counting as part of its context management behaviour.

---

#### 3.4.3 Testing with Claude Code

Start Claude Code through LiteLLM

Only after the previous tests pass, run:

```bash
claude --model qwen-local
```

Inside Claude Code, run `/status` and verify it shows:

```
Anthropic base URL: http://127.0.0.1:4000
Model: qwen-local
```

The important check is that Claude Code is talking to LiteLLM on port 4000 rather than directly to llama.cpp on port 8080.

---

Final tool-use test

A normal chat response is not enough to prove Claude Code works correctly. Claude Code must also be able to invoke tools reliably. Create a disposable test directory:

```bash
mkdir -p ~/claude-local-test && cd ~/claude-local-test
claude --model qwen-local
```

Ask Claude Code:

```
Create a file named test.txt containing exactly: hello-local
Then read the file back and tell me its contents.
```

After Claude Code finishes, verify manually:

```bash
cat ~/claude-local-test/test.txt
```

Expected: `hello-local`. This validates the full path:

```text
Claude Code tool definition
        ↓
LiteLLM translation
        ↓
Qwen tool call
        ↓
Claude Code executes tool
        ↓
Tool result returned to Qwen
        ↓
Qwen continues correctly
```

---

#### 3.4.4 Success checklist

Do not consider the setup complete until all of these pass:

```
[x] llama.cpp /v1/chat/completions works directly
[x] llama.cpp API key local-llm is accepted
[x] LiteLLM /v1/models contains qwen-local
[x] LiteLLM /v1/messages returns a valid response
[x] llama.cpp logs show LiteLLM using /v1/chat/completions
[x] LiteLLM /v1/messages/count_tokens works
[x] Claude Code /status points to port 4000
[x] Claude Code uses qwen-local
[x] No Invalid API Key errors
[x] No "System message must be at the beginning" errors
[x] Claude Code can create and read test.txt
[x] Qwen does not enter an endless reasoning loop
```

---

### 3.5. Final Configurations

#### 3.5.1 Only after everything works -- update `.bashrc`

Once the manual test environment is proven, add the required variables to `~/.bashrc`:

```bash
export LOCAL_LLAMA_API_KEY="local-llm"
export LITELLM_MASTER_KEY="sk-YOUR-LITELLM-KEY"

export ANTHROPIC_BASE_URL="http://127.0.0.1:4000"
export ANTHROPIC_AUTH_TOKEN="$LITELLM_MASTER_KEY"

export ANTHROPIC_CUSTOM_MODEL_OPTION="qwen-local"
export ANTHROPIC_CUSTOM_MODEL_OPTION_NAME="Qwen 3.5 9B Local"
export CLAUDE_CODE_MAX_CONTEXT_TOKENS="16384"

export ANTHROPIC_DEFAULT_HAIKU_MODEL="qwen-local"
export CLAUDE_CODE_SUBAGENT_MODEL="inherit"
```

Do not keep the old direct llama.cpp Claude variable `export ANTHROPIC_API_KEY="local-llm"`. Claude Code should authenticate to LiteLLM using `ANTHROPIC_AUTH_TOKEN`, while LiteLLM authenticates to llama.cpp using `LOCAL_LLAMA_API_KEY`.

Reload `.bashrc` and verify:

```bash
source ~/.bashrc
echo "$ANTHROPIC_BASE_URL"              # http://127.0.0.1:4000
echo "$ANTHROPIC_CUSTOM_MODEL_OPTION"   # qwen-local
echo "$CLAUDE_CODE_MAX_CONTEXT_TOKENS"  # 16384
```

---

#### 3.5.2 Do not enable Qwen thinking yet

Keep `--reasoning off --reasoning-budget 0` until Claude Code reliably performs multi-step tool operations. Reasoning adds another variable and Qwen3.5 has already shown looping behaviour in this environment. After the complete Claude Code -> LiteLLM -> llama.cpp tool chain is proven, reasoning can be tested separately with a bounded budget.

---

#### 3.5.3 Fallback only if LiteLLM fails

The preferred route is LiteLLM. If LiteLLM still cannot translate Claude Code tool traffic reliably, the next fallback worth considering is Claude-Code-Router. Do not introduce it unless the LiteLLM architecture above has been fully tested and shown to fail.

---

#### 3.5.4 Final architecture

```
+------------------------------+
|         Claude Code          |
|  claude --model qwen-local   |
+------------------------------+
               |
               | Anthropic API /v1/messages
               | Bearer: LiteLLM key
               v
+------------------------------+
|           LiteLLM            |
|       127.0.0.1:4000         |
|  Anthropic -> OpenAI translate|
+------------------------------+
               |
               | OpenAI API /v1/chat/completions
               | Bearer: local-llm
               v
+------------------------------+
|         llama-server         |
|       127.0.0.1:8080         |
|       alias: qwen-local      |
+------------------------------+
               |
               v
+------------------------------+
|  Qwen3.5-9B-Q5_K_M.gguf     |
|  RTX 3060 12 GB              |
+------------------------------+
```

---

#### 3.5.5 Changing context size

1. Find the maximum context for the specific model. For example, `Qwen3.5-9B-Q5_K_M.gguf` supports up to 262144 tokens. Start with a smaller value and increase steadily once the model is proven stable.

2. Set `-c` when starting `llama-server`:

    ```bash
    ~/llama.cpp/build/bin/llama-server \
      -m ~/models/gguf/Qwen3.5-9B-Q5_K_M.gguf \
      --alias qwen-local \
      -ngl 99 \
      -fa on \
      -ctk q8_0 \
      -ctv q8_0 \
      -c 262144
    ```

    `-ctk` and `-ctv` control the KV cache quantisation. `-c` sets the context window size.

3. Update the environment variable:

    ```bash
    export CLAUDE_CODE_MAX_CONTEXT_TOKENS="262144"
    ```

4. Update `~/.claude/settings.json`:

    ```json
    "CLAUDE_CODE_MAX_CONTEXT_TOKENS": "262144"
    ```

5. Restart the stack in order:

    ```bash
    source ~/.bashrc
    ~/llama.cpp/build/bin/llama-server ...
    litellm --config ~/.config/litellm/config.yaml --host 127.0.0.1 --port 4000
    claude --model qwen-local
    ```







\newpage



## Chapter 4: Agentic Alternatives for Local Models

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

\newpage

## Chapter 5: Crush — Fully Local Agentic Stack

### [INSTALL] 5.1 Software Locations — Full Stack Reference

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

### 5.2 Why Crush

- Native `llamacpp` provider type — connects to llama.cpp server directly with no LiteLLM proxy needed *(defined)*
- Also supports `litellm` provider type for when you want LiteLLM as a model router (switch models without reconfiguring Crush) *(pending)*
- Auto-discovers available models from the backend *(defined)*
- MCP support (connect to Graph Studio, filesystem, or any MCP server) *(pending)*
- LSP integration (code navigation, go-to-definition) *(pending)*

### 5.3 Install

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

### 5.4 Config File Locations

Config files can be stored in multiple locations:

- Per-project: `.crush.json` in the project root *(defined)*
- Global (Windows): `%LOCALAPPDATA%\crush\crush.json` *(defined)*
- Global (Linux/WSL2): `~/.config/crush/crush.json` *(pending)*

### 5.5 Path A: Crush → llama.cpp (direct, recommended for local-only)

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

### 5.6 Models for Path A — Desktop vs Laptop (Updated)

llama.cpp loads one model at a time. Choose based on your machine configuration:

**Desktop-Optimised Models (fit in 12GB VRAM):**

| Model | Quantisation | Size | Strengths | Ollama tag |
|---|---|---|-----------|------------|
| Qwen3 8B Q5_K_M | Q5_K_M | ~5.9 GB | **Fastest**; leaves ~6GB VRAM headroom; quick coding, shell commands | `qwen3:8b` *(defined)* |
| Gemma 4 12B | Q4_K_M | ~7.6 GB | Strong general reasoning; multimodal support | `gemma4:12b` *(defined)* |
| DeepSeek-R1 14B | Q4_K_M | ~9 GB | Good reasoning + code generation | `deepseek-r1:14b` *(defined)* |
| DeepSeek-R1 8B | Q4_K_M | ~5 GB | Lightest option; fastest inference | `deepseek-r1:8b` *(defined)* |
| Qwen 3.5 9B Q5_K_M | Q5_K_M | ~6.6 GB | **Recommended default**; coding, reasoning, agents, multimodal | `qwen3.5:9b` *(defined)* |
| Gemma 3 12B IT | Q4_K_M | ~7 GB | Stable backup; writing, summarisation, multilingual | `gemma3:12b-it` *(defined)* |

**Laptop-Optimised Models (fit in 16GB VRAM):**

| Model | Quantisation | Size | Strengths |
|---|---|---|-----------|
| Devstral 24B | Q4_K_M | ~14 GB | Agentic coding; 46.8% SWE-Bench; fits in VRAM *(defined)* |
| Qwen3 8B Q5_K_M | Q5_K_M | ~5.9 GB | Leaves ~10GB VRAM headroom; fastest option *(defined)* |
| Qwen 3.5 9B Q5_K_M | Q5_K_M | ~6.6 GB | **Default**; excellent balance of quality and speed *(defined)* |
| DeepSeek-R1 14B | Q4_K_M | ~9 GB | Reasoning, math, code generation *(defined)* |
| Gemma 4 12B | Q4_K_M | ~7.6 GB | Harder reasoning, multimodal experiments *(defined)* |

**Quantisation Guidance:**
- **Q4_K_M**: Best balance of size and quality. Recommended for Gemma models and DeepSeek-R1 variants.
- **Q5_K_M**: Slightly higher fidelity with ~1GB more VRAM. Recommended for Qwen3.5 9B (default) and Qwen3 8B.
- **Q6_K**: Highest quality; use for Qwen3.5 9B when benchmarking or maximum quality is preferred over speed/VRAM headroom.

Devstral 24B (~14GB) works on both machines but spills approximately 2GB into RAM on the desktop — functional but not fully GPU-resident.

### 5.7 Downloading GGUF Models

Yes — it is as simple as going to Hugging Face and downloading the `.gguf` file directly:

1. Go to [huggingface.co](https://huggingface.co) and search for the model
2. Look for a repo that provides GGUF quantized files — usually from **bartowski** or **lmstudio-community** (reliable quantizers)
3. Download the `Q4_K_M` variant — good balance of size and quality
4. Save to `C:\models\`

**Direct searches on HuggingFace for recommended models:**

| Model | HuggingFace repo to search | Notes |
|---|---|-------|
| DeepSeek-R1 14B | `bartowski/DeepSeek-R1-Distill-Qwen-14B-GGUF` *(defined)* | Good reasoning + code; fits in 12GB VRAM |
| DeepSeek-R1 8B | `bartowski/DeepSeek-R1-Distill-Qwen-8B-GGUF` *(defined)* | Lightest option; fastest on desktop |
| Gemma 4 12B | `bartowski/gemma-3-12b-it-GGUF` *(defined)* | Strong general reasoning and multimodal support |
| Gemma 3 12B IT | `bartowski/gemma-3-12b-it-GGUF` *(defined)* | Mature backup model; writing, summarisation, multilingual |
| Devstral 24B | `bartowski/Devstral-Small-2505-GGUF` *(defined)* | Agentic coding; fits in 16GB VRAM (laptop) |
| Qwen 3.5 9B Q5_K_M | `bartowski/Qwen3.5-9B-Instruct-Q5_K_M-GGUF` | **Recommended default**; coding, reasoning, agents |
| Qwen 3.5 9B Q6_K | `bartowski/Qwen3.5-9B-Instruct-Q6_K-GGUF` | Higher fidelity; use for benchmarking or max quality |
| Qwen3 8B Q5_K_M | `bartowski/Qwen3-8B-Instruct-Q5_K_M-GGUF` | **Fast model**; leaves most VRAM headroom |

Download only the single `.gguf` file — no other files needed for llama.cpp.

**Recommended GGUF Quantizations:**
- **Q4_K_M**: Best balance of size and quality (~4-bit). Recommended for Gemma 4 12B, DeepSeek-R1 variants, Devstral 24B.
- **Q5_K_M**: Slightly higher fidelity with ~1GB more VRAM usage. Recommended for Qwen3.5 9B (default) and Qwen3 8B.
- **Q6_K**: Highest quality among common quantizations (~6-bit). Use for Qwen3.5 9B when maximum quality is preferred over VRAM headroom.

**Note on Gemma 4 vs Gemma 3:** The HuggingFace repos may still use the `gemma-3-12b-it` naming even for Gemma 4 models. Look for the latest model version or check the model card for release date.

**To switch models:** stop the server, restart with a different `-m` flag, update `model` in `.crush.json` to match:

```powershell
# Desktop -- Qwen3 8B (fastest, leaves most VRAM)
.\llama-server.exe -m C:\models\Qwen3-8B-Q5_K_M.gguf -ngl 999 -c 32768

# Desktop -- Qwen3.5 9B (recommended default for coding)
.\llama-server.exe -m C:\models\Qwen3.5-9B-Q5_K_M.gguf -ngl 999 -c 32768

# Desktop -- Gemma 4 12B (multimodal, strong reasoning)
.\llama-server.exe -m C:\models\Gemma-4-12B-Q4_K_M.gguf -ngl 999 -c 32768

# Laptop -- Devstral 24B (agentic coding, fits in VRAM)
.\llama-server.exe -m C:\models\Devstral-24B-Q4_K_M.gguf -ngl 999 -c 32768

# Laptop -- Qwen3 8B (fastest with most context headroom)
.\llama-server.exe -m C:\models\Qwen3-8B-Q5_K_M.gguf -ngl 999 -c 32768
```

Update `.crush.json` model field to match:

```json
"model": "llamacpp/Qwen3-8B-Q5_K_M"
```

Crush auto-detects from `/v1/models` — if only one model is loaded you may not need to set this explicitly.

**Model switching workflow:**
1. Stop the current llama.cpp server (Ctrl+C)
2. Start new server with different `-m` flag pointing to desired `.gguf` file
3. Update `model` field in `.crush.json` to match the new model name (optional if Crush auto-detects)
4. Restart Crush to pick up the new configuration

### 5.8 Path B: Crush → LiteLLM → llama.cpp (use when you want model switching)

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

### 5.9 Tool Calling Note

Crush's tool-calling reliability depends on the model's native function-calling support. Devstral 24B and Qwen3 30B both support tool calling — prefer these for agentic tasks. Smaller or older models may produce unreliable tool call JSON. This is the same caveat as Aider.

### 5.10 Crush vs Aider vs Claude Code

| Feature | Crush | Aider | Claude Code |
|---|-------|--------|-------------|
| Interface | TUI (interactive) | CLI (command + session) | CLI (interactive) |
| Best model | Local llama.cpp | Local or cloud | Anthropic (Claude) |
| MCP support | Yes | No | Yes |
| Git integration | Yes | Yes (core feature) | Yes |
| Cost | Free | Free | Requires API key |
| Offline capable | Yes (Path A) | Yes | No |
