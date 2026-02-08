from django.db import connections
from django.conf import settings

def main():
    # Use Django ORM to remove the migration record if present
    import django
    django.setup()
    from django.db.migrations.recorder import MigrationRecorder

    qs = MigrationRecorder.Migration.objects.filter(app='accounts', name='0001_initial')
    deleted = qs.delete()
    print('deleted migration record:', deleted)

if __name__ == '__main__':
    main()
