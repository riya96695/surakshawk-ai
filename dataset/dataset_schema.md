# SuraksHawk AI — Dataset Schema

## 1. Dataset Purpose

The SuraksHawk AI dataset is used to develop, validate, and evaluate the system's ability to detect phishing, fraud, scams, and social-engineering attempts in digital communication.

The dataset is designed to support:

- NLP-based scam classification
- Detection of social-engineering indicators
- Language and communication-type analysis
- Risk-scoring and contextual analysis
- End-to-end system testing
- False-positive and false-negative analysis

---

## 2. Record Definition

Each dataset record represents one communication instance.

A communication instance may be:

- An SMS message
- A WhatsApp message
- An email
- A simulated call transcript

Each record contains the original communication content together with manually assigned ground-truth labels describing its scam classification and social-engineering characteristics.

The ground-truth labels represent the expected interpretation of the communication and must not be changed merely because a model produces an incorrect prediction.

---

## 3. Dataset Types

The dataset is divided into the following sets:

### Training Set

Used by the NLP/model-development process to learn patterns associated with scams and legitimate communication.

### Validation Set

Used during model development to tune and compare approaches without using the final test data.

### Test Set

Reserved for final evaluation of model performance. Test labels must not be used to tune the model.

### Golden Scenarios

A small collection of carefully designed end-to-end scenarios used to verify whether the complete SuraksHawk pipeline produces the expected risk level and intervention.
## 4. Message Dataset Schema

The primary message dataset contains one row per communication instance.

### 4.1 Core Fields

| Field | Data Type | Required | Allowed Values / Format | Description |
|---|---|---|---|---|
| `id` | String | Yes | Unique identifier, e.g. `S001` | Unique identifier for the dataset record. |
| `text` | String | Yes | Free text | The communication content being analyzed. |
| `label` | String | Yes | `SCAM`, `LEGITIMATE` | Ground-truth classification of the communication. |
| `scam_type` | String | Yes | Defined scam categories or `NOT_APPLICABLE` | The specific scam/social-engineering category represented by the communication. |
| `language` | String | Yes | `ENGLISH`, `HINDI`, `HINGLISH`, `ROMANIZED_HINDI`, `OTHER` | Primary language or language form used in the communication. |
| `communication_type` | String | Yes | `SMS`, `WHATSAPP`, `EMAIL`, `CALL_TRANSCRIPT` | Simulated communication channel represented by the record. |

### 4.2 Core Field Rules

#### `id`

Every record must have a unique ID.

Format:

```text
S001
S002
S003
...
```

## 5. Scam Type Taxonomy

Each record labeled `SCAM` must be assigned one primary scam category from the taxonomy below.

The category should describe the main social-engineering or fraud mechanism used in the communication.

| Code | Scam Type | Description |
|---|---|---|
| `BANK_IMPERSONATION` | Bank Impersonation | Attacker impersonates a bank or banking employee to obtain information, credentials, payment, or access. |
| `KYC_SCAM` | KYC Scam | Attacker claims that KYC verification, re-verification, or account compliance is required and uses this to obtain sensitive information, credentials, or payment. |
| `UPI_PAYMENT_SCAM` | UPI/Payment Scam | Communication attempts to manipulate the victim into making a fraudulent payment, approving a payment request, or transferring money. |
| `DIGITAL_ARREST_SCAM` | Digital Arrest | Attacker impersonates law enforcement or another authority and uses threats of arrest, legal action, or investigation to manipulate the victim. |
| `CUSTOMER_SUPPORT_SCAM` | Customer Support Scam | Attacker impersonates customer support or a service representative to obtain information, payment, credentials, or access. |
| `REFUND_SCAM` | Refund Scam | Attacker claims that a refund, reimbursement, or mistaken transaction must be processed and manipulates the victim into taking a fraudulent action. |
| `INVESTMENT_SCAM` | Investment Scam | Communication promotes a fraudulent investment opportunity or manipulates the victim into transferring money under false investment claims. |
| `JOB_SCAM` | Job Scam | Attacker offers a fraudulent job, recruitment opportunity, or employment-related benefit and attempts to obtain money or sensitive information. |
| `PRIZE_REWARD_SCAM` | Prize/Reward Scam | Victim is falsely told that they have won a prize, reward, lottery, cashback, or similar benefit and is manipulated into paying or providing information. |
| `REMOTE_ACCESS_SCAM` | Remote Access Scam | Attacker attempts to convince the victim to install remote-access software or provide remote control of a device. |
| `COURIER_CUSTOMS_SCAM` | Courier/Customs Scam | Attacker claims that a parcel, shipment, customs issue, or illegal package requires payment or immediate action. |
| `ACCOUNT_SUSPENSION_SCAM` | Account Suspension Scam | Attacker claims that an account, card, wallet, or service will be suspended or blocked unless the victim takes an urgent action. |
| `OTP_CREDENTIAL_THEFT` | OTP/Credential Theft | Communication attempts to obtain OTPs, passwords, PINs, CVVs, login credentials, or similar authentication information. |
| `FAMILY_EMERGENCY_IMPERSONATION` | Family/Emergency Impersonation | Attacker impersonates a family member, friend, colleague, or other trusted person and creates an urgent situation requiring money or sensitive information. |
| `OTHER_SCAM` | Other Scam | A fraudulent or social-engineering communication that does not fit the defined categories above. |
| `NOT_APPLICABLE` | Not Applicable | Used only for `LEGITIMATE` records. |
### 5.1 Scam Type Assignment Rules

