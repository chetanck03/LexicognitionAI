#!/usr/bin/env python3
"""
Verify that the application is ready for Render deployment.
Run this before deploying to catch common issues.
"""
import sys
from pathlib import Path


def check_file_exists(filepath, description):
    """Check if a file exists."""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} missing: {filepath}")
        return False


def check_requirements():
    """Check if requirements.txt has necessary packages."""
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read()
            required = ['fastapi', 'uvicorn', 'gunicorn', 'groq', 'openai']
            missing = [pkg for pkg in required if pkg not in content.lower()]
            
            if not missing:
                print(f"✅ requirements.txt has all required packages")
                return True
            else:
                print(f"❌ requirements.txt missing: {', '.join(missing)}")
                return False
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False


def check_env_example():
    """Check if .env.example exists and has required keys."""
    try:
        with open('.env.example', 'r') as f:
            content = f.read()
            required = ['GROQ_API_KEY', 'OPENAI_API_KEY', 'LLM_PROVIDER']
            missing = [key for key in required if key not in content]
            
            if not missing:
                print(f"✅ .env.example has all required keys")
                return True
            else:
                print(f"❌ .env.example missing: {', '.join(missing)}")
                return False
    except FileNotFoundError:
        print("❌ .env.example not found")
        return False


def check_gitignore():
    """Check if .gitignore excludes .env."""
    try:
        with open('.gitignore', 'r') as f:
            content = f.read()
            if '.env' in content:
                print("✅ .gitignore excludes .env (secrets safe)")
                return True
            else:
                print("⚠️  .env not in .gitignore - secrets might be committed!")
                return False
    except FileNotFoundError:
        print("⚠️  .gitignore not found")
        return False


def check_main_file():
    """Check if main.py exists and has FastAPI app."""
    try:
        with open('main.py', 'r') as f:
            content = f.read()
            if 'FastAPI' in content and 'app = FastAPI' in content:
                print("✅ main.py has FastAPI app")
                return True
            else:
                print("❌ main.py doesn't have FastAPI app")
                return False
    except FileNotFoundError:
        print("❌ main.py not found")
        return False


def main():
    """Run all checks."""
    print("🔍 Verifying Render Deployment Readiness...\n")
    
    checks = [
        check_file_exists('render.yaml', 'Render config'),
        check_file_exists('requirements.txt', 'Requirements file'),
        check_file_exists('main.py', 'Main application'),
        check_file_exists('.env.example', 'Environment template'),
        check_file_exists('DEPLOYMENT.md', 'Deployment guide'),
        check_requirements(),
        check_env_example(),
        check_gitignore(),
        check_main_file(),
    ]
    
    print("\n" + "="*50)
    
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"✅ All checks passed! ({passed}/{total})")
        print("\n🚀 Ready to deploy to Render!")
        print("\nNext steps:")
        print("1. Push to GitHub: git push origin main")
        print("2. Go to https://dashboard.render.com")
        print("3. Click 'New +' → 'Blueprint'")
        print("4. Connect your repository")
        print("5. Add API keys as secrets")
        print("\nSee RENDER_QUICKSTART.md for detailed steps.")
        return 0
    else:
        print(f"⚠️  {total - passed} check(s) failed ({passed}/{total} passed)")
        print("\n❌ Fix the issues above before deploying.")
        print("\nSee DEPLOYMENT.md for help.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
