from dataclasses import dataclass
from emtp_utils import *
from com_client import *
from unit_models import *
from unit_extractor import *

from typing import List
import pandas as pd

if __name__ == "__main__":

    emtp_client = EmtpComClient(attach_existing=True)
    emtp_object = emtp_client.emtp_object

    extractor = UnitExtractor(emtp_object=emtp_object)
    extractor.execute()

    pv_units = extractor.units.pv_units
    wf_units = extractor.units.wf_units
    bess_units = extractor.units.bess_units
    syn_units = extractor.units.syn_units

    # for unit in bess_units:
    #     print(unit.name)

    #     unit_attr = Utils.get_params_to_dict_by_path(
    #         emtp_object=emtp_object, device_path=unit.unit_path
    #     )

    #     print(unit_attr)
    #     params = {
    #         "PLLinv_ki": "10",
    #         "PLLinv_kp": "2",
    #         "PCntrl_ki": "25",
    #         "QCntrl_ki": "25",
    #     }

    #     Utils.set_params_from_dict_by_path(
    #         emtp_object=emtp_object, device_path=unit.unit_path, params=params
    #     )

    # for unit in pv_units + wf_units:

    #     unit_attr = Utils.get_params_to_dict_by_path(
    #         emtp_object=emtp_object, device_path=unit.unit_path
    #     )

    #     params = {"UseDataAcquisitionDLL": "1", "UseControlDLL": "1"}

    #     Utils.set_params_from_dict_by_path(
    #         emtp_object=emtp_object, device_path=unit.unit_path, params=params
    #     )

    #     break

    for unit in syn_units:

        # unit_attr = Utils.get_params_to_dict_by_path(
        #     emtp_object=emtp_object, device_path=unit.object
        # )
        # print(unit.object.name)

        print(unit.object.name)
        attr = unit.object.getAttribute("FormData")
        attr = attr.replace("pss_min_s = 50.0;", "pss_min_s = 5000.0;")
        attr = attr.replace("pss_min_s = 5000.0;", "pss_min_s = 50.0;")

        unit.object.setAttribute("FormData", attr)
        # print(unit_attr["Pm_c"])
        # print(unit_attr["Pe_s"])

        # params = {
        #     "InitialValues": "// ------------------------\r\n// Internal default values\r\n// ------------------------\r\n\r\np_min_default = 0.0;\r\n\r\nq_default = 0.0;\r\nv_default = 1.0;\r\n\r\nv_min = 0.95;\r\nv_max = 1.05;\r\n\r\n\r\n// ------------------------\r\n// PSS / GOV defaults\r\n// ------------------------\r\n\r\npss_min_s = 5000.0;"
        # }

        # Utils.set_params_from_dict_by_path(
        #     emtp_object=emtp_object, device_path=unit.object, params=params
        # )

    # params = {"Pe_s": "1"}

    # if unit_attr["Pe_s"] != "1":
    #     Utils.set_params_from_dict_by_path(
    #         emtp_object=emtp_object, device_path=unit.unit_path, params=params
    #     )

    # if unit_attr["Pm_c"] == "1":
    #     print(unit.object.name)
    #     params = {"Pm_c": "0"}
    #     Utils.set_params_from_dict_by_path(
    #         emtp_object=emtp_object, device_path=unit.unit_path, params=params
    # )
    # break

    # Design.save(emtp_object=emtp_object)

    # ///////
    # devices = Design.devices(emtp_object=emtp_object)

    # for device in devices:
    #     if device.getAttribute("Part") == "CEN_Meter_V_f":
    #         old_name = device.name
    #         new_name = old_name.replace("_Medidores", "_MTR")

    #         device.setAttribute("Name", new_name)
