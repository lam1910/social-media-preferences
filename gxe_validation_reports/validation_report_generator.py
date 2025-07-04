from jinja2 import Template
from pathlib import Path
import os
import json


corporate_email_template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Data Quality Report</title>
  <style>
    @media print {
      #print-button {
        display: none;
      }
    }

    body {
      font-family: 'Segoe UI', sans-serif;
      background: #ffffff;
      color: #333;
      max-width: 21cm;
      margin: auto;
      padding: 2cm;
    }

    h1 {
      text-align: center;
      color: #2c3e50;
      font-size: 2.2em;
      margin-bottom: 20px;
    }

    #print-button {
      background-color: #007BFF;
      color: white;
      border: none;
      padding: 10px 20px;
      font-size: 1em;
      border-radius: 4px;
      cursor: pointer;
      display: block;
      margin: 0 auto 30px auto;
    }

    #print-button:hover {
      background-color: #0056b3;
    }

    .summary {
      background: #f9f9f9;
      border: 1px solid #ccc;
      padding: 20px;
      margin-bottom: 30px;
    }

    .summary p {
      margin: 8px 0;
      font-size: 1em;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95em;
      background: #fff;
      margin-top: 20px;
    }

    th, td {
      padding: 12px;
      border: 1px solid #ddd;
      text-align: left;
    }

    th {
      background-color: #f1f1f1;
    }

    tr:nth-child(even) {
      background-color: #f9f9f9;
    }

    .fail {
      color: #c0392b;
      font-weight: bold;
    }

    pre {
      margin: 0;
      white-space: pre-wrap;
      font-family: Consolas, monospace;
      color: #555;
    }

    footer {
      text-align: center;
      margin-top: 50px;
      font-size: 0.8em;
      color: #777;
    }
  </style>
</head>
<body>
  <button id="print-button" onclick="window.print()">🖨️ Print Report</button>

  <h1>Data Quality Validation Report</h1>

  <div class="summary">
    <p><strong>Overall Success:</strong>
       <span style="color: {{ 'green' if success else '#c0392b' }}">{{ success }}</span>
    </p>
    <p><strong>Evaluated Expectations:</strong> {{ evaluated }}</p>
    <p><strong>Successful:</strong> {{ successful }}</p>
    <p><strong>Unsuccessful:</strong> {{ unsuccessful }}</p>
    <p><strong>Success Rate:</strong> {{ percent }}%</p>
  </div>

  <table>
    <thead>
      <tr>
        <th>Expectation Type</th>
        <th>Column</th>
        <th>Details</th>
      </tr>
    </thead>
    <tbody>
      {% for row in failed_expectations %}
      <tr>
        <td class="fail">{{ row['Expectation Type'] }}</td>
        <td>{{ row['Column'] }}</td>
        <td><pre>{{ row['Details'] }}</pre></td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  <footer>
    &copy; 2025 Internal Reporting · Data Quality Monitoring Unit
  </footer>
</body>
</html>
"""


def extract_failed_expectations(gxe_output: dict) -> list[dict]:
    failed = []
    for exp in gxe_output.get('expectations', []):
        if not exp.get('success', False):
            failed.append({
                'Expectation Type': exp.get('expectation_type', 'N/A'),
                'Column': exp.get('kwargs', {}).get('column', 'N/A'),
                'Details': json.dumps(exp.get('result', {}), indent=2)
            })
    return failed


def render_corporate_report(gxe_output: dict, output_path: Path) -> None:
    os.makedirs(output_path.parent, exist_ok=True)

    failed = extract_failed_expectations(gxe_output)
    stats = gxe_output.get('statistics', {})
    html = Template(corporate_email_template_str).render(
        success=gxe_output.get('success', False),
        evaluated=stats.get('evaluated_expectations', 0),
        successful=stats.get('successful_expectations', 0),
        unsuccessful=stats.get('unsuccessful_expectations', 0),
        percent=stats.get('success_percent', 0.0),
        failed_expectations=failed
    )

    output_path.write_text(html, encoding='utf-8')


def build_validation_report(gxe_output: dict, file_name: str) -> None:
    report_dir = Path('/opt/airflow/dags/modules/gxe_validation_reports/reports')
    report_file = report_dir / f'{file_name}.html'
    render_corporate_report(gxe_output, report_file)
    return report_file