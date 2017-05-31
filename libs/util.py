import re
import time
import scen
from fabric.api import run, settings
from constants import MACHINE_INFO


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


def get_cpu_type(host_ip, host_pass):
    with settings(
        host_string='root@'+host_ip,
        password=host_pass
    ):
        cmd = "cat /proc/cpuinfo|grep 'model name'"
        output = run(cmd)

        if re.search("AMD", output):
            cpu_type = "AMD Opteron G1"
        else:
            cpu_type = "Intel Conroe Family"

        return cpu_type


def clear_fc_scsi_lun(lun_id):
    pv = "/dev/mapper/%s" % lun_id
    vg = None
    lun_parts = []

    # Get the vg name if there exists
    cmd = "pvs|grep %s" % lun_id
    output = run(cmd)
    if output:
        vg = output.split()[1]
    else:
        # If there is lvm on the lun, get the vg from lvm
        cmd = "lsblk -l %s|grep lvm|awk '{print $1}'" % pv
        output = run(cmd)
        if output:
            alvm_blk = output.split()[0]
            new_alvm_blk = alvm_blk.replace("--", "##")
            alvm_prefix = new_alvm_blk.split('-')[0]
            vg = alvm_prefix.replace("##", "-")

        # If there is partition on the lun, get all of them
        cmd = "lsblk -l %s|grep 'part'|awk '{print $1}'" % pv
        output = run(cmd)
        if output:
             for blk_part in output.split():
                 lun_parts.append("/dev/mapper/" + blk_part)

    # Delete the lun
    cmd = "dd if=/dev/zero of=%s bs=50M count=10" % pv
    run(cmd)

    # Delete the partition if exists
    if lun_parts:
        for lun_part in lun_parts:
            cmd = "dd if=/dev/zero of=%s bs=50M count=10" % lun_part
            run(cmd)

    # Delete the vg if exists
    if vg:
        cmd = "dmsetup remove /dev/%s/*" % vg
        run(cmd)


def wait_host_up(rhvm, host_name):
    # Wait host is up
    i = 0
    host_status = "unknown"
    while True:
        if i > 60:
            return False, host_status
        host_status = rhvm.list_host(host_name)['status']
        print "HOST: %s" % host_status
        if host_status == 'up':
            return True, host_status
        elif host_status == 'install_failed':
            return False, host_status
        elif host_status == 'non_operational':
            return False, host_status
        time.sleep(10)
        i += 1


def wait_vm_up(rhvm, vm_name):
    # Wait VM is up
    i = 0
    vm_status = "unknown"
    while True:
        if i > 30:
            return False, vm_status
        vm_status = rhvm.list_vm(vm_name)['status']
        print "VM: %s" % vm_status
        if vm_status == 'up':
            return True, vm_status
        time.sleep(10)
        i += 1
