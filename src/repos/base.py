# mypy: disable-error-code="no-untyped-def"
from collections.abc import Sequence
from typing import cast

from sqlalchemy import CursorResult, delete, insert, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError, NoResultFound, StatementError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import CommonBaseORM
from src.schemas.base import BaseDTO
from src.utils.exceptions import (
    DBQueryError,
    ObjectAlreadyExistsError,
    ObjectNotFoundError,
)


class BaseRepo:
    """Базовый класс репозитория, который предоставляет
    основные методы работы с базой данных."""

    model: type[CommonBaseORM]
    schema: type[BaseDTO]

    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def get_one(self, *filter, **filter_by) -> BaseDTO:
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        try:
            result = await self.session.execute(query)
            obj = result.scalar_one()
        except NoResultFound as exc:
            raise ObjectNotFoundError from exc
        except StatementError as exc:
            raise DBQueryError from exc
        return self.schema.model_validate(obj)

    async def get_all_filtered(
        self,
        *filter,
        limit: int | None = None,
        offset: int | None = None,
        **filter_by,
    ) -> list[BaseDTO]:
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        try:
            result = await self.session.execute(query)
        except StatementError as exc:
            raise DBQueryError from exc

        return [self.schema.model_validate(obj) for obj in result.scalars().all()]

    async def get_all(self) -> list[BaseDTO]:
        return await self.get_all_filtered()

    async def get_one_or_none(self, *filter, **filter_by) -> BaseDTO | None:
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        try:
            result = await self.session.execute(query)
            obj = result.scalars().one_or_none()
        except StatementError as exc:
            raise DBQueryError from exc

        if obj is None:
            return None
        return self.schema.model_validate(obj)

    async def add_bulk(self, data: Sequence[BaseDTO]) -> list[BaseDTO]:
        add_obj_stmt = (
            insert(self.model)
            .values([item.model_dump() for item in data])
            .returning(self.model)
        )

        try:
            result = await self.session.execute(add_obj_stmt)
        except IntegrityError as exc:
            raise ObjectAlreadyExistsError from exc
        objs = result.scalars().all()
        return [self.schema.model_validate(item) for item in objs]

    async def add(self, data: BaseDTO) -> BaseDTO:
        add_obj_stmt = (
            insert(self.model).values(**data.model_dump()).returning(self.model)
        )
        try:
            result = await self.session.execute(add_obj_stmt)
        except IntegrityError as exc:
            raise ObjectAlreadyExistsError from exc

        obj = result.scalars().one()
        return self.schema.model_validate(obj)

    async def update(self, data: BaseDTO, *filter, **filter_by) -> int:
        data_ = data.model_dump()
        to_update = {k: v for k, v in data_.items() if v is not None}
        if not to_update:
            return 0

        edit_obj_stmt = (
            update(self.model)
            .filter(*filter)
            .filter_by(**filter_by)
            .values(**to_update)
        )

        try:
            result = cast(
                CursorResult,
                await self.session.execute(edit_obj_stmt),
            )
        except IntegrityError as exc:
            raise ObjectAlreadyExistsError from exc
        except DBAPIError as exc:
            raise DBQueryError from exc
        return result.rowcount

    async def delete(self, *filter, **filter_by) -> int:
        delete_obj_stmt = delete(self.model).filter(*filter).filter_by(**filter_by)
        try:
            result = cast(
                CursorResult,
                await self.session.execute(delete_obj_stmt),
            )
        except DBAPIError as exc:
            raise DBQueryError from exc

        return result.rowcount
