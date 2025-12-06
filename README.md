# MachineID.io + LangChain Starter Template
### Add device limits to LangChain agents in <10 lines.

A minimal template showing how to use MachineID.io to control LangChain-based agents or workers.  
Use this starter to prevent uncontrolled scaling, enforce hard device limits, and ensure each agent validates before running.

The free org key supports **3 devices**, with higher limits available on paid plans.

---

## What this repo gives you

- A simple Python script (`langchain_agent.py`) that:
  - Reads `MACHINEID_ORG_KEY` from the environment
  - Calls `/api/v1/devices/register` with `x-org-key` and a `deviceId`
  - Calls `/api/v1/devices/validate` before running
  - Runs a LangChain prompt that outputs a **demo 3-step example** (for illustration only).
- A minimal `requirements.txt` with no heavy dependencies
- A pattern suitable for:
  - LangChain workers  
  - LCEL chains  
  - Background jobs  
  - Multi-agent orchestration  
  - Local experimentation

---

## Quick start

### 1. Clone this repo or click **“Use this template.”**

---

### 2. Install dependencies in a virtual environment:

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 3. Get a free org key (supports 3 devices):

- Visit https://machineid.io  
- Click **“Generate free org key”**  
- Copy the key (it begins with `org_...`)

---

### 4. Set environment variables:

```bash
export MACHINEID_ORG_KEY=org_your_key_here
export OPENAI_API_KEY=sk_your_openai_key_here
export MACHINEID_DEVICE_ID=langchain-agent-01
```

**One-liner (run immediately):**

```bash
MACHINEID_ORG_KEY=org_xxx OPENAI_API_KEY=sk_xxx python langchain_agent.py
```

---

### 5. Run the starter:

```bash
python langchain_agent.py
```

You’ll see a register call, a validate call, and a LangChain response showing a **demo 3-step example** (illustration only).

---

## How it works

1. The agent registers itself with MachineID.io.  
2. It validates before running any work.  
3. If validation passes, it runs a simple LangChain chain.  
4. If not allowed, it exits immediately.

**Drop the same register/validate block into any LangChain agent, LCEL chain, background job, Celery worker, or RQ worker.**  
This ensures all your agents follow the same device policy and stay within your org limits.

This prevents runaway agent spawning and ensures controlled scaling across your fleet.

---

## Files in this repo

- `langchain_agent.py` — Register + validate + LangChain example  
- `requirements.txt` — Minimal dependencies  
- `LICENSE` — MIT licensed

---

## Links

Dashboard → https://machineid.io/dashboard  
Generate free org key → https://machineid.io  
Docs → https://machineid.io/docs  
API → https://machineid.io/api  

---

## Other templates

→ Python starter: https://github.com/machineid-io/machineid-python-starter  
→ CrewAI:       https://github.com/machineid-io/crewai-machineid-template  
→ OpenAI Swarm: https://github.com/machineid-io/swarm-machineid-template  

---

## How plans work (quick overview)

- Plans are per **org**, each with its own `orgApiKey`.  
- Device limits apply to unique `deviceId` values registered via `/devices/register`.  
- When you upgrade or change plans in Stripe, limits update immediately — **your agents do not need new code**.

MIT licensed · Built by MachineID.io

