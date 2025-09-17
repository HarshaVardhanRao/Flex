"""
Management command to create system roles and permissions
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from flexapp.models import Role, PermissionGroup


class Command(BaseCommand):
    help = 'Create default system roles and permissions'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreate existing roles',
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Creating system roles and permissions...')
        
        # Define default roles and their permissions
        roles_config = {
            'super_admin': {
                'description': 'Super Administrator with full system access',
                'hierarchy_level': 100,
                'permissions': [
                    'add_user', 'change_user', 'delete_user', 'view_user',
                    'add_student', 'change_student', 'delete_student', 'view_student',
                    'add_faculty', 'change_faculty', 'delete_faculty', 'view_faculty',
                    'add_achievement', 'change_achievement', 'delete_achievement', 'view_achievement',
                    'add_role', 'change_role', 'delete_role', 'view_role',
                    'add_auditlog', 'view_auditlog',
                    'add_securitylog', 'view_securitylog',
                    'add_apikey', 'change_apikey', 'delete_apikey', 'view_apikey'
                ]
            },
            'admin': {
                'description': 'System Administrator',
                'hierarchy_level': 90,
                'permissions': [
                    'add_student', 'change_student', 'delete_student', 'view_student',
                    'add_faculty', 'change_faculty', 'delete_faculty', 'view_faculty',
                    'add_achievement', 'change_achievement', 'view_achievement',
                    'view_auditlog', 'view_securitylog'
                ]
            },
            'hod': {
                'description': 'Head of Department',
                'hierarchy_level': 80,
                'permissions': [
                    'view_student', 'change_student',
                    'view_faculty', 'change_faculty',
                    'add_achievement', 'change_achievement', 'view_achievement',
                    'view_auditlog'
                ]
            },
            'coordinator': {
                'description': 'Department Coordinator',
                'hierarchy_level': 70,
                'permissions': [
                    'view_student', 'change_student',
                    'view_faculty',
                    'add_achievement', 'change_achievement', 'view_achievement'
                ]
            },
            'faculty': {
                'description': 'Faculty Member',
                'hierarchy_level': 60,
                'permissions': [
                    'view_student',
                    'add_achievement', 'view_achievement'
                ]
            },
            'student': {
                'description': 'Student',
                'hierarchy_level': 10,
                'permissions': [
                    'view_student',  # Own profile only
                    'add_achievement'  # Submit achievements
                ]
            },
            'guest': {
                'description': 'Guest User',
                'hierarchy_level': 1,
                'permissions': []
            }
        }
        
        # Create or update roles
        created_count = 0
        updated_count = 0
        
        for role_type, config in roles_config.items():
            role, created = Role.objects.get_or_create(
                role_type=role_type,
                defaults={
                    'name': role_type.title().replace('_', ' '),
                    'description': config['description'],
                    'hierarchy_level': config['hierarchy_level'],
                    'is_active': True
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created role: {role.name}')
                )
            elif options['force']:
                role.description = config['description']
                role.hierarchy_level = config['hierarchy_level']
                role.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated role: {role.name}')
                )
            
            # Add permissions to role
            for perm_codename in config['permissions']:
                try:
                    permission = Permission.objects.get(codename=perm_codename)
                    role.permissions.add(permission)
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.ERROR(f'Permission not found: {perm_codename}')
                    )
        
        # Create permission groups for common access patterns
        permission_groups_config = {
            'Student Management': [
                'view_student', 'add_student', 'change_student', 'delete_student'
            ],
            'Faculty Management': [
                'view_faculty', 'add_faculty', 'change_faculty', 'delete_faculty'
            ],
            'Achievement Management': [
                'view_achievement', 'add_achievement', 'change_achievement', 'delete_achievement'
            ],
            'System Administration': [
                'view_auditlog', 'view_securitylog', 'add_role', 'change_role', 'delete_role'
            ],
            'API Access': [
                'view_apikey', 'add_apikey', 'change_apikey', 'delete_apikey'
            ]
        }
        
        for group_name, permission_codes in permission_groups_config.items():
            group, created = PermissionGroup.objects.get_or_create(
                name=group_name,
                defaults={
                    'description': f'Permissions for {group_name.lower()}'
                }
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created permission group: {group_name}')
                )
            
            for perm_code in permission_codes:
                try:
                    permission = Permission.objects.get(codename=perm_code)
                    group.permissions.add(permission)
                except Permission.DoesNotExist:
                    continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Command completed successfully. '
                f'Created {created_count} roles, updated {updated_count} roles.'
            )
        )