from django.urls import path
from .views import TimeReportUpload, PayrollReportGenerate

urlpatterns = [
    path('upload-csv/', TimeReportUpload.as_view(), name='report_upload'),
    path('payroll-reports/', PayrollReportGenerate.as_view(), name='payroll-report-generate')
]
