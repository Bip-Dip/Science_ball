"""Repository for persisting numeric conditions and facts."""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.fact import Fact, NumericCondition
from app.models.base import Base

class FactsRepository:
    """
    Handles persistence of numeric conditions and the facts that link them to subjects.
    """

    async def create_numeric_condition(
        self,
        session: AsyncSession,
        data: dict
    ) -> NumericCondition:
        """
        Creates a new numeric condition record.
        Expects data compatible with NumericCondition model.
        """
        condition = NumericCondition(**data)
        session.add(condition)
        await session.flush() # Get the generated ID
        return condition

    async def create_fact(
        self,
        session: AsyncSession,
        data: dict
    ) -> Fact:
        """
        Creates a new fact record.
        Expects data compatible with Fact model.
        """
        fact = Fact(**data)
        session.add(fact)
        await session.flush()
        return fact

    async def create_condition_and_fact(
        self,
        session: AsyncSession,
        subject_id: str,
        subject_type: str,
        condition_data: dict,
        predicate: str = "OPERATES_AT_CONDITION"
    ) -> tuple[NumericCondition, Fact]:
        """
        Atomic operation to create both the condition and the fact linking it.
        """
        # 1. Create the NumericCondition
        condition = await self.create_numeric_condition(session, condition_data)

        # 2. Create the Fact linking the subject to this condition
        fact_data = {
            "subject_id": subject_id,
            "subject_type": subject_type,
            "predicate": predicate,
            "object_id": str(condition.id),
            "object_type": "NumericCondition",
            "extraction_method": "regex",
            "confidence": 1.0, # Deterministic regex is high confidence for MVP
        }
        fact = await self.create_fact(session, fact_data)

        return condition, fact
