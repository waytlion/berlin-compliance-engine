"""
Test Cases for Berlin Short-Term Rental Compliance Checker
Based on Zweckentfremdungsverbot-Gesetz Berlin (ZwVbG)

Run with: tower run --local (for development)
Or trigger via Tower cloud after deployment
"""
import os
import json

# Test cases based on Berlin ZwVbG regulations
TEST_CASES = [
    # ============ ALLOWED CASES ============
    {
        "name": "TC01: Primary residence, short stay with registration",
        "address": "Prenzlauer Allee 45, 10405 Berlin, Germany",
        "property_info": """Cozy 2-bedroom apartment in Prenzlauer Berg. 
        This is my primary residence (Hauptwohnsitz). 
        Available for 30 days this year. 
        Wohnraumschutznummer: WSN-2024-12345 displayed.
        Registered with Bezirksamt Pankow.""",
        "expected_status": "allowed",
        "expected_risk_range": (0, 30),
        "rationale": "Primary residence, <60 days, has registration number"
    },
    {
        "name": "TC02: Single room rental, owner present",
        "address": "Oranienstraße 120, 10969 Berlin, Germany",
        "property_info": """Private room in shared apartment in Kreuzberg.
        Host lives in apartment and occupies 60% of the space.
        Kitchen and bathroom shared with host.
        Short-term guests welcome. Registration number: WSN-2024-67890.""",
        "expected_status": "allowed",
        "expected_risk_range": (0, 25),
        "rationale": "Room rental with owner present occupying >50%"
    },
    {
        "name": "TC03: Temporary worker housing, 3 months",
        "address": "Karl-Marx-Allee 90, 10243 Berlin, Germany",
        "property_info": """Furnished apartment for professionals relocating to Berlin.
        Minimum stay: 3 months. Tenant must register Hauptwohnsitz.
        Suitable for corporate housing. All documents provided.
        Wohnraumschutznummer: WSN-2024-11111.""",
        "expected_status": "allowed",
        "expected_risk_range": (0, 20),
        "rationale": "Temporary housing for workers with residency requirement"
    },
    
    # ============ WARNING CASES ============
    {
        "name": "TC04: Primary residence, approaching 60-day limit",
        "address": "Schönhauser Allee 175, 10119 Berlin, Germany",
        "property_info": """My apartment in Prenzlauer Berg. Primary residence.
        Already rented 55 days this year, offering 10 more days.
        Wohnraumschutznummer registered. No permit yet.""",
        "expected_status": "warning",
        "expected_risk_range": (40, 70),
        "rationale": "Will exceed 60-day limit without permit"
    },
    {
        "name": "TC05: Subletting without clear residency",
        "address": "Torstraße 100, 10119 Berlin, Germany",
        "property_info": """Nice apartment in Mitte available for 2 months.
        Flexible terms. No registration requirements for guests.
        Perfect for digital nomads.""",
        "expected_status": "warning",
        "expected_risk_range": (50, 80),
        "rationale": "Medium-term without residency requirement is risky"
    },
    {
        "name": "TC06: Missing documentation mention",
        "address": "Frankfurter Allee 50, 10247 Berlin, Germany",
        "property_info": """Lovely apartment in Friedrichshain.
        Available for short stays. Great location.
        Owner lives elsewhere but visits occasionally.""",
        "expected_status": "warning",
        "expected_risk_range": (60, 85),
        "rationale": "No Wohnraumschutznummer mentioned, not primary residence"
    },
    
    # ============ DENIED CASES ============
    {
        "name": "TC07: Commercial holiday apartment, no permit",
        "address": "Kurfürstendamm 200, 10719 Berlin, Germany",
        "property_info": """Luxury holiday apartment in Charlottenburg!
        Perfect for tourists. Book for any duration.
        We manage 15 similar apartments in Berlin.
        Professional cleaning service included.""",
        "expected_status": "denied",
        "expected_risk_range": (80, 100),
        "rationale": "Commercial operation, multiple properties, no permit"
    },
    {
        "name": "TC08: Entire apartment, no registration displayed",
        "address": "Bergmannstraße 80, 10961 Berlin, Germany",
        "property_info": """Entire apartment in Kreuzberg for vacation rental.
        Available year-round for short stays.
        Owner lives in Hamburg. Direct booking available.
        Cash payment preferred.""",
        "expected_status": "denied",
        "expected_risk_range": (85, 100),
        "rationale": "No registration, secondary residence, cash = red flags"
    },
    {
        "name": "TC09: Airbnb style without any compliance",
        "address": "Warschauer Straße 45, 10243 Berlin, Germany",
        "property_info": """Amazing Airbnb in party district!
        Book for weekends or weeks. No minimum stay.
        Owner not present. Perfect for tourists.
        Fast check-in, no questions asked.""",
        "expected_status": "denied",
        "expected_risk_range": (90, 100),
        "rationale": "Classic illegal short-term rental pattern"
    },
    {
        "name": "TC10: Exceeding 60-day limit explicitly",
        "address": "Alexanderplatz 5, 10178 Berlin, Germany",
        "property_info": """Central Berlin apartment. My primary residence.
        Already rented 80 days this year, still accepting bookings.
        Great reviews from previous guests.
        Wohnraumschutznummer: WSN-2024-99999.""",
        "expected_status": "denied",
        "expected_risk_range": (70, 95),
        "rationale": "Exceeded 60-day limit without permit"
    },
]


