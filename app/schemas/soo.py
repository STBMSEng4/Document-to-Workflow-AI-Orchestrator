"""Sequence of Operations (SOO) schema for SpecFlow AI.

One SOORecord represents a single extracted control step from a controls
narrative or sequence of operations document — not a full document summary.
Each record captures mode, condition, action, any referenced setpoint, and
whether the step is safety-critical.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from .review import ConfidenceBand, SourceType, confidence_band_for, default_review_reason


SOOMode = Literal[
    "occupied",
    "unoccupied",
    "heating",
    "cooling",
    "deadband",
    "morning_warmup",
    "economizer",
    "emergency",
    "general",
]


class SOORecord(BaseModel):
    equipment_tag: str | None = Field(
        default=None,
        description="Equipment tag this step applies to, e.g. RTU-1. None if not identifiable.",
    )
    equipment_type: str | None = Field(
        default=None,
        description="Canonical equipment type from KB, e.g. RTU, AHU, VAV.",
    )
    mode: SOOMode = Field(
        default="general",
        description="Operating mode this step belongs to.",
    )
    step_index: int = Field(
        ...,
        description="Ordinal position of this step within the extracted sequence.",
    )
    condition: str | None = Field(
        default=None,
        description="Trigger condition clause — the 'when/if' part of the step.",
    )
    action: str = Field(
        ...,
        description="The control action or consequence described in this step.",
    )
    setpoint_name: str | None = Field(
        default=None,
        description="Name of a referenced setpoint, e.g. 'cooling setpoint'.",
    )
    setpoint_value: float | None = Field(
        default=None,
        description="Numeric setpoint value if explicitly stated in the source.",
    )
    setpoint_unit: str | None = Field(
        default=None,
        description="Engineering unit for the setpoint value, e.g. °F, %, in. WC.",
    )
    safety_critical: bool = Field(
        default=False,
        description="True when the step is a life-safety or hard-interlock path.",
    )
    source_text: str = Field(
        ...,
        description="The raw source sentence this record was extracted from.",
    )
    source_reference: str = Field(
        ...,
        description="Section heading or location reference for traceability.",
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Extraction confidence for this step.",
    )
    confidence_band: ConfidenceBand = Field(
        default="medium",
        description="Derived confidence band.",
    )
    source_type: SourceType = Field(
        default="source_extracted",
        description="How this record was produced.",
    )
    review_required: bool = Field(
        default=False,
        description="Whether a human should review this step before use.",
    )
    review_reason: str | None = Field(
        default=None,
        description="Why this step needs review.",
    )
    remarks: str | None = Field(
        default=None,
        description="Additional extraction notes.",
    )

    @field_validator(
        "equipment_tag",
        "equipment_type",
        "condition",
        "action",
        "setpoint_name",
        "setpoint_unit",
        "source_text",
        "source_reference",
        "remarks",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @model_validator(mode="after")
    def _populate_derived(self) -> "SOORecord":
        object.__setattr__(self, "confidence_band", confidence_band_for(self.confidence))
        if not self.review_reason:
            reason = default_review_reason(self.source_type, self.confidence)
            if self.safety_critical and not reason:
                reason = "safety-critical step requires human verification"
            object.__setattr__(self, "review_reason", reason)
        if self.review_reason:
            object.__setattr__(self, "review_required", True)
        return self
