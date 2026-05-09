# Microsoft 365 Login Risk Explainer Agent

## Agent Name

Microsoft 365 Login Risk Explainer Agent

---

## Agent Purpose

This agent analyzes Microsoft 365 login events and explains whether a login event appears normal or suspicious.

The agent is designed for a cybersecurity use case where suspicious Microsoft 365 account activity may indicate credential compromise, brute-force attempts, or misuse of valid cloud accounts.

The user provides login event details such as login hour, city, number of failed attempts, amount of data sent, and the accessed Microsoft 365 cloud service.  
The agent then uses a Python tool to calculate a risk score, identify suspicious indicators, map the behavior to MITRE ATT&CK techniques, and recommend a response action.

This lab connects to the previous labs:

- **Lab 1** analyzed the Jingle Thief CTI report, where attackers used phishing and smishing to steal Microsoft 365 credentials.
- **Lab 2** used anomaly detection to identify suspicious Microsoft 365 login behavior.
- **Lab 3** adds an LLM agent that can explain a specific login event by calling a Python tool.

---

## Agent Tool

The agent uses one Python tool:

### `analyze_login_event`

This tool receives Microsoft 365 login event details and returns a structured risk analysis.

#### Tool Input

The tool expects the following fields:

| Field | Type | Description |
|---|---|---|
| `hour` | integer | Login hour between 0 and 23 |
| `city` | string | City or location of the login |
| `failed_attempts` | integer | Number of failed login attempts before the successful login |
| `bytes_sent` | integer | Amount of data sent during the session |
| `cloud_service` | string | Microsoft 365 service accessed, such as SharePoint, OneDrive, Exchange, Teams, or Entra ID |

#### Tool Output

The tool returns:

| Output Field | Description |
|---|---|
| `risk_score` | Numerical score between 0 and 100 |
| `risk_level` | Low, medium, or high |
| `suspicious_indicators` | List of suspicious behaviors detected in the event |
| `mitre_mapping` | Related MITRE ATT&CK techniques |
| `recommendation` | Suggested security response |

---

## Risk Logic

The tool calculates risk based on simple rule-based indicators.

| Indicator | Reason |
|---|---|
| Unusual login hour | Logins outside normal working hours may indicate unauthorized access |
| Uncommon login location | A login from an unexpected city may suggest credential misuse |
| Many failed login attempts | Multiple failed attempts may indicate brute force activity |
| High data transfer volume | Large data transfer may indicate suspicious account activity |
| Access to sensitive cloud services | Services such as SharePoint, OneDrive, Exchange, and Entra ID may contain sensitive organizational data |

---

## MITRE ATT&CK Mapping

The agent maps suspicious login behavior to the following MITRE ATT&CK techniques:

| Technique | Description |
|---|---|
| **T1078.004 — Valid Accounts: Cloud Accounts** | Use of legitimate cloud accounts for unauthorized access |
| **T1110 — Brute Force** | Multiple login attempts that may indicate password guessing or credential attacks |
| **T1526 — Cloud Service Discovery** | Discovery or access of cloud services such as SharePoint, OneDrive, Exchange, or Entra ID |

---

## Example Interaction

### User Input

```text
Analyze this login event: hour=3, city=Moscow, failed_attempts=12, bytes_sent=15000, cloud_service=SharePoint
```

### Tool Output

```json
{
  "risk_score": 100,
  "risk_level": "high",
  "suspicious_indicators": [
    "Unusual login hour",
    "Uncommon login location",
    "High number of failed login attempts",
    "High data transfer volume",
    "Access to sensitive cloud service: SharePoint"
  ],
  "mitre_mapping": [
    "T1078.004 — Valid Accounts: Cloud Accounts",
    "T1110 — Brute Force",
    "T1526 — Cloud Service Discovery"
  ],
  "recommendation": "Investigate the login event, review the account activity, and consider resetting credentials."
}
```

### Agent Explanation

The agent explains that the event has a high risk level because it contains multiple suspicious indicators:

- The login occurred at an unusual hour.
- The login came from an uncommon location.
- There were many failed login attempts.
- The session included high data transfer.
- The accessed service was SharePoint, which may contain sensitive organizational data.

The behavior maps to MITRE ATT&CK techniques such as **Valid Accounts**, **Brute Force**, and **Cloud Service Discovery**.

The recommended action is to investigate the login event, review the account activity, and consider resetting the user's credentials.

---

## Example of a Lower-Risk Event

### User Input

```text
Analyze this login event: hour=10, city=Tel Aviv, failed_attempts=1, bytes_sent=1200, cloud_service=Teams
```

### Expected Behavior

The tool should return a lower risk score because the event looks closer to normal business activity:

- Login during working hours
- Common city
- Low number of failed attempts
- Normal data transfer
- Access to a common collaboration service

---

## How the Agent Works

The flow of the application is:

```text
User submits login event
        ↓
LLM Agent receives the message
        ↓
Agent decides to call the Python tool
        ↓
analyze_login_event() calculates risk
        ↓
Tool returns JSON result
        ↓
Agent explains the result in natural language
```

This demonstrates the difference between a regular chatbot and an LLM agent.  
A regular chatbot only generates text, while this agent can call a Python function and use the returned result to produce a more structured cybersecurity analysis.

---

## Environment Variables

The application uses environment variables from the `.env` file.

Example `.env` configuration:

```env
API_KEY=your_api_key_here
MODEL=llama-3.3-70b-versatile
API_BASE_URL=https://api.groq.com/openai/v1
```

The real `.env` file should not be committed to GitHub.

Use `.env.example` to show the expected configuration format without exposing a real API key.

---

## How to Run

From the `lab3` directory, run:

```bash
docker compose up --build
```

Then open the Chainlit application in the browser:

```text
http://localhost:8000
```

---

## Test Prompt

Use this prompt to test that the agent calls the Python tool:

```text
Analyze this login event: hour=3, city=Moscow, failed_attempts=12, bytes_sent=15000, cloud_service=SharePoint
```

Expected result:

- The Python tool `analyze_login_event` is executed.
- The tool returns a structured JSON risk analysis.
- The agent explains the risk level, suspicious indicators, MITRE ATT&CK mapping, and recommended action.

---

## Notes

This is a simplified educational prototype.  
The risk score is based on rule-based logic and is not intended to replace a real Security Information and Event Management system, Identity Protection system, or production-grade anomaly detection model.

In a real-world environment, the agent should be connected to real Microsoft 365 audit logs, identity telemetry, historical user behavior, and additional detection signals.