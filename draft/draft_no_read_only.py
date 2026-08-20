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

    all_units = (
        extractor.units.syn_units
        + extractor.units.pv_units
        + extractor.units.wf_units
        + extractor.units.bess_units
        + extractor.units.der_units
    )

    for unit in all_units:

        print(unit.name)

        subcct = unit.object.subCircuit
        subcct.isReadOnly = "False"
