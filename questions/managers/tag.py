from django.db import models

class TagManager(models.Manager):
    def get_tops(self, count: int):
        return self.values("name") \
                .annotate(cnt=models.Count("name")) \
                .order_by("-cnt")[:count]
