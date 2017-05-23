import pytest
import time
import traceback
from libs.rhevm import RhevmAction
from fabric.api import run, env, settings
from libs.util import *
from conf import *
from constants import *

# Get rhvm info
rhvm_fqdn = RHVM_FQDN
rhvm_pass = RHVM_INFO[RHVM_FQDN]['password']

# Get host to be used
host_ip = MACHINE_INFO[TEST_HOST]['ip']
host_pass = MACHINE_INFO[TEST_HOST]['password']

# Get scsi storage info
scsi_flag = MACHINE_INFO[TEST_HOST].get('scsi', None)
if not scsi_flag:
    raise RuntimeError("%s not support for test_scsi" % TEST_HOST)

available_luns = MACHINE_INFO[TEST_HOST]['scsi']['avl_luns']
lun_as_sd = available_luns[0]
lun_as_disk = available_luns[1]
lun_address = MACHINE_INFO[TEST_HOST]['scsi']['lun_address']
lun_port = MACHINE_INFO[TEST_HOST]['scsi']['lun_port']
lun_target = MACHINE_INFO[TEST_HOST]['scsi']['lun_target']

dc_name = "vdsm_scsi_dc"
cluster_name = "vdsm_scsi_cluster"
host_name = "vdsm_scsi_host"

sd_name = "vdsm_scsi_sd"
vm_name = "vdsm_scsi_vm"
disk_name = "vdsm_scsi_disk"

env.host_string = 'root@' + host_ip
env.password = host_pass


@pytest.fixture(scope="session")
def rhvm(request):
    mrhvm = RhevmAction(rhvm_fqdn)

    mrhvm.create_datacenter(dc_name)
    print "Creating datacenter..."
    time.sleep(10)

    print "Creating cluster..."
    cpu_type = get_cpu_type(host_ip, host_pass)
    mrhvm.create_cluster(dc_name, cluster_name, cpu_type)

    def fin():
        if mrhvm.list_datacenter(dc_name):
            print "Force removing datacenter..."
            mrhvm.remove_datacenter(dc_name, force=True)
        if mrhvm.list_host(host_name):
            print "Removing host..."
            mrhvm.remove_host(host_name)

        print "Removing cluster..."
        mrhvm.remove_cluster(cluster_name)

    request.addfinalizer(fin)
    return mrhvm


def test_set(rhvm):
    # Add new host to above cluster
    print "Adding new host..."
    try:
        rhvm.create_new_host(
            host_ip, host_name, host_pass, cluster_name=cluster_name)
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to add new host to cluster"
    time.sleep(30)

    # Wait host is up
    i = 0
    while True:
        if i > 60:
            assert 0, "Failed to add host %s to %s" % (host_name, dc_name)
        host_status = rhvm.list_host(host_name)['status']
        print "HOST: %s" % host_status
        if host_status == 'up':
            break
        elif host_status == 'install_failed':
            assert 0, "Failed to add host %s to %s" % (host_name, dc_name)
        time.sleep(10)
        i += 1


def test_18115(rhvm):
    """
    Add iscsi storage to rhvh in rhvm successfully after add rhvh to rhvm
    """
    # Create fc storage domain
    print "Creating scsi storage domain..."
    with settings(warn_only=True):
        clear_fc_scsi_lun(lun_as_sd)
    try:
        rhvm.create_fc_scsi_storage_domain(
            domain_name=sd_name,
            domain_type='data',
            storage_type='iscsi',
            lun_id=lun_as_sd,
            host=host_name)
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to create scsi storage domain %s for %s" % (
            sd_name, dc_name)
    time.sleep(60)

    # Attach iscsi storage domain to datacenter
    print "Attaching iscsi storage domain to datacenter..."
    try:
        rhvm.attach_sd_to_datacenter(sd_name=sd_name, dc_name=dc_name)
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to attach iscsi storage domain to datacenter"
    time.sleep(30)


def test_18132(rhvm):
    """
    Install VM on direct lun disk on iscsi storage
    """
    # Create virtual machine
    print "Creating new virtual machine..."
    try:
        rhvm.create_vm(vm_name=vm_name, cluster=cluster_name)
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to create new vm"
    time.sleep(30)

    # Create new disk attachment to above vm
    print "Creating new disk attachment to the virtual machine..."
    with settings(warn_only=True):
        clear_fc_scsi_lun(lun_as_disk)
    try:
        rhvm.create_vm_direct_lun_disk(
            disk_name=disk_name,
            vm_name=vm_name,
            host_name=host_name,
            lun_type="iscsi",
            lun_id=lun_as_disk,
            lun_addr=lun_address,
            lun_port=lun_port,
            lun_target=lun_target
        )
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to create new disk attachment to the VM"
    time.sleep(30)

    # Start the VM
    print "Starting up the new VM..."
    try:
        rhvm.operate_vm(vm_name, 'start')
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to start up the new VM"
    time.sleep(60)

    # Wait VM is up
    i = 0
    while True:
        if i > 30:
            assert 0, "Failed to start up the new VM"
        vm_status = rhvm.list_vm(vm_name)['status']
        print "VM: %s" % vm_status
        if vm_status == 'up':
            break
        time.sleep(10)
        i += 1


def test_unset(rhvm):
    # Poweroff the vm
    if rhvm.list_vm(vm_name):
        print "Poweroff the new VM..."
        try:
            rhvm.operate_vm(vm_name, 'stop')
        except Exception as e:
            print e
            print traceback.print_exc()
            assert 0, "Failed to poweroff the VM"
        time.sleep(30)

        # Wait VM is down
        i = 0
        while True:
            if i > 30:
                assert 0, "Failed to poweroff the new VM"
            vm_status = rhvm.list_vm(vm_name)['status']
            print "VM: %s" % vm_status
            if vm_status == 'down':
                break
            time.sleep(10)
            i += 1
        time.sleep(10)

        # Remove the new VM
        print "Removing the new VM..."
        try:
            rhvm.remove_vm(vm_name)
        except Exception as e:
            print e
            print traceback.print_exc()
        time.sleep(60)

    if rhvm.list_host(host_name):
        # Maintenance host
        print "Removing the host..."
        try:
            rhvm.remove_host(host_name)
        except Exception as e:
            print e
            print traceback.print_exc()
        time.sleep(30)