def format_test_case(tc: dict) -> str:
    """Format a test case for display."""
    return f"""
{'='*60}
{tc['name']}
{'='*60}
Address: {tc['address']}
Property Info: {tc['property_info'][:100]}...

Expected: {tc['expected_status'].upper()}
Risk Range: {tc['expected_risk_range'][0]}-{tc['expected_risk_range'][1]}
Rationale: {tc['rationale']}
"""


def run_test_case(tc: dict, handler_func) -> dict:
    """Run a single test case and evaluate results."""
    print(f"\n🧪 Running: {tc['name']}")
    
    result = handler_func(
        address=tc['address'],
        property_info=tc['property_info']
    )
    
    # Evaluate
    status_match = result.get('status', '').lower() == tc['expected_status']
    risk_score = result.get('risk_score', -1)
    risk_in_range = tc['expected_risk_range'][0] <= risk_score <= tc['expected_risk_range'][1]
    
    passed = status_match  # Primary criteria is status match
    
    return {
        'name': tc['name'],
        'passed': passed,
        'status_match': status_match,
        'risk_in_range': risk_in_range,
        'expected_status': tc['expected_status'],
        'actual_status': result.get('status', 'unknown'),
        'expected_risk_range': tc['expected_risk_range'],
        'actual_risk_score': risk_score,
        'issues': result.get('issues', []),
        'missing_docs': result.get('missing_docs', [])
    }


def print_test_summary(results: list):
    """Print a summary of test results."""
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    
    print("\n" + "="*60)
    print(f"TEST SUMMARY: {passed}/{total} passed")
    print("="*60)
    
    for r in results:
        icon = "✅" if r['passed'] else "❌"
        status_icon = "✓" if r['status_match'] else "✗"
        risk_icon = "✓" if r['risk_in_range'] else "✗"
        
        print(f"{icon} {r['name']}")
        print(f"   Status: {status_icon} expected={r['expected_status']}, got={r['actual_status']}")
        print(f"   Risk:   {risk_icon} expected={r['expected_risk_range']}, got={r['actual_risk_score']}")
        if not r['passed']:
            print(f"   Issues: {r['issues'][:2]}...")


if __name__ == "__main__":
    # Import the handler from compliance.py
    from compliance import handle
    
    print("Berlin Short-Term Rental Compliance Test Suite")
    print("Based on Zweckentfremdungsverbot-Gesetz (ZwVbG)")
    print("="*60)
    
    # Check if we want to run all tests or just list them
    import sys
    if "--list" in sys.argv:
        for tc in TEST_CASES:
            print(format_test_case(tc))
        sys.exit(0)
    
    if "--dry-run" in sys.argv:
        print("\nDRY RUN - Test cases that would be executed:")
        for tc in TEST_CASES:
            print(f"  • {tc['name']} -> Expected: {tc['expected_status']}")
        sys.exit(0)
    
    # Run actual tests
    print("\n⚠️  Running tests will make OpenAI API calls!")
    print(f"Total test cases: {len(TEST_CASES)}")
    
    results = []
    for tc in TEST_CASES:
        try:
            result = run_test_case(tc, handle)
            results.append(result)
        except Exception as e:
            print(f"❌ Error in {tc['name']}: {e}")
            results.append({
                'name': tc['name'],
                'passed': False,
                'error': str(e)
            })
    
    print_test_summary(results)
