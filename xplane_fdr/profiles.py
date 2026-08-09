"""Immutable stock capture profiles for X-Plane FDR recording."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from types import MappingProxyType

from .models import FDRDataref


@dataclass(frozen=True, slots=True)
class FDRTrajectorySource:
    """One mandatory v4 trajectory field and its X-Plane source."""

    field_name: str
    dataref_path: str
    multiplier: float


@dataclass(frozen=True, slots=True)
class FDRRecordingProfile:
    """An ordered, immutable collection of optional FDR DataRefs."""

    name: str
    description: str
    datarefs: tuple[FDRDataref, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "datarefs", tuple(self.datarefs))


_MANDATORY_TRAJECTORY_SOURCES = (
    FDRTrajectorySource("longitude", "sim/flightmodel/position/longitude", 1.0),
    FDRTrajectorySource("latitude", "sim/flightmodel/position/latitude", 1.0),
    FDRTrajectorySource("altitude_msl_ft", "sim/flightmodel/position/elevation", 1 / 0.3048),
    FDRTrajectorySource("heading_magnetic_deg", "sim/flightmodel/position/mag_psi", 1.0),
    FDRTrajectorySource("pitch_deg", "sim/flightmodel/position/theta", 1.0),
    FDRTrajectorySource("roll_deg", "sim/flightmodel/position/phi", 1.0),
)

_STANDARD_PATHS = (
    "sim/cockpit2/gauges/indicators/airspeed_kts_pilot",
    "sim/cockpit2/gauges/indicators/true_airspeed_kts_pilot",
    "sim/cockpit2/gauges/indicators/ground_speed_kt",
    "sim/cockpit2/gauges/indicators/altitude_ft_pilot",
    "sim/cockpit2/gauges/indicators/vvi_fpm_pilot",
    "sim/cockpit2/temperature/outside_air_temp_degc",
    "sim/flightmodel/forces/g_axil",
    "sim/flightmodel/forces/g_nrml",
    "sim/flightmodel/forces/g_side",
    "sim/joystick/yoke_pitch_ratio",
    "sim/joystick/yoke_roll_ratio",
    "sim/joystick/yoke_heading_ratio",
    "sim/cockpit2/controls/flap_ratio",
    "sim/cockpit2/controls/speedbrake_ratio",
    "sim/cockpit2/controls/gear_handle_down",
    "sim/flightmodel2/gear/deploy_ratio[0]",
    "sim/flightmodel2/gear/deploy_ratio[1]",
    "sim/flightmodel2/gear/deploy_ratio[2]",
)

_ENGINE_BASES = (
    "sim/cockpit2/engine/indicators/fuel_flow_kg_sec",
    "sim/cockpit2/engine/indicators/fuel_pressure_psi",
    "sim/cockpit2/engine/indicators/oil_temperature_deg_C",
    "sim/cockpit2/engine/indicators/oil_pressure_psi",
    "sim/cockpit2/engine/indicators/torque_n_mtr",
    "sim/cockpit2/engine/indicators/prop_speed_rsc",
    "sim/cockpit2/engine/indicators/N1_percent",
    "sim/cockpit2/engine/indicators/N2_percent",
    "sim/cockpit2/engine/indicators/ITT_deg_C",
    "sim/cockpit2/engine/indicators/EGT_deg_C",
)

_SYSTEMS_PATHS = (
    "sim/cockpit2/electrical/battery_voltage_indicated_volts[0]",
    "sim/cockpit2/electrical/battery_voltage_indicated_volts[1]",
    "sim/flightmodel/weight/m_fuel[0]",
    "sim/flightmodel/weight/m_fuel[1]",
    *(f"{base}[{index}]" for index in (0, 1) for base in _ENGINE_BASES),
)

_AVIONICS_PATHS = (
    "sim/cockpit2/gauges/actuators/barometer_setting_in_hg_pilot",
    "sim/cockpit2/autopilot/flight_director_command_bars_pilot",
    "sim/cockpit/autopilot/flight_director_roll",
    "sim/cockpit/autopilot/flight_director_pitch",
    "sim/cockpit/autopilot/autopilot_mode",
    "sim/cockpit2/autopilot/heading_mode",
    "sim/cockpit2/autopilot/altitude_mode",
    "sim/cockpit/autopilot/airspeed",
    "sim/cockpit/autopilot/airspeed_is_mach",
    "sim/cockpit/autopilot/heading_mag",
    "sim/cockpit/autopilot/vertical_velocity",
    "sim/cockpit/autopilot/altitude",
    "sim/cockpit2/radios/actuators/HSI_source_select_pilot",
    "sim/cockpit2/radios/actuators/hsi_obs_deg_mag_pilot",
    "sim/cockpit2/radios/indicators/nav1_hdef_dots_pilot",
    "sim/cockpit2/radios/indicators/nav1_vdef_dots_pilot",
    "sim/cockpit2/radios/actuators/nav1_frequency_hz",
    "sim/cockpit2/radios/actuators/nav2_frequency_hz",
    "sim/cockpit2/radios/actuators/com1_frequency_hz",
    "sim/cockpit2/radios/actuators/com2_frequency_hz",
)


def _datarefs(paths: tuple[str, ...]) -> tuple[FDRDataref, ...]:
    return tuple(FDRDataref(path, 1.0) for path in paths)


def _ordered_union(*groups: tuple[FDRDataref, ...]) -> tuple[FDRDataref, ...]:
    seen: set[str] = set()
    return tuple(dataref for group in groups for dataref in group if not (dataref.path in seen or seen.add(dataref.path)))


_STANDARD_DATAREFS = _datarefs(_STANDARD_PATHS)
_SYSTEMS_DATAREFS = _datarefs(_SYSTEMS_PATHS)
_AVIONICS_DATAREFS = _datarefs(_AVIONICS_PATHS)
_FULL_DATAREFS = _ordered_union(_STANDARD_DATAREFS, _SYSTEMS_DATAREFS, _AVIONICS_DATAREFS)

_PROFILES = (
    FDRRecordingProfile("minimal", "No optional DataRefs.", ()),
    FDRRecordingProfile("standard", "Core flight, control, and gear indicators.", _STANDARD_DATAREFS),
    FDRRecordingProfile("systems", "Electrical, fuel, and engine indicators.", _SYSTEMS_DATAREFS),
    FDRRecordingProfile("avionics", "Autopilot, radio, and navigation indicators.", _AVIONICS_DATAREFS),
    FDRRecordingProfile("full", "The ordered union of standard, systems, and avionics.", _FULL_DATAREFS),
)
_PROFILE_BY_NAME = MappingProxyType({profile.name: profile for profile in _PROFILES})


def mandatory_trajectory_sources() -> tuple[FDRTrajectorySource, ...]:
    """Return the six X-Plane mappings required for every v4 FDR sample."""
    return _MANDATORY_TRAJECTORY_SOURCES


def list_profiles() -> tuple[FDRRecordingProfile, ...]:
    """Return stock profiles in their stable public order."""
    return _PROFILES


def get_profile(name: str) -> FDRRecordingProfile:
    """Return one stock profile by name, rejecting unknown names."""
    return _PROFILE_BY_NAME[name]


def compose_profiles(names: Iterable[str]) -> tuple[FDRDataref, ...]:
    """Combine named stock profiles, retaining each path's first appearance."""
    return _ordered_union(*(get_profile(name).datarefs for name in names))
