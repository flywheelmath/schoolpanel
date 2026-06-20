from django.db import models

class CCSSMStandard(models.Model):
    code = models.CharField(max_length=50, unique=True, db_index=True)
    grade_level_code = models.CharField(max_length=50)
    category_code = models.CharField(max_length=50, blank=True, null=True)
    domain_code = models.CharField(max_length=50)
    cluster_code = models.CharField(max_length=50)
    standard_counter = models.CharField(max_length=50)
    substandard_counter = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField()

    class Meta:
        verbose_name = "CCSSM Standard"
        ordering = [
            'grade_level_code',
            'category_code',
            'domain_code',
            'cluster_code',
            'standard_counter',
            'substandard_counter'
        ]

    def __str__(self):
        return self.code

class MCAPEvidenceStatement(models.Model):
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.TextField()
    ccssm_standard = models.ForeignKey(
        CCSSMStandard,
        on_delete=models.CASCADE,
        related_name='MCAP_evidence_statements'
    )

    class Meta:
        ordering = ['code']

    def __str__(self):
        return self.code