1. Every `SCAM` record must have exactly one primary `scam_type`.
2. Choose the category representing the primary mechanism of the scam.
3. Do not create a new category for every variation of an existing scam.
4. Use `OTHER_SCAM` only when none of the defined categories reasonably applies.
5. Every `LEGITIMATE` record must use `NOT_APPLICABLE`.
6. Secondary characteristics such as urgency, threats, impersonation, payment requests, or OTP requests must be represented through the indicator fields rather than by assigning multiple scam types.
## 6. Social-Engineering Indicator Fields

Social-engineering indicators describe the tactics used within a communication to influence, pressure, deceive, or manipulate the recipient.

Each indicator is represented as a binary value:

- `1` — indicator is present
- `0` — indicator is absent

These fields are independent of the main `label` and `scam_type`.

A single communication may contain multiple indicators.

### 6.1 Indicator Schema

| Field | Data Type | Required | Allowed Values | Description |
|---|---|---|---|---|
| `urgency` | Integer | Yes | `0`, `1` | Communication creates pressure to act immediately or within a short time. |
| `threat` | Integer | Yes | `0`, `1` | Communication uses threats or consequences to pressure the recipient. |
| `impersonation` | Integer | Yes | `0`, `1` | Sender claims to represent another person, organization, authority, or trusted entity. |
| `payment_request` | Integer | Yes | `0`, `1` | Communication asks the recipient to make, approve, or facilitate a payment or money transfer. |
| `credential_request` | Integer | Yes | `0`, `1` | Communication requests passwords, PINs, CVVs, login credentials, or similar sensitive authentication information. |
| `otp_request` | Integer | Yes | `0`, `1` | Communication explicitly requests an OTP or verification code. |
| `remote_access_request` | Integer | Yes | `0`, `1` | Communication asks the recipient to install remote-access software or provide device control/access. |
| `suspicious_link` | Integer | Yes | `0`, `1` | Communication contains or directs the recipient to a potentially malicious, deceptive, or suspicious link. |
| `reward_or_promise` | Integer | Yes | `0`, `1` | Communication offers a reward, refund, prize, financial benefit, job, investment return, or other attractive promise to influence the recipient. |
| `fear` | Integer | Yes | `0`, `1` | Communication deliberately creates fear, panic, or anxiety to influence the recipient's decision. |
| `authority_claim` | Integer | Yes | `0`, `1` | Communication invokes government, police, courts, banks, legal authorities, or other institutional authority to increase compliance. |
| `financial_pressure` | Integer | Yes | `0`, `1` | Communication uses financial loss, debt, penalties, blocked funds, or similar financial consequences to pressure the recipient. |

### 6.2 Indicator Annotation Rules

#### `urgency`

Set to `1` when the communication creates time pressure.

Examples of signals include:

- "Act immediately"
- "Do this within 10 minutes"
- "Your account will be blocked today"
- "Last chance"

Routine statements about dates or deadlines should not automatically be marked as urgency.

#### `threat`

Set to `1` when the communication threatens a negative consequence.

Examples:

- Arrest
- Legal action
- Account closure
- Penalty
- Service termination
- Financial loss

