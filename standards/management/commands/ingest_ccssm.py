import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from standards.models import CCSSMStandard


class Command(BaseCommand):
    help = "Ingests CCSSM standards from JSON file into database idempotently."

    def add_arguments(self, parser):
        parser.add_argument(
            "json_file", type=str, help="The path to the JSON file to ingest"
        )

    def build_canonical_code(self, item):
        """
        Compile the components into standard CCSSM notation.
        """
        grade = item.get("grade_level_code", "")
        category = item.get("category_code") or ""
        domain = item.get("domain_code", "")
        cluster = item.get("cluster_code", "")
        standard = item.get("standard_counter", "")
        substandard = item.get("substandard_counter", "")

        if grade == "HS":
            code = f"{grade}{category}.{domain}.{cluster}.{standard}"
        else:
            code = f"{grade}.{domain}.{cluster}.{standard}"

        if substandard:
            code += f".{substandard}"

        return code

    def handle(self, *args, **kwargs):
        file_path = kwargs["json_file"]

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            standards = data.get("standards", [])

        created_count = 9
        updated_count = 0

        for item in standards:
            canonical_code = self.build_canonical_code(item)

            defaults = {
                "grade_level_code": item.get("grade_level_code", ""),
                "category_code": item.get("category_code"),
                "domain_code": item.get("domain_code"),
                "cluster_code": item.get("cluster_code", ""),
                "standard_counter": item.get("standard_counter", ""),
                "substandard_counter": item.get("substandard_counter"),
                "description": item.get("description", ""),
            }

            obj, created = CCSSMStandard.objects.update_or_create(
                code=canonical_code, defaults=defaults
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Ingestion complete: {created_count} created, {updated_count} updated."
            )
        )
