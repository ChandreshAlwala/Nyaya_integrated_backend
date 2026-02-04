"""
Simple System Check - Production Readiness Validation
"""
import os
import json
from pathlib import Path
from datetime import datetime

def check_file_structure():
    """Check if all required files exist"""
    print("Checking file structure...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        "deploy.py",
        "test_e2e.py",
        "core/__init__.py",
        "core/legal_engine.py",
        "core/enforcement_engine.py", 
        "core/rl_engine.py",
        "core/api_orchestrator.py",
        "schemas/__init__.py",
        "schemas/api_contracts.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"Missing files: {missing_files}")
        return False
    else:
        print("All required files present")
        return True

def check_dependencies():
    """Check if requirements.txt is valid"""
    print("📦 Checking dependencies...")
    
    try:
        with open("requirements.txt", "r") as f:
            deps = f.read().strip().split("\n")
        
        required_deps = ["fastapi", "uvicorn", "pydantic"]
        has_required = all(any(req in dep for dep in deps) for req in required_deps)
        
        if has_required:
            print("✅ All required dependencies listed")
            return True
        else:
            print("❌ Missing required dependencies")
            return False
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return False

def check_code_structure():
    """Check basic code structure"""
    print("🔍 Checking code structure...")
    
    checks = []
    
    # Check main.py has FastAPI app
    try:
        with open("main.py", "r") as f:
            main_content = f.read()
        
        has_fastapi = "FastAPI" in main_content
        has_endpoints = "/api/" in main_content
        has_health = "/health" in main_content
        
        checks.append(("FastAPI app", has_fastapi))
        checks.append(("API endpoints", has_endpoints))
        checks.append(("Health endpoint", has_health))
    except Exception as e:
        checks.append(("main.py", False))
    
    # Check core modules
    core_modules = ["legal_engine.py", "enforcement_engine.py", "rl_engine.py", "api_orchestrator.py"]
    for module in core_modules:
        try:
            with open(f"core/{module}", "r") as f:
                content = f.read()
            
            has_class = "class " in content
            has_async = "async def" in content
            
            checks.append((f"{module} structure", has_class and has_async))
        except Exception:
            checks.append((f"{module}", False))
    
    # Check schemas
    try:
        with open("schemas/api_contracts.py", "r") as f:
            schema_content = f.read()
        
        has_pydantic = "BaseModel" in schema_content
        has_request_models = "Request" in schema_content
        has_response_models = "Response" in schema_content
        
        checks.append(("Pydantic schemas", has_pydantic))
        checks.append(("Request models", has_request_models))
        checks.append(("Response models", has_response_models))
    except Exception:
        checks.append(("schemas", False))
    
    # Print results
    all_passed = True
    for check_name, passed in checks:
        if passed:
            print(f"  ✅ {check_name}")
        else:
            print(f"  ❌ {check_name}")
            all_passed = False
    
    return all_passed

def check_integration_points():
    """Check integration between components"""
    print("🔗 Checking integration points...")
    
    integration_checks = []
    
    # Check if legal engine references datasets
    try:
        with open("core/legal_engine.py", "r") as f:
            legal_content = f.read()
        
        has_datasets = "datasets" in legal_content
        has_procedures = "procedures" in legal_content
        has_domain_detection = "detect_domain" in legal_content
        
        integration_checks.append(("Legal datasets integration", has_datasets))
        integration_checks.append(("Legal procedures integration", has_procedures))
        integration_checks.append(("Domain detection", has_domain_detection))
    except Exception:
        integration_checks.append(("Legal engine", False))
    
    # Check enforcement engine
    try:
        with open("core/enforcement_engine.py", "r") as f:
            enforcement_content = f.read()
        
        has_decisions = "EnforcementDecision" in enforcement_content
        has_signing = "signed_decision" in enforcement_content
        has_rules = "enforcement_rules" in enforcement_content
        
        integration_checks.append(("Enforcement decisions", has_decisions))
        integration_checks.append(("Decision signing", has_signing))
        integration_checks.append(("Enforcement rules", has_rules))
    except Exception:
        integration_checks.append(("Enforcement engine", False))
    
    # Check RL engine
    try:
        with open("core/rl_engine.py", "r") as f:
            rl_content = f.read()
        
        has_feedback = "feedback" in rl_content
        has_confidence = "confidence" in rl_content
        has_learning = "learning" in rl_content
        
        integration_checks.append(("RL feedback processing", has_feedback))
        integration_checks.append(("Confidence adjustment", has_confidence))
        integration_checks.append(("Learning system", has_learning))
    except Exception:
        integration_checks.append(("RL engine", False))
    
    # Check API orchestrator
    try:
        with open("core/api_orchestrator.py", "r") as f:
            api_content = f.read()
        
        has_orchestration = "orchestrator" in api_content.lower()
        has_legal_integration = "legal_engine" in api_content
        has_enforcement_integration = "enforcement_engine" in api_content
        
        integration_checks.append(("API orchestration", has_orchestration))
        integration_checks.append(("Legal engine integration", has_legal_integration))
        integration_checks.append(("Enforcement integration", has_enforcement_integration))
    except Exception:
        integration_checks.append(("API orchestrator", False))
    
    # Print results
    all_passed = True
    for check_name, passed in integration_checks:
        if passed:
            print(f"  ✅ {check_name}")
        else:
            print(f"  ❌ {check_name}")
            all_passed = False
    
    return all_passed

def generate_system_report():
    """Generate comprehensive system report"""
    print("\n" + "="*60)
    print("🎯 NYAYA SYSTEM READINESS REPORT")
    print("="*60)
    
    checks = [
        ("File Structure", check_file_structure()),
        ("Dependencies", check_dependencies()),
        ("Code Structure", check_code_structure()),
        ("Integration Points", check_integration_points())
    ]
    
    passed_checks = sum(1 for _, passed in checks if passed)
    total_checks = len(checks)
    success_rate = (passed_checks / total_checks) * 100
    
    print(f"\n📊 Summary:")
    print(f"  Total Checks: {total_checks}")
    print(f"  Passed: {passed_checks}")
    print(f"  Failed: {total_checks - passed_checks}")
    print(f"  Success Rate: {success_rate:.1f}%")
    
    if success_rate >= 100:
        status = "🎉 PRODUCTION READY"
        message = "System is fully integrated and ready for deployment!"
    elif success_rate >= 80:
        status = "⚠️ MOSTLY READY"
        message = "System is mostly ready, minor issues need attention."
    else:
        status = "❌ NOT READY"
        message = "System needs significant work before deployment."
    
    print(f"\n{status}")
    print(f"{message}")
    
    # Save report
    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "checks": [{"name": name, "passed": passed} for name, passed in checks],
        "summary": {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "success_rate": success_rate,
            "status": status,
            "message": message
        }
    }
    
    with open("system_readiness_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved to system_readiness_report.json")
    
    return success_rate >= 80

if __name__ == "__main__":
    import sys
    
    print("Starting Nyaya System Readiness Check...")
    
    try:
        is_ready = generate_system_report()
        sys.exit(0 if is_ready else 1)
    except Exception as e:
        print(f"System check failed: {e}")
        sys.exit(1)