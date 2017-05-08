import base64
import time
import requests
import shutil
import re


class RhevmAction:
    """a rhevm rest-client warpper class
    currently can registe a rhvh to rhevm
    example:
    RhevmAction("rhevm-40-1.englab.nay.redhat.com").add_new_host("10.66.8.217", "autotest01", "redhat")
    """

    auth_format = "{user}@{domain}:{password}"
    api_url = "https://{rhevm_fqdn}/ovirt-engine/api/{item}"

    headers = {
        "Prefer": "persistent-auth",
        "Accept": "application/json",
        "Content-type": "application/xml"
    }

    cert_url = ("https://{rhevm_fqdn}/ovirt-engine/services"
                "/pki-resource?resource=ca-certificate&format=X509-PEM-CA")

    rhevm_cert = "/tmp/rhevm.cert"

    def __init__(self,
                 rhevm_fqdn,
                 user="admin",
                 password="password",
                 domain="internal"):

        self.rhevm_fqdn = rhevm_fqdn
        self.user = user
        self.password = password
        self.domain = domain
        self.token = base64.b64encode(
            self.auth_format.format(
                user=self.user, domain=self.domain, password=self.password))
        self.headers.update({
            "Authorization": "Basic {token}".format(token=self.token)
        })
        self._get_rhevm_cert_file()
        self.req = requests.Session()

    def _get_rhevm_cert_file(self):
        r = requests.get(self.cert_url.format(rhevm_fqdn=self.rhevm_fqdn),
                         stream=True,
                         verify=False)

        if r.status_code == 200:
            with open(self.rhevm_cert, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        else:
            raise RuntimeError("Can not get the cert file from %s" %
                               self.rhevm_fqdn)

    ###################################
    # Datacenter related functions
    ###################################
    def create_datacenter(self, dc_name, is_local=False):
        api_url = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn,
            item="datacenters")

        new_dc_post_body = '''
        <data_center>
          <name>{dc_name}</name>
          <local>{is_local}</local>
        </data_center>
        '''
        body = new_dc_post_body.format(
            dc_name=dc_name, is_local=is_local)

        r = self.req.post(
            api_url, headers=self.headers, verify=self.rhevm_cert, data=body)

        if r.status_code != 201:
            print r.text
            raise RuntimeError(
                "Failed to add new data center")

    def remove_datacenter(self, dc_name, force=False):
        api_url_base = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn,
            item="datacenters")

        dc_id = self.list_datacenter(dc_name)['id']
        api_url = api_url_base + '/{}'.format(dc_id)

        params = {'force': force}
        r = self.req.delete(
            api_url, headers=self.headers, verify=self.rhevm_cert, params=params)

        if r.status_code != 200:
            print r.text
            raise RuntimeError("Can not remove datacenter %s" % dc_name)

    def list_datacenter(self, dc_name):
        api_url = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn,
            item="datacenters")

        r = self.req.get(api_url, headers=self.headers, verify=self.rhevm_cert)

        if r.status_code != 200:
            print r.text
            raise RuntimeError("Can not list datacenters from %s" % self.rhevm_fqdn)

        dcs = r.json()
        if dcs:
            for dc in dcs['data_center']:
                if dc['name'] == dc_name:
                    return dc
        else:
            return

    ##################################
    # Cluster related functions
    ##################################
    def create_cluster(self, dc_name, cluster_name, cpu_type):
        api_url = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn,
            item="clusters")

        new_cluster_post_body = '''
        <cluster>
          <name>{cluster_name}</name>
          <cpu>
            <type>{cpu_type}</type>
          </cpu>
          <data_center>
            <name>{dc_name}</name>
          </data_center>
        </cluster>
        '''
        body = new_cluster_post_body.format(
            dc_name=dc_name, cluster_name=cluster_name, cpu_type=cpu_type)

        r = self.req.post(
            api_url, headers=self.headers, verify=self.rhevm_cert, data=body)

        if r.status_code != 201:
            print r.text
            raise RuntimeError(
                "Failed to add new cluster")

    def remove_cluster(self, cluster_name):
        api_url_base = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn,
            item="clusters")
        cluster_id = self.list_cluster(cluster_name)['id']
        api_url = api_url_base + '/{}'.format(cluster_id)

        r = self.req.delete(api_url, headers=self.headers, verify=self.rhevm_cert)

        if r.status_code != 200:
            print r.text
            raise RuntimeError("Can not remove cluster %s" % cluster_name)

    def list_cluster(self, cluster_name):
        api_url = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn,
            item="clusters")

        r = self.req.get(api_url, headers=self.headers, verify=self.rhevm_cert)

        if r.status_code != 200:
            print r.text
            raise RuntimeError("Can not list clusters from %s" % self.rhevm_fqdn)

        clusters = r.json()
        if clusters:
            for cluster in clusters['cluster']:
                if cluster['name'] == cluster_name:
                    return cluster
        else:
            return

    def update_cluster_cpu(self, cluster_name, cpu_type):
        api_url_base = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn,
            item="clusters")
        cluster_id = self.list_cluster(cluster_name)['id']
        api_url = api_url_base + "/%s" % cluster_id

        cluster_cpu_post_body = '''
        <cluster>
          <cpu>
            <type>{cpu_type}</type>
          </cpu>
        </cluster>
        '''
        body = cluster_cpu_post_body.format(cpu_type=cpu_type)

        r = self.req.put(api_url, headers=self.headers, verify=self.rhevm_cert, data=body)

        if r.status_code != 200:
            print r.text
            raise RuntimeError("Failed to update cluster cpu type")

    ############################################
    # Host related functions
    ############################################
    def create_new_host(self, ip, host_name, password, cluster_name='Default'):
        api_url = self.api_url.format(rhevm_fqdn=self.rhevm_fqdn, item="hosts")

        new_host_post_body = '''
        <host>
            <name>{host_name}</name>
            <address>{ip}</address>
            <root_password>{password}</root_password>
            <cluster>
              <name>{cluster_name}</name>
            </cluster>
        </host>
        '''
        body = new_host_post_body.format(
            host_name=host_name, ip=ip, password=password, cluster_name=cluster_name)

        r = self.req.post(
            api_url, data=body, headers=self.headers, verify=self.rhevm_cert)

        if r.status_code != 201:
            print r.text
            raise RuntimeError(
                "Failed to add new host, may be host already imported")

    def deactive_host(self, host_name):
        api_url_base = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn, item='hosts')
        host_id = self.list_host(host_name)['id']
        api_url = api_url_base + "/%s/deactivate" % host_id
        # print api_url
        r = self.req.post(
            api_url,
            headers=self.headers,
            verify=self.rhevm_cert,
            data="<action/>")
        ret = r.json()
        if ret['status'] != 'complete':
            raise RuntimeError(ret['fault']['detail'])

    def remove_host(self, host_name):
        api_url_base = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn, item="hosts")

        host_status = self.list_host(host_name)['status']
        if host_status == 'up':
            self.deactive_host(host_name)

        host_id = self.list_host(host_name)['id']
        time.sleep(5)
        api_url = api_url_base + '/%s' % host_id

        r = self.req.delete(
            api_url, headers=self.headers, verify=self.rhevm_cert)

        if r.status_code != 200:
            print r.text
            raise RuntimeError("Can not delete host %s" % host_name)

    def list_host(self, host_name):
        api_url = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn,
            item="hosts")
        r = self.req.get(api_url, headers=self.headers, verify=self.rhevm_cert)

        if r.status_code != 200:
            print r.text
            raise RuntimeError("Can not list hosts from %s" % self.rhevm_fqdn)

        hosts = r.json()
        if hosts:
            for host in hosts['host']:
                if host['name'] == host_name:
                    return host
        else:
            return

    ######################################
    # Storage domain related functions
    ######################################
    def create_plain_storage_domain(
            self,
            domain_name,
            domain_type,
            storage_type,
            storage_addr,
            storage_path,
            host):
        storage_domain_post_body = '''
        <storage_domain>
          <name>{domain_name}</name>
          <type>{domain_type}</type>
          <storage>
            <type>{storage_type}</type>
            <address>{storage_addr}</address>
            <path>{storage_path}</path>
          </storage>
          <host>
            <name>{host}</name>
          </host>
        </storage_domain>
        '''
        api_url = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn, item="storagedomains")

        body = storage_domain_post_body.format(
            domain_name=domain_name,
            domain_type=domain_type,
            storage_type=storage_type,
            storage_addr=storage_addr,
            storage_path=storage_path,
            host=host)

        r = self.req.post(
            api_url, data=body, headers=self.headers, verify=self.rhevm_cert)

        if r.status_code != 201:
            print r.text
            raise RuntimeError("Failed to add new storage domain %s" % domain_name)

    def create_fc_scsi_storage_domain(
            self,
            domain_name,
            domain_type,
            storage_type,
            logical_unit_id,
            host):
        api_url = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn, item="storagedomains")

        storage_domain_post_body = '''
        <storage_domain>
          <name>{domain_name}</name>
          <type>{domain_type}</type>
          <storage>
            <type>{storage_type}</type>
            <logical_units>
              <logical_unit id={logical_unit_id}/>
            </logical_units>
          </storage>
          <host>
            <name>{host}</name>
          </host>
        </storage_domain>
        '''

        body = storage_domain_post_body.format(
            domain_name=domain_name,
            domain_type=domain_type,
            storage_type=storage_type,
            storage_addr=logical_unit_id,
            host=host)

        r = self.req.post(
            api_url, data=body, headers=self.headers, verify=self.rhevm_cert)

        if r.status_code != 201:
            print r.text
            raise RuntimeError("Failed to add new storage domain %s" % domain_name)

    def list_host_storage(self, host_name):
        api_url_base = self.api_url.format(rhevm_fqdn=self.rhevm_fqdn, item="hosts")

        host_id = self.list_host(host_name)['id']
        api_url = api_url_base + '/{}'.format(host_id) + '/storage'

        r = self.req.get(api_url, headers=self.headers, verify=self.rhevm_cert)

        if r.status_code != 200:
            print r.text
            raise RuntimeError("Can not list storage of %s" % host_name)

        sts = r.json()
        return sts

    def get_unused_logical_units(self, host_name):
        storages = self.list_host_storage(host_name)
        fc_scsi_storage_dict = {}
        if storages:
            if 'logical_units' in storages.keys():
                for host_storage in storages['host_storages']:
                    if re.search('iscsi', host_storage['type']):
                        if host_storage['logical_units']['logical_unit']['status'] != 'used':
                            new_unit_dict = {'iscsi': host_storage['logical_units']['logical_unit']['id']}
                            fc_scsi_storage_dict.update(new_unit_dict)
                    elif re.search('fc', host_storage['type']):
                        if host_storage['logical_units']['logical_unit']['status'] != 'used':
                            new_unit_dict = {'fc': host_storage['logical_units']['logical_unit']['id']}
                            fc_scsi_storage_dict.update(new_unit_dict)
        return fc_scsi_storage_dict

    def attach_sd_to_datacenter(self, sd_name, dc_name):
        api_url_base = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn, item="datacenters")

        dc_id = self.list_datacenter(dc_name)['id']
        api_url = api_url_base + '/%s/storagedomains' % dc_id

        new_storage_post_body = '''
        <storage_domain>
          <name>{storage_name}</name>
        </storage_domain>
        '''
        body = new_storage_post_body.format(storage_name=sd_name)

        r = self.req.post(
            api_url, data=body, headers=self.headers, verify=self.rhevm_cert)

        if r.status_code != 201:
            print r.text
            raise RuntimeError("Failed to attach storage %s to datacenter %s" %
                               (sd_name, dc_name))

    def list_storage_domain(self, sd_name):
        api_url = self.api_url.format(rhevm_fqdn=self.rhevm_fqdn, item="storagedomains")

        r = self.req.get(api_url, headers=self.headers, verify=self.rhevm_cert)

        if r.status_code != 200:
            print r.text
            raise RuntimeError("Can not list storage domains from %s" % self.rhevm_fqdn)

        sds = r.json()
        if sds:
            for sd in sds['storage_domain']:
                if sd['name'] == sd_name:
                    return sd
        else:
            return

    """
    def is_attached_sd(self, sd_id, sd_name):
        api_url_base = self.api_url.format(rhevm_fqdn=self.rhevm_fqdn, item="storagedomains")

        api_url = api_url_base + '/{}'.format(sd_id) + '/isattached'
        post_body = '''
        <storage_domain>
          <name>{sd_name}</name>
        </storage_domain>
        '''
        body = post_body.format(sd_name=sd_name)
        r = self.req.post(api_url, data=body, headers=self.headers, verify=self.rhevm_cert)
        print r.json()
        if r.status_code != 201:
            print r.text
            raise RuntimeError("Can not list storage domains from %s" % self.rhevm_fqdn)
        return r.json()
    """

    ##########################################
    # Disk related functions
    ##########################################
    def create_image_disk(self, sd_name, disk_name, size):
        api_url = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn, item="disks")

        new_disk_post_body = '''
        <disk>
          <storage_domains>
            <storage_domain id={sd_id}/>
          </storage_domains>
          <name>{disk_name}</name>
          <provisioned_size>{size}</provisioned_size>
          <format>cow</format>
        </disk>
        '''
        sd_id = self.list_storage_domain(sd_name)['id']
        body = new_disk_post_body.format(
            sd_id=sd_id, disk_name=disk_name, size=size)

        print body
        r = self.req.post(
            api_url, data=body, headers=self.headers, verify=self.rhevm_cert)

        if r.status_code != 201:
            print r.text
            raise RuntimeError("Failed to create image disk")

    def create_direct_lun_disk(self, disk_name, host_name, lun_type, unit_id):
        api_url = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn, item="disks")

        new_disk_post_body = '''
        <disk>
          <alias>{disk_name}</alias>
          <lun_storage>
            <host>
              name={host_name}
            </host>
            <type>{lun_type}</type>
            <logical_units>
              <logical_unit id={unit_id}/>
            </logical_units>
          </lun_storage>
        </disk>
        '''
        body = new_disk_post_body.format(
            disk_name=disk_name, host_name=host_name, lun_type=lun_type, unit_id=unit_id)

        r = self.req.post(
            api_url, data=body, headers=self.headers, verify=self.rhevm_cert)

        if r.status_code != 201:
            print r.text
            raise RuntimeError("Failed to create direct lun disk")

    def attach_disk_to_vm(self, disk_name, vm_name):
        api_url_base = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn, item="vms")

        vm_id = self.list_vm(vm_name)['id']

        api_url = api_url_base + '/{}'.format(vm_id) + '/diskattachments'

        attach_disk_post_body = '''
        <disk_attachment>
          <bootable>true</bootable>
          <interface>ide</interface>
          <active>true</active>
          <disk>name={disk_name}</disk>
        </disk_attachment>
        '''

        body = attach_disk_post_body.format(disk_name=disk_name)

        r = self.req.post(
            api_url,
            data=body,
            headers=self.headers,
            verify=self.rhevm_cert)

        if r.status_code != 201:
            print r.text
            raise RuntimeError("Failed to attach disk %s to VM %s" % (
                disk_name, vm_name))

    ##########################################
    # VM related functions
    ##########################################
    def create_vm(self, vm_name, tpl_name="Blank", cluster="default"):
        api_url_base = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn, item="vms")

        new_vm_body = '''
        <vm>
        <name>{vm_name}</name>
        <description>{vm_name}</description>
        <cluster>
        <name>{cluster_name}</name>
        </cluster>
        <template>
        <name>{tpl_name}</name>
        </template>
        </vm>
        '''
        body = new_vm_body.format(
            vm_name=vm_name, tpl_name=tpl_name, cluster_name=cluster)

        r = self.req.post(
            api_url_base,
            data=body,
            headers=self.headers,
            verify=self.rhevm_cert)

        if r.status_code != 201:
            print r.text
            raise RuntimeError("Failed to create viratual machine")
        else:
            return r.json()["id"]

    def list_vm(self, vm_name):
        api_url_base = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn, item="vms")

        r = self.req.get(
            api_url_base,
            headers=self.headers,
            verify=self.rhevm_cert)

        if r.status_code != 200:
            print r.text
            raise RuntimeError("Can not list vms from %s" % self.rhevm_fqdn)

        vms = r.json()
        if vms:
            for vm in vms['vm']:
                if vm['name'] == vm_name:
                    return vm
        else:
            return

    def start_vm(self, vm_name):
        api_url_base = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn, item="vms")

        vm_id = self.list_vm(vm_name)['id']
        api_url = api_url_base + '/%s/start' % vm_id

        vm_action = '''
        <action>
          <vm>
            <os>
              <boot>
                <devices>
                  <device>hd</device>
                </devices>
              </boot>
            </os>
          </vm>
        </action>
        '''
        r = self.req.post(
            api_url,
            data=vm_action,
            headers=self.headers,
            verify=self.rhevm_cert)

        if r.status_code != 200:
            print r.text
            raise RuntimeError("Failed to start vm %s" % vm_name)

    def operate_vm(self, vm_name, operation):
        normal_operations = ['start', 'reboot', 'shutdown', 'stop', 'suspend']
        if operation not in normal_operations:
            raise RuntimeError("Only support operations ['reboot', 'shutdown', 'stop', 'suspend']")

        api_url_base = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn, item="vms")

        vm_id = self.list_vm(vm_name)['id']
        api_url = api_url_base + '/%s/%s' % (vm_id, operation)

        vm_action = '''
        <action/>
        '''
        r = self.req.post(
            api_url,
            data=vm_action,
            headers=self.headers,
            verify=self.rhevm_cert)

        if r.status_code != 200:
            print r.text
            raise RuntimeError("Failed to %s vm %s" % (operation, vm_name))

    def remove_vm(self, vm_name):
        api_url_base = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn, item="vms")

        vm_id = self.list_vm(vm_name)['id']
        api_url = api_url_base + '/%s' % vm_id

        r = self.req.delete(
            api_url,
            headers=self.headers,
            verify=self.rhevm_cert)

        if r.status_code != 200:
            print r.text
            raise RuntimeError("Failed to remove vm %s" % vm_name)

    def create_vm_disk_attachment(self, vm_name, sd_name, disk_name, disk_size):
        api_url_base = self.api_url.format(
            rhevm_fqdn=self.rhevm_fqdn, item="vms")

        vm_id = self.list_vm(vm_name)['id']
        api_url = api_url_base + '/{}'.format(vm_id) + '/diskattachments'

        attach_disk_post_body = '''
        <disk_attachment>
          <bootable>false</bootable>
          <interface>virtio</interface>
          <active>true</active>
          <disk>
            <format>cow</format>
            <name>{disk_name}</name>
            <provisioned_size>{disk_size}</provisioned_size>
            <storage_domains>
              <storage_domain>
                <name>{sd_name}</name>
              </storage_domain>
            </storage_domains>
          </disk>
        </disk_attachment>
        '''

        body = attach_disk_post_body.format(
            disk_name=disk_name, disk_size=disk_size, sd_name=sd_name)

        r = self.req.post(
            api_url,
            data=body,
            headers=self.headers,
            verify=self.rhevm_cert)

        if r.status_code != 201:
            print r.text
            raise RuntimeError("Failed to create disk attachment %s for VM %s" % (
                disk_name, vm_name))


if __name__ == '__main__':
    rhvm = RhevmAction("rhvm41-vdsm-auto.lab.eng.pek2.redhat.com")

    vm_name = "vdsm_local_vm"
    rhvm.start_vm(vm_name)
