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
    # devices = cct.devices

    # rows = []

    # rows.append(["name", "exclude"])

    # for device in devices:
    #     if device.getAttribute("LibType") == "PQ load Yg with load-flow (LF)":
    #         rows.append(
    #             [
    #                 device.name,
    #                 device.getAttribute("Exclude"),
    #             ]
    #         )

    # for row in rows:
    #     print("\t".join([str(value) for value in row]))

    # for device in devices:
    #     if device.getAttribute("LibType") == "EDAC":
    #         rows.append(
    #             [
    #                 device.name,
    #                 device.getAttribute("Exclude"),
    #             ]
    #         )

    # for row in rows:
    #     print("\t".join([str(value) for value in row]))

    # /// Gen counter

    print(f"syn: {len(extractor.units.syn_units)}")
    print(f"pv: {len(extractor.units.pv_units)}")
    print(f"wf: {len(extractor.units.wf_units)}")
    print(f"bess: {len(extractor.units.bess_units)}")
    print(f"der: {len(extractor.units.der_units)}")
