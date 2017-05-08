import pytest
import time
import traceback
from fabric.api import run, env, settings
from libs.util import *
from conf import *

rhvm_fqdn = RHVM_FQDN
host_ip = HOST_IP
host_pass = HOST_PASS

dc_name = "vdsm_nfs_dc"
cluster_name = "vdsm_nfs_cluster"
host_name = "vdsm_nfs_host"

nfs_ip = NFS_IP
nfs_pass = NFS_PASS
nfs_data_path = NFS_DATA_PATH

env.host_string = 'root@' + host_ip
env.password = host_pass


@pytest.fixture(scope="session")
def rhvm(request):
    mrhvm = RhevmAction(rhvm_fqdn)

    mrhvm.create_datacenter(dc_name, is_local=True)
    print "Creating datacenter..."
    time.sleep(10)

    print "Creating cluster..."
    cpu_type = get_cpu_type(host_ip, host_pass)
    mrhvm.create_cluster(dc_name, cluster_name, cpu_type)

    def fin():
        print "Force removing datacenter..."
        mrhvm.remove_datacenter(dc_name, force=True)
        if mrhvm.list_host(host_name):
            print "Removing host..."
            mrhvm.remove_host(host_name)
        print "Removing cluster..."
        mrhvm.remove_cluster(cluster_name)

    request.addfinalizer(fin)
    return mrhvm


def test_18120_18121(rhvm):
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
        time.sleep(10)
        i += 1

    # Create nfs storage domain
    print "Creating nfs storage domain..."

    cmd = "rm -rf %s/*" % nfs_data_path
    with settings(warn_only=True, host_string='root@' + nfs_ip, password=nfs_pass):
        run(cmd)

    sd_name = "vdsm_nfs_sd"
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

    # Create virtual machine
    print "Creating new virtual machine..."
    vm_name = "vdsm_nfs_vm"
    try:
        rhvm.create_vm(vm_name=vm_name, cluster=cluster_name)
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to create new vm"
    time.sleep(30)

    # Create new disk attachment to above vm
    print "Creating new disk attachment to the virtual machine..."
    disk_name = "vdsm_nfs_disk"
    try:
        rhvm.create_vm_disk_attachment(
            vm_name=vm_name,
            sd_name=sd_name,
            disk_name=disk_name,
            disk_size="30589934592")
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

    # Remove the new VM
    print "Removing the new VM..."
    try:
        rhvm.remove_vm(vm_name)
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to remove the new VM"
    time.sleep(60)

    # Maintenance host
    print "Maintenance the host..."
    try:
        rhvm.deactive_host(host_name)
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to maintenance the host"
    time.sleep(30)
