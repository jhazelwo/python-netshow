# python-netshow

A friendlier version of `netstat`

## usage

```
usage: netshow.py [--json|--dict|-s|-h] ['PATTERN' | WORDS]

--json    : Output as iterable of JSON objects.
--dict    : Output as list of dicts.
-s        : Hide header
-h|--help : Help

Wrap regex in single quotes.
Words can be any whole-string match.
```

## examples

* `./netshow.py `

```
Proto                           Local Address Port                          Foreign Address Port  State         PID Program name
tcp                                   0.0.0.0 22                                    0.0.0.0 *     LISTEN       1101 /usr/sbin/sshd
tcp                            172.28.142.138 22                             192.168.162.33 54101 ESTABLISHED 13269 /usr/sbin/sshd
udp                            172.28.142.138 123                                   0.0.0.0 *                  1109 /usr/sbin/ntpd
udp                                 127.0.0.1 123                                   0.0.0.0 *                  1109 /usr/sbin/ntpd
udp                                   0.0.0.0 123                                   0.0.0.0 *                  1109 /usr/sbin/ntpd
tcp6                                       :: 22                                         :: *     LISTEN       1101 /usr/sbin/sshd
udp6                 fe80::250:56ff:feb1:69bd 123                                        :: *                  1109 /usr/sbin/ntpd
udp6                                      ::1 123                                        :: *                  1109 /usr/sbin/ntpd
udp6                                       :: 123                                        :: *                  1109 /usr/sbin/ntpd
```

* `./netshow.py udp6`

```
Proto                           Local Address Port                          Foreign Address Port  State         PID Program name
udp6                 fe80::250:56ff:feb1:69bd 123                                        :: *                  1109 /usr/sbin/ntpd
udp6                                      ::1 123                                        :: *                  1109 /usr/sbin/ntpd
udp6                                       :: 123                                        :: *                  1109 /usr/sbin/ntpd
```

* `./netshow.py '22|123' -s`

```
tcp                                   0.0.0.0 22                                    0.0.0.0 *     LISTEN       1101 /usr/sbin/sshd
tcp                            172.28.142.138 22                             192.168.162.33 54101 ESTABLISHED 13269 /usr/sbin/sshd
udp                            172.28.142.138 123                                   0.0.0.0 *                  1109 /usr/sbin/ntpd
udp                                 127.0.0.1 123                                   0.0.0.0 *                  1109 /usr/sbin/ntpd
udp                                   0.0.0.0 123                                   0.0.0.0 *                  1109 /usr/sbin/ntpd
tcp6                                       :: 22                                         :: *     LISTEN       1101 /usr/sbin/sshd
udp6                 fe80::250:56ff:feb1:69bd 123                                        :: *                  1109 /usr/sbin/ntpd
udp6                                      ::1 123                                        :: *                  1109 /usr/sbin/ntpd
udp6                                       :: 123                                        :: *                  1109 /usr/sbin/ntpd
```

* `./netshow.py LISTEN`

```
Proto                           Local Address Port                          Foreign Address Port  State         PID Program name
tcp                                   0.0.0.0 22                                    0.0.0.0 *     LISTEN       1101 /usr/sbin/sshd
tcp6                                       :: 22                                         :: *     LISTEN       1101 /usr/sbin/sshd
```
