from django.db import models
from django.conf import settings
import os

def ml_model_upload_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/ml_models/user_<id>/<filename>
    return f'ml_models/user_{instance.uploaded_by.id}/{filename}'

class MLModel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    model_file = models.FileField(upload_to=ml_model_upload_path)
    version = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    accuracy = models.FloatField(null=True, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    last_used = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.name} v{self.version}"

    def save(self, *args, **kwargs):
        # If this model is being set as active, deactivate all other models
        if self.is_active:
            MLModel.objects.exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the actual file when the model is deleted
        if self.model_file:
            if os.path.isfile(self.model_file.path):
                os.remove(self.model_file.path)
        super().delete(*args, **kwargs) 