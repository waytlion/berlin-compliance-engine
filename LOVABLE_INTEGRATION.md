# Tower Compliance API - Integration Guide for Lovable

> **Copy this file to Lovable for integration.**

---

## 🚀 Webhook Integration (No Polling!)

Tower will **POST the result directly to Lovable's webhook** with Bearer auth.

---

## Authentication

```http
X-API-Key: YOUR_TOWER_API_KEY
Content-Type: application/json
```

---

## What Lovable Sends to Tower

```http
POST https://api.tower.dev/v1/apps/compliance-check/runs
X-API-Key: <TOWER_API_KEY>
Content-Type: application/json
```

```json
{
  "environment": "default",
  "parameters": {
    "address": "Friedrichstraße 123, 10117 Berlin, Germany",
    "property_info": "Property Type: apartment, Entire Unit: true. Host Status: tenant...",
    "callback_url": "https://dmjiajqzfaxeinjislsf.supabase.co/functions/v1/receive-compliance-result",
    "callback_secret": "<SHARED_SECRET>",
    "run_id": "<UNIQUE_CORRELATION_ID>"
  }
}
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `address` | ✅ Yes | Full address with city/postal code |
| `property_info` | ✅ Yes | Property details string |
| `callback_url` | ✅ Yes | Lovable webhook URL |
| `callback_secret` | ✅ Yes | Shared secret for Bearer auth |
| `run_id` | Optional | Correlation ID (auto-generated if not provided) |

---

## What Tower POSTs to Lovable Webhook

```http
POST https://dmjiajqzfaxeinjislsf.supabase.co/functions/v1/receive-compliance-result
Authorization: Bearer <SHARED_SECRET>
Content-Type: application/json
```

## Response Format (What Tower POSTs to Your Webhook)

```json
{
  "run_id": "abc123-correlation-id",
  "result": {
    "overall_assessment": {
      "result": "warning",
      "confidence": 0.68,
      "headline": "Potential Zweckentfremdung risk: entire-unit rental without permit."
    },
    "inferred_facts": {
      "is_primary_residence": true,
      "is_commercial_usage": false,
      "registration_number_present": false,
      "rented_area_less_than_50_percent": false,
      "vacancy_lt_3_months": true
    },
    "checks": [
      {
        "law": {
          "title": "Zweckentfremdungsverbot-Gesetz",
          "jurisdiction": "Berlin",
          "source": "ZwVbG",
          "as_of": "2026-01-25",
          "citations": [
            {
              "label": "§ 3 Abs. 3 ZwVbV",
              "url": "https://gesetze.berlin.de/bsbe/document/jlr-WoZwEntfrGBErahmen",
              "paragraph_text": "Eine Genehmigung ist erforderlich, wenn die gesamte Wohnung vermietet wird."
            }
          ]
        },
        "requirement_id": "berlin.zweckentfremdung.permit_required",
        "requirement_title": "Permit Requirement for Entire Apartment",
        "status": "not_fulfilled",
        "explanation": "The entire apartment is offered without a permit, which is restricted under ZwVbG.",
        "how_to_fix": "Apply for a Zweckentfremdungsgenehmigung at your local Bezirksamt if you intend to rent the entire unit short-term.",
        "evidence": [
          { "type": "listing_info", "quote": "Entire Unit: true" },
          { "type": "listing_info", "quote": "Permit Declared: no" }
        ],
        "missing_information": [],
        "recommended_action": {
          "title": "Apply for Necessary Permits",
          "owner_question": "Do you have the necessary permits to rent out the entire apartment?"
        }
      }
    ],
    "missing_document_info": [
      {
        "document_name": "Wohnraumschutznummer",
        "description": "Mandatory registration number for all short-term rentals in Berlin.",
        "source_authority": "Bezirksamt (District Office) / Senatsverwaltung",
        "application_link": "https://service.berlin.de/dienstleistung/328107/"
      }
    ],
    "ui_hints": {
      "severity_order": ["not_fulfilled", "warning", "valid"],
      "next_step_cta": "Request missing information"
    },
    "location_check": "berlin"
  }
}
```

---

## Status Values

| Status | Meaning |
|--------|---------|
| `valid` | ✅ Requirement satisfied |
| `warning` | ⚠️ Needs attention |
| `not_fulfilled` | ❌ Requirement not met |
| `skipped` | ⏭️ Non-Berlin address |
| `error` | 🚫 Processing error |

---

## Non-Berlin Response

```json
{
  "run_id": "abc123",
  "result": {
    "overall_assessment": {
      "result": "skipped",
      "confidence": 1.0,
      "headline": "Compliance check only available for Berlin."
    },
    "checks": [],
    "missing_fields": [],
    "location_check": "other"
  }
}
```

---

## TypeScript Example for Lovable

```typescript
async function runComplianceCheck(propertyData: ExtractedPropertyData) {
  const runId = crypto.randomUUID();
  
  const loc = propertyData.data.location;
  const prop = propertyData.data.propertyType;
  const host = propertyData.data.hostStatus;
  const rental = propertyData.data.rentalConfig;
  const reg = propertyData.data.registration;

  const address = [loc.street, loc.streetNumber, loc.postalCode, loc.city, "Germany"]
    .filter(Boolean).join(", ");

  const property_info = `
    Property Type: ${prop.type}, Entire Unit: ${prop.entireUnit}, Building: ${prop.buildingType}.
    Host Status: ${host.ownerOrTenant}, Primary Residence: ${host.isPrimaryResidence}, Host Present: ${host.hostPresentDuringStay}.
    Capacity: ${rental.guestCapacity} guests, ${rental.bedrooms} bedrooms.
    Registration Number: ${reg.registrationNumber || "NOT PROVIDED"}.
    Permit Declared: ${reg.permitDeclared}, Exemption: ${reg.exemptionDeclared}.
  `.trim();

  await fetch('https://api.tower.dev/v1/apps/compliance-check/runs', {
    method: 'POST',
    headers: {
      'X-API-Key': '<TOWER_API_KEY>', // Correct header name!
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      environment: 'default',
      parameters: {
        address,
        property_info,
        callback_url: 'https://dmjiajqzfaxeinjislsf.supabase.co/functions/v1/receive-compliance-result',
        callback_secret: '<SHARED_SECRET>',
        run_id: runId
      }
    })
  });

  // Result will arrive at webhook in 3-10 seconds!
  return runId;
}
```

---

## TypeScript Interfaces for Lovable

```typescript
interface ComplianceResult {
  overall_assessment: {
    result: "valid" | "warning" | "not_fulfilled" | "skipped" | "error";
    confidence: number;
    headline: string;
  };
  inferred_facts: {
    is_primary_residence: boolean;
    is_commercial_usage: boolean;
    registration_number_present: boolean;
    rented_area_less_than_50_percent: boolean;
    vacancy_lt_3_months: boolean;
  };
  checks: ComplianceCheck[];
  missing_document_info: MissingDocumentInfo[];
  ui_hints: {
    severity_order: string[];
    next_step_cta: string;
    badge_color: "red" | "yellow" | "green";
    icon: "x-circle" | "alert-triangle" | "check-circle";
  };
  location_check: "berlin" | "other";
}

