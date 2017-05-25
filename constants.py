import os


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
NETWORK_SCRIPTS_DIR = "/etc/sysconfig/network-scripts"


#
# RHVM FQDN
#
RHVM_INFO = {
    "rhvm41-vdsm-auto.lab.eng.pek2.redhat.com": {
        "ip": "10.73.75.48",
        "password": "password"
    },
    "rhvm41-vlan50-1.lab.eng.pek2.redhat.com": {
        "ip": "10.73.75.93",
        "password": "password"
    },
    "rhvm41-vlan50-2.lab.eng.pek2.redhat.com": {
        "ip": "10.73.75.151",
        "password": "password"
    },
}

#
# Info for NFS to be used in test_nfs
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
# Machines for test
#
MACHINE_INFO = {
    "dguo_local_sys": {
        "ip": "10.66.9.52",
        "password": "redhat",
        "primary_nic": "enp2s0",

        # For test_local
        "local": {"data_path": "/home/data"}
    },

    "hp-dl385g8-03.lab.eng.pek2.redhat.com": {
        "ip": "10.73.73.35",
        "password": "redhat",
        "primary_nic": "eno1",

        # For test_local
        "local": {"data_path": "/home/data"},

        # For test_fc
        "fc": {
            "boot_lun": ["36005076300810b3e0000000000000267"],
            "avl_luns": ["36005076300810b3e0000000000000268", "36005076300810b3e0000000000000269"]
        }
    },

    "hp-dl385g8-11.lab.eng.pek2.redhat.com": {
        "ip": "10.73.73.15",
        "password": "redhat",
        "primary_nic": "eno1",

        # For test_local
        "local": {"data_path": "/home/data"},

        # For test_fc
        "fc": {
            "boot_lun": ["36005076300810b3e0000000000000025"],
            "avl_luns": ["36005076300810b3e0000000000000026", "36005076300810b3e0000000000000027"]
        }
    },

    "dell-per515-01.lab.eng.pek2.redhat.com": {
        "ip": "10.73.73.17",
        "password": "redhat",
        "primary_nic": "em2",

        # For test_local
        "local": {"data_path": "/home/data"},

        # For test_scsi
        "scsi": {
            "boot_lun": ["360a9800050334c33424b41762d726954"],
            "avl_luns": ["360a9800050334c33424b41762d736d45", "360a9800050334c33424b41762d745551"],
            "lun_address": "10.73.194.25",
            "lun_port": "3260",
            "lun_target": "iqn.1992-08.com.netapp:sn.135053389"},

        # For test_bond/test_vlan/test_bv
        "network": {
            "bond": {"name": "bond0",
                     "slaves": ["em2", "em1"],
                     "em1": "08:9e:01:63:2c:b2",
                     "em2": "08:9e:01:63:2c:b3"},

            "vlan": {"id": "50",
                     "nics": ["p2p1", "p2p2", "p3p1"],
                     "p2p1": "00:1b:21:a6:64:6c",
                     "p2p2": "00:1b:21:a6:64:6d",
                     "p3p1": "00:1b:21:a6:3d:7a"},

            "bv": {"bond_name": "bond1",
                   "vlan_id": "50",
                   "slaves": ["p2p1", "p2p2", "p3p1"],
                   "p2p1": "00:1b:21:a6:64:6c",
                   "p2p2": "00:1b:21:a6:64:6d",
                   "p3p1": "00:1b:21:a6:3d:7a"}
        }
    },

    "ibm-x3650m5-04.lab.eng.pek2.redhat.com": {
        "ip": "10.73.130.225",
        "password": "redhat",
        "primary_nic": "eno1",

        # For test_local
        "local": {"data_path": "/home/data"},

        # For test_bond/test_vlan/test_bv
        "network": {
            "bond": {"name": "bond0",
                     "slaves": ["eno1", "eno2"],
                     "eno1": "08:94:ef:21:c0:4d",
                     "eno2": "08:94:ef:21:c0:4e"},
            "vlan": {"id": "50",
                     "nics": ["eno3", "eno4"],
                     "eno3": "08:94:ef:21:c0:4f",
                     "eno4": "08:94:ef:21:c0:50"},

            "bv": {"bond_name": "bond1",
                   "vlan_id": "50",
                   "slaves": ["eno3", "eno4"],
                   "eno3": "08:94:ef:21:c0:4f",
                   "eno4": "08:94:ef:21:c0:50"}
        }
    },

    "dell-per730-35.lab.eng.pek2.redhat.com": {
        "ip": "10.73.131.65",
        "password": "redhat",
        "primary_nic": "em1",

        # For test_local
        "local": {"data_path": "/home/data"},

        # For test_bond/test_vlan/test_bv
        "network": {
            "bond": {"name": "bond0",
                     "slaves": ["em1", "em2"],
                     "em1": "24:6e:96:19:b9:a4",
                     "em2": "24:6e:96:19:b9:a5"},

            "vlan": {"id": "50",
                     "nics": ["p7p1", "p7p2"],
                     "p7p1": "a0:36:9f:9d:3b:fe",
                     "p7p2": "a0:36:9f:9d:3b:ff"},

            "bv": {"bond_name": "bond1",
                   "vlan_id": "50",
                   "slaves": ["eno3", "eno4"],
                   "eno3": "08:94:ef:21:c0:4f",
                   "eno4": "08:94:ef:21:c0:50"}
        }
    },

    "dell-per730-34.lab.eng.pek2.redhat.com": {
        "ip": "",
        "password": "redhat",
        "primary_nic": "em1",

        # For test_local
        "local": {"data_path": "/home/data"},

        # For test_bond/test_vlan/test_bv
        "network": {
            "bond": {"name": "bond0",
                     "slaves": ["em1", "em2"],
                     "em1": "24:6e:96:19:bb:70",
                     "em2": "24:6e:96:19:bb:71"},

            "vlan": {"id": "50",
                     "nics": ["em3", "em4"],
                     "em3": "24:6e:96:19:bb:72",
                     "em4": "24:6e:96:19:bb:73"},

            "bv": {"bond_name": "bond1",
                   "vlan_id": "50",
                   "slaves": ["em3", "em4"],
                   "em3": "24:6e:96:19:bb:72",
                   "em4": "24:6e:96:19:bb:73"}
        }
    }
}
