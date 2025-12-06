import os
import sys
import time
from typing import Any, Dict

import requests
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


# ---------------------------------------
# MachineID.io Endpoints
# ---------------------------------------
BASE_URL = "https://machineid.io"
REGISTER_URL = f"{BASE_URL}/api/v1/devices/register"
VALIDATE_URL = f"{BASE_URL}/api/v1/devices/validate"


# ---------------------------------------
# Helper: Load org key
# ---------------------------------------
def get_org_key() -> str:
    org_key = os.getenv("MACHINEID_ORG_KEY")
    if not org_key:
        raise RuntimeError(
            "Missing MACHINEID_ORG_KEY. Set it in your environment or via a .env file.\n"
            "Example:\n"
            "  export MACHINEID_ORG_KEY=org_your_key_here\n"
        )
    return org_key.strip()


# ---------------------------------------
# Register device
# ---------------------------------------
def register_device(org_key: str, device_id: str) -> Dict[str, Any]:
    headers = {
        "x-org-key": org_key,
        "Content-Type": "application/json",
    }
    payload = {"deviceId": device_id}

    print(f"→ Registering device '{device_id}' via {REGISTER_URL} ...")
    resp = requests.post(REGISTER_URL, headers=headers, json=payload, timeout=10)

    try:
        data = resp.json()
    except Exception:
        print("❌ Could not parse JSON from register response.")
        print("Status code:", resp.status_code)
        print("Body:", resp.text)
        raise

    status = data.get("status")
    handler = data.get("handler")
    print(f"✔ register response: status={status}, handler={handler}")
    return data


# ---------------------------------------
# Validate device
# ---------------------------------------
def validate_device(org_key: str, device_id: str) -> Dict[str, Any]:
    headers = {"x-org-key": org_key}
    params = {"deviceId": device_id}

    print(f"→ Validating device '{device_id}' via {VALIDATE_URL} ...")
    resp = requests.get(VALIDATE_URL, headers=headers, params=params, timeout=10)

    try:
        data = resp.json()
    except Exception:
        print("❌ Could not parse JSON from validate response.")
        print("Status code:", resp.status_code)
        print("Body:", resp.text)
        raise

    status = data.get("status")
    handler = data.get("handler")
    allowed = bool(data.get("allowed", False))
    reason = data.get("reason", "unknown")

    print(
        f"✔ validate response: status={status}, "
        f"handler={handler}, allowed={allowed}, reason={reason}"
    )
    return data


# ---------------------------------------
# MachineID-aware LangChain example
# ---------------------------------------
def run_langchain_example() -> str:
    print("\n→ Building minimal LangChain chain...")

    model = ChatOpenAI(model="gpt-4o-mini")

    # Clean, concise prompt aligned with CrewAI + Swarm examples
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a concise assistant."),
            (
                "human",
                (
                    "Give me 3 short steps for using LangChain workers safely with MachineID.io. "
                    "MachineID.io is a lightweight device-level gate: each worker uses a user-assigned deviceId, "
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
    org_key = get_org_key()
    device_id = os.getenv("MACHINEID_DEVICE_ID", "langchain-agent-01")

    print("✔ MACHINEID_ORG_KEY loaded:", org_key[:12] + "...")
    print("Using device_id:", device_id)
    print()

    # 1) Register device
    reg = register_device(org_key, device_id)

    print("\nRegistration summary:")
    plan_tier = reg.get("planTier")
    limit = reg.get("limit")
    devices_used = reg.get("devicesUsed")
    remaining = reg.get("remaining")

    if plan_tier is not None:
        print("  planTier    :", plan_tier)
    if limit is not None:
        print("  limit       :", limit)
    if devices_used is not None:
        print("  devicesUsed :", devices_used)
    if remaining is not None:
        print("  remaining   :", remaining)
    print()

    if reg.get("status") == "limit_reached":
        print("🚫 Plan limit reached. Agent should not start.")
        sys.exit(0)

    # 2) Validate device
    print("Waiting 2 seconds before validating...")
    time.sleep(2)

    val = validate_device(org_key, device_id)
    allowed = bool(val.get("allowed", False))
    reason = val.get("reason", "unknown")

    print("\nValidation summary:")
    print("  allowed :", allowed)
    print("  reason  :", reason)
    print()

    if not allowed:
        print("🚫 Device not allowed. Agent should exit.")
        sys.exit(0)

    # 3) Run LangChain example
    print("✅ Device allowed. Running LangChain + MachineID example...\n")
    result = run_langchain_example()

    print("✔ LangChain result:\n" + result)
    print("\nDone. langchain_agent.py completed successfully.")


if __name__ == "__main__":
    main()
