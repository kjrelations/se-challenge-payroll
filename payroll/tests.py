from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import TimeReport

# These tests can be made more comprehensive as desired
class CsvImportTest(TestCase):
    def test_import_csv(self):
        # Normal upload that checks it's in the database after
        csv_file_data = b'date,hours worked,employee id,job group\n01/11/2023,8.5,123,A'
        csv_file = SimpleUploadedFile("time-report-222.csv", csv_file_data)

        response = self.client.post('/upload-csv/', {'csv_file': csv_file})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(TimeReport.objects.filter(date="2023-11-01", hours_worked=8.5, employee_id="123", job_group="A").exists())
    
    def test_same_id_insert(self):
        # Reinsert with same id
        csv_file_data = b'date,hours worked,employee id,job group\n01/11/2023,8.5,123,A'
        csv_file = SimpleUploadedFile("time-report-222.csv", csv_file_data)
        
        response = self.client.post('/upload-csv/', {'csv_file': csv_file})
        response = self.client.post('/upload-csv/', {'csv_file': csv_file})
        self.assertEqual(response.status_code, 400)
        expected_error_message = "ID already exists in the database"
        self.assertEqual(response.data['error'], expected_error_message)

    def test_miscellaneous(self):
        # Place as many invalid cases as desired or in separate functions
        # Invalid extension
        csv_file_data = b'date,hours worked,employee id,job group\n01/11/2023,8.5,123,A'
        csv_file = SimpleUploadedFile("time-report-222.txt", csv_file_data)

        response = self.client.post('/upload-csv/', {'csv_file': csv_file})
        self.assertEqual(response.status_code, 400)
        expected_error_message = "Invalid file type. Please upload a CSV file."
        self.assertEqual(response.data['error'], expected_error_message)

class PayrollGenerationTest(TestCase):
    def test_single_employee_report(self):
        # Job Type A
        csv_file_data = b'date,hours worked,employee id,job group\n01/11/2023,1.0,123,A\n05/11/2023,1.0,123,A\n15/11/2023,3.0,123,A\n18/11/2023,9.0,123,A\n18/12/2023,8.0,123,A\n01/01/2024,10.0,123,A'
        csv_file = SimpleUploadedFile("time-report-222.csv", csv_file_data)

        response = self.client.post('/upload-csv/', {'csv_file': csv_file})
        response = self.client.get('/payroll-reports/')

        self.assertEqual(response.status_code, 200)

        payroll_report = response.json()

        employee_reports = payroll_report["payrollReport"]["employeeReports"]
        # Right number of periods
        self.assertEqual(len(employee_reports), 4)
        # Correct payments
        self.assertEqual(employee_reports[0]["amountPaid"], "$100.00")
        self.assertEqual(employee_reports[1]["amountPaid"], "$180.00")
        self.assertEqual(employee_reports[2]["amountPaid"], "$160.00")
        self.assertEqual(employee_reports[3]["amountPaid"], "$200.00")
        # Correct period dates
        self.assertEqual(employee_reports[0]["payPeriod"]["startDate"], "2023-11-01")
        self.assertEqual(employee_reports[0]["payPeriod"]["endDate"], "2023-11-15")   
        self.assertEqual(employee_reports[1]["payPeriod"]["startDate"], "2023-11-16")
        self.assertEqual(employee_reports[1]["payPeriod"]["endDate"], "2023-11-30")
        self.assertEqual(employee_reports[2]["payPeriod"]["startDate"], "2023-12-16")
        self.assertEqual(employee_reports[2]["payPeriod"]["endDate"], "2023-12-31")
        self.assertEqual(employee_reports[3]["payPeriod"]["startDate"], "2024-01-01")
        self.assertEqual(employee_reports[3]["payPeriod"]["endDate"], "2024-01-15")

        TimeReport.objects.all().delete()

        # Job Type B
        csv_file_data = b'date,hours worked,employee id,job group\n01/11/2023,1.0,123,B\n05/11/2023,1.0,123,B\n15/11/2023,3.0,123,B\n18/11/2023,9.0,123,B\n18/12/2023,8.0,123,B\n01/01/2024,10.0,123,B'
        csv_file = SimpleUploadedFile("time-report-222.csv", csv_file_data)

        response = self.client.post('/upload-csv/', {'csv_file': csv_file})
        response = self.client.get('/payroll-reports/')

        self.assertEqual(response.status_code, 200)

        payroll_report = response.json()

        employee_reports = payroll_report["payrollReport"]["employeeReports"]

        # Only payments change
        self.assertEqual(employee_reports[0]["amountPaid"], "$150.00")
        self.assertEqual(employee_reports[1]["amountPaid"], "$270.00")
        self.assertEqual(employee_reports[2]["amountPaid"], "$240.00")
        self.assertEqual(employee_reports[3]["amountPaid"], "$300.00")

    # Can also test the sorting but I think that's clear enough. 
    # I would implement it in another test with a csv of unordered employees and dates then loop through the reports ensuring that the employee ids are >= the previous 
    # and the start date is => the previous.