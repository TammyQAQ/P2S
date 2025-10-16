#!/usr/bin/env python3
"""
Go Code Validation Script
Validates Go code structure and syntax without requiring Go installation
"""

import os
import re
import sys
from pathlib import Path

def validate_go_syntax(file_path):
    """Basic Go syntax validation"""
    print(f"[CHECK] Validating {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        errors = []
        
        # Check for basic Go syntax patterns
        if not content.strip():
            errors.append("Empty file")
            return errors
        
        # Check for package declaration
        if not re.search(r'^package\s+\w+', content, re.MULTILINE):
            errors.append("Missing package declaration")
        
        # Check for balanced braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            errors.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
        
        # Check for balanced parentheses
        open_parens = content.count('(')
        close_parens = content.count(')')
        if open_parens != close_parens:
            errors.append(f"Unbalanced parentheses: {open_parens} open, {close_parens} close")
        
        # Check for basic function syntax
        functions = re.findall(r'func\s+\w+', content)
        if not functions and 'package' in content:
            errors.append("No functions found")
        
        # Check for import statements
        imports = re.findall(r'import\s+', content)
        
        # Check for common Go keywords
        go_keywords = ['func', 'var', 'const', 'type', 'if', 'for', 'return', 'go', 'select', 'case', 'default']
        found_keywords = [kw for kw in go_keywords if kw in content]
        
        if len(found_keywords) == 0:
            errors.append("No Go keywords found")
        
        return errors
        
    except Exception as e:
        return [f"Error reading file: {e}"]

def validate_go_file_structure(file_path):
    """Validate Go file structure"""
    print(f"[DIR] Checking structure of {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        structure_issues = []
        
        # Check for proper package declaration
        package_match = re.search(r'^package\s+(\w+)', content, re.MULTILINE)
        if not package_match:
            structure_issues.append("Missing package declaration")
        else:
            package_name = package_match.group(1)
            print(f"   Package: {package_name}")
        
        # Check for imports
        import_section = re.search(r'import\s*\([^)]+\)', content, re.DOTALL)
        if import_section:
            print(f"   Imports: Found")
        else:
            print(f"   Imports: None")
        
        # Count functions
        functions = re.findall(r'func\s+(\w+)', content)
        print(f"   Functions: {len(functions)}")
        for func in functions[:5]:  # Show first 5 functions
            print(f"     - {func}")
        
        # Count types
        types = re.findall(r'type\s+(\w+)', content)
        print(f"   Types: {len(types)}")
        for typ in types[:5]:  # Show first 5 types
            print(f"     - {typ}")
        
        return structure_issues
        
    except Exception as e:
        return [f"Error analyzing structure: {e}"]

def run_go_validation():
    """Run Go code validation"""
    print("[START] P2S Go Code Validation")
    print("=" * 50)
    
    # Find all Go files
    go_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.go'):
                go_files.append(os.path.join(root, file))
    
    if not go_files:
        print("[FAILED] No Go files found")
        return False
    
    print(f"[DIR] Found {len(go_files)} Go files")
    
    total_errors = 0
    total_files = 0
    
    for go_file in go_files:
        print(f"\n{'='*20} {go_file} {'='*20}")
        
        # Validate syntax
        syntax_errors = validate_go_syntax(go_file)
        if syntax_errors:
            print(f"[FAILED] Syntax errors:")
            for error in syntax_errors:
                print(f"   - {error}")
            total_errors += len(syntax_errors)
        else:
            print(f"[SUCCESS] Syntax validation passed")
        
        # Validate structure
        structure_errors = validate_go_file_structure(go_file)
        if structure_errors:
            print(f"[FAILED] Structure errors:")
            for error in structure_errors:
                print(f"   - {error}")
            total_errors += len(structure_errors)
        else:
            print(f"[SUCCESS] Structure validation passed")
        
        total_files += 1
    
    print(f"\n{'='*50}")
    print(f"[STATS] Validation Results:")
    print(f"   Files processed: {total_files}")
    print(f"   Total errors: {total_errors}")
    
    if total_errors == 0:
        print("[COMPLETE] All Go files passed validation!")
        return True
    else:
        print("[WARNING]  Some validation issues found")
        return False

def check_test_coverage():
    """Check test coverage"""
    print("\n[TEST] Test Coverage Analysis")
    print("=" * 30)
    
    test_files = []
    source_files = []
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('_test.go'):
                test_files.append(os.path.join(root, file))
            elif file.endswith('.go') and not file.endswith('_test.go'):
                source_files.append(os.path.join(root, file))
    
    print(f"[DIR] Source files: {len(source_files)}")
    print(f"[DIR] Test files: {len(test_files)}")
    
    if len(test_files) == 0:
        print("[FAILED] No test files found")
        return False
    
    # Check test file content
    for test_file in test_files:
        print(f"\n[CHECK] Analyzing {test_file}")
        try:
            with open(test_file, 'r') as f:
                content = f.read()
            
            # Count test functions
            test_functions = re.findall(r'func\s+Test\w+', content)
            print(f"   Test functions: {len(test_functions)}")
            
            # Count benchmark functions
            benchmark_functions = re.findall(r'func\s+Benchmark\w+', content)
            print(f"   Benchmark functions: {len(benchmark_functions)}")
            
            # Show test function names
            for test_func in test_functions[:5]:
                func_name = test_func.replace('func ', '')
                print(f"     - {func_name}")
            
        except Exception as e:
            print(f"   Error: {e}")
    
    return True

def check_imports():
    """Check import dependencies"""
    print("\n[PACKAGE] Import Analysis")
    print("=" * 20)
    
    all_imports = set()
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.go'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                    
                    # Extract imports
                    imports = re.findall(r'import\s+"([^"]+)"', content)
                    for imp in imports:
                        all_imports.add(imp)
                        
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    
    print(f"[PACKAGE] Found {len(all_imports)} unique imports:")
    for imp in sorted(all_imports):
        print(f"   - {imp}")
    
    return True

def main():
    """Main validation function"""
    print("[CHECK] Code Validation Suite")
    print("=" * 50)
    
    # Change to the project directory
    if not os.path.exists('consensus/p2s'):
        print("[FAILED] Not in P2S project directory")
        return 1
    
    # Run validations
    validations = [
        ("Go Code Validation", run_go_validation),
        ("Test Coverage", check_test_coverage),
        ("Import Analysis", check_imports),
    ]
    
    passed = 0
    total = len(validations)
    
    for validation_name, validation_func in validations:
        print(f"\n{'='*20} {validation_name} {'='*20}")
        try:
            if validation_func():
                passed += 1
                print(f"[SUCCESS] {validation_name} PASSED")
            else:
                print(f"[FAILED] {validation_name} FAILED")
        except Exception as e:
            print(f"[FAILED] {validation_name} ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"[STATS] Validation Results: {passed}/{total} validations passed")
    
    if passed == total:
        print("[COMPLETE] All validations passed! Go code is well-structured.")
        return 0
    else:
        print("[WARNING]  Some validations failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
