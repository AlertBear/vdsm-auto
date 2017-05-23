import os
import tempfile
from fabric.api import settings, local, run
from fabric.exceptions import NetworkError
from constants import PROJECT_ROOT, NETWORK_SCRIPTS_DIR

network_scripts_dir = NETWORK_SCRIPTS_DIR
tpls_dir = os.path.join(PROJECT_ROOT, "libs", "templates")
bond_dir = os.path.join(tpls_dir, "bond")
vlan_dir = os.path.join(tpls_dir, "vlan")
bv_dir = os.path.join(tpls_dir, "bv")


def _update_kv(sfile, dfile, kv):
    for k, v in kv.items():
        cmd = "sed -i 's/{key}=.*/{key}=\"{value}\"/' {sfile} > {dfile}".format(
            key=k, value=v, sfile=sfile, dfile=dfile)
        local(cmd)


class NetworkAction:
    def __init__(self):
        self._host_ip = None
        self._host_pass = None

    @property
    def host_ip(self):
        return self._host_ip

    @host_ip.setter
    def host_ip(self, val):
        # TODO check val
        self._host_ip = val

    @property
    def host_pass(self):
        return self._host_pass

    @host_pass.setter
    def host_pass(self, val):
        self._host_pass = val

    def run_cmd(self, cmd, timeout=60):
        ret = None
        try:
            with settings(
                    host_string='root@' + self.host_ip,
                    password=self.host_pass,
                    disable_known_hosts=True,
                    connection_attempts=60):
                ret = run(cmd, quiet=True, timeout=timeout)
                if ret.succeeded:
                    return True, ret
                else:
                    return False, ret
        except NetworkError as e:
            return False, e

    def _get_pub_gw(self):
        cmd = "ip route list|grep default"
        out = self.run_cmd(cmd)
        pub_gw = out[1].split()[2]

        return pub_gw

    def _avoid_disc(self, pub_gw):
        # Add the route to avoid the disconnection from remote server
        cmd = "ip route add 10.0.0.0/8 via %s" % pub_gw
        self.run_cmd(cmd)

    def del_vlan_gw(self, vlan):
        # Delete the vlan gateway
        cmd = "ip route list|grep default|grep %s" % vlan
        out = local(cmd)

        vlan_gw = out[1].split()[2]
        cmd = "ip route del default via %s" % vlan_gw
        self.run_cmd(cmd)

    def _restore_pub_gw(self, pub_gw):
        cmd = "ip route list|grep default|grep %s" % pub_gw
        out = self.run_cmd(cmd)
        if not out[0]:
            # Add the original gateway
            cmd = "ip route add default via %s" % pub_gw
            self.run_cmd(cmd)

        cmd = "ip r s |grep %s" % "10.0.0.0/8"
        out = self.run_cmd(cmd)
        if not out[0]:
            # Delete the added route after the default was added
            cmd = "ip route del 10.0.0.0/8"
            self.run_cmd(cmd)

    def _mvfile(self, sfile, dfile):
        cmd = "mv {} {}".format(sfile, dfile)
        self.run_cmd(cmd)

    def _bak_file(self, file):
        file_dir = os.path.dirname(file)
        file_name = os.path.basename(file)
        bak_file = os.path.join(file_dir, file_name, '.bak')
        self._mvfile(file, bak_file)

    def setup_bond(self, bond_info):
        """
        bond_info:  {"name": "bond0", "slaves": ["em2", "em1"]}
        """
        # Find all the ifcfg-file templates
        bond_scfg = os.path.join(bond_dir, "ifcfg-bond0")
        slave1_scfg = os.path.join(bond_dir, "ifcfg-slave1")
        slave2_scfg = os.path.join(bond_dir, "ifcfg-slave2")

        bond = bond_info["name"]
        slave1 = bond_info["slaves"][0]
        slave2 = bond_info["slaves"][1]

        # Get the mac address of slaves
        cmd = "ip link show %s|grep 'link/ether'" % slave1
        out = self.run_cmd(cmd)
        slave1_mac = out[1].split()[1]
        cmd = "ip link show %s|grep 'link/ether'" % slave2
        out = self.run_cmd(cmd)
        slave2_mac = out[1].split()[1]

        # Update the templates to a tmp file
        s, bond_tcfg = tempfile.mkstemp()
        bond_cfg_kv = {"DEVICE": bond}
        _update_kv(bond_scfg, bond_tcfg, bond_cfg_kv)

        s, slave1_tcfg = tempfile.mkstemp()
        slave1_cfg_kv = {
            "DEVICE": slave1, "HWADDR": slave1_mac, "MASTER": bond}
        _update_kv(slave1_scfg, slave1_tcfg, slave1_cfg_kv)

        s, slave2_tcfg = tempfile.mkstemp()
        slave2_cfg_kv = {
            "DEVICE": slave1, "HWADDR": slave2_mac, "MASTER": bond}
        _update_kv(slave2_scfg, slave2_tcfg, slave2_cfg_kv)

        # Move the tmp files to /etc/sysconfig/network-scripts
        bond_dcfg = os.path.join(network_scripts_dir, "ifcfg-%s" % bond)
        slave1_dcfg = os.path.join(network_scripts_dir, "ifcfg-%s" % slave1)
        slave2_dcfg = os.path.join(network_scripts_dir, "ifcfg-%s" % slave2)
        files_dict = {bond_tcfg: bond_dcfg,
                      slave1_tcfg: slave1_dcfg,
                      slave2_tcfg: slave2_dcfg}

        for tfile, dfile in files_dict.items():
            if os.path.isfile(dfile):
                self._bak_file(dfile)
            self._mvfile(tfile, dfile)

        # Restart the service
        cmd = "service network restart"
        self.run_cmd(cmd)

    def setup_vlan(self, vlan_info):
        """
        vlan_info:  {"id": "50", "nics": ["p2p1"]}
        """
        # Find all the ifcfg-file templates
        nic_scfg = os.path.join(vlan_dir, "ifcfg-nic1")
        vlan_scfg = os.path.join(vlan_dir, "ifcfg-nic1.00")

        nic = vlan_info["nics"][0]
        vlan_id = vlan_info["id"]
        vlan = nic + '.' + vlan_id

        # Get the mac address of slaves
        cmd = "ip link show %s|grep 'link/ether'" % nic
        out = self.run_cmd(cmd)
        nic_mac = out[1].split()[1]

        # Update the templates to a tmp file
        s, nic_tcfg = tempfile.mkstemp()
        nic_cfg_kv = {"DEVICE": nic, "HWADDR": nic_mac}
        _update_kv(nic_scfg, nic_tcfg, nic_cfg_kv)

        s, vlan_tcfg = tempfile.mkstemp()
        vlan_cfg_kv = {"DEVICE": vlan}
        _update_kv(vlan_scfg, vlan_tcfg, vlan_cfg_kv)

        # Move the tmp file to /etc/sysconfig/network-scripts/
        nic_dcfg = os.path.join(network_scripts_dir, "ifcfg-%s" % nic)
        vlan_dcfg = os.path.join(network_scripts_dir, "ifcfg-%s" % vlan)
        files_dict = {nic_tcfg: nic_dcfg,
                      vlan_tcfg: vlan_dcfg}
        for tfile, dfile in files_dict.items():
            if os.path.isfile(dfile):
                self._bak_file(dfile)
            self._mvfile(tfile, dfile)

        # Add a gateway to avoid the disconnection by restart the network
        pub_gw = self._get_pub_gw()
        self._avoid_disc(pub_gw)

        # Bring up the vlan ip, may create the internal default gateway
        cmd = "ifup %s" % vlan
        self.run_cmd(cmd)

        # Delete the internal vlan gateway such as "192.168.xx.1"
        self.del_vlan_gw(vlan)

        # Restore the pub gateway
        self._restore_pub_gw(pub_gw)

    def setup_bv(self, bv_info):
        """
        bv_info: {"vlan_id": "50", "bond_name": "bond1", "slaves": ["p2p1", "p2p2"]}
        """
        # Find all the ifcfg-file templates
        bond_scfg = os.path.join(bv_dir, "ifcfg-bond1")
        slave1_scfg = os.path.join(bv_dir, "ifcfg-slave1")
        slave2_scfg = os.path.join(bv_dir, "ifcfg-slave2")
        vlan_scfg = os.path.join(bv_dir, "ifcfg-bond1.00")

        bond = bv_info["bond_name"]
        slave1 = bv_info["slaves"][0]
        slave2 = bv_info["slaves"][1]
        vlan_id = bv_info["id"]
        vlan = bond + '.' + vlan_id

        # Get the mac address of slaves
        cmd = "ip link show %s|grep 'link/ether'" % slave1
        out = self.run_cmd(cmd)
        slave1_mac = out[1].split()[1]
        cmd = "ip link show %s|grep 'link/ether'" % slave2
        out = self.run_cmd(cmd)
        slave2_mac = out[1].split()[1]

        # Update the templates to a tmp file
        s, bond_tcfg = tempfile.mkstemp()
        bond_cfg_kv = {"DEVICE": bond}
        _update_kv(bond_scfg, bond_tcfg, bond_cfg_kv)

        s, slave1_tcfg = tempfile.mkstemp()
        slave1_cfg_kv = {
            "DEVICE": slave1, "HWADDR": slave1_mac, "MASTER": bond}
        _update_kv(slave1_scfg, slave1_tcfg, slave1_cfg_kv)

        s, slave2_tcfg = tempfile.mkstemp()
        slave2_cfg_kv = {
            "DEVICE": slave1, "HWADDR": slave2_mac, "MASTER": bond}
        _update_kv(slave2_scfg, slave2_tcfg, slave2_cfg_kv)

        s, vlan_tcfg = tempfile.mkstemp()
        vlan_cfg_kv = {"DEVICE": vlan}
        _update_kv(vlan_scfg, vlan_tcfg, vlan_cfg_kv)

        # Move the tmp file to /etc/sysconfig/network-scripts/
        bond_dcfg = os.path.join(network_scripts_dir, "ifcfg-%s" % bond)
        slave1_dcfg = os.path.join(network_scripts_dir, "ifcfg-%s" % slave1)
        slave2_dcfg = os.path.join(network_scripts_dir, "ifcfg-%s" % slave2)
        vlan_dcfg = os.path.join(network_scripts_dir, "ifcfg-%s" % vlan)
        files_dict = {bond_tcfg: bond_dcfg,
                      slave1_tcfg: slave1_dcfg,
                      slave2_tcfg: slave2_dcfg,
                      vlan_tcfg: vlan_dcfg}

        for tfile, dfile in files_dict.items():
            if os.path.isfile(dfile):
                self._bak_file(dfile)
            self._mvfile(tfile, dfile)

        # Add a gateway to avoid the disconnection by restart the network
        pub_gw = self._get_pub_gw()
        self._avoid_disc(pub_gw)

        # Bring up the vlan ip, may create the internal default gateway
        cmd = "service network restart"
        self.run_cmd(cmd)

        # Delete the internal vlan gateway such as "192.168.xx.1"
        self.del_vlan_gw(vlan)

        # Restore the pub gateway
        self._restore_pub_gw(pub_gw)
