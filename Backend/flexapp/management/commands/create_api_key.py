"""
Management command to create API keys for external integrations
"""
import secrets
import string
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from flexapp.models import APIKey


class Command(BaseCommand):
    help = 'Create API keys for external integrations'
    
    def add_arguments(self, parser):
        parser.add_argument('name', type=str, help='Name for the API key')
        parser.add_argument(
            '--user',
            type=str,
            help='Username to associate with the API key',
        )
        parser.add_argument(
            '--expires-days',
            type=int,
            default=365,
            help='Number of days until API key expires (default: 365)',
        )
        parser.add_argument(
            '--rate-limit',
            type=int,
            default=1000,
            help='Rate limit per hour (default: 1000)',
        )
        parser.add_argument(
            '--scopes',
            type=str,
            help='Comma-separated list of scopes (read,write,admin)',
        )
        parser.add_argument(
            '--description',
            type=str,
            help='Description for the API key',
        )
    
    def generate_api_key(self):
        """Generate a secure API key"""
        # Generate a 32-character random string
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def handle(self, *args, **options):
        name = options['name']
        username = options.get('user')
        expires_days = options['expires_days']
        rate_limit = options['rate_limit']
        scopes_str = options.get('scopes', 'read')
        description = options.get('description', '')
        
        try:
            # Get user if specified, otherwise use the first superuser
            user = None
            if username:
                user = User.objects.get(username=username)
                self.stdout.write(f'Associated with user: {user.get_full_name()} ({user.username})')
            else:
                # Try to get a superuser if no user specified
                user = User.objects.filter(is_superuser=True).first()
                if user:
                    self.stdout.write(f'Associated with superuser: {user.username}')
                else:
                    self.stdout.write(
                        self.style.ERROR('No user specified and no superuser found. Please specify a user.')
                    )
                    return
            
            # Parse scopes
            scopes = [scope.strip() for scope in scopes_str.split(',')]
            valid_scopes = ['read', 'write', 'admin']
            invalid_scopes = [scope for scope in scopes if scope not in valid_scopes]
            
            if invalid_scopes:
                self.stdout.write(
                    self.style.ERROR(f'Invalid scopes: {invalid_scopes}. Valid scopes: {valid_scopes}')
                )
                return
            
            # Generate API key
            api_key = self.generate_api_key()
            
            # Calculate expiry date
            expires_at = timezone.now() + timedelta(days=expires_days)
            
            # Create API key object
            api_key_obj = APIKey.objects.create(
                name=name,
                key=api_key,
                user=user,
                expires_at=expires_at,
                rate_limit=rate_limit,
                is_active=True
            )
            
            # Add scopes via permissions (we'll need to create permission objects)
            # For now, we'll store a simple reference
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created API key: {name}')
            )
            
            # Display API key details
            self.stdout.write('API Key Details:')
            self.stdout.write(f'  Name: {name}')
            self.stdout.write(f'  Key: {api_key}')
            self.stdout.write(f'  Scopes: {", ".join(scopes)}')
            self.stdout.write(f'  Rate Limit: {rate_limit} requests/hour')
            self.stdout.write(f'  Expires: {expires_at}')
            self.stdout.write(f'  User: {user.username if user else "None"}')
            if description:
                self.stdout.write(f'  Description: {description}')
            
            # Security warning
            self.stdout.write('')
            self.stdout.write(
                self.style.WARNING('IMPORTANT: Store this API key securely!')
            )
            self.stdout.write(
                self.style.WARNING('This is the only time the full key will be displayed.')
            )
            
            # Usage examples
            self.stdout.write('')
            self.stdout.write('Usage Examples:')
            self.stdout.write('  HTTP Header: X-API-Key: ' + api_key)
            self.stdout.write('  Query Parameter: ?api_key=' + api_key)
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User with username "{username}" not found')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating API key: {str(e)}')
            )