from constants import MACHINE_INFO
import scen


def _exclude_scen(s, machine):
    machine_info = MACHINE_INFO[machine]
    network_s = [
        "bond_anaconda",
        "vlan_anaconda",
        "bv_anaconda",
        "bond_ifcfg",
        "vlan_ifcfg",
        "bv_ifcfg"]

    if s not in machine_info.keys():
        if s not in network_s:
            return True
        else:
            if s.split('_')[0] not in machine_info['network'].keys():
                return True

    return False


def _get_machine_ks_cases_map(machine, *scens):
    if machine not in MACHINE_INFO.keys():
        raise RuntimeError("%s not in record, see detail in constants.py" % machine)

    machine_ks_cases_map = {}

    for s in scens:
        if _exclude_scen(s, machine):
            continue
        sa = getattr(scen, s)
        ks_cases_map = {sa['KSFILE']: sa['CASES']}
        machine_ks_cases_map.update(ks_cases_map)

    return machine_ks_cases_map


def get_job_queue(machine, *scens):
    """ example
    :param machine: "ibm-x3650m5-04.lab.eng.pek2.redhat.com"
    :param scens: "bv_anaconda"
    :return: {"ibm-x3650m5-04.lab.eng.pek2.redhat.com": {
                "bv_tpl.ks": ["tests/v41/test_bv_anaconda.py"]
                }
             }
    """
    return _get_machine_ks_cases_map(machine, *scens)
