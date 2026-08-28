from django.db import models
from dataclasses import dataclass
from application import config


POPULAR_TAGS_COLORS = [
    "#ff8c00", "#ce5c00", "#2c3e50",
    "#17a2b8", "#dc3545", "#20c997",
    "#fd7e14"
]

POPULAR_TAGS_FONT_SIZES = [
    "1.2rem", "0.95rem", "1.1rem",
    "0.8rem", "1.05rem", "0.89rem",
    "1.05rem"
]


class TagManager(models.Manager):
    def get_popular_tags(self) -> 'list[PopularTagDisplay]':
        return self.__form_popular_tags_from(
            [
                name for name in self.values("content__name") \
                .annotate(count=models.Count("content__name")) \
                .order_by("-count")[:config.POPULAR_TAGS_COUNT]
                .values_list("content__name", flat=True)
            ]
        )
    
    def __form_popular_tags_from(self, tag_names: list[str]) -> 'list[PopularTagDisplay]':
        return [
            PopularTagDisplay(
                name=tag_names[i],
                color=POPULAR_TAGS_COLORS[i % len(POPULAR_TAGS_COLORS)],
                font_size=POPULAR_TAGS_FONT_SIZES[i % len(POPULAR_TAGS_FONT_SIZES)]
            )
            for i in range(len(tag_names))
        ]


@dataclass(frozen=True)
class PopularTagDisplay:
    name: str
    color: str
    font_size: str
