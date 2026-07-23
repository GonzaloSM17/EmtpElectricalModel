from unit_extractor import *

if __name__ == "__main__":

    # -------------------------------------------------------------------------
    # EMTP session and library initialization
    # -------------------------------------------------------------------------
    emtp_client = EmtpComClient(attach_existing=True)
    emtp_object = emtp_client.emtp_object

    extractor = UnitExtractor(emtp_object=emtp_object)
    extractor.execute()

    # print(extractor.units.syn_units)

    # cct = Design.circuit(emtp_object=emtp_object)
    # signals = cct.signals

    for unit in (
        extractor.units.wf_units
        + extractor.units.pv_units
        +
        # + extractor.units.bess_units
        # +
        # extractor.units.syn_units
        extractor.units.der_units
    ):

        attr_unit = Utils.get_params_to_dict_by_path(
            emtp_object=emtp_object, device_path=unit.unit_path
        )

        # print(attr_unit)

        if "PMGD" in unit.object.name:
            params = {
                "Kppll_REGC_A": "1",
                "Kipll_REGC_A": "10",
                "Vblkh": "1.5",
                "wmax_REGC_A": "330",
                "Imax": "1.1",
                "PQFLAG": "1",
            }

        else:
            params = {
                "Kppll_REGC_A": "1",
                "Kipll_REGC_A": "10",
                "Vblkh": "1.2",
                "wmax_REGC_A": "330",
                "Imax": "1.1",
                "PQFLAG": "1",
            }

        # break

        # if attr_unit["npoles"] == "4":
        #     print(unit.object.name)

        Utils.set_params_from_dict_by_path(
            emtp_object=emtp_object, device_path=unit.unit_path, params=params
        )

    # print(attr_unit)
    # break

    # Design.save(emtp_object=emtp_object)

    # attr_parent = Utils.get_params_to_dict_by_path(
    #     emtp_object=emtp_object, device_path=unit.object
    # )

    # attr_lf = Utils.get_params_to_dict_by_path(
    #     emtp_object=emtp_object, device_path=unit.loadflow_path
    # )

    # if float(attr_lf["Q_set"]) != 0 and attr_lf["Bus_Type"] == "PQ":

    #     print(unit.object.name)
    #     print(attr_lf["Bus_Type"])
    #     print(attr_lf["Q_set"])

    # break

    Design.save(emtp_object=emtp_object)

    # unit.subCircuit.

    # if attr_machine["Pm_c"] == "1":
    #     print(unit.object)
    # params = {"Pm_c": "0"}

    # Utils.set_params_from_dict_by_path(
    #     emtp_object=emtp_object, device_path=unit.unit_path, params=params
    # )
