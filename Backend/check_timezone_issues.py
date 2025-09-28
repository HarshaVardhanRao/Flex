"""
Test script to identify potential timezone warning sources
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flex.settings')
django.setup()

from django.utils import timezone
from django.db import models
from django.apps import apps
from datetime import datetime
import warnings

def check_timezone_warnings():
    """Check all models for potential timezone warning sources"""
    print("🔍 Checking for models with DateTimeField that might cause timezone warnings...")
    
    # Capture warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always", RuntimeWarning)
        
        # Get all models from flexapp
        app_models = apps.get_app_config('flexapp').get_models()
        
        for model in app_models:
            model_name = model._meta.label
            print(f"\n📋 Checking model: {model_name}")
            
            # Check for DateTimeFields
            datetime_fields = []
            for field in model._meta.fields:
                if isinstance(field, models.DateTimeField):
                    datetime_fields.append(field.name)
            
            if datetime_fields:
                print(f"   DateTimeFields found: {', '.join(datetime_fields)}")
                
                # Check if there are any records in this model
                try:
                    record_count = model.objects.count()
                    print(f"   Record count: {record_count}")
                    
                    if record_count > 0:
                        # Try to access the first record to see if it triggers warnings
                        first_record = model.objects.first()
                        for field_name in datetime_fields:
                            field_value = getattr(first_record, field_name)
                            if field_value:
                                is_naive = timezone.is_naive(field_value)
                                print(f"   Field '{field_name}': {'NAIVE' if is_naive else 'TIMEZONE-AWARE'}")
                                if is_naive:
                                    print(f"   ⚠️  WARNING: Field '{field_name}' in {model_name} has naive datetime!")
                except Exception as e:
                    print(f"   Error checking records: {e}")
            else:
                print("   No DateTimeFields found")
        
        # Check if any warnings were captured
        if w:
            print(f"\n⚠️  {len(w)} warnings captured:")
            for warning in w:
                print(f"   - {warning.message}")
        else:
            print("\n✅ No timezone warnings detected!")

if __name__ == "__main__":
    check_timezone_warnings()
