import sys
import io
import pytest
from main import read_csv_data, calculate_payout, generate_report, EmployeeDataError, parse_arguments, main

@pytest.fixture
def valid_csv_data():
    return "name,salary,hours_worked,department\nJohn,50,40,Sales\nJane,60,30,Marketing"

@pytest.fixture
def invalid_csv_data():
    return "name,salary\nJohn,50,40"

@pytest.fixture
def valid_data():
    return [
        {'name': 'John', 'salary': '50', 'hours_worked': '40', 'department': 'Sales'},
        {'name': 'Jane', 'rate': '60', 'hours_worked': '30', 'department': 'Marketing'}]

@pytest.fixture
def create_temp_file(tmpdir):
    def _create_file(content, filename="test.csv"):
        file_path = tmpdir.join(filename)
        file_path.write(content)
        return str(file_path)
    return _create_file

def test_read_csv_data_valid(create_temp_file, valid_csv_data):
    file_path = create_temp_file(valid_csv_data)
    data = read_csv_data(file_path)
    assert len(data) == 2
    assert data[0]['name'] == 'John'
    assert data[0]['salary'] == '50'
    assert data[0]['hours_worked'] == '40'
    assert data[0]['department'] == 'Sales'

def test_read_csv_data_file_not_found():
    with pytest.raises(EmployeeDataError, match="File not found"):
        read_csv_data("nonexistent.csv")

def test_read_csv_data_invalid_format(create_temp_file, invalid_csv_data):
    file_path = create_temp_file(invalid_csv_data)
    with pytest.raises(EmployeeDataError, match="Incorrect number of columns"):
        read_csv_data(file_path)

def test_calculate_payout(valid_data):
    employees = valid_data
    payouts = calculate_payout(employees, ["hourly_rate", "rate", "salary"])
    assert payouts['John'] == 2000.0

def test_generate_report_unsupported_type():
    with pytest.raises(ValueError, match="Unsupported report type"):
        generate_report("unsupported", [])

def test_main_with_valid_files(create_temp_file, valid_csv_data):
    file_path1 = create_temp_file(valid_csv_data, "test_valid1.csv")

    captured_output = io.StringIO()
    sys.stdout = captured_output
    try:
        sys.argv = ["script.py", file_path1, "--report", "payout"]
        main()
    finally:
        sys.stdout = sys.__stdout__

    output = captured_output.getvalue()
    assert "Payout Report:" in output
    assert "Department: Sales" in output
    assert "- John: $2000.00" in output
    assert "Department: Marketing" in output
    assert "- Jane: $1800.00" in output


def test_main_with_missing_file():
    captured_output = io.StringIO()
    sys.stdout = captured_output

    try:
        sys.argv = ["script.py", "nonexistent.csv", "--report", "payout"]
        main()
    finally:
        sys.stdout = sys.__stdout__

    output = captured_output.getvalue()
    assert "Error processing file nonexistent.csv: File not found" in output
