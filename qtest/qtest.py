import datetime
from base64 import b64encode

import requests


def str_to_base64(original_string):
    original_bytes = bytes(original_string, 'utf-8')
    encoded_bytes = b64encode(original_bytes)
    encoded_string = encoded_bytes.decode('utf-8')
    return encoded_string


class NaiveUTC(datetime.tzinfo):
    def tzname(self, **kwargs):
        return "UTC"

    def utcoffset(self, dt):
        return datetime.timedelta(0)

    @staticmethod
    def now_timestamp():
        return datetime.datetime.utcnow().replace(tzinfo=NaiveUTC()).isoformat(sep='T', timespec='milliseconds')


class QTestClient:

    def __init__(self, username=None, password=None, site_name=None, host=None, auth_token=None):
        if not host:
            if not site_name:
                raise Exception('You must supply a host, or a site_name to derive a host. Not neither.')
            host = 'https://' + site_name + '.qtestnet.com/'
        self.host = host
        # if we're not supplied with an auth_token get one from
        # the username and password.
        if not auth_token:
            if not username or not password:
                raise Exception('You must either give an authorization token or username/password. Not neither.')
            auth_token = QTestClient._get_bearer_token(username, password, host, site_name)
        self.auth_token = auth_token

    @staticmethod
    def enable_console_logging():
        import http.client as http_client
        import logging
        http_client.HTTPConnection.debuglevel = 1
        # You must initialize logging, otherwise you'll not see debug output.
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    # https://api.qasymphony.com/#/login/postAccessToken
    @staticmethod
    def _get_bearer_token(username, password, host, site_name):
        # http://docs.python-requests.org/en/master/user/quickstart/
        form_data = {
            'grant_type': 'password',
            'username': username,
            'password': password
        }
        # If the site_name doesn't and with a colon (and based on the documentation
        # why would you?) then let's concat one.
        if site_name and site_name[-1] != ':':
            site_name = site_name + ':'
        headers = {
            'Authorization': 'Basic ' + str_to_base64(site_name)
        }
        token = requests.post(host + 'oauth/token', data=form_data, headers=headers)
        token_json = token.json()
        return token_json

    def _gen_header_from_token(self):
        headers = dict()
        headers['Authorization'] = self.auth_token['token_type'] + ' ' + self.auth_token['access_token']
        return headers

    def get_releases(self, project_id, release_id=None):
        url = self.host + '/api/v3/projects/' + str(project_id) + '/releases'
        if release_id:
            url = url + '/' + str(release_id)
        response = requests.get(url, headers=self._gen_header_from_token())
        return response.json()

    def create_release(self, project_id, name, description):
        url = self.host + '/api/v3/projects/' + str(project_id) + '/releases'
        release = {
            "name": name,
            "description": description
        }
        response = requests.post(url, json=release, headers=self._gen_header_from_token())
        response_json = response.json()
        return response_json

    def get_test_cycles(self, project_id, test_cycle_id=None, parent_id=None, parent_type=None):
        url = self.host + '/api/v3/projects/' + str(project_id) + '/test-cycles'
        if test_cycle_id:
            url = url + '/' + str(test_cycle_id)
        params = dict()
        if parent_id:
            params['parentId'] = str(parent_id)
        if parent_type:
            params['parentType'] = str(parent_type)
        response = requests.get(url, headers=self._gen_header_from_token(), params=params)
        json = response.json()
        try:
            if json.get('message') == 'Test Cycle does not exist':
                json = list()
        except AttributeError:
            # If it's a list, there will be no "get" attribute. We're good to go!
            pass
        return json

    def create_test_cycle(self, project_id, parent_id, parent_type, name):
        url = self.host + '/api/v3/projects/' + str(project_id) + '/test-cycles'
        params = {
            'parentId': parent_id,
            'parentType': parent_type
        }
        json_body = {
            'name': name,
            'description': 'Postman CICD run for: ' + str(name),
        }
        response = requests.post(url, json=json_body, headers=self._gen_header_from_token(),
                                 params=params)
        response_json = response.json()
        return response_json

    def get_test_runs(self, project_id, parent_id=None, parent_type=None, expand=None, page=1, page_size=100):
        """
        Specify expand=descendants to include all Test Runs which are directly or indirectly under the container
        """
        params = {
            'page': page,
            'pageSize': page_size
        }
        if parent_id:
            params['parentId'] = parent_id
        if parent_type:
            params['parentType'] = parent_type
        if expand:
             params['expand'] = expand
        url = self.host + '/api/v3/projects/' + str(project_id) + '/test-runs'
        response = requests.get(url, params=params, headers=self._gen_header_from_token())
        return response.json()
    
    def get_test_runs_subhierarchy(self, project_id, parent_id=None, parent_type=None):
        params = {}
        if parent_id:
            params['parentId'] = parent_id
        if parent_type:
            params['parentType'] = parent_type
        url = self.host + '/api/v3/projects/' + str(project_id) + '/test-runs/subhierarchy'
        response = requests.get(url, params=params, headers=self._gen_header_from_token())
        return response.json()

    def create_test_run(self, project_id, name, test_case_id, parent_id=None, parent_type=None):
        url = self.host + '/api/v3/projects/' + str(project_id) + '/test-runs'
        params = dict()
        data = {
            'name': name,
            'test_case': {
                'id': test_case_id
            }
        }
        if parent_id:
            params['parentId'] = parent_id
            data['parentId'] = parent_id
        if parent_type:
            params['parentType'] = parent_type
            data['parentType'] = parent_type
        response = requests.post(url=url, headers=self._gen_header_from_token(), json=data, params=params)
        response_json = response.json()
        return response_json

    def get_test_cases(self, project_id, test_case_id=None, page=1, size=20):
        url = f"{self.host}/api/v3/projects/{project_id}/test-cases"
        if test_case_id:
            url = url + '/' + str(test_case_id)
        else:
            url = f"{url}?page={page}&size={size}"

        response = requests.get(url=url, headers=self._gen_header_from_token())
        response_json = response.json()
        return response_json

    def update_test_case(self, project_id, test_case):
        url = self.host + '/api/v3/projects/' + str(project_id) + '/test-cases/' + str(test_case['id'])
        reduced_test_case = dict()

        def copy_property(key):
            if key in test_case:
                reduced_test_case[key] = test_case[key]

        allowed_properties = ['id', 'name', 'created_date', 'last_modified_date', 'properties', 'test_steps',
                              'parent_id', 'description', 'precondition', 'agent_ids']
        [copy_property(allowed_property) for allowed_property in allowed_properties]

        response = requests.put(url=url, headers=self._gen_header_from_token(), json=reduced_test_case)
        response_json = response.json()
        return response_json
    
    def get_requirements(self, project_id, req_id=None, page=1, size=20):
        url = f"{self.host}/api/v3/projects/{project_id}/requirements"
        if req_id:
            url = url + '/' + str(req_id)
        else:
            url = f"{url}?page={page}&size={size}"

        response = requests.get(url=url, headers=self._gen_header_from_token())
        response_json = response.json()
        return response_json

    def submit_test_result(self, project_id, test_run_id, test_case_dict, html_results, has_passed):
        url = self.host + '/api/v3/projects/' + str(project_id) + '/test-runs/' + str(test_run_id) + '/auto-test-logs'
        utc_now = NaiveUTC.now_timestamp()
        body = {
            'status': 'PASS' if has_passed else 'FAIL',
            'name': test_case_dict['name'],
            'automation_content': 'Postman Result',
            'note': html_results,
            'exe_start_date': utc_now,
            'exe_end_date': utc_now,
        }
        params = {
            # False counter-intuitively means it IS html.
            'encodeNote': False
        }
        response = requests.post(url=url, json=body, params=params, headers=self._gen_header_from_token())
        response_json = response.json()
        return response_json

    def get_projects(self, project_id=None):
        url = self.host + '/api/v3/projects'
        if project_id:
            url += '/' + str(project_id)
        response = requests.get(url=url, headers=self._gen_header_from_token())
        response_json = response.json()
        return response_json

    def get_fields(self, project_id, object_type):
        url = self.host + '/api/v3/projects/' + str(project_id) + '/settings/' + str(object_type) + '/fields'
        response = requests.get(url=url, headers=self._gen_header_from_token())
        response_json = response.json()
        return response_json

    def update_system_field(self, project_id, object_type, field):
        url = self.host + '/api/v3/projects/' + str(project_id) + '/settings/' + str(
            object_type) + '/system-fields/' + str(field.get('id'))
        response = requests.post(url, headers=self._gen_header_from_token(), json=field)
        response_json = response.json()
        return response_json

    def update_custom_field(self, project_id, object_type, fields):
        # If this isn't a list of fields, wrap it.
        if type(fields) != list:
            fields = [fields]
        url = self.host + '/api/v3/projects/' + str(project_id) + '/settings/' + str(
            object_type) + '/custom-fields/active'
        response = requests.post(url=url, headers=self._gen_header_from_token(), json=fields)
        response_json = response.json()
        return response_json

    def get_linked_objects(self, project_id, object_type, ids=[]):
        url = f"{self.host}/api/v3/projects/{project_id}/linked-artifacts?type={object_type}"
        if ids:
            url = url + '&ids=' + "&ids=".join(map(str,ids))
        response = requests.get(url=url, headers=self._gen_header_from_token())
        response_json = response.json()
        return response_json

    def create_link(self, project_id, source_type, source_id, destination_type, dest_ids=[]):
        url = f"{self.host}/api/v3/projects/{project_id}/{source_type}/{source_id}/link?type={destination_type}"
        response = requests.post(url=url, json=dest_ids, headers=self._gen_header_from_token())
        response_json = response.json()
        return response_json
