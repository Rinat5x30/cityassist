from django.contrib import admin
from .models import Department, Category, Report, StatusHistory, AIClassification


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'email']
    ordering = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'department', 'icon']
    list_filter = ['department']
    search_fields = ['name', 'slug']
    ordering = ['name']


class StatusHistoryInline(admin.TabularInline):
    model = StatusHistory
    extra = 0
    readonly_fields = ['old_status', 'new_status', 'changed_by', 'comment', 'changed_at']
    can_delete = False


class AIClassificationInline(admin.StackedInline):
    model = AIClassification
    extra = 0
    readonly_fields = ['category_predicted', 'confidence', 'raw_response', 'created_at']
    can_delete = False


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'department', 'status', 'priority', 'address', 'created_at']
    list_filter = ['status', 'category', 'priority', 'department', 'created_at']
    search_fields = ['address', 'title', 'description', 'id']
    ordering = ['-created_at']
    readonly_fields = ['id', 'dept_token', 'citizen_token', 'created_at', 'updated_at']
    inlines = [StatusHistoryInline, AIClassificationInline]
    fieldsets = (
        ('Report Information', {
            'fields': ('id', 'title', 'description', 'photo', 'address')
        }),
        ('Classification', {
            'fields': ('category', 'department', 'priority', 'status')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Tokens', {
            'fields': ('dept_token', 'citizen_token'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['report', 'old_status', 'new_status', 'changed_by', 'changed_at']
    list_filter = ['new_status', 'changed_by', 'changed_at']
    search_fields = ['report__address', 'comment']
    ordering = ['-changed_at']
    readonly_fields = ['changed_at']


@admin.register(AIClassification)
class AIClassificationAdmin(admin.ModelAdmin):
    list_display = ['report', 'category_predicted', 'confidence_display', 'created_at']
    search_fields = ['report__address', 'category_predicted']
    readonly_fields = ['created_at', 'confidence_display']
    
    def confidence_display(self, obj):
        if obj.confidence is not None:
            return f"{obj.confidence:.2%}"
        return "N/A"
    confidence_display.short_description = 'Confidence'