interface ComplianceCheck {
  law: {
    title: string;
    jurisdiction: string;
    source: "ZwVbG" | "ZwVbV";
    citations: Array<{ label: string; url: string; paragraph_text: string }>;
  };
  requirement_id: string;
  requirement_title: string;
  status: "valid" | "warning" | "not_fulfilled";
  explanation: string;
  how_to_fix?: string; // New field!
  evidence: Array<{ type: string; quote: string }>;
  missing_information: Array<{ field: string; why_needed: string }>;
  recommended_action: { title: string; owner_question: string };
}

interface MissingDocumentInfo {
  document_name: string;      // e.g. "Wohnraumschutznummer"
  description: string;
  source_authority: string;   // e.g. "Bezirksamt"
  application_link: string;   // e.g. "https://service.berlin.de/..."
}
```

---

## Timeline

```
0s      → Lovable calls Tower API
0-2s    → Tower returns 201 Created (Instant)
...
15-30s  → OpenAI Analysis Completes
~30s    → Tower POSTs result to Lovable Webhook
```

**IMPORTANT**: Please ensure your frontend waits/listens for at least **30 seconds**. Detailed legal analysis takes time!

---

## Notes

1. **Processing Time**: 15-30 seconds (GPT-4o analysis)
2. **Berlin Only**: Non-Berlin addresses return `skipped`
3. **Auth**: Tower uses your `X-API-Key` header
4. **Correlation**: Use `run_id` to match requests with responses
