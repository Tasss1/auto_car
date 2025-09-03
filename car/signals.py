import os
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from .models import CarContent


def delete_file(file_field):
    """Удаляет файл, если он есть на диске."""
    try:
        if file_field and file_field.path and os.path.isfile(file_field.path):
            os.remove(file_field.path)
    except ValueError:
        # файл ещё не сохранён, path не доступен
        pass


@receiver(post_delete, sender=CarContent)
def auto_delete_files_on_delete(sender, instance, **kwargs):
    """Удаляем файлы при удалении объекта"""
    for field in ["video", "photo1", "photo2", "photo3", "photo4", "photo5"]:
        delete_file(getattr(instance, field))


@receiver(pre_save, sender=CarContent)
def auto_delete_files_on_change(sender, instance, **kwargs):
    """Удаляем старые файлы при замене"""
    if not instance.pk:
        return  # новый объект, ничего не чистим

    try:
        old = CarContent.objects.get(pk=instance.pk)
    except CarContent.DoesNotExist:
        return

    for field in ["video", "photo1", "photo2", "photo3", "photo4", "photo5"]:
        old_file = getattr(old, field)
        new_file = getattr(instance, field)
        if old_file and old_file != new_file:
            delete_file(old_file)