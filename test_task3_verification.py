#!/usr/bin/env python3
"""
Task 3 verification script - 扩展消息解析器支持小程序消息

This script verifies that the message parser has been correctly extended to support miniprogram messages.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_special_msgs_contains_miniprogram():
    """Test that SEPICIAL_MSGS contains miniprogram identifier"""
    try:
        # Import the languages module to check if miniprogram message is defined
        from wxauto.languages import MESSAGES
        
        # Check if miniprogram message is defined in MESSAGES
        miniprogram_defined = '[小程序]' in MESSAGES
        print(f"✓ [小程序] defined in MESSAGES: {miniprogram_defined}")
        
        if miniprogram_defined:
            miniprogram_msg = MESSAGES['[小程序]']
            print(f"  - Chinese: {miniprogram_msg['cn']}")
            print(f"  - Traditional Chinese: {miniprogram_msg['cn_t']}")
            print(f"  - English: {miniprogram_msg['en']}")
        
        return miniprogram_defined
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error checking MESSAGES: {e}")
        return False

def test_parse_msg_type_function_structure():
    """Test that parse_msg_type function has been updated with miniprogram support"""
    try:
        # Read the msg.py file to check for miniprogram support
        with open('wxauto/msgs/msg.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for miniprogram-related code
        checks = {
            'miniprogram_import': 'from .miniprogram import MiniprogramCardAnalyzer' in content,
            'miniprogram_function': '_is_miniprogram_message' in content,
            'miniprogram_in_special_msgs': '[小程序]' in content,
            'miniprogram_control_attrs': 'MINIPROGRAM_MSG_CONTROL_NUM' in content,
            'miniprogram_height_attrs': 'MINIPROGRAM_MSG_HEIGHT' in content,
            'miniprogram_parse_logic': 'MiniprogramMessage' in content and 'getattr(msgtype' in content,
            'miniprogram_priority_check': '_is_miniprogram_message(control)' in content
        }
        
        print("✓ parse_msg_type function structure checks:")
        for check_name, result in checks.items():
            status = "✓" if result else "✗"
            print(f"  {status} {check_name}: {result}")
        
        return all(checks.values())
        
    except Exception as e:
        print(f"✗ Error checking parse_msg_type function: {e}")
        return False

def test_miniprogram_classes_exist():
    """Test that miniprogram message classes exist"""
    try:
        # Check if miniprogram classes are defined in the respective files
        files_to_check = {
            'wxauto/msgs/miniprogram.py': ['MiniprogramMessage', 'MiniprogramInfo', 'MiniprogramCardAnalyzer'],
            'wxauto/msgs/friend.py': ['FriendMiniprogramMessage'],
            'wxauto/msgs/self.py': ['SelfMiniprogramMessage']
        }
        
        all_classes_exist = True
        
        for file_path, expected_classes in files_to_check.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"✓ Checking {file_path}:")
                for class_name in expected_classes:
                    class_exists = f'class {class_name}' in content
                    status = "✓" if class_exists else "✗"
                    print(f"  {status} {class_name}: {class_exists}")
                    if not class_exists:
                        all_classes_exist = False
                        
            except FileNotFoundError:
                print(f"✗ File not found: {file_path}")
                all_classes_exist = False
        
        return all_classes_exist
        
    except Exception as e:
        print(f"✗ Error checking miniprogram classes: {e}")
        return False

def test_message_attrs_updated():
    """Test that MESSAGE_ATTRS has been updated with miniprogram attributes"""
    try:
        with open('wxauto/msgs/msg.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for miniprogram-specific attributes
        attrs_checks = {
            'MINIPROGRAM_MSG_HEIGHT': 'MINIPROGRAM_MSG_HEIGHT' in content,
            'MINIPROGRAM_MSG_CONTROL_NUM': 'MINIPROGRAM_MSG_CONTROL_NUM' in content
        }
        
        print("✓ MESSAGE_ATTRS updates:")
        for attr_name, result in attrs_checks.items():
            status = "✓" if result else "✗"
            print(f"  {status} {attr_name}: {result}")
        
        return all(attrs_checks.values())
        
    except Exception as e:
        print(f"✗ Error checking MESSAGE_ATTRS: {e}")
        return False

def test_miniprogram_recognition_logic():
    """Test that miniprogram recognition logic is properly implemented"""
    try:
        with open('wxauto/msgs/msg.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for proper miniprogram recognition logic
        logic_checks = {
            'priority_check': 'if _is_miniprogram_message(control):' in content,
            'special_msg_check': "content == _lang('[小程序]')" in content,
            'control_num_check': 'MINIPROGRAM_MSG_CONTROL_NUM' in content,
            'analyzer_usage': 'MiniprogramCardAnalyzer' in content
        }
        
        print("✓ Miniprogram recognition logic:")
        for check_name, result in logic_checks.items():
            status = "✓" if result else "✗"
            print(f"  {status} {check_name}: {result}")
        
        return all(logic_checks.values())
        
    except Exception as e:
        print(f"✗ Error checking recognition logic: {e}")
        return False

def main():
    """Run all verification tests"""
    print("=" * 60)
    print("Task 3 Verification: 扩展消息解析器支持小程序消息")
    print("=" * 60)
    
    tests = [
        ("Special Messages Contains Miniprogram", test_special_msgs_contains_miniprogram),
        ("Parse Message Type Function Structure", test_parse_msg_type_function_structure),
        ("Miniprogram Classes Exist", test_miniprogram_classes_exist),
        ("Message Attributes Updated", test_message_attrs_updated),
        ("Miniprogram Recognition Logic", test_miniprogram_recognition_logic)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
        print(f"Result: {'PASS' if result else 'FAIL'}")
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status:4} | {test_name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("✓ All verification tests passed! Task 3 implementation is complete.")
        return True
    else:
        print("✗ Some verification tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)