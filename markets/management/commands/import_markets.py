import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from markets.models import Market


class Command(BaseCommand):
    help = "CSV → Market bulk import"

    def add_arguments(self, parser):
        parser.add_argument("--path", required=True, help="CSV file path")
        parser.add_argument("--chunksize", type=int, default=500)

    def handle(self, *args, **opts):
        path = Path(opts["path"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        rows, created = [], 0

        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                try:
                    rows.append(Market(
                        name=r["업소명"].strip(),
                        address=r["소재지"].strip(),
                        business_hours="00:00~23:59",   # 기본값
                        telephone=(r["소재지전화번호"] or "").strip() or None,
                        url=None,
                        description="",
                        type="UNKNOWN",
                        lat=float(r["위도"]),
                        lng=float(r["경도"]),
                    ))
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Row skipped: {r} ({e})"))
                    continue

                if len(rows) >= opts["chunksize"]:
                    with transaction.atomic():
                        Market.objects.bulk_create(rows, ignore_conflicts=True)
                    created += len(rows)
                    rows.clear()

            if rows:
                with transaction.atomic():
                    Market.objects.bulk_create(rows, ignore_conflicts=True)
                created += len(rows)

        self.stdout.write(self.style.SUCCESS(f"Imported ~{created} rows from {path}"))