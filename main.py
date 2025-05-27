import argparse
from typing import List, Dict

class EmployeeDataError(Exception):
    pass

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="+")
    parser.add_argument("--report", required=True, choices=["payout"])
    return parser.parse_args()

def read_csv_data(file_path: str) -> List[Dict[str, str]]:
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise EmployeeDataError("File not found")
    if not lines:
        raise EmployeeDataError("File is empty")

    header = [h.strip() for h in lines[0].strip().split(',')]
    data = []
    if not header:
        raise EmployeeDataError(f"Could not parse header")
    for line in lines[1:]:
        row = [value.strip() for value in line.strip().split(',')]
        if len(row) != len(header):
            raise EmployeeDataError(f"Incorrect number of columns in row: {line.strip()}")
        item = {}
        for i, value in enumerate(row):
            item[header[i]] = value
        data.append(item)
    return data

def calculate_payout(employees: List[Dict[str, str]], rate_column_names: List[str]) -> Dict[str, float]:
    payouts = {}
    for employee in employees:
        name = employee['name']
        if not name:
            print(f"Warning: name column not found for employee.")
            continue

        hours_worked = float(employee['hours_worked'])
        if not hours_worked:
            print(f"Warning: hours_worked column not found for employee {name}.")
            continue

        hourly_rate = None
        for item in rate_column_names:
            if item in employee:
                hourly_rate = float(employee[item])
        if not hourly_rate:
            print(f"Warning: rate column not found for employee {name}.")
            continue

        payout = hourly_rate * hours_worked
        payouts[name] = payout

    return payouts

def print_payout_report(payouts: Dict[str, float], employees: List[Dict[str, str]]):
    department_payouts: Dict[str, List[str]] = {}
    individual_payouts: List[str] = []

    for employee in employees:
        name = employee.get('name')
        department = employee.get('department')
        data = f"- {name}: ${payouts.get(name, 0.0):.2f}\n"
        if not department:
            individual_payouts.append(data)
            continue
        if department not in department_payouts:
            department_payouts[department] = []
        department_payouts[department].append(data)

    report = "Payout Report:\n"
    for key, value in department_payouts.items():
        report += f"\nDepartment: {key}\n"
        for item in value:
            report += item
    for item in individual_payouts:
        report += item
    print(report)

def generate_report(report_type: str, employee_data: List[Dict[str, str]]):
    if report_type == "payout":
        rate_names = ["hourly_rate", "rate", "salary"]
        payouts = calculate_payout(employee_data, rate_names)
        print_payout_report(payouts, employee_data)
    else:
        raise ValueError(f"Unsupported report type: {report_type}")

def main():
    args = parse_arguments()
    employees_data = []
    for file_path in args.files:
        try:
            data = read_csv_data(file_path)
            employees_data.extend(data)
        except EmployeeDataError as e:
            print(f"Error processing file {file_path}: {e}")
            return
    try:
        generate_report(args.report, employees_data)
    except ValueError as e:
        print(f"Error generating report: {e}")


if __name__ == '__main__':
    main()
