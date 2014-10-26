class NagiosMessage(object):
    """Representation of a Nagios message that is returned to NRPE"""
    NAGIOS_STATUS_OK = 0
    NAGIOS_STATUS_WARNING = 1
    NAGIOS_STATUS_CRITICAL = 2
    NAGIOS_STATUS_UNKNOWN = 3

    UOM_SEC = 's'
    UOM_MILLISEC = 'ms'
    UOM_PERCENT = '%'
    UOM_BYTE = 'B'
    UOM_KILOBYTE = 'KB'
    UOM_MEGABYTE = 'MB'
    UOM_TERABYTE = 'TB'
    UOM_CONTINUOUS = 'c'
    UOM_NONE = ''

    msg = []
    perfdata = []

    def __init__(self):
        # assume success until overridden
        self.status_code = self.NAGIOS_STATUS_OK

    def add_msg(self, msg):
        self.msg.append(msg)

    def raise_status(self, status_code):
        if status_code > self.status_code:
            self.status_code = status_code

    def add_perfdata(self, label, uom, real, warn, crit, minval='', maxval=''):
        datastr = "'%s'=%s%s;%s;%s;%s;%s" % (label, str(real), uom, str(warn), str(crit), str(minval), str(maxval))
        self.perfdata.append(datastr)

    def prepend_nagios_output(self, message):
        if self.status_code == self.NAGIOS_STATUS_OK:
            return 'OK: %s' % message
        elif self.status_code == self.NAGIOS_STATUS_WARNING:
            return 'WARNING: %s' % message
        elif self.status_code == self.NAGIOS_STATUS_CRITICAL:
            return 'CRITICAL: %s' % message
        elif self.status_code == self.NAGIOS_STATUS_UNKNOWN:
            return 'UNKNOWN: %s' % message

        return message

    def __str__(self):
        prepended_output = self.prepend_nagios_output(', '.join(self.msg) +
                                                      ' | ' + ' '.join(str(d) for d in self.perfdata))
        return prepended_output
