from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import ProtectedError
from library import Read_Excel

from .models import Resource
from .forms import ResourceForm


# Create your views here.

def home(request):
    return HttpResponse("Hello world!")


# 1. Display all resources
def resource_list(request):
    resources = Resource.objects.all().order_by('-id')

    return render(request, 'resources/list.html', {'resources': resources})


# 2. Create a resource
def resource_create(request):

    if request.method == 'POST':
        form = ResourceForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Resource created successfully.')
            return redirect('resource_list')

    else:
        form = ResourceForm()

    return render(request, 'resources/form.html', {
        'form': form,
        'page_title': 'Create Resource'
    })


# 3. Display one resource
def resource_detail(request, pk):
    resource = get_object_or_404(Resource, pk=pk)

    return render(request, 'resources/detail.html', {
        'resource': resource
    })


# 4. Update a resource
def resource_update(request, pk):
    resource = get_object_or_404(Resource, pk=pk)

    if request.method == 'POST':
        form = ResourceForm(request.POST, instance=resource)

        if form.is_valid():
            form.save()
            messages.success(request, 'Resource updated successfully.')
            return redirect('resource_list')

    else:
        form = ResourceForm(instance=resource)

    return render(request, 'resources/form.html', {
        'form': form,
        'page_title': 'Update Resource'
    })



def excel_upload(request):
    print("Excel upload function called")
    if request.method != 'POST':
        return redirect('resource_list')

    print("Request method is POST") 
    # 1. Get uploaded Excel file
    excel_file = request.FILES.get('excel_file')

    print("Excel file received:", excel_file.name)

    if not excel_file:
        messages.error(request, 'Please select an Excel file.')
        return redirect('resource_list')

    print("Excel file received:", excel_file.name)

    # 2. Check file extension
    if not excel_file.name.lower().endswith('.xlsx'):
        messages.error(request, 'Only .xlsx files are supported.')
        return redirect('resource_list')

    print("Excel file received:", excel_file.name)
    Read_Excel.read_excel_file(excel_file)

    return redirect('resource_list')





def order_list(request):
    from .models import Order

    orders = Order.objects.select_related('resource').all().order_by('-id')

    return render(request, 'resources/orderform.html', {'orders': orders})



# def upload_orders(request):

    if request.method != 'POST':
        return redirect('resource_list')

    # 1. Get uploaded Excel file
    excel_file = request.FILES.get('excel_file')

    if not excel_file:
        messages.error(request, 'Please select an Excel file.')
        return redirect('resource_list')

    # 2. Get selected Resource
    resource_id = request.POST.get('resource')

    resource = get_object_or_404(
        Resource,
        id=resource_id,
        is_active=True
    )

    # 3. Check file extension
    if not excel_file.name.lower().endswith('.xlsx'):
        messages.error(request, 'Only .xlsx files are supported.')
        return redirect('resource_list')

    try:
        # 4. Open Excel workbook
        workbook = load_workbook(
            excel_file,
            read_only=True,
            data_only=True
        )

        worksheet = workbook.active

        # 5. Extract column headers
        headers = [
            str(cell).strip().lower()
            if cell is not None else ''
            for cell in next(
                worksheet.iter_rows(
                    min_row=1,
                    max_row=1,
                    values_only=True
                )
            )
        ]

        required_columns = [
            'customer code',
            'side',
            'quantity',
            'price'
        ]

        # 6. Validate required columns
        if not all(col in headers for col in required_columns):
            raise ValueError('Required Excel columns are missing.')

        column_index = {
            name: headers.index(name)
            for name in required_columns
        }

        total_orders = 0

        # 7. Process Excel rows one by one
        with transaction.atomic():

            for row_number, row in enumerate(
                worksheet.iter_rows(
                    min_row=2,
                    values_only=True
                ),
                start=2
            ):

                # Skip completely empty rows
                if all(value is None for value in row):
                    continue

                customer_code = row[column_index['customer code']]
                side = row[column_index['side']]
                quantity = row[column_index['quantity']]
                price = row[column_index['price']]

                # 8. Validate individual row
                if not customer_code or not side:
                    raise ValueError(
                        f'Invalid customer or side at row {row_number}.'
                    )

                side = str(side).strip().upper()

                if side not in ['BUY', 'SELL']:
                    raise ValueError(
                        f'Invalid side at row {row_number}.'
                    )

                quantity = int(quantity)
                price = Decimal(str(price))

                if quantity <= 0 or price <= 0:
                    raise ValueError(
                        f'Invalid quantity or price at row {row_number}.'
                    )

                # 9. Create Order in database
                Order.objects.create(
                    customer_code=str(customer_code).strip(),
                    resource=resource,
                    side=side,
                    quantity=quantity,
                    remaining_quantity=quantity,
                    price=price
                )

                total_orders += 1

        workbook.close()

        messages.success(
            request,
            f'{total_orders} orders uploaded successfully.'
        )

    except (ValueError, TypeError, InvalidOperation) as error:
        messages.error(request, str(error))

    except Exception as error:
        messages.error(request, f'Excel processing failed: {error}')

    return redirect('resource_list')
