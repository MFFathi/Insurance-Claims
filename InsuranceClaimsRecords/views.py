from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.contrib import messages
import csv
from .models import Record

def has_record_permission(user):
    return user.is_authenticated and (
        user.is_superuser or 
        user.check_permission('records.view.all')
    )

@login_required
def sorted_records(request):
    if not has_record_permission(request.user):
        messages.error(request, "You don't have permission to view records.")
        return redirect('accounts:login')
        
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

@login_required
def export_records_csv(request):
    if not has_record_permission(request.user):
        messages.error(request, "You don't have permission to export records.")
        return redirect('sorted_records')
        
    records = Record.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Patient_records.csv"'

    writer = csv.writer(response)
    fields = [field.name for field in Record._meta.fields]
    writer.writerow(fields)

    for record in records:
        writer.writerow([getattr(record, field) for field in fields])

    return response