A normal informational warning is not automatically a threat.

#### `impersonation`

Set to `1` when the sender claims to be another trusted entity or person.

Examples:

- Bank employee
- Police officer
- Government official
- Customer-support representative
- Family member
- Employer

#### `payment_request`

Set to `1` when the communication requests or directs a financial transaction.

This includes requests to:

- Transfer money
- Pay a fee
- Approve a UPI payment
- Send a deposit
- Pay customs or processing charges

#### `credential_request`

Set to `1` when sensitive authentication information is requested.

Examples:

- Password
- UPI PIN
- ATM PIN
- CVV
- Login credentials

#### `otp_request`

Set to `1` when an OTP, verification code, or similar one-time authentication code is requested.

A message merely mentioning that an OTP exists does not automatically qualify.

#### `remote_access_request`

Set to `1` when the communication asks the recipient to provide remote access to a device or install remote-control software.

Examples:

- AnyDesk
- TeamViewer
- Remote desktop software

The field indicates the request itself, not whether the victim actually installed the software.

#### `suspicious_link`

Set to `1` when a communication contains a link that appears deceptive, malicious, or inconsistent with the claimed organization/service.

Links should be evaluated based on the context available in the dataset.

#### `reward_or_promise`

Set to `1` when the communication uses an attractive benefit to persuade the recipient.

Examples:

- Prize
- Cashback
- Refund
- Job opportunity
- Investment returns
- Lottery winnings
- Financial reward

#### `fear`

Set to `1` when fear or panic is deliberately used as a manipulation tactic.

Examples:

- "Police will arrest you"
- "Your account has been compromised"
- "You will lose your money"
- "Legal action will be taken"

Fear may coexist with `threat` and `urgency`.

#### `authority_claim`

Set to `1` when the communication invokes an authority or institution to make the recipient comply.

Examples:

- Police
- Court
- Government department
- Bank
- Tax authority
- Regulatory authority

#### `financial_pressure`

Set to `1` when financial consequences are used to pressure the recipient.

Examples:

- Threat of losing money
- Account-related financial penalty
- Demand for immediate payment
- Claim that funds will be frozen
- Demand for a fee to recover or receive money

### 6.3 Indicator Independence

Indicators must be labeled independently.

For example, a message can simultaneously contain:

```text
urgency = 1
threat = 1
impersonation = 1
payment_request = 1
fear = 1
authority_claim = 1
financial_pressure = 1
```

## 7. Context and Metadata Fields

Context and metadata fields provide additional information about the communication instance.

These fields support:

- Context-aware risk scoring
- Behavioral analysis
- Scenario generation
- Error analysis
- Testing of the complete SuraksHawk pipeline

They must not be used to alter the ground-truth `label` after annotation.

### 7.1 Context Fields

| Field | Data Type | Required | Allowed Values / Format | Description |
|---|---|---|---|---|
| `sender_type` | String | Yes | Defined sender categories | Describes who the sender claims to be. |
| `beneficiary_present` | Integer | Yes | `0`, `1` | Indicates whether the communication is associated with a payment beneficiary or recipient. |
| `transaction_present` | Integer | Yes | `0`, `1` | Indicates whether a payment or transaction context exists. |
| `transaction_amount` | Float | No | Non-negative numeric value | Simulated transaction amount associated with the communication, when applicable. |
| `link_present` | Integer | Yes | `0`, `1` | Indicates whether the communication contains a link. |
| `action_requested` | Integer | Yes | `0`, `1` | Indicates whether the communication asks the recipient to perform a specific action. |
| `sensitive_information_requested` | Integer | Yes | `0`, `1` | Indicates whether the communication requests sensitive personal, financial, or authentication information. |

### 7.2 Sender Type

The `sender_type` field represents the identity or role claimed by the sender.

Allowed values:

```text
BANK
GOVERNMENT
POLICE
CUSTOMER_SUPPORT
FAMILY_OR_FRIEND
EMPLOYER
DELIVERY_OR_COURIER
INVESTMENT_SERVICE
UNKNOWN
OTHER
```

## 8. Final Record Format

Each message dataset record must contain the fields defined in Sections 4, 5, 6, and 7.

The canonical column order is:

