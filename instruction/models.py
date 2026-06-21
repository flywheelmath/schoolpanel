import uuid
from django.db import models
from django.conf import settings

class PresentationSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='presentation_sessions'
    )
    lesson_slug = models.CharField(max_length=100, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Session: {self.lesson_slug} {self.teacher.username} {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class SessionAnnotation(models.Model):
    session = models.ForeignKey(
        PresentationSession,
        on_delete=models.CASCADE,
        related_name='annotations'
    )
    slide_index = models.IntegerField(db_index=True)
    content_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['slide_index', 'created_at']

    def __str__(self):
        return f"Annotated slide: {self.session.id}_{self.slide_index}"

class SessionFlag(models.Model):
    class FlagType(models.TextChoices):
        CORRECTION = 'correction', 'Correction'
        RETEACH = 'reteach', 'Reteach'
        DELAYED_TEST = 'delayed_test', 'Delayed test'
        SKIPPED = 'skipped', 'Skipped'
        NOTE = 'note', 'Note'

    session = models.ForeignKey(
        PresentationSession,
        on_delete=models.CASCADE,
        related_name='flags'
    )
    slide_index = models.IntegerField(db_index=True)
    flag_type = models.CharField(max_length=50, choices=FlagType.choices)
    notes = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['resolved', '-created_at']

    def __str__(self):
        return f"Flagged slide: {self.get_flag_type_display()} on {self.session.lesson_slug}_{self.slide_index}"
