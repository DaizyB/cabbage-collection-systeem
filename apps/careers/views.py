from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import CollectorApplication
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.utils import timezone


@login_required
def application_status(request):
    # Show the latest application for this user (by user link or email)
    qs = CollectorApplication.objects.filter(user=request.user)
    if not qs.exists():
        # fallback: try by email match
        qs = CollectorApplication.objects.filter(email__iexact=request.user.email)
    app = qs.order_by('-applied_at').first()
    if not app:
        return redirect('careers:apply-collector')
    # Map status to message / CTA
    status = app.status
    messages = {
        app.APPLICATION_SUBMITTED: ("Your application has been submitted successfully.", "View details"),
        app.APPLICATION_UNDER_REVIEW: ("Your application is currently under review. Please check back later.", None),
        app.KYC_UNDER_VERIFICATION: ("Your KYC documents are being verified.", None),
        app.KYC_VERIFICATION_FAILED: ("KYC verification failed. Please contact our administrator.", "Contact admin"),
        app.APPLICATION_APPROVED: ("Your application has passed review. You can now access the Collector Dashboard.", "Go to dashboard"),
        app.APPLICATION_REJECTED: ("Your application was rejected. Please contact admin for details.", "Contact admin"),
    }
    message, cta = messages.get(status, ("Status: " + status, None))
    context = {'application': app, 'status_message': message, 'cta': cta}
    return render(request, 'careers/application_status.html', context)


def apply_collector(request):
    """Handle collector applications.

    - If the request looks like an API/ajax call, return JSON.
    - Otherwise, after successful POST redirect to a human-friendly success page.
    """
    if request.method == 'POST':
        # Basic required fields
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        national_id = request.POST.get('national_id')

        # Driving / vehicle
        driving_license_number = request.POST.get('driving_license_number')
        license_class = request.POST.get('license_class')
        license_expiry = request.POST.get('license_expiry') or None
        # Normalize date format if present
        if license_expiry:
            license_expiry = license_expiry.replace('/', '-')
        vehicle_number_plate = request.POST.get('vehicle_number_plate')
        vehicle_type = request.POST.get('vehicle_type') or 'truck'
        ownership = request.POST.get('ownership') or 'personal'

        # Files
        resume = request.FILES.get('resume')
        id_photo = request.FILES.get('id_photo')
        license_photo = request.FILES.get('license_photo')
        plate_photo = request.FILES.get('plate_photo')
        selfie_photo = request.FILES.get('selfie_photo')

        # Quiz answers
        answers = {}
        for q in ('q1', 'q2', 'q3', 'q4', 'q5'):
            answers[q] = request.POST.get(q)

        # Declaration
        declaration = request.POST.get('declaration')

        # Basic validation
        errors = []
        if not full_name or not email or not phone or not national_id:
            errors.append('Full name, phone, email and national ID are required.')
        if not declaration:
            errors.append('You must agree to the declaration before submitting.')
        # require at least one of the recommended uploads
        if not (id_photo or license_photo or plate_photo or resume):
            errors.append('At least one required upload (ID or license or plate or resume) is required.')

        # Conditional validation rules
        # If ownership is company, require driving license info + license photo
        if ownership == 'company':
            if not driving_license_number or not license_class or not license_expiry or not license_photo:
                errors.append('For company-owned trucks, driving license number, class, expiry and license photo are required.')

        # Vehicle-type specific: trucks/compactors require license; pickups require plate
        if vehicle_type in ('truck', 'compactor'):
            if not driving_license_number or not license_photo:
                errors.append('Trucks and compactors require driving license number and license photo.')
        elif vehicle_type == 'pickup':
            if not vehicle_number_plate or not plate_photo:
                errors.append('Pickup vehicles require number plate and plate photo.')

        if errors:
            return render(request, 'careers/apply.html', {'errors': errors, 'data': request.POST})

        a = CollectorApplication.objects.create(
            full_name=full_name,
            phone=phone,
            email=email,
            national_id=national_id,
            driving_license_number=driving_license_number or '',
            license_class=license_class or '',
            license_expiry=license_expiry or None,
            vehicle_number_plate=vehicle_number_plate or '',
            vehicle_type=vehicle_type,
            resume=resume,
            id_photo=id_photo,
            license_photo=license_photo,
            plate_photo=plate_photo,
            selfie_photo=selfie_photo,
            answers=answers,
        )
        # Link application to authenticated user when available
        if request.user.is_authenticated:
            a.user = request.user
            a.save()

        # Evaluate test and set status
        try:
            a.evaluate_test()
        except Exception:
            # evaluation shouldn't block submission; mark for manual review
            a.status = CollectorApplication.APPLICATION_UNDER_REVIEW
            a.status_changed_at = timezone.now()
            a.save()
        # ensure initial status/timestamp when submitted
        if not a.status_changed_at:
            a.status_changed_at = a.applied_at
            a.save()
        # If JSON or AJAX, return JSON for API consumers
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'
        if is_ajax:
            return JsonResponse({'ok': True, 'id': a.id})
        # For standard browser form posts, redirect to a success page
        return redirect('careers:apply-success')
    return render(request, 'careers/apply.html')


def apply_success(request):
    return render(request, 'careers/success.html')
