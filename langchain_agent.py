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
            "Missing MACHINEID_ORG_KEY. Set it in your environment.\n"
            "Example:\n"
            "  export MACHINEID_ORG_KEY=org_your_key_here\n"
        )
    return org_key


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
    data = resp.json()

    print(f"✔ register response: status={data.get('status')}, handler={data.get('handler')}")
    return data


# ---------------------------------------
# Validate device
# ---------------------------------------
def validate_device(org_key: str, device_id: str) -> Dict[str, Any]:
    headers = {"x-org-key": org_key}
    params = {"deviceId": device_id}

    print(f"→ Validating device '{device_id}' via {VALIDATE_URL} ...")
    resp = requests.get(VALIDATE_URL, headers=headers, params=params, timeout=10)
    data = resp.json()

    print(
        f"✔ validate response: status={data.get('status')}, "
        f"handler={data.get('handler')}, allowed={data.get('allowed')}, reason={data.get('reason')}"
    )
    return data


# ---------------------------------------
# MachineID-aware LangChain example
# ---------------------------------------
def run_langchain_example() -> str:
    print("\n→ Building minimal LangChain chain...")

    model = ChatOpenAI(model="gpt-4o-mini")

    # ⭐ Clean, concise, aligned with CrewAI + Swarm examples
    prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a concise assistant."),
        (
    "human",
    "Give me 3 practical steps for using LangChain workers safely with MachineID.io. "
    "MachineID.io provides device-level registration and validation to keep worker fleets "
    "predictable and under control. Focus your steps on registering each worker with a unique, "
    "stable deviceId (such as a name or UUID), validating with MachineID.io before running tasks, "
    "and stopping workers when validation indicates a limit has been reached or the worker "
    "is not allowed to continue."
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
    print("  planTier    :", reg.get("planTier"))
    print("  limit       :", reg.get("limit"))
    print("  devicesUsed :", reg.get("devicesUsed"))
    print("  remaining   :", reg.get("remaining"))
    print()

    if reg.get("status") == "limit_reached":
        print("🚫 Plan limit reached. Agent should not start.")
        sys.exit(0)

    # 2) Validate device
    print("Waiting 2 seconds before validating...")
    time.sleep(2)

    val = validate_device(org_key, device_id)

    print("\nValidation summary:")
    print("  allowed :", val.get("allowed"))
    print("  reason  :", val.get("reason"))
    print()

    if not val.get("allowed"):
        print("🚫 Device not allowed. Agent should exit.")
        sys.exit(0)

    # 3) Run LangChain example
    print("✅ Device allowed. Running LangChain + MachineID example...\n")
    result = run_langchain_example()

    print("✔ LangChain result:\n" + result)
    print("\nDone. langchain_agent.py completed successfully.")


if __name__ == "__main__":
    main()
