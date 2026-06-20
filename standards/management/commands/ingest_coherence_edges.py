import json
import os
from django.core.management.base import BaseCommand
from standards.models import CCSSMStandard

class Command(BaseCommand):
    help = 'Ingests AchieveTheCore.org Coherence Map dependencies.'

    def add_arguments(self, parser):
        parser.add_argument('json_file', type=str, help='The path to the CCSSM-dependencies JSON file.')

    def handle(self, *args, **kwargs):
        file_path = kwargs['json_file']

        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            edges = data.get('dependencies', [])

        success_count = 0
        missing_nodes = set()

        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')

            source_obj = CCSSMStandard.objects.filter(code=source).first()
            target_obj = CCSSMStandard.objects.filter(code=target).first()

            if source_obj and target_obj:
                target_obj.prerequisites.add(source_obj)
                success_count += 1
            else:
                if not source_obj:
                    missing_nodes.add(source)
                if not target_obj:
                    missing_nodes.add(target)

        self.stdout.write(self.style.SUCCESS(
            f"Edge ingestion complete: {success_count} dependencies added."
        ))

        if missing_nodes:
            self.stdout.write(self.style.WARNING(
                f"Warning: {len(missing_nodes)} standards referenced in the edges were not found in the database. "
            ))
