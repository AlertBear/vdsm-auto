import pytest
import time
import traceback
from fabric.api import run, env, settings
from libs.util import *
from conf import *

rhvm_fqdn = RHVM_FQDN
host_ip = HOST_IP
host_pass = HOST_PASS

dc_name = "vdsm_local_dc"
cluster_name = "vdsm_local_cluster"
host_name = "vdsm_local_host"

local_data_path = LOCAL_DATA_PATH

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


def test_18113(rhvm):
    # Create new host to above cluster
    print "Adding new host..."
    try:
        rhvm.create_new_host(
            host_ip, host_name, host_pass, cluster_name=cluster_name)
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to add new host"
    time.sleep(15)

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

    # Remove host from above cluster
    print "Removing the host..."
    try:
        rhvm.remove_host(host_name)
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to remove host from cluster"
    time.sleep(30)


def test_18114(rhvm):
    # Add new host to above cluster
    print "Adding new host..."
    try:
        rhvm.create_new_host(
            host_ip, host_name, host_pass, cluster_name=cluster_name)
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to add new host to cluster"
    time.sleep(15)

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

    # Make dir for local data
    print "Making local storage directory..."
    with settings(warn_only=True):
        cmd = "test -r %s" % local_data_path
        output = run(cmd)

        if output.failed:
            cmd = "mkdir -p %s" % local_data_path
            run(cmd)
        else:
            cmd = "rm -rf %s/*" % local_data_path
            run(cmd)

    # Create local storage domain above local storage dir
    print "Creating local storage domain..."
    storage_domain_name = "vdsm_local_sd"
    try:
        rhvm.create_plain_storage_domain(
            domain_name=storage_domain_name,
            domain_type='data',
            storage_type='localfs',
            storage_addr='',
            storage_path='/home/data',
            host=host_name)
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to create local storage domain %s for %s" % (
            storage_domain_name, dc_name)
    time.sleep(60)

    # Create virtual machine
    print "Creating new virtual machine..."
    vm_name = "vdsm_local_vm"
    try:
        rhvm.create_vm(vm_name=vm_name, cluster=cluster_name)
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to create new vm"
    time.sleep(30)

    # Create new disk attachment to above vm
    print "Creating new disk attachment to the virtual machine..."
    disk_name = "vdsm_local_disk"
    try:
        rhvm.create_vm_disk_attachment(
            vm_name=vm_name,
            sd_name=storage_domain_name,
            disk_name=disk_name,
            disk_size="30589934592")
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to create disk attachement to the VM"
    time.sleep(30)

    # Maintenance host
    print "Maintenance the host..."
    try:
        rhvm.deactive_host(host_name)
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to maintenance the host"
    time.sleep(30)
