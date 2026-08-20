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

    threshold = 150.0

    for unit in pv_units + wf_units:

        unit_attr = Utils.get_params_to_dict_by_path(
            emtp_object=emtp_object, device_path=unit.unit_path
        )

        s = float(unit_attr["Sgen"]) * float(unit_attr["Ngen"])

        if s > threshold:

            print(unit.object.name)
            print(
                f"Unit {unit.object.name} has Sgen*Ngen = {s} > {threshold}, updating parameters."
            )
            # params = {"Kppll_REGC_A": "15", "Kipll_REGC_A": "158"}
            params = {"Kppll_REGC_A": "38", "Kipll_REGC_A": "987"}
            # params = {"Kppll_REGC_A": "75", "Kipll_REGC_A": "3400"}
            # params = {"Kppll_REGC_A": "151", "Kipll_REGC_A": "15791"}

            Utils.set_params_from_dict_by_path(
                emtp_object=emtp_object, device_path=unit.unit_path, params=params
            )

    Design.save(emtp_object=emtp_object)
