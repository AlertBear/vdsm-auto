
default = {
    "TAG": ["RHVH41"],
    "CONFIG": "tests/v41/conf.py",
    "DEPEND_MACHINE": [],
    "KSFILE": "default_tpl.ks",
    "CASES": [
        "tests/v41/test_local.py",
        "tests/v41/test_nfs.py",
    ]
}

fc = {
    "TAG": ["RHVH41"],
    "CONFIG": "tests/v41/conf.py",
    "DEPEND_MACHINE": [],
    "KSFILE": "fc_tpl.ks",
    "CASES": [
        "tests/v41/test_fc.py",
    ]
}

scsi = {
    "TAG": ["RHVH41"],
    "CONFIG": "tests/v41/conf.py",
    "DEPEND_MACHINE": [],
    "KSFILE": "scsi_tpl.ks",
    "CASES": [
        "tests/v41/test_scsi.py",
    ]
}

bond_anaconda = {
    "TAG": ["RHVH41"],
    "CONFIG": "tests/v41/conf.py",
    "DEPEND_MACHINE": [],
    "KSFILE": "bond_tpl.ks",
    "CASES": [
        "tests/v41/test_bond_anaconda.py",
    ]
}

vlan_anaconda = {
    "TAG": ["RHVH41"],
    "CONFIG": "tests/v41/conf.py",
    "DEPEND_MACHINE": [],
    "KSFILE": "vlan_tpl.ks",
    "CASES": [
        "tests/v41/test_vlan_anaconda.py",
    ]
}

bv_anaconda = {
    "TAG": ["RHVH41"],
    "CONFIG": "tests/v41/conf.py",
    "DEPEND_MACHINE": [],
    "KSFILE": "bv_tpl.ks",
    "CASES": [
        "tests/v41/test_bv_anaconda.py",
    ]
}

bond_ifcfg = {
    "TAG": ["RHVH41"],
    "CONFIG": "tests/v41/conf.py",
    "DEPEND_MACHINE": [],
    "KSFILE": "default_tpl.ks",
    "CASES": [
        "tests/v41/test_bond_ifcfg.py",
    ]
}

vlan_ifcfg = {
    "TAG": ["RHVH41"],
    "CONFIG": "tests/v41/conf.py",
    "DEPEND_MACHINE": [],
    "KSFILE": "default_tpl.ks",
    "CASES": [
        "tests/v41/test_vlan_ifcfg.py",
    ]
}

bv_ifcfg = {
    "TAG": ["RHVH41"],
    "CONFIG": "tests/v41/conf.py",
    "DEPEND_MACHINE": [],
    "KSFILE": "default_tpl.ks",
    "CASES": [
        "tests/v41/test_bv_ifcfg.py",
    ]
}
