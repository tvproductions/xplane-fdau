"""Public behavior tests for the stock recording profiles."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
import unittest

import xplane_fdau.formats.xplane_fdr.profiles as profile_module
from xplane_fdau.formats.xplane_fdr import (
    compose_profiles,
    get_profile,
    list_profiles,
    mandatory_trajectory_sources,
)


STANDARD_PATHS = (
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

ENGINE_BASES = (
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

SYSTEMS_PATHS = (
    "sim/cockpit2/electrical/battery_voltage_indicated_volts[0]",
    "sim/cockpit2/electrical/battery_voltage_indicated_volts[1]",
    "sim/flightmodel/weight/m_fuel[0]",
    "sim/flightmodel/weight/m_fuel[1]",
    *(f"{base}[{index}]" for index in (0, 1) for base in ENGINE_BASES),
)

AVIONICS_PATHS = (
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


class FDRProfilesTests(unittest.TestCase):
    """Stock profiles expose an ordered, immutable public contract."""

    def test_stock_profiles_have_exact_ordered_membership_and_unit_scale(self) -> None:
        """Changing a stock path, order, or scale must break callers' recordings."""
        expected = {
            "minimal": (),
            "standard": STANDARD_PATHS,
            "systems": SYSTEMS_PATHS,
            "avionics": AVIONICS_PATHS,
            "full": STANDARD_PATHS + SYSTEMS_PATHS + AVIONICS_PATHS,
        }

        self.assertEqual(("minimal", "standard", "systems", "avionics", "full"), tuple(profile.name for profile in list_profiles()))
        for name, paths in expected.items():
            profile = get_profile(name)
            self.assertEqual(paths, tuple(dataref.path for dataref in profile.datarefs))
            self.assertEqual((1.0,) * len(paths), tuple(dataref.scale for dataref in profile.datarefs))
            self.assertEqual(len(paths), len(set(paths)))

    def test_trajectory_sources_have_exact_v4_spine_mappings(self) -> None:
        """Changing a mandatory mapping would produce invalid v4 samples."""
        self.assertEqual(
            (
                ("longitude", "sim/flightmodel/position/longitude", 1.0),
                ("latitude", "sim/flightmodel/position/latitude", 1.0),
                ("altitude_msl_ft", "sim/flightmodel/position/elevation", 1 / 0.3048),
                ("heading_magnetic_deg", "sim/flightmodel/position/mag_psi", 1.0),
                ("pitch_deg", "sim/flightmodel/position/theta", 1.0),
                ("roll_deg", "sim/flightmodel/position/phi", 1.0),
            ),
            tuple((source.field_name, source.dataref_path, source.multiplier) for source in mandatory_trajectory_sources()),
        )

    def test_profile_values_and_returned_sequences_are_immutable(self) -> None:
        """Mutating a returned profile must be impossible or leave future reads unchanged."""
        profile = get_profile("standard")
        self.assertIsInstance(profile.datarefs, tuple)
        with self.assertRaises(FrozenInstanceError):
            setattr(profile, "name", "changed")
        with self.assertRaises(AttributeError):
            getattr(profile.datarefs, "append")(profile.datarefs[0])
        with self.assertRaises(FrozenInstanceError):
            setattr(profile.datarefs[0], "path", "changed")
        self.assertEqual(STANDARD_PATHS, tuple(dataref.path for dataref in get_profile("standard").datarefs))
        self.assertIsInstance(profile_module._STANDARD_DATAREFS, tuple)
        with self.assertRaises(AttributeError):
            getattr(profile_module._STANDARD_DATAREFS, "append")(profile.datarefs[0])
        self.assertEqual(STANDARD_PATHS, tuple(dataref.path for dataref in profile_module._STANDARD_DATAREFS))
        with self.assertRaises(FrozenInstanceError):
            setattr(mandatory_trajectory_sources()[0], "field_name", "changed")

    def test_composition_preserves_first_appearance_and_rejects_unknown_profiles(self) -> None:
        """Changing composition order or accepting misspellings would corrupt capture schemas."""
        self.assertEqual((), get_profile("minimal").datarefs)
        self.assertEqual(get_profile("full").datarefs, compose_profiles(("standard", "systems", "avionics")))
        self.assertEqual(get_profile("standard").datarefs, compose_profiles(("standard", "standard")))
        with self.assertRaises(KeyError):
            get_profile("unknown")
        with self.assertRaises(KeyError):
            compose_profiles(("standard", "unknown"))


if __name__ == "__main__":
    unittest.main()
