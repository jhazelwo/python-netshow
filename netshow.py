#!/usr/bin/env python
""" -*- coding: utf-8 -*-
By: "John Hazelwood" <jhazelwo@users.noreply.github.com>

Tested with Python 2.6.6 on CentOS 6.5
"""

import re
import sys
import pwd
import os
import glob
import socket
import struct
import json
from pprint import pprint


class NetStack(object):
    """ Object to hold data about network connections. """
    def __init__(self):
        """ . """
        self.use_header = True  # Show header in __str__ output
        self.as_json = False    # Output as list of dicts.
        self.as_dict = False    # Output as iterable of JSON objects.
        self.results = []       # Store filter results, if any.
        self.contents = []      # Store complete network stack as list of dicts.
        self.contents.extend(self.proc_to_dict('tcp'))
        self.contents.extend(self.proc_to_dict('udp'))
        self.contents.extend(self.proc_to_dict('tcp6'))
        self.contents.extend(self.proc_to_dict('udp6'))

    def usage(self):
        return """
        netshow.py, version 1.0

        usage: netshow.py [--json|--dict|-s|-h] ['PATTERN' | WORDS]

        --json    : Output as iterable of JSON objects.
        --dict    : Output as list of dicts.
        -s        : Hide header
        -h|--help : Help

        Wrap regex in single quotes.
        Words can be any whole-string match.

        examples:
            netshow.py 80
            netshow.py tcp6
            netshow.py tcp 22
            netshow.py 10.2.3.4 53 'tcp|udp'
            netshow.py '.*sshd$'
        """

    def search_dict_values(self, pattern, d):
        """ . """
        is_regex = False
        special_charters = ['^', '*', '?', '[', '(', '|', '$']
        for has in special_charters:
            if has in pattern:
                is_regex = True
        if is_regex:
            for v in d.values():
                try:
                    if re.match(pattern, v):
                        return d
                except Exception as e:
                    print('invalid regex: {0}'.format(e))
                    exit(2)
        else:
            if pattern in d.values():
                return d
        return False

    def match_all_needles(self, needle, haystack):
        """ . """
        for n in needle:
            if n not in haystack and not self.search_dict_values(n, haystack):
                return False
        return haystack

    def filter(self, params):
        """ . """
        if not params:
            return True
        for connection in self.contents:
            match = self.match_all_needles(params, connection)
            if match:
                self.results.append(match)
        if not self.results:
            return False
        return True

    def line_to_dict(self, line, protocol):
        """ Construct dict of elements in {line}. """
        d = {}
        connection_states = {
            '01':'ESTABLISHED',
            '02':'SYN_SENT',
            '03':'SYN_RECV',
            '04':'FIN_WAIT1',
            '05':'FIN_WAIT2',
            '06':'TIME_WAIT',
            '07':'CLOSE',
            '08':'CLOSE_WAIT',
            '09':'LAST_ACK',
            '0A':'LISTEN',
            '0B':'CLOSING' }
        line_array = self._remove_empty(line.split(' '))
        d['protocol'] = protocol
        d['local_ip'], d['local_port'] = self._convert_ip_port(line_array[1])
        d['remote_ip'], d['remote_port'] = self._convert_ip_port(line_array[2])
        if 'tcp' in protocol:
            d['state'] = connection_states[line_array[3]]
        else:
            d['state'] = ''
        d['pid'] = self.pid_of_inode(line_array[9])
        d['program'] = self.name_of_pid(d['pid'])
        return d

    def proc_to_dict(self, protocol):
        """ Return list of dicts of /proc/net/{protocol}. """
        if protocol not in ['tcp', 'tcp6', 'udp', 'udp6']:
            raise TypeError('Unknown protocol {0}'.format(protocol))
        l = []
        with open('/proc/net/{0}'.format(protocol), 'r') as handle:
            for line in handle:
                line = line.rstrip('\n').strip(' ')
                if ':' in line:
                    l.append(self.line_to_dict(line, protocol))
        return l

    def _convert_ip(self, address):
        """
        Convert and squash addresses to familiar format.
        ipv6    Convert '000080FE00000000FF565002BD69B1FE'
                To 'fe80::250:56ff:feb1:69bd'

        ipv4    Convert '8A8E1CAC'
                To '172.28.142.138'
        """
        if len(address) > 16:
            ## http://stackoverflow.com/questions/41940483
            address = address.decode('hex')
            address = struct.unpack('>IIII', address)
            address = struct.pack('@IIII', *address)
            address = socket.inet_ntop(socket.AF_INET6, address).lower()
        else:
            address = '{0}.{1}.{2}.{3}'.format(
                (self._hex2dec(address[6:8])),
                (self._hex2dec(address[4:6])),
                (self._hex2dec(address[2:4])),
                (self._hex2dec(address[0:2]))
            )
        return address

    def _hex2dec(self, this):
        """ . """
        return str(int(this,16))

    def _remove_empty(self, this):
        """ . """
        return [x for x in this if x]

    def _convert_ip_port(self, array):
        """ Convert ipaddress and port from hex to decimal."""
        host,port = array.split(':')
        _port = self._hex2dec(port)
        if _port == '0':
            _port = '*'
        return self._convert_ip(host),_port

    def pid_of_inode(self, inode):
        """ Find PID of process bound to given inode. """
        for item in glob.glob('/proc/[0-9]*/fd/[0-9]*'):
            try:
                if '[{0}]'.format(inode) in os.readlink(item):
                    return item.split('/')[2]
            except:
                pass
        return ''  # TIME_WAIT

    def name_of_pid(self, pid):
        """ Return /name/of/program if possible. """
        if pid:
            try:
                return os.readlink('/proc/{0}/exe'.format(pid))
            except:
                pass
        return ''  # No permission to see cmd (not owner or root)

    def __str__(self):
        """ Return contents as multi-line string similar to netstat. """
        template = '{protocol:<5} {local_ip:>39} {local_port:<5} ' + \
        '{remote_ip:>39} {remote_port:<5} {state:<11} {pid:>5} {program}\n'
        s = ''
        subject = self.contents
        if netstat.results:
            subject = self.results
        if self.as_json:
            return str(json.dumps(subject))
        if self.as_dict:
            return str(self.contents)
        if self.use_header:
            s = template.format(
                protocol = 'Proto',
                local_ip = 'Local Address',
                local_port = 'Port',
                remote_ip = 'Foreign Address',
                remote_port = 'Port',
                state = 'State',
                pid = 'PID',
                program = 'Program name'
            )
        for c in subject:
            s += template.format(
            protocol = c['protocol'],
            local_ip = c['local_ip'],
            local_port = c['local_port'],
            remote_ip = c['remote_ip'],
            remote_port = c['remote_port'],
            state = c['state'],
            pid = c['pid'],
            program = c['program']
            )
        return s.rstrip('\n')


if __name__ == '__main__':
    netstat = NetStack()
    args = sys.argv[1:]
    if '--help' in args or '-h' in args:
        print(netstat.usage())
        exit(0)
    if '--json' in args and '--dict' in args:
        print('--json and --dict are mutually exclusive')
        exit(1)
    if '--json' in args:
        netstat.as_json = True
        args.remove('--json')
    if '--dict' in args:
        netstat.as_dict = True
        args.remove('--dict')
    if '-s' in args:
        netstat.use_header = False
        args.remove('-s')
    if args and not netstat.filter(args):
        exit(1)
    print(netstat)
