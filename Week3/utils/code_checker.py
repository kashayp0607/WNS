import subprocess
import tempfile
import os
import sys
from typing import Dict, Any, List

class CodeChecker:
    """Code Quality Checker using Ruff linter"""
    
    @staticmethod
    def is_ruff_installed() -> bool:
        """Check if Ruff is installed"""
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'ruff', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    @staticmethod
    def check_python_code(code: str) -> Dict[str, Any]:
        """Check Python code quality using Ruff"""
        if not CodeChecker.is_ruff_installed():
            return {
                "success": False,
                "error": "Ruff is not installed. Install it with: pip install ruff",
                "skip_linting": True
            }
        
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(code)
                temp_file_path = temp_file.name
            
            result = subprocess.run(
                [sys.executable, '-m', 'ruff', 'check', temp_file_path, '--output-format=json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            try:
                os.unlink(temp_file_path)
            except:
                pass
            
            if result.stdout:
                import json
                try:
                    issues = json.loads(result.stdout)
                except json.JSONDecodeError:
                    issues = []
                
                return {
                    "success": True,
                    "has_issues": len(issues) > 0,
                    "issue_count": len(issues),
                    "issues": CodeChecker._format_ruff_issues(issues)
                }
            else:
                return {
                    "success": True,
                    "has_issues": False,
                    "issue_count": 0,
                    "issues": [],
                    "message": "✅ No issues found! Code quality is excellent."
                }
                
        except Exception as e:
            try:
                os.unlink(temp_file_path)
            except:
                pass
            return {
                "success": False,
                "error": f"Error: {str(e)}",
                "skip_linting": True
            }
    
    @staticmethod
    def _format_ruff_issues(issues: List[Dict]) -> List[Dict[str, Any]]:
        """Format Ruff issues for display"""
        formatted = []
        for issue in issues:
            formatted.append({
                "line": issue.get("location", {}).get("row", "N/A"),
                "column": issue.get("location", {}).get("column", "N/A"),
                "rule": issue.get("code", "N/A"),
                "message": issue.get("message", "N/A"),
                "severity": CodeChecker._get_severity(issue.get("code", "")),
                "fix": issue.get("fix", {}).get("message") if issue.get("fix") else None
            })
        return formatted
    
    @staticmethod
    def _get_severity(rule_code: str) -> str:
        """Determine severity based on rule code"""
        if rule_code.startswith("E"):
            return "🔴 Error"
        elif rule_code.startswith("W"):
            return "🟡 Warning"
        elif rule_code.startswith("F"):
            return "🔴 Fatal"
        else:
            return "ℹ️ Info"
    
    @staticmethod
    def format_issues_for_display(issues: List[Dict[str, Any]]) -> str:
        """Format issues for Streamlit display"""
        if not issues:
            return "✅ **No issues found!**"
        
        formatted = f"### ⚠️ Found {len(issues)} Issue(s)\n\n"
        for i, issue in enumerate(issues, 1):
            formatted += f"**Issue {i}:** {issue['severity']}\n"
            formatted += f"- **Location:** Line {issue['line']}, Column {issue['column']}\n"
            formatted += f"- **Rule:** `{issue['rule']}`\n"
            formatted += f"- **Message:** {issue['message']}\n"
            if issue.get('fix'):
                formatted += f"- **Suggested Fix:** {issue['fix']}\n"
            formatted += "\n"
        return formatted
