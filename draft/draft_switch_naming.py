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

    cct = emtp_object.currentDesign
    devices = cct.devices

    numeric = 1
    for device in devices:
        if "CP line" in device.getAttribute("LibType"):
            # name = "SW" + str(numeric)
            device.setAttributeVis("Value1", False)
            print(f"Name: {device.name}")
            # device.setAttribute("Name", name)
            numeric += 1
            # print(f"New name: {device.name}")
            # if numeric > 5:
            #     break
