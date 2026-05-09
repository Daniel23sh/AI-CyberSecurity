import os
import json
import chainlit as cl
from dotenv import load_dotenv
from autogen import ConversableAgent


load_dotenv()

API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL", "llama-3.3-70b-versatile")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.groq.com/openai/v1")

if not API_KEY:
    raise ValueError("API_KEY is missing. Please add it to lab3/.env")


llm_config = {
    "config_list": [
        {
            "model": MODEL,
            "api_key": API_KEY,
            "base_url": API_BASE_URL,
        }
    ],
    "temperature": 0.2,
}


def analyze_login_event(
    hour: int,
    city: str,
    failed_attempts: int,
    bytes_sent: int,
    cloud_service: str,
) -> str:
    """
    Analyze a Microsoft 365 login event and return a simple risk assessment.

    Args:
        hour: Login hour, from 0 to 23.
        city: Login location.
        failed_attempts: Number of failed login attempts before success.
        bytes_sent: Amount of data sent during the session.
        cloud_service: Microsoft 365 service accessed.

    Returns:
        JSON string with risk score, risk level, suspicious indicators, and MITRE mapping.
    """

    risk_score = 0
    indicators = []
    mitre_mapping = set()

    common_cities = {"Tel Aviv", "Jerusalem", "Haifa", "Beer Sheva", "Ramat Gan"}
    sensitive_cloud_services = {"SharePoint", "OneDrive", "Exchange", "Entra ID"}

    if hour < 7 or hour > 20:
        risk_score += 25
        indicators.append("Unusual login hour")
        mitre_mapping.add("T1078.004 — Valid Accounts: Cloud Accounts")

    if city not in common_cities:
        risk_score += 25
        indicators.append("Uncommon login location")
        mitre_mapping.add("T1078.004 — Valid Accounts: Cloud Accounts")

    if failed_attempts >= 5:
        risk_score += 25
        indicators.append("High number of failed login attempts")
        mitre_mapping.add("T1110 — Brute Force")

    if bytes_sent >= 7000:
        risk_score += 15
        indicators.append("High data transfer volume")
        mitre_mapping.add("T1078.004 — Valid Accounts: Cloud Accounts")

    if cloud_service in sensitive_cloud_services:
        risk_score += 10
        indicators.append(f"Access to sensitive cloud service: {cloud_service}")
        mitre_mapping.add("T1526 — Cloud Service Discovery")

    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        risk_level = "high"
    elif risk_score >= 40:
        risk_level = "medium"
    else:
        risk_level = "low"

    result = {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "suspicious_indicators": indicators,
        "mitre_mapping": sorted(list(mitre_mapping)),
        "recommendation": (
            "Investigate the login event, review the account activity, and consider resetting credentials."
            if risk_level in ["medium", "high"]
            else "No immediate action is required, but the event should remain logged."
        ),
    }

    return json.dumps(result, indent=2)


agent = ConversableAgent(
    name="m365_login_risk_explainer_agent",
    system_message=(
        "You are a Microsoft 365 Login Risk Explainer Agent. "
        "Your task is to help users analyze Microsoft 365 login events. "
        "When the user provides login event details such as hour, city, failed_attempts, "
        "bytes_sent, and cloud_service, you must call the analyze_login_event tool. "
        "After receiving the tool result, explain the risk level, suspicious indicators, "
        "MITRE ATT&CK mapping, and recommended action in clear English. "
        "Keep the explanation concise and technical. "
        "If the user does not provide enough fields, ask them for the missing values."
    ),
    llm_config=llm_config,
    human_input_mode="NEVER",
    functions=[analyze_login_event],
)


@cl.on_chat_start
async def on_chat_start():
    await cl.Message(
        content=(
            "# Microsoft 365 Login Risk Explainer Agent\n\n"
            "Send me a Microsoft 365 login event and I will analyze its risk using a Python tool.\n\n"
            "Example:\n\n"
            "`Analyze this login event: hour=3, city=Moscow, failed_attempts=12, "
            "bytes_sent=15000, cloud_service=SharePoint`"
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    user_message = message.content

    # Step 1: Ask the agent to decide whether a tool should be called
    response = await cl.make_async(agent.generate_reply)(
        messages=[
            {
                "role": "user",
                "content": user_message,
            }
        ]
    )

    # Step 2: If the agent requested a tool call, execute the tool manually
    if isinstance(response, dict) and response.get("tool_calls"):
        tool_call = response["tool_calls"][0]
        function_name = tool_call["function"]["name"]

        try:
            arguments = json.loads(tool_call["function"]["arguments"])
        except json.JSONDecodeError:
            await cl.Message(
                content=(
                    "### Error\n\n"
                    "The agent tried to call a tool, but the tool arguments were not valid JSON."
                )
            ).send()
            return

        if function_name == "analyze_login_event":
            try:
                tool_result = analyze_login_event(**arguments)
            except TypeError as e:
                await cl.Message(
                    content=(
                        "### Missing or Invalid Fields\n\n"
                        "Please provide all required login event fields:\n\n"
                        "- `hour`\n"
                        "- `city`\n"
                        "- `failed_attempts`\n"
                        "- `bytes_sent`\n"
                        "- `cloud_service`\n\n"
                        f"Technical details: `{str(e)}`"
                    )
                ).send()
                return

            # Step 3: Show the raw tool output clearly
            await cl.Message(
                content=(
                    "## Tool Output\n\n"
                    "The Python tool `analyze_login_event` was executed successfully.\n\n"
                    "```json\n"
                    f"{tool_result}\n"
                    "```"
                )
            ).send()

            # Step 4: Ask the agent to explain the tool result
            final_response = await cl.make_async(agent.generate_reply)(
                messages=[
                    {
                        "role": "user",
                        "content": user_message,
                    },
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": response["tool_calls"],
                    },
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": function_name,
                        "content": tool_result,
                    },
                    {
                        "role": "user",
                        "content": (
                            "Explain the tool result clearly and professionally. "
                            "Use the following structure: "
                            "Risk Level, Suspicious Indicators, MITRE ATT&CK Mapping, "
                            "and Recommended Action. "
                            "Do not repeat the raw JSON."
                        ),
                    },
                ]
            )

            if isinstance(final_response, dict):
                final_content = final_response.get("content", str(final_response))
            else:
                final_content = str(final_response)

            await cl.Message(
                content=(
                    "## Agent Explanation\n\n"
                    f"{final_content}"
                )
            ).send()

            return

    # Step 5: Fallback if no tool was called
    if isinstance(response, dict):
        content = response.get("content", str(response))
    else:
        content = str(response)

    await cl.Message(content=content).send()