```text
id
text
label
scam_type
language
communication_type
urgency
threat
impersonation
payment_request
credential_request
otp_request
remote_access_request
suspicious_link
reward_or_promise
fear
authority_claim
financial_pressure
sender_type
beneficiary_present
transaction_present
transaction_amount
link_present
action_requested
sensitive_information_requested
source_type
split
annotation_status
notes

### 8.2 Example — SCAM Record

```csv
id,text,label,scam_type,language,communication_type,urgency,threat,impersonation,payment_request,credential_request,otp_request,remote_access_request,suspicious_link,reward_or_promise,fear,authority_claim,financial_pressure,sender_type,beneficiary_present,transaction_present,transaction_amount,link_present,action_requested,sensitive_information_requested,source_type,split,annotation_status,notes
S001,"Your bank account will be blocked today. Verify your KYC immediately using this link and pay the verification fee.",SCAM,KYC_SCAM,ENGLISH,SMS,1,1,1,1,0,0,0,1,0,1,1,1,BANK,0,1,499,1,1,0,SYNTHETIC,TRAIN,FINAL,"Synthetic KYC scam example."
```

### 8.3 Example — LEGITIMATE Record

```csv
id,text,label,scam_type,language,communication_type,urgency,threat,impersonation,payment_request,credential_request,otp_request,remote_access_request,suspicious_link,reward_or_promise,fear,authority_claim,financial_pressure,sender_type,beneficiary_present,transaction_present,transaction_amount,link_present,action_requested,sensitive_information_requested,source_type,split,annotation_status,notes
S002,"Your monthly bank statement is now available in your official banking app.",LEGITIMATE,NOT_APPLICABLE,ENGLISH,SMS,0,0,0,0,0,0,0,0,0,0,1,0,BANK,0,0,,0,1,0,SYNTHETIC,TRAIN,FINAL,"Synthetic legitimate notification example."
```

The examples above are schema examples only and must not be treated as sufficient training data.

---

## 9. Dataset Validation Rules

Every record should pass the following validation checks before being used.

### 9.1 Required Fields

The following fields must not be missing:

```text
id
text
label
scam_type
language
communication_type
urgency
threat
impersonation
payment_request
credential_request
otp_request
remote_access_request
suspicious_link
reward_or_promise
fear
authority_claim
financial_pressure
sender_type
beneficiary_present
transaction_present
link_present
action_requested
sensitive_information_requested
source_type
split
annotation_status
```

`transaction_amount` and `notes` may be empty when not applicable.

### 9.2 Label Consistency

- `label` must be either `SCAM` or `LEGITIMATE`.
- If `label = SCAM`, `scam_type` must not be `NOT_APPLICABLE`.
- If `label = LEGITIMATE`, `scam_type` must be `NOT_APPLICABLE`.
- `scam_type` must be one of the defined taxonomy values.

### 9.3 Indicator Validation

All indicator fields must contain only:

```text
0
1
```

The indicator fields are:

```text
urgency
threat
impersonation
payment_request
credential_request
otp_request
remote_access_request
suspicious_link
reward_or_promise
fear
authority_claim
financial_pressure
beneficiary_present
transaction_present
link_present
action_requested
sensitive_information_requested
```

### 9.4 Transaction Validation

- `transaction_present = 0` means there is no associated transaction context.
- When `transaction_present = 0`, `transaction_amount` should normally be empty.
- When `transaction_present = 1`, `transaction_amount` may contain a non-negative simulated amount.
- Do not use negative transaction amounts.
- Do not insert real financial transaction data.

### 9.5 Link Validation

- `link_present = 0` means no link is present.
- `link_present = 1` means a link is present.
- `suspicious_link` is independently annotated.
- Normally, `suspicious_link = 0` when `link_present = 0`.

### 9.6 Split Validation

Allowed values:

```text
TRAIN
VALIDATION
TEST
SCENARIO
```

Rules:

- Training data is used for model learning.
- Validation data is used for model selection and tuning.
- Test data is reserved for final evaluation.
- Scenario records are used for end-to-end golden tests.

### 9.7 Annotation Status

Allowed values:

```text
PENDING
REVIEWED
FINAL
```

Only records marked `FINAL` should be included in the final evaluation dataset.

### 9.8 ID Validation

- IDs must be unique.
- IDs should follow the `S001`, `S002`, `S003` pattern.
- IDs must not be reused across different records.

---

## 10. Dataset Quality Principles

### 10.1 Class Balance

The dataset should contain both `SCAM` and `LEGITIMATE` records.

Avoid extreme class imbalance where practical.

For the prototype, report the class distribution rather than claiming that the dataset is balanced unless it actually is.

### 10.2 Scam-Type Coverage

The dataset should contain examples covering the major scam categories relevant to the SuraksHawk use case.

Rare categories may have fewer examples, but their presence should be documented.

### 10.3 Language Diversity

Where feasible, include:

- English
- Hindi
- Hinglish
- Romanized Hindi

Do not claim multilingual performance if the relevant language examples are not represented in the evaluation data.

### 10.4 Communication Diversity

Include multiple communication types where possible:

- SMS
- WhatsApp
- Email
- Simulated call transcripts

Do not assume that performance on one channel automatically represents performance on all channels.

### 10.5 Indicator Diversity

The dataset should contain:

- Single-indicator scams
- Multi-indicator scams
- Low-pressure scams
- High-pressure scams
- Scam messages without obvious keywords
- Legitimate messages containing words that may superficially resemble scam signals

This is important for evaluating both false positives and false negatives.

### 10.6 Realism

Synthetic messages should resemble realistic communication patterns, including:

- Informal language
- Spelling variations
- Common abbreviations
- Hinglish and Romanized Hindi where applicable
- Different levels of urgency
- Different scam narratives

Do not make every scam message obviously fraudulent through identical wording or repeated keywords.

### 10.7 No Data Leakage

Avoid placing near-duplicate or templated versions of the same message across training and test sets.

If a message template is used to generate multiple examples, related variants should be grouped appropriately to reduce train/test leakage.

### 10.8 Privacy and Safety

Do not include real:

- Personal names
- Phone numbers
- Email addresses
- Bank account numbers
- Card numbers
- UPI IDs
- Passwords
- PINs
- OTPs
- Authentication credentials
- Other sensitive personal or financial information

Use synthetic placeholders instead.

### 10.9 Ground-Truth Integrity

Ground truth must be determined independently of model predictions.

Do not relabel a record simply because the model classified it incorrectly.

When an annotation is genuinely uncertain, mark it for review rather than silently changing it to improve evaluation results.

---

## 11. Recommended Dataset Structure

The repository may organize dataset artifacts as follows:

```text
dataset/
├── raw/
│   └── external_sources_or_original_data
├── processed/
│   └── cleaned_and_normalized_data
├── train/
│   └── training_data.csv
├── validation/
│   └── validation_data.csv
├── test/
│   └── test_data.csv
└── scenarios/
    └── golden_scenarios.csv
