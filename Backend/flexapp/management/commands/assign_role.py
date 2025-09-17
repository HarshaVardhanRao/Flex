"""
Management command to assign roles to users
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from flexapp.models import Role, UserRole


class Command(BaseCommand):
    help = 'Assign roles to users'
    
    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to assign role to')
        parser.add_argument('role_type', type=str, help='Role type to assign')
        parser.add_argument(
            '--department',
            type=str,
            help='Department for the role assignment',
        )
        parser.add_argument(
            '--duration',
            type=int,
            help='Duration in days for the role assignment',
        )
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date for role assignment (YYYY-MM-DD)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force assignment even if user already has the role',
        )
    
    def handle(self, *args, **options):
        username = options['username']
        role_type = options['role_type']
        department = options.get('department')
        duration = options.get('duration')
        start_date_str = options.get('start_date')
        force = options.get('force', False)
        
        try:
            # Get user
            user = User.objects.get(username=username)
            self.stdout.write(f'Found user: {user.get_full_name()} ({user.username})')
            
            # Get role
            role = Role.objects.get(role_type=role_type, is_active=True)
            self.stdout.write(f'Found role: {role.name}')
            
            # Parse start date
            start_date = timezone.now()
            if start_date_str:
                try:
                    start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d')
                    start_date = timezone.make_aware(start_date)
                except ValueError:
                    self.stdout.write(
                        self.style.ERROR('Invalid date format. Use YYYY-MM-DD')
                    )
                    return
            
            # Calculate end date
            end_date = None
            if duration:
                end_date = start_date + timedelta(days=duration)
            
            # Check if user already has this role
            existing_assignment = UserRole.objects.filter(
                user=user,
                role=role,
                is_active=True
            ).first()
            
            if existing_assignment and not force:
                self.stdout.write(
                    self.style.WARNING(
                        f'User {username} already has role {role_type}. '
                        f'Use --force to override.'
                    )
                )
                return
            
            if existing_assignment and force:
                # Deactivate existing assignment
                existing_assignment.is_active = False
                existing_assignment.save()
                self.stdout.write(
                    self.style.WARNING(f'Deactivated existing role assignment')
                )
            
            # Create new role assignment
            user_role = UserRole.objects.create(
                user=user,
                role=role,
                assigned_by=None,  # System assignment
                start_date=start_date,
                end_date=end_date,
                department=department,
                is_active=True,
                assignment_reason=f'Assigned via management command'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully assigned role {role_type} to user {username}'
                )
            )
            
            # Display assignment details
            self.stdout.write(f'Assignment details:')
            self.stdout.write(f'  - Start Date: {start_date}')
            self.stdout.write(f'  - End Date: {end_date or "No expiration"}')
            self.stdout.write(f'  - Department: {department or "Not specified"}')
            
            # List user's permissions
            permissions = role.permissions.values_list('codename', flat=True)
            if permissions:
                self.stdout.write(f'Role permissions:')
                for perm in permissions:
                    self.stdout.write(f'  - {perm}')
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with username "{username}" not found')
            )
        except Role.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Role with type "{role_type}" not found')
            )
            # List available roles
            available_roles = Role.objects.filter(is_active=True).values_list('role_type', flat=True)
            self.stdout.write('Available roles:')
            for role in available_roles:
                self.stdout.write(f'  - {role}')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error assigning role: {str(e)}')
            )