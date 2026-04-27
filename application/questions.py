from dataclasses import dataclass
from collections import Counter
from typing import (overload,
                    Union,
                    List)

@dataclass
class Question:
    id: int
    title: str
    content: str
    tags: list[str]
    answer_count: int
    vote_count: int

@dataclass
class Answer:
    content: str
    vote_count: int
    is_correct: bool

@dataclass
class PopularTag:
    name: str
    color: str
    font_size: str

DEFAULT_POPULAR_TAGS_COUNT: int = 7

ANSWERS: dict[str, list[Answer]] = {
    "correct": [
        Answer("Correct #1", 34, True),
        Answer("Correct #2", 10, True),
        Answer("Correct #3", 5, True)
    ],
    "not_checked": [
        Answer("Not checked #1", 2, False),
        Answer("Not checked #2", 0, False),
        Answer("Not checked #3", 5, False),
        Answer("Not checked #4", 0, False)
    ]
}

QUESTIONS = [
    Question(
        id=i,
        title=f"Title #{i}",
        content=f"Question text #{i}",
        tags=[
            f"Tag_{j}" for j in range(1, (i+1) % 5 + 2)
        ],
        answer_count=(i+ (i+1) % 7) % 15,
        vote_count=(i+ (i % 4) + 3) % 13,
    )
    for i in range(0, 30)
]

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

@overload
def get_popular_tags(content: List[str], count: int = DEFAULT_POPULAR_TAGS_COUNT) -> List[PopularTag]:
    pass

@overload
def get_popular_tags(content: List[Question], count: int = DEFAULT_POPULAR_TAGS_COUNT) -> List[PopularTag]:
    pass

def get_popular_tags(
        content: Union[List[str], List[Question]],
        count: int = DEFAULT_POPULAR_TAGS_COUNT
    ) -> List[PopularTag]:
    if len(content) == 0:
        return []
    
    counted_tags: Counter[str] = Counter()
    if isinstance(content[0], str):
        counted_tags = Counter(content) # type: ignore

    elif isinstance(content[0], Question):
        tags: list[str] = []
        for question in content:
            tags.extend(question.tags) # type: ignore

        counted_tags = Counter(tags)
    else:
        raise TypeError()

    popular_tag_names = list(
        sorted(counted_tags, key=lambda tag: counted_tags[tag], reverse=True)
    )[:count]

    return form_popular_tags(popular_tag_names)

def form_popular_tags(tag_names: List[str]) -> List[PopularTag]:
    return [
        PopularTag(
            name=tag_names[i],
            color=POPULAR_TAGS_COLORS[i % len(POPULAR_TAGS_COLORS)],
            font_size=POPULAR_TAGS_FONT_SIZES[i % len(POPULAR_TAGS_FONT_SIZES)]
        )
        for i in range(len(tag_names))
    ]

def get_hot_questions(questions: List[Question]) -> List[Question]:
    return list(
        sorted(questions, key=lambda q: q.vote_count, reverse=True)
    )
