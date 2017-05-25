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

# Get NFS info
nfs_ip = NFS_INFO[NFS_HOST_BE_USED]['ip']
nfs_pass = NFS_INFO[NFS_HOST_BE_USED]['password']
nfs_data_path = NFS_INFO[NFS_HOST_BE_USED]['data_path'][0]

dc_name = "vdsm_nfs_dc"
cluster_name = "vdsm_nfs_cluster"
host_name = "vdsm_nfs_host"

sd_name = "vdsm_nfs_sd"
vm_name = "vdsm_nfs_vm"
disk_name = "vdsm_nfs_disk"

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


def test_18120(rhvm):
    """
    Add NFS storage to rhvh in rhvm successfully after add rhvh to rhvm
    """
    # Create nfs storage domain
    print "Creating nfs storage domain..."

    cmd = "rm -rf %s/*" % nfs_data_path
    with settings(warn_only=True, host_string='root@' + nfs_ip, password=nfs_pass):
        run(cmd)

    try:
        rhvm.create_plain_storage_domain(
            domain_name=sd_name,
            domain_type='data',
            storage_type='nfs',
            storage_addr=nfs_ip,
            storage_path=nfs_data_path,
            host=host_name)
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to create nfs storage domain %s for %s" % (
            sd_name, dc_name)
    time.sleep(60)

    # Attach nfs storage domain to datacenter
    print "Attaching nfs storage domain to datacenter..."
    try:
        rhvm.attach_sd_to_datacenter(sd_name=sd_name, dc_name=dc_name)
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to attach nfs storage domain to datacenter"
    time.sleep(30)


def test_18121(rhvm):
    """
    Create VMs on rhvh from rhvm side successfully after add rhvh to rhvm
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
    try:
        rhvm.create_vm_image_disk(
            vm_name=vm_name,
            sd_name=sd_name,
            disk_name=disk_name,
            disk_size="30589934592")
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to create new disk attachment to the VM"
    time.sleep(30)


def test_18122(rhvm):
    """
    Check VMs lifecycle successfully after add rhvh to rhvm
    """
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

    '''
    # Suspend the vm
    print "Suspended the new VM..."
    try:
        rhvm.operate_vm(vm_name, 'suspend')
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to suspend the VM"
    time.sleep(30)

    # Wait VM is suspended
    i = 0
    while True:
        if i > 30:
            assert 0, "Failed to suspend the new VM"
        vm_status = rhvm.list_vm(vm_name)['status']
        print "VM: %s" % vm_status
        if vm_status == 'pending':
            break
        time.sleep(10)
        i += 1
    time.sleep(30)

    # Startup the vm
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

    # Shutdown the vm
    print "Shutdown the new VM..."
    try:
        rhvm.operate_vm(vm_name, 'shutdown')
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to shutdown the VM"
    time.sleep(30)

    # Wait VM is down
    i = 0
    while True:
        if i > 30:
            assert 0, "Failed to shutdown the new VM"
        vm_status = rhvm.list_vm(vm_name)['status']
        print "VM: %s" % vm_status
        if vm_status == 'down':
            break
        time.sleep(10)
        i += 1
    time.sleep(10)

    # Startup the vm
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
    '''

    # Reboot the vm
    print "Reboot the new VM..."
    try:
        rhvm.operate_vm(vm_name, 'reboot')
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to reboot the VM"
    time.sleep(30)

    # Wait VM is up
    i = 0
    while True:
        if i > 60:
            assert 0, "Failed to reboot the new VM"
        vm_status = rhvm.list_vm(vm_name)['status']
        print "VM: %s" % vm_status
        if vm_status == 'up':
            break
        time.sleep(10)
        i += 1

    # Poweroff the VM
    print "Poweroff the new VM..."
    try:
        rhvm.operate_vm(vm_name, 'stop')
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to stop the VM"
    time.sleep(30)

    # Wait VM is down
    i = 0
    while True:
        if i > 30:
            assert 0, "Failed to stop the new VM"
        vm_status = rhvm.list_vm(vm_name)['status']
        print "VM: %s" % vm_status
        if vm_status == 'down':
            break
        time.sleep(10)
        i += 1
    time.sleep(30)


def test_18130(rhvm):
    """
    Verify delete VM successful
    """
    # Remove the new VM
    print "Removing the new VM..."
    try:
        rhvm.remove_vm(vm_name)
    except Exception as e:
        print e
        print traceback.print_exc()
    time.sleep(60)


def test_unset(rhvm):
    # Maintenance host
    print "Maintenance the host..."
    try:
        rhvm.deactive_host(host_name)
    except Exception as e:
        print e
        print traceback.print_exc()
    time.sleep(30)

    # Remove host
    print "Removing the host..."
    try:
        rhvm.remove_host(host_name)
    except Exception as e:
        print e
        print traceback.print_exc()
    time.sleep(30)
