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


'''
@pytest.fixture(scope="module")
def minerhvm(request):
    rhvm = RhevmAction(rhvm_fqdn)
    rhvm.create_datacenter(dc_name, is_local=True)
    print "Creating datacenter..."
    time.sleep(10)
    cpu_type = get_cpu_type(host_ip, host_pass)
    rhvm.create_cluster(dc_name, cluster_name, cpu_type)

    def fin():
        rhvm.remove_datacenter(dc_name)
        rhvm.remove_cluster(cluster_name)

    # request.addfinalizer(fin)
    return rhvm
'''


def test_18113():
    rhvm = RhevmAction(rhvm_fqdn)

    # Create datacenter
    print "Creating new datacenter..."
    rhvm.create_datacenter(dc_name, is_local=True)
    time.sleep(10)

    # Create cluster
    print "Creating new cluster..."
    cpu_type = get_cpu_type(host_ip, host_pass)
    rhvm.create_cluster(dc_name, cluster_name, cpu_type)

    # Create new host to above cluster
    print "Adding new host..."
    rhvm.create_new_host(
        host_ip, host_name, host_pass, cluster_name=cluster_name)

    # Wait host is up
    time.sleep(15)
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
    rhvm.remove_host(host_name)
    time.sleep(30)

    # Force remove datacenter and cluster
    print "Removing the cluster..."
    rhvm.remove_cluster(cluster_name)
    print "Removing the datacenter..."
    rhvm.remove_datacenter(dc_name)


def test_18114():
    rhvm = RhevmAction(rhvm_fqdn)

    # Create new datacenter
    print "Creating new datacenter..."
    rhvm.create_datacenter(dc_name, is_local=True)
    time.sleep(10)

    # Create new cluster
    print "Creating new cluster..."
    cpu_type = get_cpu_type(host_ip, host_pass)
    rhvm.create_cluster(dc_name, cluster_name, cpu_type)

    # Add new host to above cluster
    print "Adding new host..."
    rhvm.create_new_host(
        host_ip, host_name, host_pass, cluster_name=cluster_name)

    # Wait host is up
    time.sleep(15)
    i = 0
    while True:
        print i
        if i > 60:
            assert 0, "Failed to add host %s to %s" % (host_name, dc_name)
        host_status = rhvm.list_host(host_name)['status']
        print host_status
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

    # Create disk for vm over local storage domain
    print "Creating new disk for vm to use..."
    vm_disk = "vdsm_local_disk"
    try:
        rhvm.create_image_disk(storage_domain_name, vm_disk, '50000')
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to create disk from storage domain %s" % storage_domain_name
    time.sleep(15)

    # Create vm and attach disk to this vm
    print "Creating new virtual machine..."
    vm_name = "vdsm_local_vm"
    rhvm.create_vm(vm_name=vm_name, cluster=cluster_name)
    time.sleep(30)

    # Attach new disk to above vm
    print "Attaching new disk to the virtual machine..."
    rhvm.attach_disk_to_vm(disk_name=vm_disk, vm_name=vm_name)
    time.sleep(30)

    # Maintenance host
    print "Maintenance the host..."
    host_id = rhvm.list_host(host_name)
    rhvm.deactive_host(host_id)

    # Force remove datacenter and cluster
    print "Force removing the datacenter..."
    rhvm.remove_datacenter(dc_name)
    print "Removing the host..."
    rhvm.remove_host(host_name)
    print "Remove the cluster..."
    rhvm.remove_cluster(cluster_name)
