# MachineID + LangChain Starter Template
### Add hard device limits to LangChain agents with one small register/validate block.

A minimal LangChain starter showing how to wrap any agent or worker with MachineID device registration and validation.  
Use this template to prevent uncontrolled scaling, enforce hard device limits, and ensure each agent validates before running.

The free org key supports **3 devices**, with higher limits available on paid plans.

---

## What this repo gives you

- A simple Python script (`langchain_agent.py`) that:
  - Reads `MACHINEID_ORG_KEY` from the environment  
  - Calls **POST** `/api/v1/devices/register` with `x-org-key` and a `deviceId`  
  - Calls **POST** `/api/v1/devices/validate` (canonical) before running  
  - Enforces a **hard gate**:
    - If `allowed == false`, execution stops immediately  
  - Prints stable decision metadata:
    - `allowed`
    - `code`
    - `request_id`
  - Runs a LangChain prompt that outputs a demo 3-step example (illustration only)  
- A minimal `requirements.txt`
- A pattern suitable for:
  - LangChain workers  
  - LCEL chains  
  - Background jobs  
  - Multi-agent orchestration  
  - Local experimentation  

---

## Quick start

### 1. Clone this repo or click **“Use this template.”**

```bash
git clone https://github.com/machineid-io/langchain-machineid-template.git
cd langchain-machineid-template
```

---

### 2. Install dependencies in a virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 3. Get a free org key (supports 3 devices)

Visit https://machineid.io  
Click **“Generate free org key”**  
Copy the key (it begins with `org_`)

---

### 4. Set environment variables

```bash
export MACHINEID_ORG_KEY=org_your_key_here
export OPENAI_API_KEY=sk_your_openai_key_here
```

Optional override:

```bash
export MACHINEID_DEVICE_ID=langchain:agent-01
```

**One-liner (run immediately):**

```bash
MACHINEID_ORG_KEY=org_xxx OPENAI_API_KEY=sk_xxx python langchain_agent.py
```

---

### 5. Run the starter

```bash
python langchain_agent.py
```

You’ll see a register call, a validate decision (`allowed/code/request_id`), and then a LangChain response.

---

## How it works

1. The worker registers itself with MachineID (idempotent)  
2. It validates (POST, canonical) before running any work  
3. If `allowed == true`, it runs a LangChain chain  
4. If `allowed == false`, it exits immediately (hard gate)  

This prevents accidental worker explosions and enforces clean scaling behavior.

---

## Using this in your own LangChain agents

To integrate MachineID:

- Call **register** when your worker starts  
- Call **validate** before executing major actions or generating output  
- Stop execution immediately when `allowed == false`  

Drop the same register/validate block into any LangChain agent, LCEL chain, or background worker.  
This is all you need to enforce simple device limits across your LangChain fleet.

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

---

## Other templates

→ Python starter: https://github.com/machineid-io/machineid-python-starter  
→ CrewAI:        https://github.com/machineid-io/crewai-machineid-template  
→ OpenAI Swarm:  https://github.com/machineid-io/swarm-machineid-template  

---

## How plans work (quick overview)

- Plans are per **org**, each with its own `orgApiKey`  
- Device limits apply to unique `deviceId` values registered via `/api/v1/devices/register`  
- Plan changes take effect immediately — no agent code changes required  

MIT licensed · Built by MachineID
