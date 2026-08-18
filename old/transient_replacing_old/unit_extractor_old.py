from dataclasses import dataclass, field
from emtp_utils import *
from com_client import *
from unit_models import *

from typing import List
from pathlib import Path
import openpyxl


@dataclass
class UnitManager:

    pv_units: List[Photovoltaic] = field(default_factory=list)
    wt_units: List[WindTurbine] = field(default_factory=list)
    bess_units: List[Bess] = field(default_factory=list)
    synchronous_units: List[Synchronous] = field(default_factory=list)


class UnitExtractor:

    def __init__(self, emtp_object):
        self.emtp_object = emtp_object

        self.units = UnitManager()

    def _get_devices(self):

        cct = self.emtp_object.currentCircuit
        self.devices = cct.devices

    def _classify_devices(self):

        _devices = self.devices

        for device in _devices:
            # if "WECC PV" in device.getAttribute(
            #     "LibType" or "PV_TEMPLATE" in device.getAttribute("LibType")
            # ) and "PFV_" in device.getAttribute("Name"):

            #     unit = Photovoltaic(object=None, unit_object=device)

            #     self.units.pv_units.append(unit)

            # if (
            #     "WECC W" in device.getAttribute("LibType")
            #     or "WT_TEMPLATE" in device.getAttribute("LibType")
            # ) and "PE_" in device.getAttribute("Name"):
            #     unit = WindTurbine(object=None, unit_object=device)
            #     self.units.wt_units.append(unit)

            # # elif device.getAttribute("LibType") == "Bess":
            # #     self.units.bess_units.append(device)

            # elif "AC-DC converter" in device.getAttribute(
            #     "LibType"
            # ) or "BESS_TEMPLATE" in device.getAttribute("LibType"):
            #     unit = Bess(object=None, unit_object=device)
            #     self.units.bess_units.append(unit)

            if any(
                prefix in device.getAttribute("Name")[:4]
                for prefix in ["HE_", "HP_", "TER_", "GEO_"]
            ):
                parent_device = device
                subcct = parent_device.subCircuit

                syn_unit = None
                lf_unit = None

                for sub_device in subcct.devices:
                    if "synchronous" in sub_device.getAttribute("LibType").lower():
                        syn_unit = sub_device

                    elif "Load-Flow" in sub_device.getAttribute("LibType"):
                        lf_unit = sub_device

                    elif (
                        "TR_" in sub_device.getAttribute("Name")
                        or "p30" in sub_device.getAttribute("Part")
                        or "n30" in sub_device.getAttribute("Part")
                        or "m30" in sub_device.getAttribute("Part")
                    ):
                        trf_unit = sub_device
                    else:
                        if sub_device.getAttribute("Part") == "PQload":
                            load_unit = sub_device
                        else:
                            load_unit = None

                if syn_unit and lf_unit and trf_unit:
                    # print(parent_device.name)
                    unit = Synchronous(
                        object=parent_device,
                        unit_object=syn_unit,
                        loadflow_object=lf_unit,
                        trf_object=trf_unit,
                        load_object=load_unit,
                    )
                    self.units.synchronous_units.append(unit)

                    syn_unit = None
                    lf_unit = None
                    trf_unit = None
                    load_unit = None

                else:
                    print(
                        f"Error: {device.name} does not have a synchronous or load-flow unit."
                    )
                    syn_unit = None
                    lf_unit = None
                    trf_unit = None
                    load_unit = None

    def execute(self):

        self._get_devices()
        self._classify_devices()


if __name__ == "__main__":

    emtp_client = EmtpComClient(attach_existing=True)
    emtp_object = emtp_client.emtp_object

    extractor = UnitExtractor(emtp_object=emtp_object)
    extractor.execute()

    for unit in extractor.units.synchronous_units:

        attr_trf = Utils.get_params_to_dict_by_path(
            emtp_object=emtp_object, device_path=unit.trf_path
        )
        tap_ratio = attr_trf["tap_ratio"]
        dw = attr_trf["DW"]

        attr_unit = Utils.get_params_to_dict_by_path(
            emtp_object=emtp_object, device_path=unit.unit_path
        )

        try:
            attr_lf = Utils.get_params_to_dict_by_path(
                emtp_object=emtp_object, device_path=unit.loadflow_path
            )
        except:
            if not unit.loadflow_object.getAttribute("Script.DevObj"):
                unit.loadflow_object.setAttribute(
                    "Script.DevObj", "load_flow_bus_d.dwj"
                )
            attr_lf = Utils.get_params_to_dict_by_path(
                emtp_object=emtp_object, device_path=unit.loadflow_path
            )

        q_max = float(attr_lf["Q_max"])
        q_min = float(attr_lf["Q_min"])

        s_machine = float(attr_unit["Rating_S"])

        if q_max > s_machine:
            # q_max = 0.44 * s_machine
            print(unit.object.name)
            print(f"max: {q_max}. It's out of range of s:{s_machine}")

        if q_min < (-1) * s_machine:
            print(unit.object.name)
            print(f"min: {q_min}. It's out of range of s:{s_machine}")
