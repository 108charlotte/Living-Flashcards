from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
import sqlite3
from django.db import connection


class Command(BaseCommand):
    help = "Show DB config, resolved sqlite path, and list tables."

    def handle(self, *args, **options):
        db_conf = settings.DATABASES.get('default')
        self.stdout.write(f"DB config: {db_conf}")

        name = db_conf.get('NAME') if db_conf else None
        self.stdout.write(f"Raw NAME: {name}")

        resolved = None
        if name:
            resolved = Path(name)
            if not resolved.is_absolute():
                base = getattr(settings, 'BASE_DIR', None)
                if base:
                    resolved = Path(base) / name

        self.stdout.write(f"Resolved path: {resolved} (exists={resolved.exists() if resolved else False})")

        if resolved and resolved.exists():
            try:
                conn = sqlite3.connect(str(resolved))
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
                tables = [r[0] for r in cur.fetchall()]
                self.stdout.write(f"SQLite tables: {tables}")
                conn.close()
            except Exception as e:
                self.stderr.write(f"SQLite introspection failed: {e}")
        else:
            self.stderr.write("Resolved DB file does not exist or NAME is not configured.")

        # Also show what Django's connection sees
        try:
            with connection.cursor() as cur:
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
                rows = cur.fetchall()
                self.stdout.write(f"Tables via Django connection: {[r[0] for r in rows]}")
        except Exception as e:
            self.stderr.write(f"Django connection introspect failed: {e}")
