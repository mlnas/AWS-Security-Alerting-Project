import json
from datetime import datetime

class FindingParser:
    def __init__(self, sns_message):
        """Initialize parser with SNS message"""
        self.message = sns_message
        self.source = self._determine_source()

    def _determine_source(self):
        """Determine if finding is from GuardDuty or Security Hub"""
        if 'detail-type' in self.message:
            if self.message['detail-type'] == 'GuardDuty Finding':
                return 'guardduty'
            elif self.message['detail-type'] == 'Security Hub Findings - Imported':
                return 'securityhub'
        return 'unknown'

    def parse(self):
        """Parse finding based on source"""
        if self.source == 'guardduty':
            return self._parse_guardduty()
        elif self.source == 'securityhub':
            return self._parse_securityhub()
        else:
            raise ValueError(f"Unknown finding source: {self.source}")

    def _parse_guardduty(self):
        """Parse GuardDuty finding"""
        detail = self.message['detail']
        
        return {
            'title': detail['title'],
            'description': self._format_guardduty_description(detail),
            'severity': self._map_guardduty_severity(detail['severity']),
            'type': detail['type'],
            'region': self.message['region'],
            'account_id': self.message['account'],
            'time': detail['updatedAt'],
            'resource': detail.get('resource', {}),
            'raw_finding': detail
        }

    def _parse_securityhub(self):
        """Parse Security Hub finding"""
        findings = self.message['detail']['findings']
        if not findings:
            raise ValueError("No findings in Security Hub message")
            
        finding = findings[0]  # Process first finding
        
        return {
            'title': finding['Title'],
            'description': self._format_securityhub_description(finding),
            'severity': self._map_securityhub_severity(finding['Severity']['Label']),
            'type': finding['Types'][0] if finding.get('Types') else 'Unknown',
            'region': finding['Region'],
            'account_id': finding['AwsAccountId'],
            'time': finding['UpdatedAt'],
            'resource': finding.get('Resources', [{}])[0],
            'raw_finding': finding
        }

    def _format_guardduty_description(self, detail):
        """Format GuardDuty finding description"""
        return f"""
*Finding Details*
Type: {detail['type']}
First Seen: {detail['service']['eventFirstSeen']}
Last Seen: {detail['service']['eventLastSeen']}
Count: {detail['service']['count']}

*Affected Resource*
Type: {detail['resource']['resourceType']}
ID: {detail['resource'].get('resourceId', 'N/A')}

*Description*
{detail['description']}

*Additional Info*
{json.dumps(detail['service'].get('additionalInfo', {}), indent=2)}
"""

    def _format_securityhub_description(self, finding):
        """Format Security Hub finding description"""
        return f"""
*Finding Details*
Standard: {finding['ProductName']}
First Seen: {finding['FirstObservedAt']}
Last Seen: {finding['LastObservedAt']}
Status: {finding['Workflow']['Status']}

*Affected Resource*
Type: {finding['Resources'][0]['Type']}
ID: {finding['Resources'][0]['Id']}

*Description*
{finding['Description']}

*Remediation*
{finding.get('Remediation', {}).get('Recommendation', {}).get('Text', 'No remediation recommendation available')}
"""

    def _map_guardduty_severity(self, severity):
        """Map GuardDuty severity (0.1-10.0) to standard severity levels"""
        if severity >= 8.0:
            return 'CRITICAL'
        elif severity >= 6.0:
            return 'HIGH'
        elif severity >= 4.0:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _map_securityhub_severity(self, severity_label):
        """Map Security Hub severity labels to standard severity levels"""
        severity_map = {
            'CRITICAL': 'CRITICAL',
            'HIGH': 'HIGH',
            'MEDIUM': 'MEDIUM',
            'LOW': 'LOW',
            'INFORMATIONAL': 'LOW'
        }
        return severity_map.get(severity_label, 'MEDIUM') 