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

    for load in extractor.units.load_units:

        print(load.name)

        try:
            if load.object:
                attr_load = Utils.get_params_to_dict_by_path(
                    emtp_object=emtp_object,
                    device_path=load.object.getAttribute("Name"),
                )
                print(attr_load)
                new_attr = {"GlobalData": "1", "UpdateGlobalData": "1"}
                Utils.set_params_from_dict_by_path(
                    emtp_object=emtp_object,
                    device_path=load.object.getAttribute("Name"),
                    params=new_attr,
                )

            else:
                continue

        except Exception as e:
            print(f"Error setting attribute for {load.name}: {e}")
