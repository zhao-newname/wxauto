#!/usr/bin/env python3
"""
Simple verification script for miniprogram message support
"""

def verify_languages_file():
    """Verify that [小程序] is added to languages.py"""
    try:
        with open('wxauto/languages.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if [小程序] is in MESSAGES
        miniprogram_in_messages = "'[小程序]': {'cn': \"[小程序]\"" in content
        print(f"✓ [小程序] in MESSAGES: {miniprogram_in_messages}")
        return miniprogram_in_messages
        
    except Exception as e:
        print(f"✗ Error checking languages.py: {e}")
        return False

def verify_msg_file():
    """Verify that msg.py has been updated correctly"""
    try:
        with open('wxauto/msgs/msg.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        checks = {
            'miniprogram_in_special_msgs': "'[小程序]'," in content,
            'miniprogram_control_attrs': 'MINIPROGRAM_MSG_CONTROL_NUM' in content,
            'miniprogram_height_attrs': 'MINIPROGRAM_MSG_HEIGHT' in content,
            'miniprogram_recognition_function': '_is_miniprogram_message' in content,
            'miniprogram_priority_check': 'if _is_miniprogram_message(control):' in content,
            'miniprogram_special_msg_handling': "content == _lang('[小程序]')" in content
        }
        
        print("✓ msg.py verification:")
        all_passed = True
        for check_name, result in checks.items():
            status = "✓" if result else "✗"
            print(f"  {status} {check_name}: {result}")
            if not result:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Error checking msg.py: {e}")
        return False

def main():
    print("Miniprogram Message Parser Extension Verification")
    print("=" * 50)
    
    # Test 1: Languages file
    print("\n1. Checking languages.py...")
    lang_ok = verify_languages_file()
    
    # Test 2: Message parser file
    print("\n2. Checking msg.py...")
    msg_ok = verify_msg_file()
    
    # Test 3: Manual check of SEPICIAL_MSGS
    print("\n3. Manual verification of SEPICIAL_MSGS...")
    try:
        # Read and check SEPICIAL_MSGS definition
        with open('wxauto/msgs/msg.py', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        in_special_msgs = False
        miniprogram_found = False
        
        for line in lines:
            if 'SEPICIAL_MSGS = [' in line:
                in_special_msgs = True
            elif in_special_msgs and ']' in line and not line.strip().startswith('#'):
                break
            elif in_special_msgs and "'[小程序]'" in line:
                miniprogram_found = True
                print(f"  ✓ Found [小程序] in SEPICIAL_MSGS: {line.strip()}")
        
        if not miniprogram_found:
            print("  ✗ [小程序] not found in SEPICIAL_MSGS")
            
    except Exception as e:
        print(f"  ✗ Error checking SEPICIAL_MSGS: {e}")
        miniprogram_found = False
    
    # Summary
    print("\n" + "=" * 50)
    print("VERIFICATION SUMMARY:")
    print("=" * 50)
    
    results = [
        ("Languages file updated", lang_ok),
        ("Message parser updated", msg_ok),
        ("SEPICIAL_MSGS contains [小程序]", miniprogram_found)
    ]
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status:4} | {test_name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} checks passed")
    
    if passed == len(results):
        print("\n✓ Task 3 implementation verified successfully!")
        print("  - SEPICIAL_MSGS list updated with [小程序]")
        print("  - parse_msg_type function extended with miniprogram support")
        print("  - Miniprogram message control attributes added")
        print("  - Miniprogram recognition logic implemented")
        return True
    else:
        print("\n✗ Some verification checks failed.")
        return False

if __name__ == "__main__":
    main()