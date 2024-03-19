"""
Copyright (c) 2020 Cisco Systems Inc or its affiliates.

All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
--------------------------------------------------------------------------------

Name:       fmc.py
Purpose:    This is contains FMC related REST methods
"""

import time
import requests
import logging
import json
import ast
from utility import TokenCaller
import utility as utl
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logging.basicConfig(force=True, level="INFO")
logging.getLogger("paramiko").setLevel(logging.WARNING)
logger = logging.getLogger()

class FirepowerManagementCenter:
    """
        FirepowerManagementCenter class has REST methods for FMC connections
    """
    def __init__(self, fmc_server, username, password, accesspolicy=None):
        self.server = 'https://' + fmc_server
        self.username = username
        self.password = password
        self.headers = []
        self.domain_uuid = ""
        self.authTokenTimestamp = 0
        self.authTokenMaxAge = 30*60  # seconds - 30 minutes is the max without using refresh
        self.accessPolicyName = accesspolicy
        
        #Input for calling TOKEN MANAGER FUNCTION
        self.compartmentId = ""
        self.appName = ""
        self.tokenEndpoint = ""

    def rest_get(self, url):
        """
        Purpose:    Issue REST get to the specified URL
        Parameters: url
        Returns:    r.text is the text response (r.json() is a python dict version of the json response)
                    r.status_code = 2xx on success
        Raises:
        """
        # if the token is too old then get another
        if time.time() > self.authTokenMaxAge + self.authTokenTimestamp:
            logging.debug("FMC: Token got expired in between, requesting a new authToken. Time since last token: {0:.2f}".format(int(time.time()) - self.authTokenTimestamp))
            tokenHandler = TokenCaller(self.compartmentId,self.appName)
            token = tokenHandler.invoke_token_manager(self.tokenEndpoint)
            self.write_existing_token(token)
        try:
            # REST call with SSL verification turned off:
            logging.debug("FMC: Request: " + url)
            r = requests.get(url, headers=self.headers, verify=False)
            # REST call with SSL verification turned on:
            # r = requests.get(url, headers=headers, verify='/path/to/ssl_certificate')
            status_code = r.status_code
            resp = r.text
            logging.debug("FMC: Response status_code: " + str(status_code))
            logging.debug("FMC: Response body: " + str(resp))
            if 200 <= status_code <= 300:
                # logging.debug("GET successful. Response data --> ")
                # json_resp = json.loads(resp)
                # logging.debug(json.dumps(json_resp,sort_keys=True,indent=4, separators=(',', ': ')))
                pass
            else:
                r.raise_for_status()
                #raise Exception("Error occurred in Get -->"+resp)
        except requests.exceptions.HTTPError as err:
            raise Exception("Error in connection --> "+str(err))
        finally:
            if r: r.close()
            return r

    def rest_post(self, url, post_data):
        """
        Purpose:    Issue REST post to the specified url with the post_data provided
        Parameters: url, post data
        Returns:    This function will return 'r' which is the response from the post:
                    r.text is the text response (r.json() is a python dict version of the json response)
                    r.status_code = 2xx on success
        Raises:     Error occurred in post
        """
        if time.time() > self.authTokenMaxAge + self.authTokenTimestamp:
            logging.debug("FMC: Token got expired in between, requesting a new authToken. Time since last token: {0:.2f}".format(int(time.time()) - self.authTokenTimestamp))
            tokenHandler = TokenCaller(self.compartmentId,self.appName)
            token = tokenHandler.invoke_token_manager(self.tokenEndpoint)
            self.write_existing_token(token)
        try:
            # REST call with SSL verification turned off:
            logging.debug("FMC: Request: " + url)
            logging.debug("FMC: Post_data " + str(post_data))
            r = requests.post(url, data=json.dumps(post_data), headers=self.headers, verify=False)
            # REST call with SSL verification turned on:
            # r = requests.post(url,data=json.dumps(post_data), headers=self.headers, verify='/path/to/ssl_certificate')
            status_code = r.status_code
            resp = r.text
            logging.debug("FMC: Response status_code: " + str(status_code))
            logging.debug("FMC: Response body: " + str(resp))
            # logging.debug("Status code is: "+str(status_code))
            if 201 <= status_code <= 202:
                # json_resp = json.loads(resp)
                # logging.debug(json.dumps(json_resp,sort_keys=True,indent=4, separators=(',', ': ')))
                pass
            else:
                r.raise_for_status()
                raise Exception("Error occurred in POST --> "+resp)
        except requests.exceptions.HTTPError as err:
            raise Exception("Error in connection --> "+str(err))
        finally:
            if r: r.close()
            return r

    def rest_put(self, url, put_data):
        """
        Purpose:    Issue REST put to specific url with the put_data provided
        Parameters: url, put data
        Returns:    This function will return 'r' which is the response from the put:
                    r.text is the text response (r.json() is a python dict version of the json response)
                    r.status_code = 2xx on success
        Raises:
        """
        if time.time() > self.authTokenMaxAge + self.authTokenTimestamp:
            logging.debug("FMC: Token got expired in between, requesting a new authToken. Time since last token: {0:.2f}".format(int(time.time()) - self.authTokenTimestamp))
            tokenHandler = TokenCaller(self.compartmentId,self.appName)
            token = tokenHandler.invoke_token_manager(self.tokenEndpoint)
            self.write_existing_token(token)
        try:
            # REST call with SSL verification turned off:
            logging.debug("FMC: Request: " + url)
            logging.debug("FMC: Put_data: " + str(put_data))
            r = requests.put(url, data=json.dumps(put_data), headers=self.headers, verify=False)
            # REST call with SSL verification turned on:
            # r = requests.put(url, data=json.dumps(put_data), headers=headers, verify='/path/to/ssl_certificate')
            status_code = r.status_code
            resp = r.text
            logging.info("FMC: Response status_code: " + str(status_code))
            logging.info("FMC: Response body: " + str(resp))
            if status_code == 200:
                pass
            else:
                r.raise_for_status()
                raise Exception("FMC: Error occurred in put -->" + resp)
        except requests.exceptions.HTTPError as err:
            raise Exception("FMC: Error in connection --> "+str(err))
        finally:
            if r: r.close()
            return r

    def rest_delete(self, url):
        """
        Purpose:    Issue REST delete to the specified URL
        Parameters: url
        Returns:    This function will return 'r' which is the response to the request:
                    r.text is the text response (r.json() is a python dict version of the json response)
                    r.status_code = 2xx on success
        Raises:
        """
        if time.time() > self.authTokenMaxAge + self.authTokenTimestamp:
            logging.debug("FMC: Token got expired in between, requesting a new authToken. Time since last token: {0:.2f}".format(int(time.time()) - self.authTokenTimestamp))
            tokenHandler = TokenCaller(self.compartmentId,self.appName)
            token = tokenHandler.invoke_token_manager(self.tokenEndpoint)
            self.write_existing_token(token)

        try:
            # REST call with SSL verification turned off:
            logging.debug("FMC: Request: " + url)
            r = requests.delete(url, headers=self.headers, verify=False)
            # REST call with SSL verification turned on:
            # r = requests.delete(url, headers=headers, verify='/path/to/ssl_certificate')
            status_code = r.status_code
            resp = r.text
            logging.debug("FMC: Response status_code: " + str(status_code))
            logging.debug("FMC: Response body: " + str(resp))
            if 200 <= status_code <= 300:
                # logging.debug("GET successful. Response data --> ")
                # json_resp = json.loads(resp)
                # logging.debug(json.dumps(json_resp,sort_keys=True,indent=4, separators=(',', ': ')))
                pass
            else:
                r.raise_for_status()
                raise Exception("Error occurred in Delete -->"+resp)
        except requests.exceptions.HTTPError as err:
            raise Exception("Error in connection --> "+str(err))
        finally:
            if r: r.close()
            return r

    def get_auth_token(self):
        """
        Purpose:    get a new REST authentication token
                    update the 'headers' variable
                    set a timestamp for the header (tokens expire)
        Parameters:
        Returns:
        Raises:
        """
        self.headers = {'Content-Type': 'application/json'}
        api_auth_path = "/api/fmc_platform/v1/auth/generatetoken"
        auth_url = self.server + api_auth_path
        try:
            # 2 ways of making a REST call are provided:
            # One with "SSL verification turned off" and the other with "SSL verification turned on".
            # The one with "SSL verification turned off" is commented out. If you like to use that then
            # uncomment the line where verify=False and comment the line with =verify='/path/to/ssl_certificate'
            # REST call with SSL verification turned off:
            r = requests.post(auth_url, headers=self.headers,
                              auth=requests.auth.HTTPBasicAuth(self.username, self.password), verify=False)
            # REST call with SSL verification turned on: Download SSL certificates
            # from your FMC first and provide its path for verification.
            # r = requests.post(auth_url, headers=self.headers,
            #                   auth=requests.auth.HTTPBasicAuth(username,password), verify='/path/to/ssl_certificate')
            auth_headers = r.headers
            auth_token = auth_headers.get('X-auth-access-token', default=None)
            self.domain_uuid = auth_headers.get('domain_uuid', default=None)
            self.headers['X-auth-access-token'] = auth_token
            self.authTokenTimestamp = int(time.time())
            auth_headers["authTokenTimestamp"] = self.authTokenTimestamp
            # logging.debug("Acquired AuthToken: " + auth_token)
            # logging.debug("domain_uuid: " + domain_uuid)
            return auth_headers
            if auth_token is None:
                logging.debug("auth_token not found. Exiting...")
                # raise Exception("Error occurred in get auth token ")
                return None
        except Exception as err:
            logger.error("FMC: Error in generating auth token --> " + str(err))
            return None
        finally:
            if r: r.close()

    def write_existing_token(self, token_str):
        try:
            #token = json.loads(token_str) token = ast.literal_eval(token_str)
            token = dict(token_str)
            self.headers = {'Content-Type': 'application/json'}
            
            auth_headers = token
            auth_token = auth_headers.get('X-auth-access-token', None)
            self.domain_uuid = auth_headers.get('domain_uuid', None)
            self.headers['X-auth-access-token'] = auth_token
            self.authTokenTimestamp = auth_headers.get('authTokenTimestamp', time.time())
            return
        except Exception as e:
            raise Exception("FMC: ERROR IN WRITING EXISTING TOKEN  "+repr(e))
            
    def verify_existing_token(self):
        try:
            api_path = "/api/fmc_platform/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/audit/auditrecords"
            url = self.server + api_path
            #r = self.rest_get(url)
            for i in range(0,3):
                r = requests.get(url, headers=self.headers, verify=False)
                status_code = r.status_code
                if 200 <= status_code <=202:
                    #return r.json()['items'][0]['time']*1000
                    return True
                time.sleep(2)
            return None
        except Exception as e:
            logger.error(e)
            return None

    def get_device_grp_id_by_name(self, name):
        """
        Purpose:    To get device group id by passing name of the group
        Parameters: Name of device group
        Returns:    Group Id or None
        Raises:
        """
        try: 
            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/devicegroups/devicegrouprecords"
            url = self.server + api_path + '?offset=0&limit=9000'
            r = self.rest_get(url)
            if 'items' in r.json():
                for item in r.json()['items']:
                    if item['name'] == name:
                        return str(item['id'])
            return None
        except Exception as e: 
            raise Exception("FMC: get_device_grp_id_by_name  "+repr(e))
        

    def get_member_list_in_device_grp(self, grp_id):
        """
        Purpose:    To get devices name list from grp id
        Parameters: Group Id
        Returns:    list or None
        Raises:
        """
        try: 
            member_name_list = []
            member_id_list = []
            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/devicegroups/devicegrouprecords/"
            url = self.server + api_path + grp_id
            r = self.rest_get(url)
            if 'members' in r.json():
                for item in r.json()['members']:
                    member_name_list.append(item['name'])
                    member_id_list.append(item['id'])
    
            return member_name_list, member_id_list
        except Exception as e: 
            raise Exception("FMC: get_member_list_in_device_grp  "+repr(e))
        

    def get_security_objectid_by_name(self, name):
        """
        Purpose:    Get Zone ID from it's name
        Parameters: Zone Name
        Returns:    Zone ID, None
        Raises:
        """
        try: 
            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/object/securityzones"
            url = self.server + api_path + '?offset=0&limit=9000'
            r = self.rest_get(url)
            if 'items' in r.json():
                for item in r.json()['items']:
                    if item['name'] == name:
                        return str(item['id'])
            return None
        except Exception as e: 
            raise Exception("FMC: Exception"+repr(e))
        

    # Get network objects (all network and host objects)
    def get_network_objectid_by_name(self, name):
        """
        Purpose:    Get Network object Id by its name
        Parameters: Object Name
        Returns:    Object Id
        Raises:
        """
        try: 
            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/object/networkaddresses"
            url = self.server + api_path + '?offset=0&limit=10000'
            r = self.rest_get(url)
            for item in r.json()['items']:
                if item['type'] == 'Network' and item['name'] == name:
                    return str(item['id'])
            # raise Exception('network object with name ' + name + ' was not found')
            return ''
        except Exception as e: 
            raise Exception("FMC: get_security_objectid_by_name  "+repr(e))
        

    def get_port_objectid_by_name(self, name):
        """
        Purpose:    Get Port object Id by its name
        Parameters: Object Name
        Returns:    Object Id
        Raises:
        """
        try: 
            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/object/protocolportobjects"
            url = self.server + api_path + '?offset=0&limit=10000'
            r = self.rest_get(url)
            for item in r.json()['items']:
                if item['type'] == 'ProtocolPortObject' and item['name'] == name:
                    return str(item['id'])
            # raise Exception('network port with name ' + name + ' was not found')
            return ''
        except Exception as e: 
            raise Exception("FMC: get_port_objectid_by_name  "+repr(e))
        

    def get_host_objectid_by_name(self, name):
        """
        Purpose:    Get Host object Id by Name
        Parameters: Object Name
        Returns:    Object Id
        Raises:
        """
        try: 
            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/object/hosts"
            url = self.server + api_path + '?offset=0&limit=10000'
            r = self.rest_get(url)
            for item in r.json()['items']:
                if item['type'] == 'Host' and item['name'] == name:
                    return str(item['id'])
            # raise Exception('host object with name ' + name + ' was not found')
            return ''
        except Exception as e: 
            raise Exception("FMC: get_host_objectid_by_name  "+repr(e))
        

    def get_device_id_by_name(self, name):
        """
        Purpose:    Get Device Id by its name
        Parameters: Device Name
        Returns:    Device Id
        Raises:
        """
        try: 
            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/devices/devicerecords"
            url = self.server + api_path + '?offset=0&limit=10000'
            r = self.rest_get(url)
            if 'items' in r.json():
                for item in r.json()['items']:
                    if item['name'] == name:
                        return str(item['id'])
            # or return empty string
            return ''
        except Exception as e: 
            raise Exception("FMC: get_device_id_by_name  "+repr(e))
        

    def get_access_policy_id_by_name(self, name):
        """
        Purpose:    Get Access Policy Id by its name
        Parameters: Access policy name
        Returns:    Access Policy Id, None
        Raises:
        """
        try: 
            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/policy/accesspolicies"
            url = self.server + api_path + '?offset=0&limit=10000'
            r = self.rest_get(url)
            # Search for policy by name
            if 'items' in r.json():
                for item in r.json()['items']:
                    if item['name'] == name:
                        return str(item['id'])
            return None
        except Exception as e: 
            raise Exception("FMC: get_access_policy_id_by_name  "+repr(e))
        

    def get_nic_id_by_name(self, device_id, nic_name):
        """
        Purpose:    Get Nic Id by device & nic name
        Parameters: Device Name, Nic name
        Returns:    Nic Id, None
        Raises:
        """
        try: 
            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/devices/devicerecords/" + \
                       device_id + "/physicalinterfaces"
            url = self.server + api_path
            r = self.rest_get(url)
            if 'items' in r.json():
                for item in r.json()['items']:
                    if item['name'] == nic_name:
                        return str(item['id'])
            return None
        except Exception as e: 
            raise Exception("FMC: get_nic_id_by_name  "+repr(e))
        

    def get_time_stamp(self):
        """
        Purpose:    Get time stamp
        Parameters:
        Returns:    Audit time stamp
        Raises:
        """
        try: 
            api_path = "/api/fmc_platform/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/audit/auditrecords"
            url = self.server + api_path
            r = self.rest_get(url)
            return r.json()['items'][0]['time']*1000
        except Exception as e: 
            raise Exception("FMC: get_time_stamp  "+repr(e))
        

    def get_deployable_devices(self):
        """
        Purpose:    Get list of deployable devices
        Parameters:
        Returns:    List of devices, pending to be deployed
        Raises:
        """
        api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/deployment/deployabledevices"
        url = self.server + api_path
        try:
            r = self.rest_get(url)
            logging.debug("deployable devices:" + str(r.json()))
            device_list = []
            if 'items' in r.json():
                for item in r.json()['items']:
                    if item['type'] == 'DeployableDevice':
                        device_list.append(item['name'])
            return device_list
        except Exception as e:
            logger.warning("HTTPError : "+ repr(e))
            return None

    def get_nic_status(self, device_id, nic, nic_id, ifname, zone_id, ip=None):
        """
        Purpose:    To check whether Nic is configured or not configured
        Parameters: Device Id, Nic, Nic Id, Interface Name, Zone Id, Ip
        Returns:    CONFIGURED, MIS-CONFIGURED, UN-CONFIGURED
        Raises:
        """
        api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/devices/devicerecords/" + \
                   device_id + "/physicalinterfaces/" + nic_id
        url = self.server + api_path
        r = self.rest_get(url)
        flag1, flag2 = 0, 0
        try:
            if 'ipv4' in r.json():
                item = dict.copy(r.json()['ipv4']['static'])
                if item['address'] == ip:
                    flag1 = 1
        except:
            try:
                if 'ipv4' in r.json():
                    item = dict.copy(r.json()['ipv4']['dhcp'])
                    flag1 = 1
            except:
                flag1 = 0
        try:
            if r.json()['name'] == nic:
                if r.json()['ifname'] == ifname:
                    flag2 = 1
            if r.json()['securityZone']['id'] != zone_id:
                flag2 = 0
        except:
            flag2 = 0

        if flag1 == 1 and flag2 == 1:
            return "CONFIGURED"
        elif (flag1 == 1 and flag2 == 0) or (flag1 == 0 and flag2 == 1):
            logger.critical("Interface Mis-Configured! ")

        return "UN-CONFIGURED"

    def check_static_route(self, device_id, interface_name, _object_name, gate_way):
        """
        Purpose:    Check if a static route exists on a device
        Parameters: Device, Interface name, Network, Gateway
        Returns:    CONFIGURED, UN-CONFIGURED
        Raises:
        """
        try: 
            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/devices/devicerecords/" + \
                       device_id + "/routing/ipv4staticroutes"
            url = self.server + api_path + '?offset=0&limit=10000'
            r = self.rest_get(url)
    
            if 'items' in r.json():
                for key1 in r.json()['items']:
                    id = key1['id']
                    url = self.server + api_path + '/' + id
                    r = self.rest_get(url)
                    if r.json()['interfaceName'] == interface_name:
                        for key2 in r.json()['selectedNetworks']:
                            if key2['name'] == _object_name:
                                try:
                                    element = dict.copy(r.json()['gateway']['object'])
                                    if element['name'] == gate_way:
                                        return "CONFIGURED"
                                except:
                                    pass
                                try:
                                    element = dict.copy(r.json()['gateway']['literal'])
                                    if element['value'] == gate_way:
                                        return "CONFIGURED"
                                except:
                                    pass
            return "UN-CONFIGURED"
        except Exception as e: 
            raise Exception("FMC: check_static_route"+repr(e))
        

    def configure_nic_dhcp(self, device_id, nic_id, nic, nic_name, mgmt_only, mode, zone_id, mtu):
        """
        Purpose:    Configure an Nic interface as DHCP
        Parameters: Device Name, Nic, Nic name, Zone, MTU
        Returns:    REST put response
        Raises:
        """
        try: 
            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/devices/devicerecords/" + \
                       device_id + "/physicalinterfaces/" + nic_id
            url = self.server + api_path
            put_data = {
                    "type": "PhysicalInterface",
                    "managementOnly": mgmt_only,
                    "MTU": int(mtu),
                    "ipv4": {
                        "dhcp": {
                            "enableDefaultRouteDHCP": "false",
                            "dhcpRouteMetric": 1
                            }
                    },
                    "securityZone": {
                        "id": zone_id,
                        "type": "SecurityZone"
                    },
                    "mode": mode,
                    "ifname": nic_name,
                    "enabled": "true",
                    "name": nic,
                    "id": nic_id
                    }
            r = self.rest_put(url, put_data)
            return r
        except Exception as e: 
            raise Exception("FMC: configure_nic_dhcp  "+repr(e))
        

    def configure_nic_static(self, device_id, nic_id, nic, nic_name, mgmt_only, mode, zone_id, mtu, ip, netmask):
        """
        Purpose:    Configure an Nic interface as Static
        Parameters: Device Name, Nic, Nic name, Zone, IP, Netmask
        Returns:    REST put response
        Raises:
        """
        try: 
            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/devices/devicerecords/" + \
                       device_id + "/physicalinterfaces/" + nic_id
            url = self.server + api_path
            put_data = {
                    "type": "PhysicalInterface",
                    "managementOnly": mgmt_only,
                    "MTU": mtu,
                    "ipv4": {
                        "static": {
                            "address": ip,
                            "netmask": netmask
                        }
                    },
                    "securityZone": {
                        "id": zone_id,
                        "type": "SecurityZone"
                    },
                    "mode": mode,
                    "ifname": nic_name,
                    "enabled": "true",
                    "name": nic,
                    "id": nic_id
                    }
            r = self.rest_put(url, put_data)
            return r
        except Exception as e: 
            raise Exception("FMC: configure_nic_static  "+repr(e))
        

    def create_static_route(self, device_id, interface_name, _type, _object_name, _object_id, gate_way, metric):
        """
        Purpose:    To create static route on device
        Parameters: Device, Interface Name, Host, Gateway, Metric
        Returns:    REST response
        Raises:
        """

        try: 
            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/devices/devicerecords/" + \
                       device_id + "/routing/ipv4staticroutes"  # param
            url = self.server + api_path
    
            post_data = {
                "interfaceName": interface_name,
                "selectedNetworks": [
                    {
                        "type": _type,
                        "id": _object_id,
                        "name": _object_name
                    }
                ],
                "gateway": gate_way,
                "metricValue": metric,
                "type": "IPv4StaticRoute",
                "isTunneled": False
            }
            r = self.rest_post(url, post_data)
            return r
        except Exception as e: 
            raise Exception("FMC: create_static_route  "+repr(e))
        

    def register_device(self, name, mgmt_ip, policy_id, reg_id, nat_id, license_caps, performance_tier, device_grp_id):
        """
        Purpose:    Register the device to FMC
        Parameters: Name of device, Mgmt ip, Access Policy Id, Registration & NAT id, Licenses Caps, Group Id
        Returns:    REST post response
        Raises:
        """
        try: 
            logger.info("Registering: "+name)
            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/devices/devicerecords"
            url = self.server + api_path
            post_data = {
                "name": name,
                "hostName": mgmt_ip,
                "regKey": reg_id,
                "natID": nat_id,
                "type": "Device",
                "license_caps": license_caps,
                "performanceTier": performance_tier,
                "accessPolicy": {
                    "id": policy_id,
                    "type": "AccessPolicy"
                },
                "deviceGroup": {
                    "id": device_grp_id,
                    "type": "DeviceGroup"
                }
            }
    
            r = self.rest_post(url, post_data)
            return r
        except Exception as e: 
            raise Exception("FMC: register_device  "+repr(e))
        

    def deregister_device(self, name):
        """
        Purpose:    De-registers the device from FMC
        Parameters: Device Name
        Returns:    REST delete response
        Raises:
        """
        try: 
            logger.info("De-registering: " + name)
            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/devices/devicerecords/"
            dev_id = self.get_device_id_by_name(name)
            url = self.server + api_path + dev_id
            r = self.rest_delete(url)
            return r
        except Exception as e: 
            raise Exception("FMC: deregister_device  "+repr(e))
        

    def start_deployment(self, device_name):
        """
        Purpose:    Deploys policy changes on device
        Parameters: Device name
        Returns:    Task Id
        Raises:
        """
        try: 
            logger.info("Deploy called for: " + device_name)
            device_list = self.get_deployable_devices()
            logging.debug("Device List = " + str(device_list))
            if device_name in device_list:
                logging.debug("deploying on device: " + device_name)
                api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/deployment/deploymentrequests"
                url = self.server + api_path
                post_data = {
                    "type": "DeploymentRequest",
                    "version": str(self.get_time_stamp()),
                    "forceDeploy": True,
                    "ignoreWarning": True,
                    "deviceList": [self.get_device_id_by_name(device_name)]
                }
                try:
                    r = self.rest_post(url, post_data)
                    if 'type' in r.json():
                        if r.json()['type'] == 'DeploymentRequest':
                            return r.json()['metadata']['task']['id']
                except Exception as e:
                    logger.error("FTDv CONFIGURE:"+repr(e))
                    return None
            return None
        except Exception as e: 
            raise Exception("FMC: start_deployment  "+repr(e))
        

    def check_reg_status_from_fmc(self, vm_name):
        """
        Purpose:    Checks if device is registered to FMC
        Parameters: Device Name
        Returns:    SUCCESS, FAILED
        Raises:
        """
        try:
            device_id = self.get_device_id_by_name(vm_name)
        except Exception as e:
            logger.debug(str(e))
        else:
            if device_id != '':
                return "SUCCESS"
            else:
                return "FAILED"

    def check_deploy_status(self, vm_name):
        """
        Purpose:    Checks if any deployment pending for device
        Parameters: Device name
        Returns:    DEPLOYED, NOT-DEPLOYED
        Raises:
        """
        try: 
            r = self.get_deployable_devices()
            if r == None:
                return "NOT-KNOWN"
            for device in r:
                if device == vm_name:
                    logger.debug("Policies not deployed on " + vm_name)
                    return "NOT-DEPLOYED"
            logger.debug("Policies deployed on " + vm_name)
            return "DEPLOYED"
        except Exception as e: 
            raise Exception("FMC: check_deploy_status  "+repr(e))
        

    def check_object_fmc(self, obj_name):
        """
        Purpose:    Checks for Object in FMC
        Parameters: Object name
        Returns:    Object Id
        Raises:
        """
        try: 
            obj_id = self.get_network_objectid_by_name(obj_name)
            if obj_id == '':
                obj_id = self.get_host_objectid_by_name(obj_name)
                if obj_id == '':
                    obj_id = self.get_port_objectid_by_name(obj_name)
                    if obj_id == '':
                        logger.error("Unable to find object %s" % obj_name)
                        return ''
            return obj_id
        except Exception as e: 
            raise Exception("FMC: check_object_fmc  "+repr(e))
        

    def get_memory_metrics_from_fmc(self, device_id):
        """
        Purpose:    Fetch Memory Metric
        Parameters: device id
        Returns:
        Raises:
        """
        try:
            api_path = f'/api/fmc_config/v1/domain/{self.domain_uuid}/health/metrics'
            # Values are fetched from last one minute at interval of 10 sec (step).
            end_time = int(time.time())
            start_time = end_time - 60
            step_size = 10
            regexFilter = "used_percentage_system_and_swap"
            api_suffix = f'?offset=0&limit=100&filter=deviceUUIDs%3A{device_id}%3Bmetric%3Amem%3BstartTime%3A{start_time}%3BendTime%3A{end_time}%3Bstep%3A{step_size}%3BregexFilter%3A{regexFilter}&expanded=true'
            url = self.server + api_path + api_suffix
            r = self.rest_get(url)
            resp = r.text
            return json.loads(resp)
        except Exception as e:
            logger.error("Error {}".format(e))
            return None

    def get_policy_assign_targets(self, pol_id):
        """
        Purpose:    Get targets by its policy id
        Parameters: Device Name
        Returns:    Device Id
          "targets": [
                    {
                      "id": "87b98de4-919c-11ea-bedf-d2d17d1b9702",
                      "type": "DeviceGroup",
                      "name": "AWS-Cisco-NGFW-VMs-2"
                    },
                    {
                      "id": "d263cee0-919c-11ea-ad04-b08a2fa13b2d",
                      "type": "DeviceGroup",
                      "name": "AWS-Cisco-NGFW-VMs-1"
                    },
                    {
                      "id": "4d71e0d4-91e0-11ea-b727-a060bdd6dece",
                      "type": "DeviceGroup",
                      "name": "AWS-Cisco-NGFW-VMs-3"
                    }
                  ]
        """
        try: 
            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/assignment/policyassignments/"
            url = self.server + api_path + pol_id
            r = self.rest_get(url)
            if 'targets' in r.json():
                return r.json()["targets"]
            else:
                return []
        except Exception as e: 
            raise Exception("FMC: get_policy_assign_targets"+repr(e))
        

    def get_nat_policy_id(self, pol_name):
        """
        Purpose:    Gets policy id
        Parameters: Policy Name
        Returns:    Policy Id

        """
        try: 
            api_path = "/api/fmc_config/v1/domain/e276abec-e0f2-11e3-8169-6d9ed49b625f/policy/ftdnatpolicies"
            url = self.server + api_path + '?offset=0&limit=10000'
            r = self.rest_get(url)
            for item in r.json()['items']:
                if item['name'] == pol_name:
                    return str(item['id'])
            else:
                return None
        except Exception as e: 
            raise Exception("FMC: get_nat_policy_id"+repr(e))
        

