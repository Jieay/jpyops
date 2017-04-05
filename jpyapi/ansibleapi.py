#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
 
from tempfile import NamedTemporaryFile
import os.path
 
from ansible.inventory.group import Group
from ansible.inventory.host import Host
from ansible.inventory import Inventory
from ansible.runner import Runner
from ansible.playbook import PlayBook
from ansible import callbacks
from ansible import utils
import ansible.constants as C
from passlib.hash import sha512_crypt
from django.template.loader import get_template
from django.template import Context
 
 
 
API_DIR = os.path.dirname(os.path.abspath(__file__))
ANSIBLE_DIR = os.path.join(API_DIR, 'playbooks')
C.HOST_KEY_CHECKING = False
 
 
class AnsibleError(StandardError):
    """
    the base AnsibleError which contains error(required),
    data(optional) and message(optional).
    存储所有Ansible 异常对象
    """
    def __init__(self, error, data='', message=''):
        super(AnsibleError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message
 
 
class CommandValueError(AnsibleError):
    """
    indicate the input value has error or invalid. 
    the data specifies the error field of input form.
    输入不合法 异常对象
    """
    def __init__(self, field, message=''):
        super(CommandValueError, self).__init__('value:invalid', field, message)
 
 
class MyInventory(Inventory):
    """
    this is my ansible inventory object.
    """
    def __init__(self, resource):
        """
        resource的数据格式是一个列表字典，比如
            {
                "group1": {
                    "hosts": [{"hostname": "10.10.10.10", "port": "22", "username": "test", "password": "mypass"}, ...],
                    "vars": {"var1": value1, "var2": value2, ...}
                }
            }
 
        如果你只传入1个列表，这默认该列表内的所有主机属于my_group组,比如
            [{"hostname": "10.10.10.10", "port": "22", "username": "test", "password": "mypass"}, ...]
        """
        self.resource = resource
        self.inventory = Inventory(host_list=[])
        self.gen_inventory()
 
    def my_add_group(self, hosts, groupname, groupvars=None):
        """
        add hosts to a group
        """
        my_group = Group(name=groupname)
 
        # if group variables exists, add them to group
        if groupvars:
            for key, value in groupvars.iteritems():
                my_group.set_variable(key, value)
 
        # add hosts to group
        for host in hosts:
            # set connection variables
            hostname = host.get("hostname")
            hostip = host.get('ip', hostname)
            hostport = host.get("port")
            username = host.get("username")
            password = host.get("password")
            ssh_key = host.get("ssh_key")
            my_host = Host(name=hostname, port=hostport)
            my_host.set_variable('ansible_ssh_host', hostip)
            my_host.set_variable('ansible_ssh_port', hostport)
            my_host.set_variable('ansible_ssh_user', username)
            my_host.set_variable('ansible_ssh_pass', password)
            my_host.set_variable('ansible_ssh_private_key_file', ssh_key)
 
            # set other variables 
            for key, value in host.iteritems():
                if key not in ["hostname", "port", "username", "password"]:
                    my_host.set_variable(key, value)
            # add to group
            my_group.add_host(my_host)
 
        self.inventory.add_group(my_group)
 
    def gen_inventory(self):
        """
        add hosts to inventory.
        """
        if isinstance(self.resource, list):
            self.my_add_group(self.resource, 'default_group')
        elif isinstance(self.resource, dict):
            for groupname, hosts_and_vars in self.resource.iteritems():
                self.my_add_group(hosts_and_vars.get("hosts"), groupname, hosts_and_vars.get("vars"))
 
 
class MyRunner(MyInventory):
    """
    This is a General object for parallel execute modules.
    """
    def __init__(self, *args, **kwargs):
        super(MyRunner, self).__init__(*args, **kwargs)
        self.results_raw = {}
 
    def run(self, module_name='shell', module_args='', timeout=10, forks=10, pattern='*',
            become=False, become_method='sudo', become_user='root', become_pass='', transport='paramiko'):
        """
        run module from andible ad-hoc.
        module_name: ansible module_name
        module_args: ansible module args
        """
        hoc = Runner(module_name=module_name,
                     module_args=module_args,
                     timeout=timeout,
                     inventory=self.inventory,
                     pattern=pattern,
                     forks=forks,
                     become=become,
                     become_method=become_method,
                     become_user=become_user,
                     become_pass=become_pass,
                     transport=transport
                     )
        self.results_raw = hoc.run()
#         logger.debug(self.results_raw)
        return self.results_raw
 
    @property
    def results(self):
        """
        {'failed': {'localhost': ''}, 'ok': {'jumpserver': ''}}
        """
        result = {'failed': {}, 'ok': {}}
        dark = self.results_raw.get('dark')
        contacted = self.results_raw.get('contacted')
        if dark:
            for host, info in dark.items():
                result['failed'][host] = info.get('msg')
 
        if contacted:
            for host, info in contacted.items():
                if info.get('invocation').get('module_name') in ['raw', 'shell', 'command', 'script']:
                    if info.get('rc') == 0:
                        result['ok'][host] = info.get('stdout') + info.get('stderr')
                    else:
                        result['failed'][host] = info.get('stdout') + info.get('stderr')
                else:
                    if info.get('failed'):
                        result['failed'][host] = info.get('msg')
                    else:
                        result['ok'][host] = info.get('changed')
        return result
 
 
class Command(MyInventory):
    """
    this is a command object for parallel execute command.
    """
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.results_raw = {}
 
    def run(self, command, module_name="command", timeout=10, forks=10, pattern=''):
        """
        run command from andible ad-hoc.
        command  : 必须是一个需要执行的命令字符串， 比如 
                 'uname -a'
        """
        data = {}
 
        if module_name not in ["raw", "command", "shell"]:
            raise CommandValueError("module_name",
                                    "module_name must be of the 'raw, command, shell'")
        hoc = Runner(module_name=module_name,
                     module_args=command,
                     timeout=timeout,
                     inventory=self.inventory,
                     pattern=pattern,
                     forks=forks,
                     )
        self.results_raw = hoc.run()
 
    @property
    def result(self):
        result = {}
        for k, v in self.results_raw.items():
            if k == 'dark':
                for host, info in v.items():
                    result[host] = {'dark': info.get('msg')}
            elif k == 'contacted':
                for host, info in v.items():
                    result[host] = {}
                    if info.get('stdout'):
                        result[host]['stdout'] = info.get('stdout')
                    elif info.get('stderr'):
                        result[host]['stderr'] = info.get('stderr')
        return result
 
    @property
    def state(self):
        result = {}
        if self.stdout:
            result['ok'] = self.stdout
        if self.stderr:
            result['err'] = self.stderr
        if self.dark:
            result['dark'] = self.dark
        return result
 
    @property
    def exec_time(self):
        """
        get the command execute time.
        """
        result = {}
        all = self.results_raw.get("contacted")
        for key, value in all.iteritems():
            result[key] = {
                    "start": value.get("start"),
                    "end"  : value.get("end"),
                    "delta": value.get("delta"),}
        return result
 
    @property
    def stdout(self):
        """
        get the comamnd standard output.
        """
        result = {}
        all = self.results_raw.get("contacted")
        for key, value in all.iteritems():
            result[key] = value.get("stdout")
        return result
 
    @property
    def stderr(self):
        """
        get the command standard error.
        """
        result = {}
        all = self.results_raw.get("contacted")
        for key, value in all.iteritems():
            if value.get("stderr") or value.get("warnings"):
                result[key] = {
                    "stderr": value.get("stderr"),
                    "warnings": value.get("warnings"),}
        return result
 
    @property
    def dark(self):
        """
        get the dark results.
        """
        return self.results_raw.get("dark")
 
 
class CustomAggregateStats(callbacks.AggregateStats):
    """                                                                             
    Holds stats about per-host activity during playbook runs.                       
    """
    def __init__(self):
        super(CustomAggregateStats, self).__init__()
        self.results = []
 
    def compute(self, runner_results, setup=False, poll=False,
                ignore_errors=False):
        """                                                                         
        Walk through all results and increment stats.                               
        """
        super(CustomAggregateStats, self).compute(runner_results, setup, poll,
                                              ignore_errors)
 
        self.results.append(runner_results)
 
    def summarize(self, host):
        """                                                                         
        Return information about a particular host                                  
        """
        summarized_info = super(CustomAggregateStats, self).summarize(host)
 
        # Adding the info I need                                                    
        summarized_info['result'] = self.results
 
        return summarized_info
 
 
class MyPlaybook(MyInventory):
    """
    this is my playbook object for execute playbook.
    """
    def __init__(self, *args, **kwargs):
        super(MyPlaybook, self).__init__(*args, **kwargs)
 
    def run(self, playbook_relational_path, extra_vars=None):
        """
        run ansible playbook,
        only surport relational path.
        """
        stats = callbacks.AggregateStats()
        playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)
        playbook_path = os.path.join(ANSIBLE_DIR, playbook_relational_path)
 
        pb = PlayBook(
            playbook=playbook_path,
            stats=stats,
            callbacks=playbook_cb,
            runner_callbacks=runner_cb,
            inventory=self.inventory,
            extra_vars=extra_vars,
            check=False)
 
        self.results = pb.run()
 
    @property
    def raw_results(self):
        """
        get the raw results after playbook run.
        """
        return self.results
 
 
class App(MyPlaybook):
    """
    this is a app object for inclue the common playbook.
    """
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
 
 
if __name__ == "__main__":
 
#   resource =  {
#                "group1": {
#                    "hosts": [{"hostname": "127.0.0.1", "port": "22", "username": "root", "password": "xxx"},],
#                    "vars" : {"var1": "value1", "var2": "value2"},
#                          },
#                }
 
    resource = [{"hostname": "192.168.1.184", "port": "22", "username": "root", "password": "jj123456",
                 # "ansible_become": "yes",
                 # "ansible_become_method": "sudo",
                 # # "ansible_become_user": "root",
                 # "ansible_become_pass": "yusky0902",
                 }]
 
    playbook = MyPlaybook(resource)
    playbook.run('nginx.yml')
    print playbook.raw_results
     
    cmd = Command(resource)
    cmd.run('hostname', pattern='*')
    print cmd.stdout    
 
 
 
 


