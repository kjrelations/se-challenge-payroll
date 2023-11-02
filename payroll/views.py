from rest_framework import generics
from .models import TimeReport
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response
from datetime import datetime, timedelta
import csv
import io

class TimeReportUpload(generics.ListCreateAPIView):

    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('csv_file')
        
        if not csv_file:
            return Response({'error': 'No CSV file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not csv_file.name.endswith('.csv'):
            return Response({'error': 'Invalid file type. Please upload a CSV file.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Can check valid CSV content with MIME type

        file_name = csv_file.name
        try:
            # Expected format: time-report-x.csv
            time_report_id = int(file_name.split('-')[2].split('.')[0])
        except (IndexError, ValueError):
            return Response({'error': 'Invalid file name format'}, status=status.HTTP_400_BAD_REQUEST)

        if TimeReport.objects.filter(report_id=time_report_id).exists():
            return Response({'error': 'ID already exists in the database'}, status=status.HTTP_400_BAD_REQUEST)

        csv_data = self.parse_csv(csv_file)
        time_reports_list = []
        for row in csv_data:
            # try, except if invalid cases missed
            try:
                time_report = TimeReport(
                    report_id = time_report_id,
                    date=row['date'],
                    hours_worked=row['hours_worked'],
                    employee_id=row['employee_id'],
                    job_group=row['job_group']
                )
                time_reports_list.append(time_report)
            except:
                return Response({'error': 'Invalid values'}, status=status.HTTP_400_BAD_REQUEST)
        TimeReport.objects.bulk_create(time_reports_list)

        return Response({'success': 'CSV file uploaded and processed'}, status=status.HTTP_201_CREATED)

    def parse_csv(self, file):
        csv_data = []
        text_data = file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(text_data))
        for row in csv_reader:
            # Could add data validation here for each field e.g.
            """
            try:
                date = datetime.strptime(row['date'], '%d/%m/%Y')
            except ValueError:
                raise and return a response error
            But a larger try except block surrounding all validation or have it be it's own function
            """
            csv_data.append({
                'date': datetime.strptime(row['date'], '%d/%m/%Y'),
                'hours_worked': float(row['hours worked']),
                'employee_id': row['employee id'],
                'job_group': row['job group'],
            })
            
        return csv_data
        
class PayrollReportGenerate(generics.ListCreateAPIView):
    
    def get(self, request):
        time_reports = TimeReport.objects.all()
        payroll_report = {
            "payrollReport": {
                "employeeReports": []
            }
        }

        employee_payroll = {}

        for time_report in time_reports:
            employee_id = time_report.employee_id
            job_group = time_report.job_group
            date = time_report.date

            if date.day <= 15:
                start_date = date.replace(day=1)
                end_date = date.replace(day=15)
            else:
                start_date = date.replace(day=16)
                next_month = date.replace(day=1) + timedelta(days=32)
                end_date = next_month.replace(day=1) - timedelta(days=1)

            if job_group == 'A':
                hourly_rate = 20
            else:
                hourly_rate = 30

            hours_worked = time_report.hours_worked
            amount_paid = hours_worked * hourly_rate

            period_key = (employee_id, start_date, end_date)
            if period_key in employee_payroll:
                employee_payroll[period_key] += amount_paid
            else:
                employee_payroll[period_key] = amount_paid

        for (employee_id, start_date, end_date), amount_paid in employee_payroll.items():
            report_entry = {
                "employeeId": employee_id,
                "payPeriod": {
                    "startDate": start_date.strftime("%Y-%m-%d"),
                    "endDate": end_date.strftime("%Y-%m-%d"),
                },
                "amountPaid": f"${amount_paid:.2f}",
            }

            payroll_report["payrollReport"]["employeeReports"].append(report_entry)

        sorted_employee_reports = sorted(
            payroll_report["payrollReport"]["employeeReports"],
            key=lambda x: (x["employeeId"], x["payPeriod"]["startDate"])
        )

        payroll_report = {
            "payrollReport": {
                "employeeReports": sorted_employee_reports
            }
        }

        return JsonResponse(payroll_report, json_dumps_params={'indent': 2})
