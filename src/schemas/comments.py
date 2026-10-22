from datetime import datetime

from pydantic import Field, field_validator

from src.schemas.base import BaseDTO


class CommentCreateDTO(BaseDTO):
    content: str = Field(
        min_length=1,
        max_length=2200,
        description="Текст комментария. От 1 до 2200 символов. Не может состоять только из пробелов.",
        examples=["Отличный пост! Спасибо за информацию."],
    )

    @field_validator("content")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Комментарий не может быть пустым")
        return value


class CommentDTO(BaseDTO):
    id: int = Field(description="Уникальный ID комментария")
    user_id: int = Field(description="ID автора комментария")
    post_id: int = Field(description="ID поста, к которому относится комментарий")
    content: str = Field(description="Текст комментария")
    created_at: datetime = Field(description="Дата и время создания комментария")
    updated_at: datetime = Field(
        description="Дата и время последнего изменения комментария"
    )


class CommentAddDTO(BaseDTO):
    user_id: int = Field(description="ID автора комментария")
    post_id: int = Field(description="ID поста, к которому добавляется комментарий")
    content: str = Field(
        description="Текст создаваемого комментария",
        examples=["Отличный пост!"],
    )


class CommentResponseDTO(BaseDTO):
    id: int = Field(description="Уникальный ID комментария")
    post_id: int = Field(description="ID поста, к которому относится комментарий")
    user_id: int = Field(description="ID автора комментария")
    content: str = Field(description="Текст комментария")
    created_at: datetime = Field(description="Дата и время создания комментария")
    updated_at: datetime = Field(
        description="Дата и время последнего изменения комментария"
    )


class CommentFeedResponseDTO(BaseDTO):
    page: int = Field(description="Номер текущей страницы")
    per_page: int = Field(description="Количество комментариев на странице")
    total_pages: int = Field(description="Общее количество страниц")
    data: list[CommentResponseDTO] = Field(
        description="Список комментариев на текущей странице"
    )


class SingleCommentResponseDTO(BaseDTO):
    data: CommentResponseDTO = Field(description="Данные одного комментария")


class CommentEditDTO(BaseDTO):
    content: str = Field(
        min_length=1,
        max_length=2200,
        description="Новый текст комментария. От 1 до 2200 символов. Не может состоять только из пробелов.",
        examples=["Обновлённый текст комментария."],
    )

    @field_validator("content")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Комментарий не может быть пустым")
        return value


class CommentDeleteDataDTO(BaseDTO):
    deleted_count: int = Field(description="Количество удалённых комментариев")


class CommentDeleteResponseDTO(BaseDTO):
    data: CommentDeleteDataDTO = Field(
        description="Информация о результате удаления комментария"
    )
