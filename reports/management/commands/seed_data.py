from django.core.management.base import BaseCommand
from django.conf import settings
from reports.models import Department, Category


class Command(BaseCommand):
    help = 'Seeds initial departments and categories'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding initial data...')

        # Use configured email so department notifications go to a real inbox.
        # In production, update each department's email via Django admin.
        default_email = settings.EMAIL_HOST_USER or 'admin@cityassist.az'

        # Create departments
        departments_data = [
            {
                'name': 'Roads & Transportation Department',
                'email': default_email,
                'phone': '+994-12-555-0101',
            },
            {
                'name': 'Sanitation & Waste Management',
                'email': default_email,
                'phone': '+994-12-555-0102',
            },
            {
                'name': 'Public Lighting Department',
                'email': default_email,
                'phone': '+994-12-555-0103',
            },
            {
                'name': 'Parks & Recreation',
                'email': default_email,
                'phone': '+994-12-555-0104',
            },
            {
                'name': 'General Services',
                'email': default_email,
                'phone': '+994-12-555-0105',
            },
        ]
        
        departments = {}
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                email=dept_data['email'],
                defaults=dept_data
            )
            departments[dept_data['name']] = dept
            if created:
                self.stdout.write(f'Created department: {dept.name}')
            else:
                self.stdout.write(f'Department already exists: {dept.name}')
        
        # Create categories with department mappings
        categories_data = [
            {
                'name': 'Road Damage',
                'slug': 'road_damage',
                'department': 'Roads & Transportation Department',
                'icon': '🛣️',
            },
            {
                'name': 'Trash Overflow',
                'slug': 'trash_overflow',
                'department': 'Sanitation & Waste Management',
                'icon': '🗑️',
            },
            {
                'name': 'Street Light Issue',
                'slug': 'street_light',
                'department': 'Public Lighting Department',
                'icon': '💡',
            },
            {
                'name': 'Graffiti',
                'slug': 'graffiti',
                'department': 'General Services',
                'icon': '🎨',
            },
            {
                'name': 'Sidewalk Issue',
                'slug': 'sidewalk_issue',
                'department': 'Roads & Transportation Department',
                'icon': '🚶',
            },
            {
                'name': 'Traffic Sign',
                'slug': 'traffic_sign',
                'department': 'Roads & Transportation Department',
                'icon': '🚦',
            },
            {
                'name': 'Park Maintenance',
                'slug': 'park_maintenance',
                'department': 'Parks & Recreation',
                'icon': '🌳',
            },
        ]
        
        for cat_data in categories_data:
            dept_name = cat_data.pop('department')
            dept = departments.get(dept_name)
            
            cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={**cat_data, 'department': dept}
            )
            if created:
                self.stdout.write(f'Created category: {cat.name}')
            else:
                self.stdout.write(f'Category already exists: {cat.name}')
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded initial data'))
