import re
import traceback
import functools
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