class DerivedFMC(FirepowerManagementCenter):
    """
        DerivedFMC is a child class of FirepowerManagementCenter, updates parameters & methods
    """
    def __init__(self, fmc_server, username, password, accesspolicy):
        super().__init__(fmc_server, username, password, accesspolicy)

        self.d_grp_name = ''
        self.a_policy_name = ''
        self.nat_policy_name = ''
        self.seczone_name = []
        self.network_obj_name = []
        self.host_obj_name = []

        self.d_grp_id = ''
        self.a_policy_id = ''
        self.nat_policy_id = ''
        self.seczone_obj_pair = {}
        self.network_obj_pair = {}
        self.host_obj_pair = {}

        self.reachable = False
        self.configuration = {}
        self.configuration_status = ""

    def reach_fmc_(self):
        """
        Purpose:    To get Auth token & update self.reachable value
        Parameters:
        Returns:    self.reachable
        Raises:
        """
        try:
            self.get_auth_token()
            if self.headers['X-auth-access-token']:
                self.reachable = 'AVAILABLE'
        except Exception as e:
            logger.error(e)
            self.reachable = 'UN-AVAILABLE'
        self.configuration.update({'fmc_reachable': self.reachable})
        return self.reachable

    def reach_fmc_with_manual_token(self, token):
        """
        Purpose:    To get Auth token & update self.reachable value
        Parameters:
        Returns:    self.reachable
        Raises:
        """
        try:
            self.write_existing_token(token)
            if self.headers['X-auth-access-token']:
                self.reachable = 'AVAILABLE'
        except Exception as e:
            logger.error(e)
            self.reachable = 'UN-AVAILABLE'
        self.configuration.update({'fmc_reachable': self.reachable})
        return self.reachable

    def set_fmc_configuration(self):
        """
        Purpose:    To update DerivedFMC class parameters
        Parameters:
        Returns:    Object
        Raises:
        """
        try: 
            if self.d_grp_name:
                self.d_grp_id = self.get_device_grp_id_by_name(self.d_grp_name)
                self.configuration.update({"device_grp": {self.d_grp_name: self.d_grp_id}})
            if self.a_policy_name:
                self.a_policy_id = self.get_access_policy_id_by_name(self.a_policy_name)
                self.configuration.update({"access_policy": {self.a_policy_name: self.a_policy_id}})
            if self.nat_policy_name:
                self.nat_policy_id = self.get_nat_policy_id(self.nat_policy_name)
                self.configuration.update({"nat_policy": {self.nat_policy_name: self.nat_policy_id}})
            if self.seczone_name:
                for i in self.seczone_name:
                    self.seczone_obj_pair.update({i: self.get_security_objectid_by_name(i)})
                self.configuration.update({"security_zones": self.seczone_obj_pair})
            if self.network_obj_name:
                for i in self.network_obj_name:
                    self.network_obj_pair.update({i: self.get_network_objectid_by_name(i)})
                self.configuration.update({"net_objects": self.network_obj_pair})
            if self.host_obj_name:
                for i in self.host_obj_name:
                    self.host_obj_pair.update({i: self.get_host_objectid_by_name(i)})
                self.configuration.update({"host_objects": self.host_obj_pair})
            logger.debug(json.dumps(self.configuration, separators=(',', ':')))
            return
        except Exception as e: 
            raise Exception("FMC: set_fmc_configuration  "+repr(e))
        

    def update_fmc_config_user_input(self, d_grp_name, a_policy_name, nat_policy_name,
                                     l_seczone_name, l_network_obj_name, l_host_obj_name):
        """
        Purpose:    To take parameters to DerivedFMC class
        Parameters:
        Returns:
        Raises:
        """
        try: 
            self.d_grp_name = d_grp_name
            self.a_policy_name = a_policy_name
            self.nat_policy_name = nat_policy_name
            self.seczone_name = l_seczone_name
            self.network_obj_name = l_network_obj_name
            self.host_obj_name = l_host_obj_name
            return
        except Exception as e: 
            raise Exception("FMC: update_fmc_config_user_input  "+repr(e))
        

    def check_fmc_configuration(self):
        """
        Purpose:    To inspect if Derived FMC class has all required variables
        Parameters:
        Returns:    self.configuration_status
        Raises:
        """
        try: 
            self.configuration_status = 'UN-CONFIGURED'
    
            if self.reachable == 'AVAILABLE':
                if self.d_grp_id == '':
                    return self.configuration_status
                if self.a_policy_id == '':
                    return self.configuration_status
                else:
                    r = self.get_policy_assign_targets(self.a_policy_id)
                    if not utl.find_value_in_list(r, self.d_grp_id):
                        return self.configuration_status
                if self.nat_policy_id == '':
                    return self.configuration_status
                else:
                    r = self.get_policy_assign_targets(self.nat_policy_id)
                    if not utl.find_value_in_list(r, self.d_grp_id):
                        return self.configuration_status
    
                for (k, v) in self.seczone_obj_pair.items():
                    if v is None:
                        return self.configuration_status
                for (k, v) in self.network_obj_pair.items():
                    if v is None:
                        return self.configuration_status
                for (k, v) in self.host_obj_pair.items():
                    if v is None:
                        return self.configuration_status
    
            self.configuration_status = 'CONFIGURED'
            self.configuration.update({'fmc_configuration_status': self.configuration_status})
            return self.configuration_status
        except Exception as e: 
            raise Exception("FMC: check_fmc_configuration  "+repr(e))
        

    def register_ftdv(self, vm_name, mgmt_ip, reg_id, nat_id, license_caps, performance_tier):
        """
        Purpose:    Register the device to FMC
        Parameters: Device Name, Mgmgt Ip, Registration & NAT id, Licenses cap
        Returns:    Task id, None
        Raises:
        """
        try:
            logger.debug("Registering FTDv: " + vm_name + " to FMC with policy id: " + self.a_policy_name)
            r = self.register_device(vm_name, mgmt_ip, self.a_policy_id, reg_id, nat_id, license_caps, performance_tier, self.d_grp_id)
            logger.debug("Register response was: " + str(r.json()))
            if 'type' in r.json():
                if r.json()['type'] == 'Device':
                    logger.info("NGFWv: " + vm_name + " registration started and task ID is: " +
                                r.json()['metadata']['task']['id'])
                    return r.json()['metadata']['task']['id']
            return None
            
        except Exception as e:
            logger.exception("FMC: register_ftdv  "+repr(e))
            return None

    def conf_static_rt(self, device_id, int_name, rt_type, net_name, net_id, gateway, metric):
        """
        Purpose:    To configure gateway if required for static_route
        Parameters:
        Returns:    response
        Raises:
        """
        try: 
            gateway_id = self.get_host_objectid_by_name(gateway)
            # Gateway can be an object or IP literal
            if gateway_id != '':
                gate_way = {
                    "object": {
                        "type": "Host",
                        "id": gateway_id,
                        "name": gateway
                    }
                }
            else:
                gate_way = {
                    "literal": {
                        "type": "Host",
                        "value": gateway
                    }
                }
            try:
                r = self.create_static_route(device_id, int_name, rt_type, net_name, net_id, gate_way, metric)
                return r
            except Exception as e:
                logger.error(e)
                return None
        except Exception as e: 
            raise Exception("FMC: conf_static_rt  "+repr(e))
        
