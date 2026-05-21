import os
import re
from datetime import datetime

def analyze_logs(log_file_path, report_output_path):
    print(f"[+] Launching Cyber Security Log Analysis on: {log_file_path}")
    
    if not os.path.exists(log_file_path):
        print(f"[-] Error: Target log file '{log_file_path}' does not exist.")
        return

    # Dictionary to track failed attempts per IP address
    failed_attempts = {}
    
    # Regex pattern to capture timestamp, log level, message, and IP address
    log_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\w+) (.*) from (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'

    with open(log_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            match = re.search(log_pattern, line)
            if match:
                timestamp, log_level, message, ip_address = match.groups()
                
                # Isolate WARN levels indicating failed login attempts
                if "Failed login" in message or log_level == "WARN":
                    failed_attempts[ip_address] = failed_attempts.get(ip_address, 0) + 1

    # Threshold configuration: More than 3 failures triggers an incident flag
    SUSPICIOUS_THRESHOLD = 3
    flagged_incidents = {ip: count for ip, count in failed_attempts.items() if count > SUSPICIOUS_THRESHOLD}

    # Generate the Automated Incident Markdown Report
    generate_markdown_report(report_output_path, log_file_path, flagged_incidents, failed_attempts)

def generate_markdown_report(output_path, source_log, flagged_incidents, all_failures):
    timestamp_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(output_path, 'w', encoding='utf-8') as report:
        report.write(f"# 🛡️ Automated Cyber Security Incident Report\n\n")
        report.write(f"**Generated On:** {timestamp_now}  \n")
        report.write(f"**Source Log Audited:** `{source_log}`  \n")
        report.write(f"**Status:** {'⚠️ ACTION REQUIRED' if flagged_incidents else '✅ SYSTEM SECURE'}\n\n")
        report.write("--- \n\n")
        
        if flagged_incidents:
            report.write("## 🚨 High-Risk Anomalies Detected (Brute-Force Threat Indicators)\n")
            report.write("The system flagged the following external IP addresses for exceeding the unauthorized access failure threshold:\n\n")
            report.write("| Target Attacker IP | Total Failed Attempts | Security Severity Level |\n")
            report.write("| :--- | :---: | :--- |\n")
            
            for ip, count in flagged_incidents.items():
                report.write(f"| `{ip}` | {count} | **CRITICAL (Potential Brute Force)** |\n")
            
            report.write("\n### 🛠️ Recommended Mitigation Protocols:\n")
            report.write("1. Implement an immediate perimeter firewall block on the flagged malicious IP addresses.\n")
            report.write("2. Force password resets for commonly targeted usernames (e.g., `root`, `admin`).\n")
            report.write("3. Enable Multi-Factor Authentication (MFA) across all external-facing SSH endpoints.\n")
        else:
            report.write("## ✅ Internal System Audit Results\n")
            report.write("No suspicious login patterns or threshold breaches were identified during this operational log review cycle.\n")

    print(f"[+] Security analysis complete.")
    print(f"[+] Incident Summary compiled and saved to: {output_path}")

if __name__ == "__main__":
    analyze_logs('auth.log', 'incident_report.md')