```

External/public datasets should retain their original source information in documentation.

Do not commit large raw datasets to GitHub unless licensing, size, and privacy requirements allow it.

---

## 12. Annotation Workflow

Recommended workflow:

```text
Collect / Create Data
        ↓
Clean / Normalize
        ↓
Initial Annotation
        ↓
Review
        ↓
Resolve Ambiguities
        ↓
Mark FINAL
        ↓
Split into Train / Validation / Test
        ↓
Run Validation Checks
        ↓
Use in Model Development / Evaluation
```

Important:

- Test data should be isolated before model tuning.
- Annotation decisions should be based on the communication and available context, not on model predictions.
- Ambiguous records should be reviewed by a second person where practical.
- Changes to final annotations should be documented in `notes` or project documentation.

---

## 13. Evaluation Data Principles

The final test set should be used to measure:

- Accuracy
- Precision
- Recall
- F1-score
- Confusion matrix
- False-positive rate
- False-negative rate
- Scam-type performance where sample sizes permit
- Language-wise performance where sample sizes permit
- Communication-type performance where sample sizes permit

For the SuraksHawk prototype, evaluation should also consider:

- Risk-score behavior
- Correct intervention category
- Explainability of triggered risk factors
- Robustness to realistic wording variations

Do not report metrics for a subgroup when it has too few examples to support a meaningful conclusion.

---

## 14. Schema Change Policy

This schema is the agreed contract between dataset, NLP, risk-scoring, testing, and integration work.

Before changing:

- Field names
- Allowed values
- Data types
- Label definitions
- Scam taxonomy
- Canonical column order

the change should be communicated to the relevant team members and reflected in the schema documentation.

Any breaking schema change should be reviewed before dependent code is updated.
