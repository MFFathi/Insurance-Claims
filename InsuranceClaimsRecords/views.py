from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Record
from django.http import HttpResponse
import csv

def sorted_records(request):
    sort_by = request.GET.get('sort', 'accident_date')
    records_list = Record.objects.all().order_by(sort_by)

    paginator = Paginator(records_list, 10)  # 10 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Pass field names for table headers
    fields = [field.name for field in Record._meta.fields]

    return render(request, 'records.html', {
        'records': page_obj,
        'fields': fields,
        'sort_by': sort_by
    })

def export_records_csv(request):
    records = Record.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Patient_records.csv"'

    writer = csv.writer(response)
    fields = [field.name for field in Record._meta.fields]
    writer.writerow(fields)

    for record in records:
        writer.writerow([getattr(record, field) for field in fields])

    return response
