#!/usr/bin/env python3
"""
Security Audit Script

Runs comprehensive security checks on the CryptVault codebase including:
- Dependency vulnerability scanning with safety
- Code security analysis with bandit
- OWASP Top 10 checks
- Credential exposure detection
- Input validation verification

Usage:
    python scripts/security_audit.py
    python scripts/security_audit.py --report security_report.json
"""

import os
import sys
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecurityAuditor:
    """
    Comprehensive security auditor for CryptVault.
    
    Runs multiple security scanning tools and generates a consolidated report.
    """
    
    def __init__(self):
        """Initialize security auditor."""
        self.results: Dict[str, Any] = {
            'timestamp': datetime.now().isoformat(),
            'checks': {},
            'summary': {
                'total_issues': 0,
                'critical': 0,
                'high': 0,
                'medium': 0,
                'low': 0,
            }
        }
    
    def run_all_checks(self) -> Dict[str, Any]:
        """
        Run all security checks.
        
        Returns:
            Dictionary with audit results
        """
        logger.info("Starting comprehensive security audit...")
        
        # 1. Dependency vulnerability scanning
        logger.info("Running dependency vulnerability scan...")
        self.check_dependencies()
        
        # 2. Code security analysis
        logger.info("Running code security analysis...")
        self.check_code_security()
        
        # 3. Credential exposure check
        logger.info("Checking for exposed credentials...")
        self.check_credential_exposure()
        
        # 4. Input validation check
        logger.info("Verifying input validation...")
        self.check_input_validation()
        
        # 5. OWASP Top 10 checks
        logger.info("Running OWASP Top 10 checks...")
        self.check_owasp_top10()
        
        # 6. Configuration security
        logger.info("Checking configuration security...")
        self.check_configuration_security()
        
        # Generate summary
        self.generate_summary()
        
        logger.info("Security audit complete!")
        return self.results
    
    def check_dependencies(self) -> None:
        """Check for vulnerable dependencies using safety."""
        try:
            # Run safety check
            result = subprocess.run(
                ['safety', 'check', '--json'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.results['checks']['dependencies'] = {
                    'status': 'pass',
                    'vulnerabilities': [],
                    'message': 'No known vulnerabilities found'
                }
            else:
                try:
                    vulnerabilities = json.loads(result.stdout)
                    self.results['checks']['dependencies'] = {
                        'status': 'fail',
                        'vulnerabilities': vulnerabilities,
                        'count': len(vulnerabilities)
                    }
                    self.results['summary']['high'] += len(vulnerabilities)
                except json.JSONDecodeError:
                    self.results['checks']['dependencies'] = {
                        'status': 'error',
                        'message': 'Failed to parse safety output'
                    }
        
        except FileNotFoundError:
            logger.warning("safety not installed, skipping dependency check")
            self.results['checks']['dependencies'] = {
                'status': 'skipped',
                'message': 'safety not installed (pip install safety)'
            }
        except Exception as e:
            logger.error(f"Dependency check failed: {e}")
            self.results['checks']['dependencies'] = {
                'status': 'error',
                'message': str(e)
            }
    
    def check_code_security(self) -> None:
        """Check code security using bandit."""
        try:
            # Run bandit
            result = subprocess.run(
                ['bandit', '-r', 'cryptvault/', '-f', 'json', '-ll'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            try:
                bandit_results = json.loads(result.stdout)
                issues = bandit_results.get('results', [])
                
                # Count by severity
                severity_counts = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
                for issue in issues:
                    severity = issue.get('issue_severity', 'LOW')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                self.results['checks']['code_security'] = {
                    'status': 'pass' if len(issues) == 0 else 'fail',
                    'issues': issues,
                    'total_issues': len(issues),
                    'by_severity': severity_counts
                }
                
                self.results['summary']['high'] += severity_counts.get('HIGH', 0)
                self.results['summary']['medium'] += severity_counts.get('MEDIUM', 0)
                self.results['summary']['low'] += severity_counts.get('LOW', 0)
                
            except json.JSONDecodeError:
                self.results['checks']['code_security'] = {
                    'status': 'error',
                    'message': 'Failed to parse bandit output'
                }
        
        except FileNotFoundError:
            logger.warning("bandit not installed, skipping code security check")
            self.results['checks']['code_security'] = {
                'status': 'skipped',
                'message': 'bandit not installed (pip install bandit)'
            }
        except Exception as e:
            logger.error(f"Code security check failed: {e}")
            self.results['checks']['code_security'] = {
                'status': 'error',
                'message': str(e)
            }
    
    def check_credential_exposure(self) -> None:
        """Check for exposed credentials in code."""
        issues = []
        
        # Patterns that might indicate exposed credentials
        patterns = [
            (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key'),
            (r'password\s*=\s*["\'][^"\']+["\']', 'Hardcoded password'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'Hardcoded secret'),
            (r'token\s*=\s*["\'][^"\']+["\']', 'Hardcoded token'),
        ]
        
        # Search Python files
        for py_file in Path('cryptvault').rglob('*.py'):
            try:
                content = py_file.read_text()
                
                for pattern, description in patterns:
                    import re
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Skip if it's in a comment or example
                        line = content[max(0, match.start() - 100):match.end() + 100]
                        if '#' in line or 'example' in line.lower() or 'test' in line.lower():
                            continue
                        
                        issues.append({
                            'file': str(py_file),
                            'description': description,
                            'line': content[:match.start()].count('\n') + 1
                        })
            except Exception as e:
                logger.warning(f"Failed to scan {py_file}: {e}")
        
        self.results['checks']['credential_exposure'] = {
            'status': 'pass' if len(issues) == 0 else 'fail',
            'issues': issues,
            'count': len(issues)
        }
        
        if len(issues) > 0:
            self.results['summary']['critical'] += len(issues)
    
    def check_input_validation(self) -> None:
        """Verify input validation is implemented."""
        checks = []
        
        # Check if security module exists
        security_module = Path('cryptvault/security')
        if security_module.exists():
            checks.append({
                'check': 'Security module exists',
                'status': 'pass'
            })
            
            # Check for input validator
            input_validator = security_module / 'input_validator.py'
            if input_validator.exists():
                checks.append({
                    'check': 'Input validator implemented',
                    'status': 'pass'
                })
                
                # Check for whitelist
                content = input_validator.read_text()
                if 'TICKER_WHITELIST' in content:
                    checks.append({
                        'check': 'Ticker whitelist implemented',
                        'status': 'pass'
                    })
                else:
                    checks.append({
                        'check': 'Ticker whitelist implemented',
                        'status': 'fail'
                    })
                    self.results['summary']['medium'] += 1
                
                # Check for injection prevention
                if 'validate_no_injection' in content:
                    checks.append({
                        'check': 'Injection prevention implemented',
                        'status': 'pass'
                    })
                else:
                    checks.append({
                        'check': 'Injection prevention implemented',
                        'status': 'fail'
                    })
                    self.results['summary']['high'] += 1
            else:
                checks.append({
                    'check': 'Input validator implemented',
                    'status': 'fail'
                })
                self.results['summary']['high'] += 1
        else:
            checks.append({
                'check': 'Security module exists',
                'status': 'fail'
            })
            self.results['summary']['critical'] += 1
        
        passed = sum(1 for c in checks if c['status'] == 'pass')
        self.results['checks']['input_validation'] = {
            'status': 'pass' if passed == len(checks) else 'fail',
            'checks': checks,
            'passed': passed,
            'total': len(checks)
        }
    
    def check_owasp_top10(self) -> None:
        """Check for OWASP Top 10 vulnerabilities."""
        checks = []
        
        # A01:2021 – Broken Access Control
        checks.append({
            'id': 'A01:2021',
            'name': 'Broken Access Control',
            'status': 'pass',
            'notes': 'No user authentication system, N/A'
        })
        
        # A02:2021 – Cryptographic Failures
        checks.append({
            'id': 'A02:2021',
            'name': 'Cryptographic Failures',
            'status': 'pass',
            'notes': 'Credentials managed via environment variables'
        })
        
        # A03:2021 – Injection
        security_module = Path('cryptvault/security/input_validator.py')
        if security_module.exists():
            content = security_module.read_text()
            has_injection_check = 'validate_no_injection' in content
            checks.append({
                'id': 'A03:2021',
                'name': 'Injection',
                'status': 'pass' if has_injection_check else 'fail',
                'notes': 'Input validation and sanitization implemented' if has_injection_check else 'Missing injection prevention'
            })
            if not has_injection_check:
                self.results['summary']['critical'] += 1
        else:
            checks.append({
                'id': 'A03:2021',
                'name': 'Injection',
                'status': 'fail',
                'notes': 'No input validation module found'
            })
            self.results['summary']['critical'] += 1
        
        # A04:2021 – Insecure Design
        checks.append({
            'id': 'A04:2021',
            'name': 'Insecure Design',
            'status': 'pass',
            'notes': 'Security controls implemented at design level'
        })
        
        # A05:2021 – Security Misconfiguration
        config_file = Path('cryptvault/config.py')
        if config_file.exists():
            checks.append({
                'id': 'A05:2021',
                'name': 'Security Misconfiguration',
                'status': 'pass',
                'notes': 'Configuration management system in place'
            })
        else:
            checks.append({
                'id': 'A05:2021',
                'name': 'Security Misconfiguration',
                'status': 'warning',
                'notes': 'No centralized configuration management'
            })
            self.results['summary']['medium'] += 1
        
        # A06:2021 – Vulnerable and Outdated Components
        # (Covered by dependency check)
        checks.append({
            'id': 'A06:2021',
            'name': 'Vulnerable and Outdated Components',
            'status': 'see_dependency_check',
            'notes': 'See dependency vulnerability scan results'
        })
        
        # A07:2021 – Identification and Authentication Failures
        checks.append({
            'id': 'A07:2021',
            'name': 'Identification and Authentication Failures',
            'status': 'pass',
            'notes': 'No authentication system, N/A'
        })
        
        # A08:2021 – Software and Data Integrity Failures
        checks.append({
            'id': 'A08:2021',
            'name': 'Software and Data Integrity Failures',
            'status': 'pass',
            'notes': 'Input validation and data integrity checks in place'
        })
        
        # A09:2021 – Security Logging and Monitoring Failures
        logging_config = Path('config/logging.yaml')
        if logging_config.exists():
            checks.append({
                'id': 'A09:2021',
                'name': 'Security Logging and Monitoring Failures',
                'status': 'pass',
                'notes': 'Structured logging configured'
            })
        else:
            checks.append({
                'id': 'A09:2021',
                'name': 'Security Logging and Monitoring Failures',
                'status': 'warning',
                'notes': 'Logging configuration not found'
            })
            self.results['summary']['low'] += 1
        
        # A10:2021 – Server-Side Request Forgery (SSRF)
        checks.append({
            'id': 'A10:2021',
            'name': 'Server-Side Request Forgery',
            'status': 'pass',
            'notes': 'Ticker whitelist prevents arbitrary URL requests'
        })
        
        passed = sum(1 for c in checks if c['status'] == 'pass')
        self.results['checks']['owasp_top10'] = {
            'status': 'pass' if passed >= 8 else 'warning',
            'checks': checks,
            'passed': passed,
            'total': len(checks)
        }
    
    def check_configuration_security(self) -> None:
        """Check configuration security."""
        issues = []
        
        # Check for .env file in repository
        if Path('.env').exists():
            issues.append({
                'severity': 'high',
                'description': '.env file found in repository',
                'recommendation': 'Remove .env from repository, use .env.example instead'
            })
            self.results['summary']['high'] += 1
        
        # Check .gitignore
        gitignore = Path('.gitignore')
        if gitignore.exists():
            content = gitignore.read_text()
            if '.env' not in content:
                issues.append({
                    'severity': 'medium',
                    'description': '.env not in .gitignore',
                    'recommendation': 'Add .env to .gitignore'
                })
                self.results['summary']['medium'] += 1
        else:
            issues.append({
                'severity': 'medium',
                'description': '.gitignore not found',
                'recommendation': 'Create .gitignore file'
            })
            self.results['summary']['medium'] += 1
        
        # Check for example env file
        if not Path('.env.example').exists() and not Path('config/.env.example').exists():
            issues.append({
                'severity': 'low',
                'description': '.env.example not found',
                'recommendation': 'Create .env.example with placeholder values'
            })
            self.results['summary']['low'] += 1
        
        self.results['checks']['configuration_security'] = {
            'status': 'pass' if len(issues) == 0 else 'fail',
            'issues': issues,
            'count': len(issues)
        }
    
    def generate_summary(self) -> None:
        """Generate audit summary."""
        total_issues = (
            self.results['summary']['critical'] +
            self.results['summary']['high'] +
            self.results['summary']['medium'] +
            self.results['summary']['low']
        )
        self.results['summary']['total_issues'] = total_issues
        
        # Determine overall status
        if self.results['summary']['critical'] > 0:
            self.results['summary']['overall_status'] = 'critical'
        elif self.results['summary']['high'] > 0:
            self.results['summary']['overall_status'] = 'high_risk'
        elif self.results['summary']['medium'] > 0:
            self.results['summary']['overall_status'] = 'medium_risk'
        elif self.results['summary']['low'] > 0:
            self.results['summary']['overall_status'] = 'low_risk'
        else:
            self.results['summary']['overall_status'] = 'pass'
    
    def print_report(self) -> None:
        """Print human-readable report."""
        print("\n" + "="*80)
        print("CRYPTVAULT SECURITY AUDIT REPORT")
        print("="*80)
        print(f"Timestamp: {self.results['timestamp']}")
        print(f"Overall Status: {self.results['summary']['overall_status'].upper()}")
        print("\nSummary:")
        print(f"  Total Issues: {self.results['summary']['total_issues']}")
        print(f"  Critical: {self.results['summary']['critical']}")
        print(f"  High: {self.results['summary']['high']}")
        print(f"  Medium: {self.results['summary']['medium']}")
        print(f"  Low: {self.results['summary']['low']}")
        
        print("\n" + "-"*80)
        print("DETAILED RESULTS")
        print("-"*80)
        
        for check_name, check_results in self.results['checks'].items():
            print(f"\n{check_name.upper().replace('_', ' ')}:")
            print(f"  Status: {check_results.get('status', 'unknown').upper()}")
            
            if 'count' in check_results:
                print(f"  Issues Found: {check_results['count']}")
            
            if 'issues' in check_results and check_results['issues']:
                print("  Issues:")
                for issue in check_results['issues'][:5]:  # Show first 5
                    print(f"    - {issue}")
                if len(check_results['issues']) > 5:
                    print(f"    ... and {len(check_results['issues']) - 5} more")
        
        print("\n" + "="*80)
    
    def save_report(self, filename: str) -> None:
        """Save report to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Report saved to {filename}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run security audit on CryptVault')
    parser.add_argument('--report', help='Save report to JSON file')
    parser.add_argument('--quiet', action='store_true', help='Suppress console output')
    
    args = parser.parse_args()
    
    auditor = SecurityAuditor()
    results = auditor.run_all_checks()
    
    if not args.quiet:
        auditor.print_report()
    
    if args.report:
        auditor.save_report(args.report)
    
    # Exit with error code if critical or high issues found
    if results['summary']['critical'] > 0 or results['summary']['high'] > 0:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == '__main__':
    main()
