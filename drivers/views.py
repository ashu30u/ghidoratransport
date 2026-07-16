from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from .models import Driver, Vehicle, get_assigned_driver
from .forms import DriverForm, VehicleForm


# ---------------------------------------------------------------------
# ADMIN SIDE — Driver Management Dashboard
# ---------------------------------------------------------------------

@staff_member_required
def driver_list(request):
    drivers = Driver.objects.all()
    return render(request, 'drivers/driver_list.html', {'drivers': drivers})


@staff_member_required
def driver_add(request):
    if request.method == 'POST':
        driver_form = DriverForm(request.POST, request.FILES)
        vehicle_form = VehicleForm(request.POST, request.FILES)
        if driver_form.is_valid() and vehicle_form.is_valid():
            driver = driver_form.save()
            vehicle = vehicle_form.save(commit=False)
            vehicle.driver = driver
            vehicle.save()
            messages.success(request, f"Driver '{driver.name}' add ho gaya.")
            return redirect('drivers:driver_list')
    else:
        driver_form = DriverForm()
        vehicle_form = VehicleForm()

    return render(request, 'drivers/driver_form.html', {
        'driver_form': driver_form, 'vehicle_form': vehicle_form, 'mode': 'add'
    })


@staff_member_required
def driver_edit(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    vehicle = getattr(driver, 'vehicle_detail', None)

    if request.method == 'POST':
        driver_form = DriverForm(request.POST, request.FILES, instance=driver)
        vehicle_form = VehicleForm(request.POST, request.FILES, instance=vehicle)
        if driver_form.is_valid() and vehicle_form.is_valid():
            driver = driver_form.save()
            v = vehicle_form.save(commit=False)
            v.driver = driver
            v.save()
            messages.success(request, f"Driver '{driver.name}' update ho gaya.")
            return redirect('drivers:driver_list')
    else:
        driver_form = DriverForm(instance=driver)
        vehicle_form = VehicleForm(instance=vehicle)

    return render(request, 'drivers/driver_form.html', {
        'driver_form': driver_form, 'vehicle_form': vehicle_form, 'mode': 'edit', 'driver': driver
    })


@staff_member_required
def driver_detail(request, pk):
    driver = get_object_or_404(Driver, pk=pk)
    return render(request, 'drivers/driver_detail.html', {'driver': driver})


@staff_member_required
def make_default_driver(request, pk):
    """Admin manually kisi bhi driver ko default (permanent auto-assign) bana sakta hai."""
    driver = get_object_or_404(Driver, pk=pk)
    driver.is_default = True
    driver.save()
    messages.success(request, f"{driver.name} ab default driver hai — naye bookings usi ko assign honge.")
    return redirect('drivers:driver_list')


# ---------------------------------------------------------------------
# BOOKING ASSIGNMENT — integrate this with your Booking model
# ---------------------------------------------------------------------

def auto_assign_driver_to_booking(booking):
    """
    Apne Booking model ke save()/create ke baad isko call karein:

        from drivers.views import auto_assign_driver_to_booking
        auto_assign_driver_to_booking(booking)

    Ye function booking.assigned_driver field set karega (aapko Booking
    model me ForeignKey('drivers.Driver', null=True, blank=True) add karna hoga).
    Agar sirf ek hi driver hai, wahi hamesha assign hoga (permanent),
    jab tak admin khud change na kare.
    """
    if getattr(booking, 'assigned_driver_id', None):
        return booking.assigned_driver  # already assigned — admin ka manual choice preserve karo

    driver = get_assigned_driver()
    if driver:
        booking.assigned_driver = driver
        booking.save(update_fields=['assigned_driver'])
    return driver


# ---------------------------------------------------------------------
# CUSTOMER SIDE — driver card on booking status page
# ---------------------------------------------------------------------

def customer_driver_card(request, booking):
    """
    Apne booking-status view se is context ko template me pass karein,
    ya seedha {% include 'drivers/customer_driver_card.html' %} use karein
    with 'driver' context variable = booking.assigned_driver
    """
    return render(request, 'drivers/customer_driver_card.html', {'driver': booking.assigned_driver})
