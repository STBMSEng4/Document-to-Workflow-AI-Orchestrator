"""Point schema models for SpecFlow AI.

These records are designed to bridge document extraction and controls delivery:
they preserve human-readable point names while supporting common BAS naming
patterns, I/O types, BACnet-style objects, and review flags used in points
lists, I/O schedules, and submittals.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from .review import ConfidenceBand, SourceType, confidence_band_for, default_review_reason


PointType = Literal[
    "AI",
    "AO",
    "DI",
    "DO",
    "AV",
    "BV",
    "BI",
    "BO",
    "MSI",
    "MSO",
    "MSV",
    "SP",
    "Status",
    "Alarm",
    "Calc",
    "Network",
]

SignalType = Literal["analog", "binary", "multistate", "network", "calculated", "text"]

PointRole = Literal[
    "sensor",
    "command",
    "status",
    "setpoint",
    "alarm",
    "interlock",
    "calculated",
    "network",
]

ObjectType = Literal[
    "analogInput",
    "analogOutput",
    "analogValue",
    "binaryInput",
    "binaryOutput",
    "binaryValue",
    "multiStateInput",
    "multiStateOutput",
    "multiStateValue",
    "device",
    "notificationClass",
    "trendLog",
]


class PointRecord(BaseModel):
    equipment_tag: str | None = Field(default=None, description="Parent equipment tag, e.g. AHU-1.")
    equipment_type: str | None = Field(default=None, description="Parent equipment type from the KB.")
    controller_tag: str | None = Field(default=None, description="Associated controller/panel/device reference.")
    controller_model: str | None = Field(default=None, description="Controller make/model if explicitly stated.")
    system: str | None = Field(default=None, description="Top-level system such as HVAC, CHW, steam, power.")
    location: str | None = Field(default=None, description="Room, floor, or physical location.")
    point_name: str = Field(..., description="Human-readable point name from source or normalized schedule.")
    normalized_point_name: str = Field(
        default="",
        description="Canonical normalized point name for grouping and dedupe.",
    )
    point_code: str | None = Field(
        default=None,
        description="Short engineering abbreviation, e.g. SAT, SF-STS, CHWV-POS.",
    )
    point_type: PointType = Field(..., description="I/O / object shorthand such as AI, AO, DI, DO, AV, BV.")
    signal_type: SignalType = Field(..., description="Signal family: analog, binary, multistate, network, etc.")
    point_role: PointRole = Field(..., description="Functional role: sensor, command, status, setpoint, etc.")
    object_type: ObjectType | None = Field(
        default=None,
        description="BACnet-style object type when the point maps directly to one.",
    )
    object_instance: int | None = Field(default=None, description="BACnet object instance when listed.")
    protocol: str | None = Field(default=None, description="BACnet/IP, BACnet MS/TP, Modbus, Lon, OPC UA, etc.")
    network_address: str | None = Field(default=None, description="MAC, IP, register, or other network address.")
    engineering_unit: str | None = Field(default=None, description="Engineering unit such as °F, %, CFM, psi.")
    display_precision: int | None = Field(default=None, description="Preferred display precision if specified.")
    range_min: float | None = Field(default=None, description="Published or scheduled low end of scale.")
    range_max: float | None = Field(default=None, description="Published or scheduled high end of scale.")
    default_value: str | None = Field(default=None, description="Default state/setpoint/value when explicitly listed.")
    writable: bool | None = Field(default=None, description="Whether the point is expected to be writable.")
    commandable: bool | None = Field(default=None, description="Whether the point should accept BMS commands.")
    alarmed: bool | None = Field(default=None, description="Whether this point is expected to generate alarms.")
    trended: bool | None = Field(default=None, description="Whether this point is expected to be trended.")
    required: bool | None = Field(default=None, description="Whether the source implies this point is required.")
    safety_interlock: bool | None = Field(default=None, description="True if this point participates in a safety path.")
    description: str | None = Field(default=None, description="Freeform description or sequence note.")
    source_reference: str = Field(..., description="Page/sheet/section reference for traceability.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence.")
    confidence_band: ConfidenceBand = Field(default="medium", description="Derived confidence band for row review.")
    source_type: SourceType = Field(default="source_extracted", description="How this record was produced.")
    review_required: bool = Field(default=False, description="Whether a human should review this record before use.")
    review_reason: str | None = Field(default=None, description="Why the row needs review.")
    remarks: str | None = Field(default=None, description="Additional source notes or review comments.")

    @field_validator(
        "equipment_tag",
        "equipment_type",
        "controller_tag",
        "controller_model",
        "system",
        "location",
        "point_name",
        "normalized_point_name",
        "point_code",
        "protocol",
        "network_address",
        "engineering_unit",
        "default_value",
        "description",
        "source_reference",
        "remarks",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("point_code", mode="after")
    @classmethod
    def _normalize_point_code(cls, value: str | None) -> str | None:
        if value:
            return value.upper()
        return value

    @model_validator(mode="after")
    def _populate_defaults(self) -> "PointRecord":
        if not self.normalized_point_name:
            object.__setattr__(self, "normalized_point_name", self.point_name)
        object.__setattr__(self, "confidence_band", confidence_band_for(self.confidence))
        if not self.review_reason:
            object.__setattr__(self, "review_reason", default_review_reason(self.source_type, self.confidence))
        if self.review_reason:
            object.__setattr__(self, "review_required", True)
        return self
