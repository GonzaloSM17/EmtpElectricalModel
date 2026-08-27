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

    for unit in syn_units:

        unit_attr = Utils.get_params_to_dict_by_path(
            emtp_object=emtp_object, device_path=unit.unit_path
        )

        h = unit_attr["Mass_data"]
        h = float(h.split(" ")[1])

        ks2 = round(10 / (2 * h), 2)

        print(unit.object.name)
        print(ks2)

        # Looking for PSS2B
        subcct = unit.object.subCircuit
        for dev in subcct.devices:
            if "Control_" in dev.name:
                # print(dev.name)
                _subcct = dev.subCircuit
                for _dev in _subcct.devices:
                    if "PSS2B" in _dev.name:
                        # print(_dev.name)
                        pss_path = unit.object.name + "/" + dev.name + "/" + _dev.name
                        unit_attr = Utils.get_params_to_dict_by_path(
                            emtp_object=emtp_object,
                            device_path=unit.unit_path,
                        )

                        mass_data = str(unit_attr["Mass_data"]).split()
                        h = float(mass_data[1])

                        if h <= 0:
                            raise ValueError(f"Invalid H for {unit.object.name}: {h}")

                        T7 = 10.0
                        ks2 = round(T7 / (2.0 * h), 2)

                        params = {
                            "TW1": "10",
                            "TW2": "10",
                            "TW3": "10",
                            "TW4": "0",
                            "T6": "0",
                            "T7": "10",
                            "KS1": "3",
                            "KS2": str(ks2),
                            "KS3": "1",
                            "VSI1MAX": "2",
                            "VSI1MIN": "-2",
                            "VSI2MAX": "2",
                            "VSI2MIN": "-2",
                            "T1": "0.15",
                            "T2": "0.025",
                            "T3": "0.15",
                            "T4": "0.02",
                            "T8": "0.5",
                            "T9": "0.1",
                            "T10": "0",
                            "T11": "0.033",
                            "VSTMAX": "0.2",
                            "VSTMIN": "-0.2",
                        }

                        Utils.set_params_from_dict_by_path(
                            emtp_object=emtp_object, device_path=pss_path, params=params
                        )
