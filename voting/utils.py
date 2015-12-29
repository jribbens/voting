"""voting utility functions."""

import dns.exception
import dns.ipv4
import dns.ipv6
import dns.resolver


def fetch_asn_info(ipaddr):
    """Fetch ASN information for the given IP address."""
    try:
        v6addr = dns.ipv6.inet_aton(ipaddr)
        if dns.ipv6.is_mapped(v6addr):
            parts = ["{:d}".format(byte) for byte in v6addr[12:]]
        else:
            parts = ["{:x}.{:x}".format(byte & 0x0f, byte >> 4)
                     for byte in v6addr]
    except (ValueError, dns.exception.DNSException):
        parts = ["{:d}".format(byte) for byte in dns.ipv4.inet_aton(ipaddr)]
    parts.reverse()
    if len(parts) > 4:
        qname = ".".join(parts) + ".origin6.asn.cymru.com"
    else:
        qname = ".".join(parts) + ".origin.asn.cymru.com"
    try:
        answers = dns.resolver.query(qname, "TXT")
    except dns.exception.DNSException:
        return
    answer = answers[0].strings[0]
    qname = "as" + answer.split("|", 1)[0].strip() + ".asn.cymru.com"
    try:
        answers = dns.resolver.query(qname, "TXT")
    except dns.exception.DNSException:
        return answer
    answer += " | " + answers[0].strings[0].rsplit("|", 1)[1].strip()
    return answer
