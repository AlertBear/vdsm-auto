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

dc_name = "vdsm_bonda_dc"
cluster_name = "vdsm_bonda_cluster"
host_name = "vdsm_bonda_host"

# Get the bond info
bond_flag = MACHINE_INFO[TEST_HOST].get('network', None).get('bond')
if not bond_flag:
    raise RuntimeError("%s not support for test_bond_anaconda" % TEST_HOST)

bond = MACHINE_INFO[TEST_HOST]['network']['bond']['name']

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


def test_18156(rhvm):
    """
    Add rhvh to engine over dhcp bond after anaconda installation
    """
    with settings(warn_ony=True):
        cmd = "ip a s|grep %s|grep inet" % bond
        res = run(cmd)
    if res.failed:
        assert 0, "%s is not configured or name incorrect" % bond
    bond_ip = res.split()[1].split('/')[0]

    # Add new host to above cluster
    print "Adding new host..."
    try:
        rhvm.create_new_host(
            bond_ip, host_name, host_pass, cluster_name=cluster_name)
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


def test_unset(rhvm):
    # Remove host
    if rhvm.list_host(host_name):
        print "Removing the host..."
        try:
            rhvm.remove_host(host_name)
        except Exception as e:
            print e
            print traceback.print_exc()
        time.sleep(30)
