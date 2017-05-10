#
# RHVM FQDN
#
RHVM_INFO = {
    "rhvm41-vdsm-auto.lab.eng.pek2.redhat.com": {
        "ip": "10.73.75.48",
        "password": "password"
    },
}

#
# Machines for local storage test
#
LOCAL_SYS = {
    "10.66.9.52": {
        "ip": "10.66.9.52",
        "password": "redhat",
        "data_path": "/home/data",
    },
}

#
# Info for NFS storage test
#
NFS_INFO = {
    "10.66.8.173": {
        "ip": "10.66.8.173",
        "password": "l1admin",
        "data_path": ["/home/dguo/Public/vdsm/data"],
        "iso_path": ["/home/dguo/Public/vdsm/iso"]
    },
}

#
# Machines for FC storage test
#
FC_SYS = {
    "hp-dl385g8-03.lab.eng.pek2.redhat.com": {
        "ip": ["10.73.73.35"],
        "password": "redhat",
        "local_disk": "",
        "lun_address": "",
        "lun_port": "",
        "lun_target": "",
        "boot_lun": ["36005076300810b3e0000000000000267"],
        "avl_luns": ["36005076300810b3e0000000000000268", "36005076300810b3e0000000000000269"]
    },
    "hp-dl385g8-11.lab.eng.pek2.redhat.com": {
        "ip": ["10.73.73.15"],
        "password": "redhat",
        "local_disk": "",
        "lun_address": "",
        "lun_port": "",
        "lun_target": "",
        "boot_lun": [],
        "avl_luns": []
    }
}

#
# Machines for SCSI storage test
#
SCSI_SYS = {
    "dell-per515-01.lab.eng.pek2.redhat.com": {
        "ip": ["10.73.73.7"],
        "password": "redhat",
        "local_disk": [],
        "lun_address": "10.73.194.25",
        "lun_port": "3260",
        "lun_target": "iqn.1992-08.com.netapp:sn.135053389",
        "boot_lun": ["360a9800050334c33424b41762d726954"],
        "avl_luns": ["360a9800050334c33424b41762d736d45", "360a9800050334c33424b41762d745551"]
    },
    "dell-per515-02.lab.eng.pek2.redhat.com": {
        "ip": [""],
        "password": "redhat",
        "local_disk": [""],
        "lun_address": "",
        "lun_port": "",
        "lun_target": "",
        "boot_lun": [""],
        "avl_luns": [""]
    },
}

#
# Machines for Network bond/vlan/bv test
#
NETWORK_SYS = {
    "ibm-x3650m5-04.lab.eng.pek2.redhat.com": {
        "ip": ["10.73.130.225", ""],
        "pub_nic": ["eno1", "eno2"],
        "bond": {"eno1": "mac1", "eno2": "mac2"},
        "bond_mode": "",
        "vlan": {"eno3": "mac3", "eno4": "mac4"},
        "vlan_id": "50",
        "bv_mode": "",
    },

    "dell-per730-35.lab.eng.pek2.redhat.com": {
        "ip": ["", ""],
        "pub_nic": ["em1", "em2"],
        "bond": {"em1": "mac1", "em2": "mac2"},
        "bond_mode": "",
        "vlan": {"p7p1": "mac3", "p7p2": "mac4"},
        "vlan_id": "50",
        "bv_mode": ""
    },

    "dell-per730-34.lab.eng.pek2.redhat.com": {
        "pub_ip": ["", ""],
        "pub_nic": ["eno1", "eno2"],
        "bond": {"eno1": "mac1", "eno2": "mac2"},
        "bond_mode": "",
        "vlan": {"eno3": "mac3", "eno4": "mac4"},
        "vlan_id": "50",
        "bv_mode": ""
    }
}
