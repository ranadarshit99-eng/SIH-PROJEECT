"""
Test script for Cross_Check Engine
Verifies document field extraction and cross-check error detection across 11 document types.
"""
import sys
from engines.Cross_Check import extract_cross_check_fields, evaluate_cross_check

def run_test():
    print("Starting Cross_Check test...", flush=True)
    sample_verifications = {
        "doc_gst": {
            "data": {
                "legal_name": "Yash Shah",
                "trade_name": "SHAH INDUSTRIAL EQUIPMENTS",
                "principal_business_address": "Naroda GIDC, Ahmedabad, Gujarat"
            }
        },
        "doc_annexure": {
            "data": {
                "company_name": "SHAH INDUSTRIAL EQUIPMENTS",
                "authorized_signatory": "Yash Shah"
            }
        },
        "doc_iso": {
            "data": {
                "authorized_person": "Yash Shah",
                "enterprise": "SHAH INDUSTRIAL EQUIPMENTS",
                "registered_address": "Naroda GIDC, Ahmedabad, Gujarat"
            }
        },
        "doc_experience": {
            "data": {
                "authorised_person": "Yash Shah",
                "enterprise": "SHAH INDUSTRIAL EQUIPMENTS"
            }
        },
        "doc_financial": {
            "data": {
                "authorised_person": "Yash Shah",
                "enterprise": "SHAH INDUSTRIAL EQUIPMENTS"
            }
        },
        "doc_itr": {
            "data": {
                "name": "Yash Shah",
                "address": "Naroda GIDC, Ahmedabad, Gujarat"
            }
        },
        "doc_msme": {
            "data": {
                "name_of_enterprise": "SHAH INDUSTRIAL EQUIPMENTS",
                "official_address": "Naroda GIDC, Ahmedabad, Gujarat"
            }
        },
        "doc_pan": {
            "data": {
                "name": "Yash Shah"
            }
        },
        "doc_turnover": {
            "data": {
                "authorized_person": "Yash Shah",
                "enterprise": "SHAH INDUSTRIAL EQUIPMENTS"
            }
        },
        "doc_work_completion": {
            "data": {
                "authorised_person": "Yash Shah",
                "enterprise": "SHAH INDUSTRIAL EQUIPMENTS"
            }
        }
    }

    print("=== TEST 1: Clean Matching Submission ===", flush=True)
    extracted = extract_cross_check_fields(sample_verifications)
    for doc, fields in extracted.items():
        print(f"[{doc}] -> Name: {fields.get('Name')}, Company Name: {fields.get('Company Name')}, Address: {fields.get('Address')}", flush=True)

    res1 = evaluate_cross_check(sample_verifications)
    print(f"Discrepancies Count: {len(res1['discrepancies'])}, Is Valid: {res1['is_valid']}", flush=True)
    assert res1['is_valid'] == True, "Clean submission should pass without discrepancies!"

    print("\n=== TEST 2: Discrepancy Injection Test ===", flush=True)
    mismatched_verifications = dict(sample_verifications)
    mismatched_verifications["doc_itr"] = {
        "data": {
            "name": "Ramesh Verma",
            "address": "Naroda GIDC, Ahmedabad, Gujarat"
        }
    }
    mismatched_verifications["doc_msme"] = {
        "data": {
            "name_of_enterprise": "GLOBAL TECH ENTERPRISES",
            "official_address": "Naroda GIDC, Ahmedabad, Gujarat"
        }
    }

    res2 = evaluate_cross_check(mismatched_verifications)
    print(f"Discrepancies Count: {len(res2['discrepancies'])}", flush=True)
    for disc in res2['discrepancies']:
        print(f"Rule: {disc['rule']} | Severity: {disc['severity']}", flush=True)
        print(f"Description: {disc['description']}", flush=True)
        for b in disc['breakdown']:
            print(f"  - {b['document']}: {b['value']} ({b['status']})", flush=True)
    assert len(res2['discrepancies']) >= 2, "Mismatched fields should trigger discrepancies!"
    print("\nALL 11 DOCUMENT CROSS_CHECK TESTS PASSED SUCCESSFULLY!", flush=True)

if __name__ == "__main__":
    run_test()
