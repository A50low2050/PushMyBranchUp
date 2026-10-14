from pydantic import Field, field_validator
from src.schemas.base import BaseDTO
from datetime import datetime


class PostCreateDTO(BaseDTO):
    content: str = Field(
        min_length=1,
        max_length=2200,
        description="Текст поста. От 1 до 2200 символов, не может состоять только из пробелов.",
        examples=["Сегодня начал работать над новым проектом!"],
    )

    @field_validator("content")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Пост не может быть пустым")
        return value


class PostDTO(BaseDTO):
    id: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime


class PostEditDTO(BaseDTO):
    content: str = Field(
        min_length=1,
        max_length=2200,
        description="Текст поста. От 1 до 2200 символов, не может состоять только из пробелов.",
        examples=["Сегодня начал работать над новым проектом!"],
    )
    
    @field_validator("content")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Пост не может быть пустым")
        return value


class PostResponseDTO(BaseDTO):
    post_id: int = Field(description="Уникальный ID поста")
    user_id: int = Field(description="ID автора поста")
    content: str = Field(description="Текст поста")
    likes_count: int = Field(description="Количество лайков")
    is_liked: bool = Field(description="Поставил ли текущий пользователь лайк")
    comments_count: int = Field(description="Количество комментариев")
    created_at: datetime = Field(description="Дата и время создания поста")
    updated_at: datetime = Field(description="Дата и время последнего изменения поста")


class PostAddDTO(BaseDTO):
    user_id: int
    content: str


class PostFeedResponseDTO(BaseDTO):
    page: int = Field(description="Номер текущей страницы")
    per_page: int = Field(description="Количество постов на странице")
    total_pages: int = Field(description="Общее количество страниц")
    data: list[PostResponseDTO] = Field(description="Список постов")


class SinglePostResponseDTO(BaseDTO):
    data: PostResponseDTO


class PostDeleteResultDTO(BaseDTO):
    comments: int = Field(description="Количество удалённых комментариев")
    likes: int = Field(description="Количество удалённых лайков")
    posts: int = Field(description="Количество удалённых постов")


class PostDeleteResponseDTO(BaseDTO):
    data: PostDeleteResultDTO
