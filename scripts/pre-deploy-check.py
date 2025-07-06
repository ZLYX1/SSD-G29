#!/usr/bin/env python3
"""
Pre-deployment validation script for Safe Companions project.
This script checks for common issues that break CI/CD deployments.
"""

import os
import sys
import re
import subprocess
from pathlib import Path

def check_git_merge_conflicts():
    """Check for unresolved Git merge conflicts."""
    print("Checking for Git merge conflicts...")
    
    conflict_patterns = [
        r'<<<<<<<\s',
        r'=======\s*$',
        r'>>>>>>>\s'
    ]
    
    issues = []
    
    # Check all Python files
    for py_file in Path('.').rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in conflict_patterns:
                        if re.search(pattern, line):
                            issues.append(f"  ERROR: {py_file}:{i} - Merge conflict marker found")
        except Exception as e:
            print(f"  WARNING: Could not read {py_file}: {e}")
    
    if issues:
        print("ERROR: Git merge conflicts found:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("PASS: No Git merge conflicts found")
        return True

def check_duplicate_routes():
    """Check for duplicate Flask route definitions."""
    print("Checking for duplicate Flask routes...")
    
    route_definitions = {}
    function_names = {}
    issues = []
    
    # Check all Python files in blueprint directory
    blueprint_dir = Path('blueprint')
    if blueprint_dir.exists():
        for py_file in blueprint_dir.glob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                    current_route = None
                    blueprint_name = None
                    
                    for i, line in enumerate(lines):
                        # Find blueprint definition
                        if '_bp = Blueprint(' in line:
                            blueprint_name = line.split('_bp')[0].strip()
                        
                        # Find route definitions
                        if '@' in line and '.route(' in line:
                            route_match = re.search(r'@(\w+)\.route\([\'"]([^\'"]+)[\'"]', line)
                            if route_match:
                                bp_name = route_match.group(1)
                                route_path = route_match.group(2)
                                current_route = (bp_name, route_path)
                        
                        # Find function definitions that come after routes
                        elif current_route and line.strip().startswith('def '):
                            func_match = re.search(r'def\s+(\w+)\s*\(', line)
                            if func_match:
                                func_name = func_match.group(1)
                                bp_name, route_path = current_route
                                
                                # Check for duplicate routes in same blueprint
                                route_key = f"{bp_name}:{route_path}"
                                if route_key in route_definitions:
                                    issues.append(f"  ERROR: Duplicate route '{route_path}' in blueprint '{bp_name}' ({py_file})")
                                else:
                                    route_definitions[route_key] = (py_file, func_name)
                                
                                # Check for duplicate function names in same file
                                func_key = f"{py_file}:{func_name}"
                                if func_key in function_names:
                                    issues.append(f"  ERROR: Duplicate function '{func_name}' in {py_file}")
                                else:
                                    function_names[func_key] = route_key
                                
                                current_route = None
                            
            except Exception as e:
                print(f"  WARNING: Could not read {py_file}: {e}")
    
    if issues:
        print("ERROR: Duplicate routes/functions found:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("PASS: No duplicate routes found")
        return True

def check_python_syntax():
    """Check Python syntax for all files."""
    print("Checking Python syntax...")
    
    issues = []
    
    # Check all Python files
    for py_file in Path('.').rglob('*.py'):
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', str(py_file)],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                issues.append(f"  ERROR: {py_file} - Syntax error: {result.stderr.strip()}")
        except Exception as e:
            issues.append(f"  ERROR: {py_file} - Could not check syntax: {e}")
    
    if issues:
        print("ERROR: Python syntax errors found:")
        for issue in issues:
            print(issue)
        return False
    else:
        print("PASS: No Python syntax errors found")
        return True

def check_flask_imports():
    """Check if Flask application can be imported."""
    print("Checking Flask application imports...")
    
    try:
        # Try to import the main app
        result = subprocess.run(
            [sys.executable, '-c', 'from app import app; print("PASS: Flask app imported successfully")'],
            capture_output=True,
            text=True,
            cwd='.'
        )
        
        if result.returncode == 0:
            print("PASS: Flask application imports successfully")
            return True
        else:
            print(f"ERROR: Flask import failed: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"ERROR: Could not test Flask imports: {e}")
        return False

def main():
    """Run all pre-deployment checks."""
    print("Safe Companions Pre-Deployment Validation")
    print("=" * 50)
    
    checks = [
        check_git_merge_conflicts,
        check_duplicate_routes,
        check_python_syntax,
        check_flask_imports
    ]
    
    all_passed = True
    
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("SUCCESS: All pre-deployment checks passed! Safe to deploy.")
        return 0
    else:
        print("FAILED: Some checks failed. Please fix the issues before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
