"""Multi-format exporting for scan results."""

import json
import csv
from pathlib import Path
from typing import List, Optional
from datetime import datetime


class Exporter:
    """Export scan results to multiple formats."""

    def __init__(self, output_dir: Path = None):
        """Initialize exporter.

        Args:
            output_dir: Directory for exported files
        """
        self.output_dir = output_dir or Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def to_json(self, findings: List, scan_session, filename: str = "findings.json") -> Path:
        """Export to JSON format.

        Args:
            findings: List of findings
            scan_session: Associated scan session
            filename: Output filename

        Returns:
            Path to exported file
        """
        output_path = self.output_dir / filename

        data = {
            "session_id": scan_session.id,
            "target_path": scan_session.target_path,
            "mode": scan_session.mode,
            "start_time": scan_session.start_time.isoformat() if scan_session.start_time else None,
            "end_time": scan_session.end_time.isoformat() if scan_session.end_time else None,
            "total_findings": len(findings),
            "findings": [
                {
                    "id": f.id,
                    "file_path": f.file_path,
                    "data_type": f.data_type,
                    "pattern_id": f.pattern_id,
                    "risk_score": f.risk_score,
                    "confidence": f.confidence.value if hasattr(f.confidence, "value") else str(f.confidence),
                    "detected_at": f.discovered_at.isoformat(),
                }
                for f in findings
            ],
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        return output_path

    def to_csv(self, findings: List, filename: str = "findings.csv") -> Path:
        """Export to CSV format.

        Args:
            findings: List of findings
            filename: Output filename

        Returns:
            Path to exported file
        """
        output_path = self.output_dir / filename

        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "File Path",
                    "Data Type",
                    "Pattern",
                    "Risk Score",
                    "Confidence",
                    "Detected At",
                ]
            )

            for finding in findings:
                writer.writerow(
                    [
                        finding.file_path,
                        finding.data_type,
                        finding.pattern_id,
                        finding.risk_score,
                        finding.confidence.value if hasattr(finding.confidence, "value") else str(finding.confidence),
                        finding.discovered_at.isoformat(),
                    ]
                )

        return output_path

    def to_txt(self, findings: List, scan_session, filename: str = "findings.txt") -> Path:
        """Export to TXT format.

        Args:
            findings: List of findings
            scan_session: Associated scan session
            filename: Output filename

        Returns:
            Path to exported file
        """
        output_path = self.output_dir / filename

        with open(output_path, "w") as f:
            f.write("=" * 70 + "\n")
            f.write("DATA-SHIELD SCAN REPORT\n")
            f.write("=" * 70 + "\n\n")

            f.write(f"Session ID: {scan_session.id}\n")
            f.write(f"Target: {scan_session.target_path}\n")
            f.write(f"Mode: {scan_session.mode}\n")
            f.write(f"Start Time: {scan_session.start_time}\n")
            f.write(f"End Time: {scan_session.end_time}\n")
            f.write(f"Total Findings: {len(findings)}\n\n")

            f.write("-" * 70 + "\n")
            f.write("FINDINGS\n")
            f.write("-" * 70 + "\n\n")

            for i, finding in enumerate(findings, 1):
                f.write(f"{i}. {finding.file_path}\n")
                f.write(f"   Type: {finding.data_type}\n")
                f.write(f"   Pattern: {finding.pattern_id}\n")
                f.write(f"   Risk: {finding.risk_score}/100\n")
                f.write(f"   Detected: {finding.discovered_at}\n\n")

        return output_path

    def to_html(self, findings: List, scan_session, filename: str = "findings.html") -> Path:
        """Export to HTML format.

        Args:
            findings: List of findings
            scan_session: Associated scan session
            filename: Output filename

        Returns:
            Path to exported file
        """
        output_path = self.output_dir / filename

        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Data-Shield Scan Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        .high {{ color: red; font-weight: bold; }}
        .medium {{ color: orange; }}
        .low {{ color: green; }}
    </style>
</head>
<body>
    <h1>Data-Shield Scan Report</h1>
    <p><strong>Session ID:</strong> {scan_session.id}</p>
    <p><strong>Target:</strong> {scan_session.target_path}</p>
    <p><strong>Mode:</strong> {scan_session.mode}</p>
    <p><strong>Start Time:</strong> {scan_session.start_time}</p>
    <p><strong>End Time:</strong> {scan_session.end_time}</p>
    <p><strong>Total Findings:</strong> {len(findings)}</p>

    <h2>Findings</h2>
    <table>
        <tr>
            <th>File Path</th>
            <th>Data Type</th>
            <th>Pattern</th>
            <th>Risk Score</th>
            <th>Confidence</th>
            <th>Detected At</th>
        </tr>
"""

        for finding in findings:
            risk_class = "high" if finding.risk_score >= 70 else "medium" if finding.risk_score >= 40 else "low"
            html_content += f"""
        <tr>
            <td>{finding.file_path}</td>
            <td>{finding.data_type}</td>
            <td>{finding.pattern_id}</td>
            <td class="{risk_class}">{finding.risk_score}</td>
            <td>{finding.confidence.value if hasattr(finding.confidence, "value") else str(finding.confidence)}</td>
            <td>{finding.discovered_at.isoformat()}</td>
        </tr>
"""

        html_content += """
    </table>
</body>
</html>
"""

        with open(output_path, "w") as f:
            f.write(html_content)

        return output_path
