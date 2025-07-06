# Pre-Deployment Validation Scripts

This directory contains scripts to validate your code before deploying to production, helping prevent CI/CD pipeline failures.

## Scripts

### 1. `pre-deploy-check.py`
**Main validation script** that checks for common issues that break production deployments.

**Checks performed:**
- ✅ Git merge conflicts (unresolved conflict markers)
- ✅ Duplicate Flask route definitions
- ✅ Python syntax errors
- ✅ Flask application import issues

**Usage:**
```bash
python scripts/pre-deploy-check.py
```

### 2. `pre-deploy-check.bat`
**Windows batch script** wrapper for easy execution on Windows.

**Usage:**
```cmd
scripts\pre-deploy-check.bat
```

### 3. `pre-deploy-check.ps1`
**PowerShell script** wrapper for PowerShell users.

**Usage:**
```powershell
.\scripts\pre-deploy-check.ps1
```

## Integration with CI/CD

### Recommended Usage

**Before every deployment:**
1. Run the pre-deployment check script
2. Fix any issues found
3. Re-run the script to confirm all issues are resolved
4. Deploy to production

### Example Integration

Add to your CI/CD pipeline:
```yaml
- name: Pre-deployment validation
  run: python scripts/pre-deploy-check.py
```

## Common Issues Detected

### 1. Git Merge Conflicts
**What it catches:**
- Unresolved merge conflict markers: `<<<<<<<`, `=======`, `>>>>>>>`
- Invalid syntax from incomplete merges

**Example:**
```python
# Bad - This will break production
def my_function():
<<<<<<< HEAD
    return "version 1"
=======
    return "version 2"
>>>>>>> branch
```

### 2. Duplicate Flask Routes
**What it catches:**
- Multiple `@blueprint.route()` definitions with same path
- Duplicate function names in same blueprint

**Example:**
```python
# Bad - This will break Flask
@browse_bp.route('/browse', methods=['GET'])
def browseEscort():
    return render_template('browse.html')

@browse_bp.route('/browse', methods=['GET'])  # Duplicate!
def browseEscort():  # Same name!
    return render_template('browse.html')
```

### 3. Python Syntax Errors
**What it catches:**
- Invalid Python syntax
- Missing imports
- Indentation errors

### 4. Flask Import Issues
**What it catches:**
- Missing Flask dependencies
- Circular import problems
- Configuration issues

## Exit Codes

- `0`: All checks passed ✅
- `1`: One or more checks failed ❌

## Customization

To add more checks, edit `pre-deploy-check.py` and add new validation functions to the `checks` list in `main()`.

## History

**Created:** July 5, 2025  
**Purpose:** Prevent CI/CD pipeline failures from common code issues  
**Motivation:** Resolved production deployment failure caused by unresolved Git merge conflicts in `browse.py`
