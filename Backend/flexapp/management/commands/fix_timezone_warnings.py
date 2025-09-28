"""
Django Management Command to fix timezone warnings for Achievement model
This command will update any naive datetime fields to be timezone-aware
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from flexapp.models import Achievement
from datetime import datetime
import pytz

class Command(BaseCommand):
    help = 'Fix timezone warnings by converting naive datetimes to timezone-aware datetimes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 Checking for Achievement records with naive datetimes...')
        )
        
        dry_run = options['dry_run']
        
        # Get all Achievement records
        achievements = Achievement.objects.all()
        total_count = achievements.count()
        
        if total_count == 0:
            self.stdout.write(
                self.style.WARNING('No Achievement records found in database.')
            )
            return
        
        self.stdout.write(f'Found {total_count} Achievement records to check.')
        
        updated_count = 0
        
        for achievement in achievements:
            needs_update = False
            
            # Check submission_date
            if achievement.submission_date and timezone.is_naive(achievement.submission_date):
                needs_update = True
                if not dry_run:
                    # Convert naive datetime to UTC timezone-aware datetime
                    achievement.submission_date = timezone.make_aware(
                        achievement.submission_date, 
                        timezone=pytz.UTC
                    )
            
            # Check review_date
            if achievement.review_date and timezone.is_naive(achievement.review_date):
                needs_update = True
                if not dry_run:
                    achievement.review_date = timezone.make_aware(
                        achievement.review_date,
                        timezone=pytz.UTC
                    )
            
            # Check approval_date
            if achievement.approval_date and timezone.is_naive(achievement.approval_date):
                needs_update = True
                if not dry_run:
                    achievement.approval_date = timezone.make_aware(
                        achievement.approval_date,
                        timezone=pytz.UTC
                    )
            
            if needs_update:
                updated_count += 1
                if dry_run:
                    self.stdout.write(
                        f'Would update Achievement ID {achievement.id}: {achievement.title}'
                    )
                else:
                    achievement.save()
                    self.stdout.write(
                        f'✅ Updated Achievement ID {achievement.id}: {achievement.title}'
                    )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would update {updated_count} records')
            )
            self.stdout.write(
                'Run without --dry-run to actually update the records'
            )
        else:
            if updated_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Successfully updated {updated_count} Achievement records')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('✅ All Achievement records already have timezone-aware datetimes')
                )
        
        self.stdout.write(
            self.style.SUCCESS('🎉 Timezone warning fix completed!')
        )
