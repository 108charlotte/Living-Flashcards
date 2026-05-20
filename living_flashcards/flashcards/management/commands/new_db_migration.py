from django.core.management.base import BaseCommand
import psycopg2
import io
import subprocess
import os

class Command(BaseCommand): 
    def add_arguments(self, parser): 
        parser.add_argument('--orig_path', dest='orig_path', type=str)
        parser.add_argument('--new_path', dest='new_path', type=str)
        parser.add_argument('--migrate', action='store_true', dest='migrate')

    def handle(self, *args, **options): 
        print("migrate flag:", options.get('migrate'))
        orig_path = options.get('orig_path')
        new_path = options.get('new_path')

        orig_conn = psycopg2.connect(orig_path)
        new_conn = psycopg2.connect(new_path)

        if options.get('migrate'):
            subprocess.run(["python", "manage.py", "migrate"], env={**os.environ, "DATABASE_URL": new_path}, check=True)

        print(f"Starting copying all tables")
        with orig_conn.cursor() as orig_cur, new_conn.cursor() as new_cur: 
            # put independent tables first, dependent tables after, so I don't get errors
            TABLE_ORDER = [
                'django_content_type',
                'auth_permission',
                'auth_group',
                'auth_group_permissions',
                'auth_user',
                'auth_user_groups',
                'auth_user_user_permissions',
                'django_admin_log',
                'django_session',
                'authentication_userstudysettings',
                'lang_selection_userlanguage',
                'flashcards_deck',
                'flashcards_cardinfo',
                'flashcards_cardtouser',
                'flashcards_review',
            ]

            # replace the dynamic table fetch with this
            tables = TABLE_ORDER

            # clean up from past run
            for table in tables:
                new_cur.execute(f"TRUNCATE {table} CASCADE")
            new_conn.commit()

            for table in tables:
                print(f"Reading {table}")
                buffer = io.StringIO()
                orig_cur.copy_expert(f"COPY {table} TO STDOUT", buffer)
                buffer.seek(0)

                print(f"Copying {table}")
                new_cur.copy_expert(f"COPY {table} FROM STDIN", buffer)
                new_conn.commit()

        new_conn.close()
        orig_conn.close()