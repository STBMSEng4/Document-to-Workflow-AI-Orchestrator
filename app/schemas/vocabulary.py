"""Vocabulary schema models for SpecFlow AI.

This layer gives the knowledge-base parser a typed contract without forcing the
rest of the scoring pipeline to change all at once.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class VocabularyTerm(BaseModel):
    """Normalized knowledge-base term definition.

    Core fields map directly to the current Markdown table structure while the
    optional fields provide room for future schema-aware extraction work.
    """

    term: str = Field(..., description="Primary KB term as written in the vocabulary.")
    normalized_term: str = Field(
        default="",
        description="Canonical normalized form used for scoring/grouping.",
    )
    category: str = Field(..., description="Vocabulary group, e.g. equipment_type or protocol.")
    weight: float = Field(..., ge=0.0, le=1.0, description="Base KB weight from 0.00 to 1.00.")
    scope: str = Field(default="all", description="Deployment or domain scope, e.g. all, alerton, climatec.")
    aliases: list[str] = Field(default_factory=list, description="Synonyms and alternate spellings.")
    notes: str = Field(default="", description="Freeform notes about usage, meaning, or limitations.")
    is_skip: bool = Field(default=False, description="True if the term should suppress workflow output.")

    # Optional future-facing fields for structured extraction
    equipment_type: str | None = Field(default=None, description="Related equipment class if this term maps to one.")
    point_type: str | None = Field(default=None, description="Related point class if the term is point-like.")
    signal_type: str | None = Field(default=None, description="Analog/binary/network signal hint.")
    engineering_unit: str | None = Field(default=None, description="Unit hint when applicable.")
    source_notes: str | None = Field(default=None, description="Additional structured notes for downstream extractors.")

    @field_validator("term", "category", "scope", mode="before")
    @classmethod
    def _strip_required_text(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("normalized_term", mode="before")
    @classmethod
    def _strip_normalized_term(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("aliases", mode="before")
    @classmethod
    def _normalize_aliases(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            raw = value.split(",")
        else:
            raw = list(value)

        cleaned: list[str] = []
        for alias in raw:
            alias_text = str(alias).strip()
            if alias_text and alias_text not in cleaned:
                cleaned.append(alias_text)
        return cleaned

    @model_validator(mode="after")
    def _populate_defaults(self) -> "VocabularyTerm":
        if not self.normalized_term:
            object.__setattr__(self, "normalized_term", self.term)
        return self

    @classmethod
    def from_kb_row(
        cls,
        *,
        term: str,
        weight: float,
        category: str,
        scope: str = "all",
        variants: str = "",
        notes: str = "",
        is_skip: bool = False,
    ) -> "VocabularyTerm":
        """Create a model from the current Markdown KB row shape."""
        return cls(
            term=term,
            normalized_term=term,
            category=category,
            weight=weight,
            scope=scope,
            aliases=variants,
            notes=notes,
            is_skip=is_skip,
        )
