from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Movement, Animal

@receiver(post_save, sender=Movement)
def sync_animal_group(sender, instance: Movement, created, **kwargs):
    # Sempre que registra movimentação, atualiza o lote atual do animal
    if instance.to_group and instance.animal.group_id != instance.to_group_id:
        Animal.objects.filter(id=instance.animal_id).update(group=instance.to_group)
