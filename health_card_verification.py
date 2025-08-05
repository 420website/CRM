import sys
import re

def test_health_card_categorization():
    """Test the health card categorization logic to verify different counts"""
    print("🚀 Testing Health Card Categorization Logic")
    print("=" * 60)
    
    # Test data
    no_health_cards = [
        None,
        "",
        "null",
        "none",
        "nan",
        "0000000000 NA",
        "0000000000",
        "NA",
        "0000000000NA"
    ]
    
    invalid_health_cards = [
        "1234567890",
        "9876543210",
        "5555555555",
        "1111111111",
        "9999999999",
        "12345",
        "123456789",
        "12345678901",
        "123456789A",
        "ABCDEFGHIJ",
        "1234567890ABC"
    ]
    
    valid_health_cards = [
        "1234567890AB",
        "9876543210CD",
        "5555555555EF",
        "1111111111GH",
        "9999999999IJ"
    ]
    
    # Initialize counters
    total_records = 0
    no_hc_count = 0
    invalid_hc_count = 0
    valid_hc_count = 0
    
    # Process each health card
    all_health_cards = []
    
    # Add no health cards
    for hc in no_health_cards:
        all_health_cards.append({"HC": hc, "expected_category": "no_hc"})
    
    # Add invalid health cards
    for hc in invalid_health_cards:
        all_health_cards.append({"HC": hc, "expected_category": "invalid_hc"})
    
    # Add valid health cards
    for hc in valid_health_cards:
        all_health_cards.append({"HC": hc, "expected_category": "valid_hc"})
    
    # Process each record
    for record in all_health_cards:
        total_records += 1
        
        # Get health card value
        hc = record.get('HC')
        hc_str = str(hc).strip() if hc is not None else ""
        
        # Check if no health card (empty, null, or 0000000000 NA patterns)
        if (not hc_str or 
            hc_str.lower() in ['', 'null', 'none', 'nan'] or
            hc_str == '0000000000 NA' or
            hc_str == '0000000000' or
            hc_str == 'NA' or
            hc_str == '0000000000NA'):
            no_hc_count += 1
            record["actual_category"] = "no_hc"
        else:
            # Has some health card data - check if it's invalid (missing 2-letter suffix)
            if re.match(r'^\d{10}$', hc_str):  # Exactly 10 digits with no letters
                invalid_hc_count += 1
                record["actual_category"] = "invalid_hc"
            elif re.match(r'^\d{10}[A-Za-z]{2}$', hc_str):  # 10 digits + 2 letters (valid format)
                valid_hc_count += 1
                record["actual_category"] = "valid_hc"
            else:
                # Other formats that don't match standard patterns - treat as invalid
                invalid_hc_count += 1
                record["actual_category"] = "invalid_hc"
    
    # Print results
    print("\n📊 Health Card Categorization Results:")
    print(f"Total records: {total_records}")
    print(f"No health cards: {no_hc_count}")
    print(f"Invalid health cards: {invalid_hc_count}")
    print(f"Valid health cards: {valid_hc_count}")
    
    # Verify that the counts are different
    if no_hc_count != invalid_hc_count:
        print(f"\n✅ VERIFICATION PASSED: 'No health cards' count ({no_hc_count}) is different from 'Invalid health cards' count ({invalid_hc_count})")
    else:
        print(f"\n❌ VERIFICATION FAILED: 'No health cards' count ({no_hc_count}) is the same as 'Invalid health cards' count ({invalid_hc_count})")
        return False
    
    # Verify that each record was categorized correctly
    categorization_errors = []
    for record in all_health_cards:
        if record["expected_category"] != record["actual_category"]:
            categorization_errors.append({
                "health_card": record["HC"],
                "expected": record["expected_category"],
                "actual": record["actual_category"]
            })
    
    if categorization_errors:
        print("\n❌ CATEGORIZATION ERRORS:")
        for error in categorization_errors:
            print(f"  - Health card '{error['health_card']}' was categorized as '{error['actual']}' but should be '{error['expected']}'")
        return False
    else:
        print("\n✅ All health cards were categorized correctly")
    
    # Verify that '0000000000 NA' is categorized as 'no health card'
    test_record = {"HC": "0000000000 NA"}
    
    # Process the record
    hc = test_record.get('HC')
    hc_str = str(hc).strip() if hc is not None else ""
    
    # Check if no health card (empty, null, or 0000000000 NA patterns)
    if (not hc_str or 
        hc_str.lower() in ['', 'null', 'none', 'nan'] or
        hc_str == '0000000000 NA' or
        hc_str == '0000000000' or
        hc_str == 'NA' or
        hc_str == '0000000000NA'):
        test_record["category"] = "no_hc"
    else:
        # Has some health card data - check if it's invalid (missing 2-letter suffix)
        if re.match(r'^\d{10}$', hc_str):  # Exactly 10 digits with no letters
            test_record["category"] = "invalid_hc"
        elif re.match(r'^\d{10}[A-Za-z]{2}$', hc_str):  # 10 digits + 2 letters (valid format)
            test_record["category"] = "valid_hc"
        else:
            # Other formats that don't match standard patterns - treat as invalid
            test_record["category"] = "invalid_hc"
    
    if test_record["category"] == "no_hc":
        print("\n✅ VERIFICATION PASSED: '0000000000 NA' is correctly categorized as 'no health card'")
    else:
        print(f"\n❌ VERIFICATION FAILED: '0000000000 NA' is incorrectly categorized as '{test_record['category']}' instead of 'no health card'")
        return False
    
    # Generate context text similar to server.py
    context_text = f"""
HEALTH CARD STATISTICS:
Total records: {total_records}
No health cards (including 0000000000 NA): {no_hc_count}
Invalid health cards (missing 2-letter suffix): {invalid_hc_count}
Valid health cards: {valid_hc_count}
Percentage with no health cards: {no_hc_count/total_records*100:.1f}%
Percentage with invalid health cards: {invalid_hc_count/total_records*100:.1f}%
"""
    
    print("\n📝 Generated Context for Claude AI:")
    print(context_text)
    
    # Final verification
    print("\n📊 Final Verification:")
    print(f"✅ 'No health cards' count: {no_hc_count}")
    print(f"✅ 'Invalid health cards' count: {invalid_hc_count}")
    print(f"✅ 'Valid health cards' count: {valid_hc_count}")
    print(f"✅ Total records: {total_records}")
    
    if no_hc_count != invalid_hc_count:
        print(f"\n✅ FINAL VERIFICATION PASSED: 'No health cards' and 'Invalid health cards' have different counts")
        return True
    else:
        print(f"\n❌ FINAL VERIFICATION FAILED: 'No health cards' and 'Invalid health cards' have the same count")
        return False

if __name__ == "__main__":
    success = test_health_card_categorization()
    sys.exit(0 if success else 1)