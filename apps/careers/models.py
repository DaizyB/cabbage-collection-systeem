from django.db import models
from django.utils import timezone
from django.conf import settings


class CollectorApplication(models.Model):
    APPLICATION_SUBMITTED = 'APPLICATION_SUBMITTED'
    APPLICATION_UNDER_REVIEW = 'APPLICATION_UNDER_REVIEW'
    APPLICATION_APPROVED = 'APPLICATION_APPROVED'
    KYC_UNDER_VERIFICATION = 'KYC_UNDER_VERIFICATION'
    KYC_VERIFICATION_FAILED = 'KYC_VERIFICATION_FAILED'
    APPLICATION_REJECTED = 'APPLICATION_REJECTED'
    STATUS_REJECTED = APPLICATION_REJECTED  # For admin compatibility

    STATUS_CHOICES = [
        (APPLICATION_SUBMITTED, 'Submitted'),
        (APPLICATION_UNDER_REVIEW, 'Under review'),
        (KYC_UNDER_VERIFICATION, 'KYC under verification'),
        (KYC_VERIFICATION_FAILED, 'KYC verification failed'),
        (APPLICATION_APPROVED, 'Approved collector'),
        (APPLICATION_REJECTED, 'Rejected'),
    ]

    # Personal identity
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32)
    email = models.EmailField()
    national_id = models.CharField(max_length=128)

    # Driving & vehicle eligibility
    driving_license_number = models.CharField(max_length=128, blank=True)
    license_class = models.CharField(max_length=64, blank=True)
    license_expiry = models.DateField(null=True, blank=True)
    vehicle_number_plate = models.CharField(max_length=64, blank=True)
    VEHICLE_CHOICES = [('truck', 'Truck'), ('pickup', 'Pickup'), ('compactor', 'Compactor'), ('other', 'Other')]
    vehicle_type = models.CharField(max_length=32, choices=VEHICLE_CHOICES, default='truck')
    # Ownership: company-owned truck vs personal/third-party
    OWNERSHIP_CHOICES = [('company', 'Company-owned'), ('personal', 'Personal / third-party')]
    ownership = models.CharField(max_length=16, choices=OWNERSHIP_CHOICES, default='personal')

    # Uploads
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    id_photo = models.ImageField(upload_to='kyc/', null=True, blank=True)
    license_photo = models.ImageField(upload_to='kyc/', null=True, blank=True)
    plate_photo = models.ImageField(upload_to='kyc/', null=True, blank=True)
    selfie_photo = models.ImageField(upload_to='kyc/', null=True, blank=True)

    # Test results and status
    answers = models.JSONField(default=dict, blank=True)
    test_score = models.IntegerField(null=True, blank=True)
    test_passed = models.BooleanField(default=False)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default=APPLICATION_SUBMITTED)

    applied_at = models.DateTimeField(default=timezone.now)
    reviewed = models.BooleanField(default=False)
    status_changed_at = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Application {self.full_name} ({self.email})"

    def evaluate_test(self):
        """Grade the short qualification test supplied in `answers`.

        Rules derived from the conversation:
        - Q1 (has driving license) must be Yes else auto-fail.
        - Score is percentage of correct MCQs/situational (excluding Q1 auto-fail check).
        - Pass mark is 70%.
        """
        # expected answers
        correct = {
            'q2': 'B',
            'q3': 'C',
            'q4': 'B',
            'q5': 'B',
        }
        # Q1 special
        q1 = str(self.answers.get('q1', '')).strip().lower()
        if q1 not in ('yes', 'y', 'true', '1'):
            self.test_score = 0
            self.test_passed = False
            self.status = self.STATUS_FAILED_TEST
            self.save()
            return

        total = len(correct)
        got = 0
        for k, v in correct.items():
            if str(self.answers.get(k, '')).strip().upper() == v:
                got += 1
        score = int((got / total) * 100) if total else 0
        self.test_score = score
        self.test_passed = score >= 70
        self.status = self.STATUS_KYC_REVIEW if self.test_passed else self.STATUS_FAILED_TEST
        self.save()
