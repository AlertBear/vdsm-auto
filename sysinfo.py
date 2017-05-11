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
        "ip": "10.73.73.35",
        "password": "redhat",
        "local_disk": "",
        "boot_lun": ["36005076300810b3e0000000000000267"],
        "avl_luns": ["36005076300810b3e0000000000000268", "36005076300810b3e0000000000000269"]
    },

    "hp-dl385g8-11.lab.eng.pek2.redhat.com": {
        "ip": "10.73.73.15",
        "password": "redhat",
        "local_disk": "",
        "boot_lun": [],
        "avl_luns": []
    }
}

#
# Machines for SCSI storage test
#
SCSI_SYS = {
    "dell-per515-01.lab.eng.pek2.redhat.com": {
        "ip": "10.73.75.170",
        "password": "redhat",
        "local_disk": [],
        "boot_lun": ["360a9800050334c33424b41762d726954"],
        "avl_luns": ["360a9800050334c33424b41762d736d45", "360a9800050334c33424b41762d745551"],
        "lun_address": "10.73.194.25",
        "lun_port": "3260",
        "lun_target": "iqn.1992-08.com.netapp:sn.135053389"
    },

    "dell-per515-02.lab.eng.pek2.redhat.com": {
        "ip": "",
        "password": "redhat",
        "local_disk": [""],
        "boot_lun": [""],
        "avl_luns": [""],
        "lun_address": "",
        "lun_port": "",
        "lun_target": ""
    },
}

#
# Machines for Network bond/vlan/bv test
#
NETWORK_SYS = {
    "dell-per515-01.lab.eng.pek2.redhat.com": {
        "ip": "10.73.75.170",
        "pub_nic": "em2",
        "bond": {"em1": "08:9e:01:63:2c:b2", "em2": "08:9e:01:63:2c:b3"},
        "bond_mode": "",
        "vlan": {"p2p1": "00:1b:21:a6:64:6c", "p2p2": "00:1b:21:a6:64:6d", "p3p1": "00:1b:21:a6:3d:7a"},
        "vlan_id": "50",
        "bv_mode": "",
    },

    "ibm-x3650m5-04.lab.eng.pek2.redhat.com": {
        "ip": "10.73.130.225",
        "pub_nic": "eno1",
        "bond": {"eno1": "08:94:ef:21:c0:4d", "eno2": "08:94:ef:21:c0:4e"},
        "bond_mode": "",
        "vlan": {"eno3": "08:94:ef:21:c0:4f", "eno4": "08:94:ef:21:c0:50"},
        "vlan_id": "50",
        "bv_mode": "",
    },

    "dell-per730-35.lab.eng.pek2.redhat.com": {
        "ip": "",
        "pub_nic": "em1",
        "bond": {"em1": "24:6e:96:19:b9:a4", "em2": "24:6e:96:19:b9:a5"},
        "bond_mode": "",
        "vlan": {"p7p1": "a0:36:9f:9d:3b:fe", "p7p2": "a0:36:9f:9d:3b:ff"},
        "vlan_id": "50",
        "bv_mode": ""
    },

    "dell-per730-34.lab.eng.pek2.redhat.com": {
        "ip": "",
        "pub_nic": "em1",
        "bond": {"em1": "24:6e:96:19:bb:70", "em2": "24:6e:96:19:bb:71"},
        "bond_mode": "",
        "vlan": {"em3": "24:6e:96:19:bb:72", "em4": "24:6e:96:19:bb:73"},
        "vlan_id": "50",
        "bv_mode": ""
    }
}
