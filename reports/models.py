import uuid
import secrets
from django.db import models


def generate_dept_token():
    return secrets.token_urlsafe(32)


def generate_citizen_token():
    return secrets.token_urlsafe(32)


class Department(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'

    def __str__(self):
        return self.name


class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='categories'
    )
    icon = models.CharField(max_length=100, blank=True, help_text='Icon class or name')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Report(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Gözləmədə'),
        ('accepted', 'Qəbul edilib'),
        ('in_progress', 'İcrada'),
        ('resolved', 'Həll edilib'),
        ('rejected', 'Rədd edilib'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Aşağı'),
        ('medium', 'Orta'),
        ('high', 'Yüksək'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports'
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports'
    )
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    photo = models.ImageField(upload_to='reports/%Y/%m/%d/')
    latitude = models.DecimalField(max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, null=True, blank=True)
    address = models.CharField(max_length=500)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    citizen_email = models.EmailField(blank=True)
    dept_token = models.CharField(
        max_length=64,
        default=generate_dept_token,
        unique=True,
        db_index=True
    )
    citizen_token = models.CharField(
        max_length=64,
        default=generate_citizen_token,
        unique=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reports'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        ordering = ['-created_at']

    def __str__(self):
        return f"Report {self.id} - {self.status}"


class StatusHistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='status_history'
    )
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.CharField(max_length=255, blank=True, help_text='User or system that changed the status')
    comment = models.TextField(blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'status_history'
        verbose_name = 'Status History'
        verbose_name_plural = 'Status History'
        ordering = ['-changed_at']

    def __str__(self):
        return f"{self.old_status} -> {self.new_status} ({self.report.id})"


class AIClassification(models.Model):
    id = models.BigAutoField(primary_key=True)
    report = models.OneToOneField(
        Report,
        on_delete=models.CASCADE,
        related_name='ai_classification'
    )
    category_predicted = models.CharField(max_length=255)
    confidence = models.FloatField()
    raw_response = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_classifications'
        verbose_name = 'AI Classification'
        verbose_name_plural = 'AI Classifications'

    def __str__(self):
        return f"AI Classification for {self.report.id}"
