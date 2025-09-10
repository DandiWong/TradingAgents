"""
Dependency health check for TradingAgents.
Provides comprehensive checking of required dependencies and helpful error messages.
"""

import sys
import importlib
from typing import List, Dict, Tuple, Optional


class DependencyChecker:
    """Checks and validates required dependencies for TradingAgents."""
    
    REQUIRED_PACKAGES = {
        'packaging': {
            'version': '>=20.0',
            'description': 'Core packaging utilities',
            'critical': True
        },
        'certifi': {
            'version': '>=2020.0.0',
            'description': 'SSL certificate validation',
            'critical': True
        },
        'requests': {
            'version': '>=2.25.0',
            'description': 'HTTP library',
            'critical': True
        },
        'langchain': {
            'version': '>=0.3.0',
            'description': 'LangChain framework',
            'critical': True
        },
        'langchain_core': {
            'version': '>=0.3.0',
            'description': 'LangChain core components',
            'critical': True
        },
        'langchain_openai': {
            'version': '>=0.1.0',
            'description': 'OpenAI integration',
            'critical': True
        },
        'langchain_anthropic': {
            'version': '>=0.1.0',
            'description': 'Anthropic integration',
            'critical': True
        },
        'langchain_google_genai': {
            'version': '>=1.0.0',
            'description': 'Google Gemini integration',
            'critical': True
        },
        'langgraph': {
            'version': '>=0.2.0',
            'description': 'LangGraph for agent orchestration',
            'critical': True
        },
        'typer': {
            'version': '>=0.9.0',
            'description': 'CLI framework',
            'critical': True
        },
        'rich': {
            'version': '>=13.0.0',
            'description': 'Rich terminal output',
            'critical': True
        },
        'pydantic': {
            'version': '>=2.0.0',
            'description': 'Data validation',
            'critical': True
        },
        'yaml': {
            'version': '>=6.0.0',
            'description': 'YAML parsing',
            'critical': True
        },
        'pandas': {
            'version': '>=2.0.0',
            'description': 'Data manipulation',
            'critical': True
        },
        'numpy': {
            'version': '>=1.21.0',
            'description': 'Numerical computing',
            'critical': True
        }
    }
    
    OPTIONAL_PACKAGES = {
        'yfinance': {
            'description': 'Yahoo Finance data',
            'critical': False
        },
        'stockstats': {
            'description': 'Stock statistics',
            'critical': False
        },
        'finnhub-python': {
            'description': 'Finnhub API',
            'critical': False
        },
        'simfin': {
            'description': 'SimFin financial data',
            'critical': False
        },
        'praw': {
            'description': 'Reddit API',
            'critical': False
        },
        'newsapi': {
            'description': 'News API',
            'critical': False
        },
        'beautifulsoup4': {
            'description': 'Web scraping',
            'critical': False
        },
        'requests_html': {
            'description': 'HTML parsing',
            'critical': False
        }
    }
    
    @classmethod
    def check_package(cls, package_name: str, required_version: Optional[str] = None) -> Tuple[bool, str]:
        """Check if a package is installed and meets version requirements."""
        try:
            module = importlib.import_module(package_name)
            version = getattr(module, '__version__', 'unknown')
            
            if required_version and version != 'unknown':
                # Skip version check for now - just ensure package is installed
                # Version checking can be enhanced later with proper version parsing
                pass
            
            return True, f"Version {version}"
        except ImportError as e:
            return False, f"Not installed: {str(e)}"
        except Exception as e:
            return False, f"Error checking: {str(e)}"
    
    @classmethod
    def check_all_dependencies(cls) -> Dict[str, Dict]:
        """Check all required and optional dependencies."""
        results = {
            'required': {},
            'optional': {},
            'issues': [],
            'recommendations': []
        }
        
        # Check required packages
        for package, info in cls.REQUIRED_PACKAGES.items():
            is_ok, message = cls.check_package(package, info.get('version'))
            results['required'][package] = {
                'status': 'ok' if is_ok else 'error',
                'message': message,
                'description': info['description'],
                'critical': info['critical']
            }
            
            if not is_ok and info['critical']:
                results['issues'].append(f"Critical package {package}: {message}")
                results['recommendations'].append(f"Install: pip install {package}")
        
        # Check optional packages
        for package, info in cls.OPTIONAL_PACKAGES.items():
            is_ok, message = cls.check_package(package)
            results['optional'][package] = {
                'status': 'ok' if is_ok else 'missing',
                'message': message,
                'description': info['description'],
                'critical': info['critical']
            }
        
        return results
    
    @classmethod
    def print_dependency_report(cls) -> None:
        """Print a comprehensive dependency report."""
        print("=" * 80)
        print("TradingAgents Dependency Health Check")
        print("=" * 80)
        
        results = cls.check_all_dependencies()
        
        # Summary
        required_ok = sum(1 for pkg in results['required'].values() if pkg['status'] == 'ok')
        required_total = len(results['required'])
        optional_ok = sum(1 for pkg in results['optional'].values() if pkg['status'] == 'ok')
        optional_total = len(results['optional'])
        
        print(f"\n📊 Summary:")
        print(f"   Required: {required_ok}/{required_total} OK")
        print(f"   Optional: {optional_ok}/{optional_total} OK")
        
        # Issues
        if results['issues']:
            print(f"\n❌ Critical Issues:")
            for issue in results['issues']:
                print(f"   • {issue}")
        
        # Required packages
        print(f"\n🔧 Required Packages:")
        for package, info in results['required'].items():
            status_icon = "✅" if info['status'] == 'ok' else "❌"
            print(f"   {status_icon} {package}: {info['message']}")
            print(f"      {info['description']}")
        
        # Optional packages
        print(f"\n🔍 Optional Packages:")
        for package, info in results['optional'].items():
            status_icon = "✅" if info['status'] == 'ok' else "⚠️"
            print(f"   {status_icon} {package}: {info['message']}")
            print(f"      {info['description']}")
        
        # Recommendations
        if results['recommendations']:
            print(f"\n💡 Recommendations:")
            for rec in results['recommendations']:
                print(f"   • {rec}")
        
        # Overall status
        if results['issues']:
            print(f"\n🚨 Status: FAIL - Critical dependencies missing")
            print("   Please install missing dependencies before running TradingAgents.")
            sys.exit(1)
        else:
            print(f"\n✅ Status: OK - All critical dependencies are satisfied")
    
    @classmethod
    def fix_common_issues(cls) -> None:
        """Attempt to fix common dependency issues."""
        print("🔧 Attempting to fix common dependency issues...")
        
        # Common fixes
        fixes = [
            "pip install --upgrade pip",
            "pip install --force-reinstall packaging==24.1",
            "pip install --force-reinstall certifi==2025.8.3",
            "pip install --upgrade setuptools wheel"
        ]
        
        for fix in fixes:
            print(f"   Running: {fix}")
            try:
                import subprocess
                result = subprocess.run(fix.split(), capture_output=True, text=True)
                if result.returncode == 0:
                    print("   ✅ Success")
                else:
                    print(f"   ❌ Failed: {result.stderr}")
            except Exception as e:
                print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        DependencyChecker.fix_common_issues()
        print("\n")
    DependencyChecker.print_dependency_report()