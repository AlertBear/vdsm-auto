import re
import traceback
import functools
from rhevm import RhevmAction
from fabric.api import run, settings


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


def prepare_dc_for_host(
        rhvm_fqdn, cluster_name, host_ip, host_pass):
    # Mainly update the CPU type of cluster for
    cpu_type = get_cpu_type(host_ip, host_pass)
    rhvm = RhevmAction(rhvm_fqdn)
    rhvm.update_cluster_cpu(cluster_name, cpu_type)


def exception(text):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            try:
                func(*args, **kw)
            except Exception as e:
                print e
                print traceback.print_exc()
                print text
            return func(*args, **kw)
        return wrapper
    return decorator
