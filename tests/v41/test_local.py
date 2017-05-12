import pytest
import time
import traceback
from libs.rhevm import RhevmAction
from fabric.api import run, env, settings
from libs.util import *
from conf import *
from sysinfo import *

# Get rhvm fqdn info
rhvm_fqdn = RHVM_FQDN
rhvm_pass = RHVM_INFO[RHVM_FQDN]['ip']

# Get host info
host_ip = LOCAL_SYS[LOCAL_HOST]['ip']
host_pass = LOCAL_SYS[LOCAL_HOST]['password']
local_data_path = LOCAL_SYS[LOCAL_HOST]['data_path']

dc_name = "vdsm_local_dc"
cluster_name = "vdsm_local_cluster"
host_name = "vdsm_local_host"

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
    pass


def test_18113(rhvm):
    """
    Add rhvh to rhvm successfully
    """
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
        elif host_status == 'install_failed':
            assert 0, "Failed to add host %s to %s" % (host_name, dc_name)
        time.sleep(10)
        i += 1
    time.sleep(10)


def test_18124(rhvm):
    """
    rhvh info check in rhvm
    """
    pass


def test_18136(rhvm):
    """
    Check fcoe.service, lldpad.socket and lldpad.service status after add RHVH to RHEV-M
    """
    pass


def test_18127(rhvm):
    """
    Verify rhvh can be removed in rhvm
    """
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
    """
    Add local storage(xfs/ext4) to host in rhvm successfully after add rhvh to rhvm
    """
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
        elif host_status == 'install_failed':
            assert 0, "Failed to add host %s to %s" % (host_name, dc_name)
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


def test_18123(rhvm):
    """
    Change host status to maintenance mode
    """
    # Maintenance host
    print "Maintenance the host..."
    try:
        rhvm.deactive_host(host_name)
    except Exception as e:
        print e
        print traceback.print_exc()
        assert 0, "Failed to maintenance the host"
    time.sleep(30)


def test_unset(rhvm):
    # Remove datacenter
    print "Removing the datacenter..."
    try:
        rhvm.remove_datacenter(dc_name, force=True)
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
