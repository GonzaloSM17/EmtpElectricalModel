from dataclasses import dataclass
from emtp_utils import *
from com_client import *
from unit_models import *
from unit_extractor import *

from typing import List
import pandas as pd


@dataclass
class UnitInfo:
    name: str
    apparent_power: float
    in_service: int
    p_setpoint: float
    bus_type: str
    q_setpoint: float
    v_setpoint: float = None
    h: float = None
    zone: str = None


@dataclass
class LoadInfo:
    name: str
    in_service: int
    p_load: float
    q_load: float
    zone: str = None


def is_inverter_based_unit(unit) -> bool:
    name = unit.object.name

    return "BESS_" in name or "PFV_" in name or "PE_" in name or "PMGD_" in name


if __name__ == "__main__":

    emtp_client = EmtpComClient(attach_existing=True)
    emtp_object = emtp_client.emtp_object

    # Design.open_design(emtp_object=emtp_object)

    extractor = UnitExtractor(emtp_object=emtp_object)
    extractor.execute()

    units_info_list: List[UnitInfo] = []
    loads_info_list: List[LoadInfo] = []

    all_units = (
        extractor.units.syn_units
        + extractor.units.pv_units
        + extractor.units.wf_units
        + extractor.units.bess_units
        + extractor.units.der_units
    )

    for unit in all_units:

        print(unit.name)

        s = None
        v_setpoint = None
        bus_type = "PQ"

        # -------------------------------------------------------------
        # Inverter-based units
        # -------------------------------------------------------------
        # Avoid Utils.get_params_to_dict_by_path here unless strictly needed.
        # That COM call is usually expensive.

        if is_inverter_based_unit(unit):

            # If later needed, only then uncomment:
            unit_attr = Utils.get_params_to_dict_by_path(
                emtp_object=emtp_object,
                device_path=unit.unit_path,
            )
            s = round(float(unit_attr["Sgen"]) * float(unit_attr["Ngen"]), 2)
            # s = None
            v_setpoint = None
            bus_type = "PQ"
            h = None

        # -------------------------------------------------------------
        # Synchronous / other units
        # -------------------------------------------------------------

        else:
            try:
                unit_attr = Utils.get_params_to_dict_by_path(
                    emtp_object=emtp_object,
                    device_path=unit.unit_path,
                )

                s = round(float(unit_attr["Rating_S"]), 2)
                v_setpoint = unit.get_v()
                bus_type = unit.get_bus_type()

                # print(unit_attr)
                h = unit_attr["Mass_data"]
                h = float(h.split(" ")[1])

            except KeyError:
                s = None
                v_setpoint = None
                bus_type = None

        in_service = unit.get_in_service()
        p_setpoint = unit.get_p()
        q_setpoint = unit.get_q()
        zone = unit.object.getAttribute("Zone")

        unit_info = UnitInfo(
            name=unit.name,
            apparent_power=s,
            in_service=in_service,
            p_setpoint=p_setpoint,
            bus_type=bus_type,
            q_setpoint=q_setpoint,
            v_setpoint=v_setpoint,
            h=h,
            zone=zone,
        )

        units_info_list.append(unit_info)

    for load in extractor.units.load_units:

        print(load.name)

        if load.object:
            p = round(float(load.get_p()), 2)
            q = round(float(load.get_q()), 2)
            zone = load.object.getAttribute("Zone")

        else:
            try:
                load_attr = Utils.get_params_to_dict_by_path(
                    emtp_object=emtp_object,
                    device_path=load.load_path,
                )

                p = load_attr.get("activePower_A", 0)
                q = load_attr.get("reactivePower_A", 0)

                p = round(3 * float(p), 2)
                q = round(3 * float(q), 2)

                zone = load.load_object.getAttribute("Zone")

            except:
                p = None
                q = None

        in_service = load.get_in_service()

        load_info = LoadInfo(
            name=load.name, in_service=in_service, p_load=p, q_load=q, zone=zone
        )

        loads_info_list.append(load_info)

    # ------------------------
    # Export sheets
    # ------------------------

    sheets = {
        "Unit Manager": units_info_list,
        "Load Manager": loads_info_list,
    }

    with pd.ExcelWriter("EMTP Assets_v0.19.xlsx") as writer:

        for sheet_name, asset_list in sheets.items():

            if not asset_list:
                continue

            df = pd.DataFrame(asset_list)

            if sheet_name == "Load Manager":
                df = df.rename(
                    columns={
                        "name": "emtp_name",
                        "in_service": "In Service",
                        "p_load": "P Load [MW]",
                        "q_load": "Q Load [MVAr]",
                        "zone": "Zone",
                    }
                )

            else:
                df = df.rename(
                    columns={
                        "name": "emtp_name",
                        "apparent_power": "App. Power [MVA]",
                        "h": "Inertia [s]",
                        "zone": "Zone",
                        "in_service": "In Service",
                        "p_setpoint": "P Setpoint [MW]",
                        "bus_type": "Bus Type",
                        "q_setpoint": "Q Setpoint [MVAr]",
                        "v_setpoint": "V Setpoint [pu]",
                    }
                )

            df = df.sort_values("emtp_name").reset_index(drop=True)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
