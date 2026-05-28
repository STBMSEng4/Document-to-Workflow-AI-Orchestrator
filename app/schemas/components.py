"""Linked HVAC/BMS component schema models for SpecFlow AI.

These records capture common controls-facing component data that should remain
separate from the core equipment record once extraction is implemented:
valves, dampers, actuators, and sensors. The field sets are designed around
typical HVAC schedules, control submittals, and BAS integration data.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from .review import ConfidenceBand, SourceType, confidence_band_for, default_review_reason


ParentComponentType = Literal["equipment", "valve", "damper", "actuator", "sensor"]


class _LinkedRecord(BaseModel):
    equipment_tag: str | None = Field(default=None, description="Associated parent equipment tag, e.g. AHU-1.")
    equipment_type: str | None = Field(default=None, description="Associated parent equipment type from the KB.")
    system: str | None = Field(default=None, description="Top-level system such as HVAC, CHW, HHW, steam.")
    service: str | None = Field(default=None, description="Service such as cooling, heating, OA, RA, SA, EA.")
    location: str | None = Field(default=None, description="Room, floor, or physical location.")
    source_reference: str = Field(..., description="Page/sheet/section reference for traceability.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence.")
    confidence_band: ConfidenceBand = Field(default="medium", description="Derived confidence band for row review.")
    source_type: SourceType = Field(default="source_extracted", description="How this record was produced.")
    review_required: bool = Field(default=False, description="Whether a human should review this record before use.")
    review_reason: str | None = Field(default=None, description="Why the row needs review.")
    remarks: str | None = Field(default=None, description="Freeform notes preserved from the source.")

    @field_validator(
        "equipment_tag",
        "equipment_type",
        "system",
        "service",
        "location",
        "source_reference",
        "remarks",
        mode="before",
    )
    @classmethod
    def _strip_shared_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @model_validator(mode="after")
    def _apply_review_defaults(self):
        object.__setattr__(self, "confidence_band", confidence_band_for(self.confidence))
        if not self.review_reason:
            object.__setattr__(self, "review_reason", default_review_reason(self.source_type, self.confidence))
        if self.review_reason:
            object.__setattr__(self, "review_required", True)
        return self


class ValveRecord(_LinkedRecord):
    valve_tag: str = Field(..., description="Document-facing valve identifier, e.g. V-1 or CHWV-1.")
    valve_type: str | None = Field(default=None, description="2-way, 3-way, butterfly, globe, PICV, etc.")
    control_function: str | None = Field(default=None, description="Modulating, isolation, diverting, balancing, etc.")
    body_material: str | None = Field(default=None, description="Bronze, brass, cast iron, stainless, etc.")
    size: str | None = Field(default=None, description="Valve nominal size, e.g. 2 in.")
    line_size: str | None = Field(default=None, description="Associated pipe size if explicitly different from valve size.")
    end_connection: str | None = Field(default=None, description="Threaded, flanged, grooved, sweat, press, etc.")
    trim_type: str | None = Field(default=None, description="Equal percentage, linear, quick opening, etc.")
    flow_gpm: float | None = Field(default=None, description="Rated or scheduled flow.")
    pressure_drop_psi: float | None = Field(default=None, description="Rated pressure drop in psi.")
    pressure_drop_ft_head: float | None = Field(default=None, description="Rated pressure drop in feet of head.")
    flow_coefficient_cv: float | None = Field(default=None, description="Published valve Cv.")
    closeoff_pressure: str | None = Field(default=None, description="Closeoff pressure or differential pressure rating.")
    body_rating: str | None = Field(default=None, description="Pressure class / body rating.")
    leakage_class: str | None = Field(default=None, description="ANSI/FCI leakage class where applicable.")
    fail_position: str | None = Field(default=None, description="Fail open, fail closed, fail last, etc.")
    actuator_tag: str | None = Field(default=None, description="Linked actuator tag when listed separately.")
    actuator_type: str | None = Field(default=None, description="Electric, spring return, floating, analog, etc.")

    @field_validator(
        "valve_tag",
        "valve_type",
        "control_function",
        "body_material",
        "size",
        "line_size",
        "end_connection",
        "trim_type",
        "closeoff_pressure",
        "body_rating",
        "leakage_class",
        "fail_position",
        "actuator_tag",
        "actuator_type",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class DamperRecord(_LinkedRecord):
    damper_tag: str = Field(..., description="Document-facing damper identifier.")
    damper_type: str | None = Field(default=None, description="OA, RA, EA, smoke, fire, control, backdraft, etc.")
    application: str | None = Field(default=None, description="Economizer, isolation, bypass, relief, mixed air, etc.")
    size: str | None = Field(default=None, description="Nominal damper size, e.g. 24x18.")
    width_in: float | None = Field(default=None, description="Nominal width in inches when separable.")
    height_in: float | None = Field(default=None, description="Nominal height in inches when separable.")
    area_sqft: float | None = Field(default=None, description="Face area when available.")
    blade_type: str | None = Field(default=None, description="Parallel blade, opposed blade, airfoil, etc.")
    frame_type: str | None = Field(default=None, description="Frame style or sleeve style.")
    leakage_class: str | None = Field(default=None, description="AMCA leakage class if specified.")
    pressure_class_in_wg: float | None = Field(default=None, description="Pressure class in inches water gauge.")
    airflow_cfm: float | None = Field(default=None, description="Scheduled airflow through the damper.")
    face_velocity_fpm: float | None = Field(default=None, description="Damper face velocity.")
    smoke_fire_rating: str | None = Field(default=None, description="UL/Smoke/Fire classification where listed.")
    low_leakage: bool | None = Field(default=None, description="True when explicitly called out as low leakage.")
    fail_position: str | None = Field(default=None, description="Fail open, fail closed, fail last, etc.")
    actuator_tag: str | None = Field(default=None, description="Linked actuator tag when listed separately.")
    actuator_torque_in_lb: float | None = Field(default=None, description="Required actuator torque when listed.")

    @field_validator(
        "damper_tag",
        "damper_type",
        "application",
        "size",
        "blade_type",
        "frame_type",
        "leakage_class",
        "smoke_fire_rating",
        "fail_position",
        "actuator_tag",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class ActuatorRecord(_LinkedRecord):
    actuator_tag: str = Field(..., description="Document-facing actuator identifier.")
    parent_component_type: ParentComponentType = Field(
        default="equipment",
        description="Which linked record this actuator primarily belongs to.",
    )
    parent_component_tag: str | None = Field(default=None, description="Referenced valve/damper/equipment tag.")
    manufacturer: str | None = Field(default=None, description="Actuator manufacturer.")
    model: str | None = Field(default=None, description="Actuator model number.")
    actuator_type: str | None = Field(default=None, description="Electric, pneumatic, spring return, modulating, etc.")
    power_supply: str | None = Field(default=None, description="24 VAC, 120 VAC, 24 VDC, etc.")
    control_signal: str | None = Field(default=None, description="2-position, floating, 0-10 VDC, 4-20 mA, etc.")
    fail_position: str | None = Field(default=None, description="Fail open, fail closed, fail last, etc.")
    spring_return: bool | None = Field(default=None, description="Whether spring return is present.")
    torque_in_lb: float | None = Field(default=None, description="Rated torque when listed.")
    run_time_sec: float | None = Field(default=None, description="Run time in seconds.")
    stroke_time_sec: float | None = Field(default=None, description="Stroke time in seconds.")
    closeoff_pressure: str | None = Field(default=None, description="Closeoff rating when actuator is valve-associated.")
    mounting: str | None = Field(default=None, description="Direct-coupled, bracketed, shaft mount, etc.")
    auxiliary_switches_qty: int | None = Field(default=None, description="Auxiliary switch count.")
    ingress_rating: str | None = Field(default=None, description="NEMA/IP/environmental protection rating.")

    @field_validator(
        "actuator_tag",
        "parent_component_tag",
        "manufacturer",
        "model",
        "actuator_type",
        "power_supply",
        "control_signal",
        "fail_position",
        "closeoff_pressure",
        "mounting",
        "ingress_rating",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value


class SensorRecord(_LinkedRecord):
    sensor_tag: str = Field(..., description="Document-facing sensor identifier.")
    sensor_type: str | None = Field(default=None, description="Temperature, humidity, pressure, flow, CO2, smoke, etc.")
    measured_variable: str | None = Field(default=None, description="What the sensor measures.")
    engineering_unit: str | None = Field(default=None, description="F, %RH, in.w.g., psi, ppm, etc.")
    sensing_range: str | None = Field(default=None, description="Published range or scheduled range.")
    output_signal: str | None = Field(default=None, description="10k thermistor, 4-20 mA, 0-10 VDC, dry contact, etc.")
    accuracy: str | None = Field(default=None, description="Published accuracy where specified.")
    installation_location: str | None = Field(default=None, description="Duct, room, pipe well, mixed air plenum, etc.")
    probe_length_in: float | None = Field(default=None, description="Probe length for insertion sensors.")
    well_required: bool | None = Field(default=None, description="Whether a thermowell or well is called for.")
    averaging: bool | None = Field(default=None, description="True when averaging sensor is explicitly called out.")
    differential: bool | None = Field(default=None, description="True when sensor is differential pressure/temperature/etc.")
    network_address: str | None = Field(default=None, description="Address or instance when a networked sensor lists one.")

    @field_validator(
        "sensor_tag",
        "sensor_type",
        "measured_variable",
        "engineering_unit",
        "sensing_range",
        "output_signal",
        "accuracy",
        "installation_location",
        "network_address",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value
