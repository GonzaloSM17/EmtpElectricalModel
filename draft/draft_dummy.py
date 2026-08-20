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

    for unit in pv_units + wf_units:

        unit_attr = Utils.get_params_to_dict_by_path(
            emtp_object=emtp_object, device_path=unit.unit_path
        )

        print(unit.object.name)

        params = {"Kppll_REGC_A": "30", "Kipll_REGC_A": "300"}

        Utils.set_params_from_dict_by_path(
            emtp_object=emtp_object, device_path=unit.unit_path, params=params
        )

    for unit in bess_units:

        unit_attr = Utils.get_params_to_dict_by_path(
            emtp_object=emtp_object, device_path=unit.unit_path
        )

        # print(unit_attr)

        params = {"FRT_OFF": "0.2", "OVRT_protection": ""}

        Utils.set_params_from_dict_by_path(
            emtp_object=emtp_object, device_path=unit.unit_path, params=params
        )

    Design.save(emtp_object=emtp_object)
