"""Equipment schema models for SpecFlow AI.

The goal is to support real HVAC/BMS schedule extraction with a stable core
record plus nested attribute buckets for equipment-specific data.

Field coverage is grounded in common HVAC schedule / submittal / controls data
seen across AHRI-rated unitary equipment, ERV/HRV performance data, ASHRAE
terminology, and typical manufacturer schedules for AHUs, FCUs, VAVs, and
VRF/VRV systems.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator, model_validator

from .review import ConfidenceBand, SourceType, confidence_band_for, default_review_reason


class ElectricalAttributes(BaseModel):
    voltage: str | None = None
    phase: str | None = None
    frequency_hz: float | None = None
    minimum_circuit_ampacity_amps: float | None = None
    maximum_overcurrent_protection_amps: float | None = None
    full_load_amps: float | None = None
    fan_motor_hp: float | None = None
    fan_motor_kw: float | None = None
    compressor_motor_hp: float | None = None
    compressor_motor_kw: float | None = None
    power_kw: float | None = None
    power_source: str | None = None
    disconnect_type: str | None = None
    starter_type: str | None = None


class AirflowAttributes(BaseModel):
    airflow_cfm: float | None = None
    minimum_airflow_cfm: float | None = None
    maximum_airflow_cfm: float | None = None
    outdoor_air_cfm: float | None = None
    return_air_cfm: float | None = None
    exhaust_air_cfm: float | None = None
    relief_air_cfm: float | None = None
    external_static_in_wg: float | None = None
    total_static_in_wg: float | None = None
    supply_fan_rpm: float | None = None
    fan_type: str | None = None
    fan_quantity: int | None = None
    fan_drive_type: str | None = None
    fan_arrangement: str | None = None
    filter_type: str | None = None
    filter_merv: str | None = None
    filter_face_size: str | None = None
    filter_quantity: int | None = None


class CoolingAttributes(BaseModel):
    cooling_type: str | None = None
    cooling_capacity_tons: float | None = None
    cooling_capacity_btuh: float | None = None
    sensible_capacity_btuh: float | None = None
    latent_capacity_btuh: float | None = None
    sensible_heat_ratio: float | None = None
    eer: float | None = None
    ieer: float | None = None
    seer: float | None = None
    cop: float | None = None
    refrigerant: str | None = None
    compressor_quantity: int | None = None
    compressor_stages: int | None = None
    compressor_type: str | None = None
    condenser_type: str | None = None
    dx_coil_rows: int | None = None
    cooling_coil_face_area_sqft: float | None = None
    cooling_coil_type: str | None = None
    entering_air_db_f: float | None = None
    entering_air_wb_f: float | None = None
    leaving_air_db_f: float | None = None
    leaving_air_wb_f: float | None = None


class HeatingAttributes(BaseModel):
    heating_type: str | None = None
    heating_capacity_btuh: float | None = None
    heating_capacity_mbh: float | None = None
    heating_input_btuh: float | None = None
    heating_output_btuh: float | None = None
    thermal_efficiency_pct: float | None = None
    heating_stages: int | None = None
    electric_heat_kw: float | None = None
    furnace_input_btuh: float | None = None
    steam_pressure_psig: float | None = None
    fuel_type: str | None = None
    preheat_coil_type: str | None = None
    reheat_type: str | None = None
    reheat_capacity_btuh: float | None = None


class HydronicAttributes(BaseModel):
    chilled_water_gpm: float | None = None
    heating_hot_water_gpm: float | None = None
    condenser_water_gpm: float | None = None
    entering_chilled_water_temp_f: float | None = None
    leaving_chilled_water_temp_f: float | None = None
    entering_hot_water_temp_f: float | None = None
    leaving_hot_water_temp_f: float | None = None
    entering_condenser_water_temp_f: float | None = None
    leaving_condenser_water_temp_f: float | None = None
    fluid_type: str | None = None
    pipe_size: str | None = None
    pressure_drop_ft_head: float | None = None
    pressure_drop_psi: float | None = None
    valve_type: str | None = None
    valve_size: str | None = None
    valve_cv: float | None = None
    valve_closeoff_pressure: str | None = None
    actuator_type: str | None = None


class VentilationAttributes(BaseModel):
    heat_recovery_type: str | None = None
    sensible_effectiveness_pct: float | None = None
    latent_effectiveness_pct: float | None = None
    supply_air_pressure_drop_in_h2o: float | None = None
    exhaust_air_pressure_drop_in_h2o: float | None = None
    exhaust_air_transfer_ratio_pct: float | None = None
    outdoor_air_correction_factor: float | None = None
    frost_control_type: str | None = None
    purge_section_present: bool | None = None
    wheel_speed_rpm: float | None = None


class DamperEconomizerAttributes(BaseModel):
    damper_type: str | None = None
    damper_size: str | None = None
    damper_leakage_class: str | None = None
    blade_type: str | None = None
    economizer_type: str | None = None
    actuator_fail_position: str | None = None
    low_leakage_damper: bool | None = None


class ControlsAttributes(BaseModel):
    controller_manufacturer: str | None = None
    controller_model: str | None = None
    network_type: str | None = None
    bacnet_instance: int | None = None
    mstp_mac: int | None = None
    ip_addressing: str | None = None
    points_count_di: int | None = None
    points_count_do: int | None = None
    points_count_ai: int | None = None
    points_count_ao: int | None = None
    sequence_reference: str | None = None
    safeties: list[str] = Field(default_factory=list)


class MechanicalAttributes(BaseModel):
    dimensions: str | None = None
    cabinet_size: str | None = None
    weight_lb: float | None = None
    sound_level_db: float | None = None
    installation_orientation: str | None = None
    mounting_type: str | None = None
    inlet_size: str | None = None
    outlet_size: str | None = None
    coil_type: str | None = None
    access_section: str | None = None
    drain_pan_type: str | None = None


class VrfAttributes(BaseModel):
    system_type: str | None = None
    outdoor_unit_count: int | None = None
    indoor_unit_count: int | None = None
    connected_capacity_ratio_pct: float | None = None
    branch_selector_required: bool | None = None
    total_piping_length_ft: float | None = None
    longest_run_length_ft: float | None = None
    vertical_separation_ft: float | None = None
    heat_recovery_configuration: str | None = None
    indoor_unit_types: list[str] = Field(default_factory=list)


class EquipmentAttributes(BaseModel):
    electrical: ElectricalAttributes = Field(default_factory=ElectricalAttributes)
    airflow: AirflowAttributes = Field(default_factory=AirflowAttributes)
    cooling: CoolingAttributes = Field(default_factory=CoolingAttributes)
    heating: HeatingAttributes = Field(default_factory=HeatingAttributes)
    hydronic: HydronicAttributes = Field(default_factory=HydronicAttributes)
    ventilation: VentilationAttributes = Field(default_factory=VentilationAttributes)
    dampers_and_economizer: DamperEconomizerAttributes = Field(default_factory=DamperEconomizerAttributes)
    controls: ControlsAttributes = Field(default_factory=ControlsAttributes)
    mechanical: MechanicalAttributes = Field(default_factory=MechanicalAttributes)
    vrf: VrfAttributes = Field(default_factory=VrfAttributes)


class EquipmentRecord(BaseModel):
    equipment_tag: str = Field(..., description="Document-facing equipment identifier, e.g. RTU-1.")
    equipment_type: str = Field(..., description="Canonical equipment class from the KB master list.")
    equipment_name: str | None = Field(default=None, description="Human-readable equipment name.")
    system: str | None = Field(default=None, description="Top-level system, e.g. HVAC, CHW, steam.")
    subsystem: str | None = Field(default=None, description="Subsystem such as ventilation, cooling, heat recovery.")
    parent_equipment_tag: str | None = Field(default=None, description="Parent / serving equipment tag where relationships exist.")
    location: str | None = Field(default=None, description="Physical location or room.")
    served_area: str | None = Field(default=None, description="Served space/zone/floor/tenant.")
    manufacturer: str | None = Field(default=None, description="OEM or equipment manufacturer.")
    model: str | None = Field(default=None, description="Manufacturer model number.")
    serial_number: str | None = Field(default=None, description="Serial number if available.")
    quantity: int | None = Field(default=None, description="Count of identical units represented.")
    service: str | None = Field(default=None, description="Service description, e.g. supply air, chilled water, relief.")
    protocol: str | None = Field(default=None, description="Primary BAS/controls protocol if specified.")
    remarks: str | None = Field(default=None, description="Freeform source notes worth preserving.")
    source_reference: str = Field(..., description="Page/sheet/section reference for traceability.")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Extraction confidence.")
    confidence_band: ConfidenceBand = Field(default="medium", description="Derived confidence band for row review.")
    source_type: SourceType = Field(default="source_extracted", description="How this record was produced.")
    review_required: bool = Field(default=False, description="Whether a human should review this record before use.")
    review_reason: str | None = Field(default=None, description="Why the row needs review.")
    attributes: EquipmentAttributes = Field(default_factory=EquipmentAttributes)

    @field_validator(
        "equipment_tag",
        "equipment_type",
        "equipment_name",
        "system",
        "subsystem",
        "parent_equipment_tag",
        "location",
        "served_area",
        "manufacturer",
        "model",
        "serial_number",
        "service",
        "protocol",
        "remarks",
        "source_reference",
        mode="before",
    )
    @classmethod
    def _strip_strings(cls, value):
        if isinstance(value, str):
            return value.strip()
        return value

    @model_validator(mode="after")
    def _apply_review_defaults(self) -> "EquipmentRecord":
        object.__setattr__(self, "confidence_band", confidence_band_for(self.confidence))
        if not self.review_reason:
            object.__setattr__(self, "review_reason", default_review_reason(self.source_type, self.confidence))
        if self.review_reason:
            object.__setattr__(self, "review_required", True)
        return self
