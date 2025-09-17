from django.core.management.base import BaseCommand
from flexapp.models import CoordinatorRole, Faculty
from django.db import transaction


class Command(BaseCommand):
    help = 'Create placement coordinator role and assign it to faculty members'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-role',
            action='store_true',
            help='Create the placement coordinator role',
        )
        parser.add_argument(
            '--assign-faculty',
            type=str,
            help='Assign placement coordinator role to faculty by username',
        )
        parser.add_argument(
            '--list-coordinators',
            action='store_true',
            help='List all placement coordinators',
        )

    def handle(self, *args, **options):
        if options['create_role']:
            self.create_placement_coordinator_role()
        
        if options['assign_faculty']:
            self.assign_faculty_to_placement_role(options['assign_faculty'])
        
        if options['list_coordinators']:
            self.list_placement_coordinators()

    def create_placement_coordinator_role(self):
        """Create the placement coordinator role"""
        try:
            with transaction.atomic():
                role, created = CoordinatorRole.objects.get_or_create(
                    name='Placement Coordinator',
                    defaults={
                        'description': 'Has access to placement dashboard and placement-related data',
                        'can_view_placement': True,
                        'can_view_certificates': True,  # Usually placement coordinators need this
                        'can_view_projects': True,      # Usually placement coordinators need this
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Successfully created placement coordinator role: {role.name}'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Placement coordinator role already exists: {role.name}'
                        )
                    )
                    # Update permissions if role exists but doesn't have placement permission
                    if not role.can_view_placement:
                        role.can_view_placement = True
                        role.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                'Updated existing role with placement permissions'
                            )
                        )
                        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating placement coordinator role: {str(e)}')
            )

    def assign_faculty_to_placement_role(self, username):
        """Assign a faculty member to the placement coordinator role"""
        try:
            with transaction.atomic():
                faculty = Faculty.objects.get(username=username)
                
                # Get or create the placement coordinator role
                role, created = CoordinatorRole.objects.get_or_create(
                    name='Placement Coordinator',
                    defaults={
                        'description': 'Has access to placement dashboard and placement-related data',
                        'can_view_placement': True,
                        'can_view_certificates': True,
                        'can_view_projects': True,
                    }
                )
                
                # Add faculty to the role
                role.faculties.add(faculty)
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully assigned {faculty.username} ({faculty.get_full_name()}) '
                        f'to placement coordinator role'
                    )
                )
                
        except Faculty.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Faculty with username "{username}" does not exist')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error assigning faculty to placement role: {str(e)}')
            )

    def list_placement_coordinators(self):
        """List all placement coordinators"""
        try:
            placement_roles = CoordinatorRole.objects.filter(can_view_placement=True)
            
            if not placement_roles.exists():
                self.stdout.write(
                    self.style.WARNING('No placement coordinator roles found')
                )
                return
            
            self.stdout.write(
                self.style.SUCCESS('\n=== Placement Coordinator Roles ===')
            )
            
            for role in placement_roles:
                self.stdout.write(f'\nRole: {role.name}')
                self.stdout.write(f'Description: {role.description}')
                
                faculties = role.faculties.all()
                if faculties.exists():
                    self.stdout.write('Assigned Faculty:')
                    for faculty in faculties:
                        self.stdout.write(f'  - {faculty.username} ({faculty.get_full_name()}) - {faculty.dept}')
                else:
                    self.stdout.write('  No faculty assigned to this role')
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error listing placement coordinators: {str(e)}')
            )