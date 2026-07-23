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
        + extractor.units.der_units
        + extractor.units.bess_units
    ):

        attr_unit = Utils.get_params_to_dict_by_path(
            emtp_object=emtp_object, device_path=unit.unit_path
        )

        # print(attr_unit)

        # break

        params = {
            "Kppll_REGC_A": "10",
            "Kipll_REGC_A": "30",
            "wmax_REGC_A": "330",
            "Imax": "1.1",
            "PQFLAG": "1",
        }

        if "PMGD" in unit.object.name:
            params["Vblkh"] = "1.5"
            params["Kp_REPC"] = "1"
            params["Ki_REPC"] = "10"
            params["VDL_VqIqCurveData"] = (
                "0\t0.4\n0.4\t0.4\n0.9\t0.4\n1\t0.4\n1.1\t0.4\n1.5\t0.4\n1.51\t0\n3\t0"
            )
            params["VDL_VpIpCurveData"] = (
                "0\t0\n0.4\t0\n0.9\t1.1\n1\t1.1\n1.1\t1.1\n1.11\t1\n1.2\t1\n1.21\t0\n3\t0"
            )
            params["Rrpwr_REGC_A"] = "0.5"

        else:
            params["Vblkh"] = "1.2"
            params["VDL_VqIqCurveData"] = (
                "0\t1\n0.4\t1\n0.9\t1\n1\t1\n1.1\t1\n1.11\t1\n1.2\t1\n1.21\t0\n3\t0"
            )
            params["VDL_VpIpCurveData"] = (
                "0\t0\n0.4\t0\n0.9\t1.1\n1\t1.1\n1.1\t1.1\n1.11\t1\n1.2\t1\n1.21\t0\n3\t0"
            )

        params_bess = {
            "PLLinv_kp": "10",
            "PLLinv_ki": "30",
            "Igsc_max_pu": "1.1",
            "FRT_ON": "0.2",
            "FRT_ON": "0.1",
        }

        if "BESS" in unit.object.name:
            Utils.set_params_from_dict_by_path(
                emtp_object=emtp_object, device_path=unit.unit_path, params=params_bess
            )
        else:
            Utils.set_params_from_dict_by_path(
                emtp_object=emtp_object, device_path=unit.unit_path, params=params
            )
        print(unit.object.name)

    Design.save(emtp_object=emtp_object)
