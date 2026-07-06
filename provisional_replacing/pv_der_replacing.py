from unit_extractor_v1 import *

library_path = "C:\\Users\\gonzalo.sanchez\\OneDrive - Coordinador Eléctrico Nacional\\C01. Simulación y Laboratorio en Tiempo Real\\04. EMTP Modelo Eléctrico\\09. Templates Reemplazo\\CEN Devices.clf"

if __name__ == "__main__":

    emtp_client = EmtpComClient(attach_existing=True)
    emtp_object = emtp_client.emtp_object

    if not emtp_object.currentDesign:
        Design.open_design(emtp_object=emtp_object)

    ## Loading Library
    Library.open_library(emtp_object=emtp_object, library_path=library_path)

    unit_extractor = UnitExtractor(emtp_object=emtp_object)
    unit_extractor.execute()

    pv_units = unit_extractor.units.pv_units

    i = 0
    for pv_unit in pv_units:

        # Data extraction
        attr_unit = Device.get_params_to_dict(
            emtp_object=emtp_object, device=pv_unit.unit_object
        )
        # print(f"PV Unit: {pv_unit.name}")
        # print(attr_unit)

        attr_to_draw = {
            "name": pv_unit.unit_object.name,
            "posX": pv_unit.unit_object.posX,
            "posY": pv_unit.unit_object.posY,
            "orientation": pv_unit.unit_object.orientation,
        }

        if attr_to_draw["orientation"] == "w":
            attr_to_draw["posX"] = attr_to_draw["posX"] + 100

        pin = pv_unit.unit_object.pins[0]
        signal = pin.signal

        ## Calculate some attr
        ngen = float(attr_unit.get("Ngen", 0))
        sgen = float(attr_unit.get("Sgen", 0))
        ngen_in_service = float(attr_unit.get("Ngen_in_service", ngen))
        pref_poi = float(attr_unit.get("Pref_poi", 0))
        qpoi_pu = float(attr_unit.get("Qpoi_pu", 0))
        in_service = pv_unit.unit_object.getAttribute("Exclude")
        voltage_level = attr_unit.get("Vpoi_kVRMSLL", "220")

        attr_to_set = {"sgn": round(ngen * sgen, 2)}

        ## attribute_to_mask
        if in_service == "Ex":
            in_service = 0
            p_setpoint = 0
            q_setpoint = 0

        else:
            in_service = 1
            p_setpoint = round(pref_poi * sgen * ngen_in_service, 2)
            q_setpoint = round(qpoi_pu * sgen * ngen_in_service, 2)

        attr_to_mask = {
            "in_service": in_service,
            "p_setpoint": p_setpoint,
            "q_setpoint": q_setpoint,
        }

        ## AddObject
        if "PMGD" in pv_unit.unit_object.name:
            library_template_name = "DER_TEMPLATE"
        else:
            library_template_name = "PV_TEMPLATE"
        ## Delete old object
        pv_unit.unit_object.remove

        library_object = Library.find_type(
            emtp_object=emtp_object,
            library_name="CEN Devices",
            type_name=library_template_name,
        )

        new_model_mask = Design.design(emtp_object).addDevice(
            library_object,
            attr_to_draw["posX"],
            attr_to_draw["posY"] + 100,
            attr_to_draw["orientation"],
        )

        try:
            new_model_mask.makeUnique()
        except Exception as e:
            new_model_mask.makeUnique
            # print(f"() not working")

        # Connection
        new_pin = new_model_mask.pins[0]
        new_pin.connectTo(signal, True)

        new_model_mask.setAttribute("Name", attr_to_draw["name"])

        new_model_subcc = new_model_mask.subCircuit
        new_model = new_model_subcc.devices[0]
        new_model.setAttribute("Name", attr_to_draw["name"])

        new_model_path = new_model_mask.name + "/" + new_model.name

        # Design.save(emtp_object=emtp_object)

        device = Photovoltaic(object=new_model_mask, unit_object=new_model)

        device.set_in_service(attr_to_mask["in_service"])
        device.set_p(attr_to_mask["p_setpoint"])
        device.set_q(attr_to_mask["q_setpoint"])

        # Prepare new parameters:

        new_attr = Utils.get_params_to_dict_by_path(
            emtp_object=emtp_object,
            device_path=new_model_path,
        )

        # Calculate
        sgn = float(attr_to_set["sgn"])

        new_sgen = new_attr.get("Sgen", 0)

        new_ngen = str(int(round((sgn / float(new_sgen)), 0)))
        new_ngen_in_service = new_ngen

        new_params = {
            "Ngen": new_ngen,
            "Ngen_in_service": new_ngen_in_service,
            "Vpoi_kVRMSLL": voltage_level,
            "S1_WP": str(float(sgn) * 1.1),
            "V2_WP": voltage_level,
        }

        Utils.set_params_from_dict_by_path(
            emtp_object=emtp_object,
            device_path=new_model_path,
            params=new_params,
        )

        ## Setting mask
        device.set_in_service(attr_to_mask["in_service"])
        device.set_p(attr_to_mask["p_setpoint"])
        device.set_q(attr_to_mask["q_setpoint"])

        # try:
        #     device.object.open()
        # except Exception as e:
        #     print(f"no () en open")
        #     device.object.open

        i += 1
        if i >= 3:
            Design.save(emtp_object=emtp_object)
            Simulation.run_load_flow(emtp_object=emtp_object)
            break
