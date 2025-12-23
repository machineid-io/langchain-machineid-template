#!/usr/bin/env python3

import os
import sys
import time
from typing import Any, Dict

import requests
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# ---------------------------------------
# MachineID Endpoints
# ---------------------------------------
BASE_URL = os.getenv("MACHINEID_BASE_URL", "https://machineid.io").rstrip("/")
REGISTER_URL = f"{BASE_URL}/api/v1/devices/register"
VALIDATE_URL = f"{BASE_URL}/api/v1/devices/validate"


# ---------------------------------------
# Helper: env + required env
# ---------------------------------------
def env(name: str, default: str | None = None) -> str | None:
    v = os.getenv(name)
    if v is None:
        return default
    v = v.strip()
    return v if v else default


def must_env(name: str) -> str:
    v = env(name)
    if not v:
        print(f"[fatal] Missing required env var: {name}", file=sys.stderr)
        sys.exit(2)
    return v


# ---------------------------------------
# HTTP helper: POST JSON (canonical)
# ---------------------------------------
def post_json(url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout_s: int = 10) -> Dict[str, Any]:
    resp = requests.post(url, headers=headers, json=payload, timeout=timeout_s)
    try:
        data = resp.json()
    except Exception:
        print("❌ Could not parse JSON response.")
        print("Status code:", resp.status_code)
        print("Body:", resp.text)
        raise

    if resp.status_code >= 400:
        # normalize error shape for logging/debugging
        if isinstance(data, dict) and data.get("error"):
            return {"status": "error", "error": data.get("error"), "http": resp.status_code}
        return {"status": "error", "error": f"HTTP {resp.status_code}", "http": resp.status_code, "body": data}

    return data


# ---------------------------------------
# Register device (idempotent)
# ---------------------------------------
def register_device(org_key: str, device_id: str) -> Dict[str, Any]:
    headers = {"x-org-key": org_key, "Content-Type": "application/json"}
    payload = {"deviceId": device_id}

    print(f"→ Registering device '{device_id}'")
    data = post_json(REGISTER_URL, headers, payload)

    print(f"✔ register status={data.get('status')}")
    return data


# ---------------------------------------
# Validate device (POST canonical, hard gate)
# ---------------------------------------
def validate_device(org_key: str, device_id: str) -> Dict[str, Any]:
    headers = {"x-org-key": org_key, "Content-Type": "application/json"}
    payload = {"deviceId": device_id}

    print(f"→ Validating device '{device_id}' (POST canonical)")
    data = post_json(VALIDATE_URL, headers, payload)

    allowed = data.get("allowed")
    code = data.get("code")
    request_id = data.get("request_id")
    print(f"✔ decision allowed={allowed} code={code} request_id={request_id}")
    return data


# ---------------------------------------
# MachineID-aware LangChain example
# ---------------------------------------
def run_langchain_example() -> str:
    print("\n→ Building minimal LangChain chain...")

    model = ChatOpenAI(model="gpt-4o-mini")

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a concise assistant."),
            (
                "human",
                (
                    "Give me 3 short steps for using LangChain workers safely with MachineID. "
                    "MachineID is a lightweight device-level gate: each worker uses a user-assigned deviceId, "
                    "registers once, and validates before running tasks so organizations can enforce simple device "
                    "limits and prevent uncontrolled scaling. Keep each step brief and practical, focusing only on "
                    "registering, validating, and stopping workers when validation fails."
                ),
            ),
        ]
    )

    chain = prompt | model
    response = chain.invoke({})
    return response.content


# ---------------------------------------
# Main
# ---------------------------------------
def main() -> None:
    org_key = must_env("MACHINEID_ORG_KEY")

    # deterministic, non-identifying default
    device_id = env("MACHINEID_DEVICE_ID", "langchain:agent-01") or "langchain:agent-01"

    if not org_key.startswith("org_"):
        print("[fatal] MACHINEID_ORG_KEY must start with org_", file=sys.stderr)
        sys.exit(2)

    print("✔ MACHINEID_ORG_KEY loaded:", org_key[:12] + "…")
    print("Using base_url:", BASE_URL)
    print("Using device_id:", device_id)
    print()

    # 1) Register (idempotent)
    reg = register_device(org_key, device_id)
    reg_status = reg.get("status")

    print("\nRegistration summary:")
    if reg.get("planTier") is not None:
        print("  planTier    :", reg.get("planTier"))
    if reg.get("limit") is not None:
        print("  limit       :", reg.get("limit"))
    if reg.get("devicesUsed") is not None:
        print("  devicesUsed :", reg.get("devicesUsed"))
    print()

    if reg_status not in ("ok", "exists"):
        # If register fails, do not proceed. This is a safety boundary.
        print("🚫 Register did not succeed. Exiting.")
        sys.exit(1)

    # 2) Validate (hard gate)
    time.sleep(1)
    val = validate_device(org_key, device_id)

    allowed = bool(val.get("allowed", False))
    code = val.get("code")
    request_id = val.get("request_id")

    print("\nValidation summary:")
    print("  allowed    :", allowed)
    print("  code       :", code)
    print("  request_id :", request_id)
    print()

    if not allowed:
        print("🚫 Execution denied (hard gate). Exiting immediately.")
        sys.exit(0)

    # 3) Run LangChain example
    print("✅ Execution allowed. Running LangChain example...\n")
    result = run_langchain_example()

    print("✔ LangChain result:\n" + result)
    print("\nDone. langchain_agent.py completed successfully.")


if __name__ == "__main__":
    main()
