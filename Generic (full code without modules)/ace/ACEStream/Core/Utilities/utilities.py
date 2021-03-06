#Embedded file name: ACEStream\Core\Utilities\utilities.pyo
import socket
from time import time, strftime, gmtime
from base64 import encodestring, decodestring
from ACEStream.Core.Utilities.TSCrypto import sha
import sys
import os
import copy
from types import UnicodeType, StringType, LongType, IntType, ListType, DictType
from ACEStream.Core.Utilities.odict import odict
import urlparse
from traceback import print_exc, print_stack
import binascii
STRICT_CHECK = True
DEBUG = False
infohash_len = 20

def bin2str(bin):
    return encodestring(bin).replace('\n', '')


def str2bin(str):
    return decodestring(str)


def validName(name):
    if not isinstance(name, str) and len(name) == 0:
        raise RuntimeError, 'invalid name: ' + name
    return True


def validPort(port):
    port = int(port)
    if port < 0 or port > 65535:
        raise RuntimeError, 'invalid Port: ' + str(port)
    return True


def validIP(ip):
    try:
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            socket.getaddrinfo(ip, None)
            return True

    except:
        print_exc()

    raise RuntimeError, 'invalid IP address: ' + ip


def get_ip(ip):
    try:
        socket.inet_aton(ip)
        return ip
    except socket.error:
        try:
            ip = socket.getaddrinfo(ip, None)[0][4][0]
        except:
            return


def validPermid(permid):
    if not isinstance(permid, str):
        raise RuntimeError, 'invalid permid: ' + permid
    return True


def validInfohash(infohash):
    if not isinstance(infohash, str):
        raise RuntimeError, 'invalid infohash ' + infohash
    if STRICT_CHECK and len(infohash) != infohash_len:
        raise RuntimeError, 'invalid length infohash ' + infohash
    return True


def isValidPermid(permid):
    try:
        return validPermid(permid)
    except:
        return False


def isValidInfohash(infohash):
    try:
        return validInfohash(infohash)
    except:
        return False


def isValidPort(port):
    try:
        return validPort(port)
    except:
        return False


def isValidIP(ip):
    try:
        return validIP(ip)
    except:
        return False


def isValidName(name):
    try:
        return validPort(name)
    except:
        return False


def validTorrentFile(metainfo):
    if type(metainfo) != DictType and type(metainfo) != odict:
        raise ValueError('metainfo not dict')
    if 'info' not in metainfo:
        raise ValueError('metainfo misses key info')
    if 'announce' in metainfo and not isValidURL(metainfo['announce']):
        raise ValueError('announce URL bad')
    if 'nodes' in metainfo:
        nodes = metainfo['nodes']
        if type(nodes) != ListType:
            raise ValueError('nodes not list, but ' + `(type(nodes))`)
        for pair in nodes:
            if type(pair) != ListType and len(pair) != 2:
                raise ValueError('node not 2-item list, but ' + `(type(pair))`)
            host, port = pair
            if type(host) != StringType:
                raise ValueError('node host not string, but ' + `(type(host))`)
            if type(port) != IntType:
                raise ValueError('node port not int, but ' + `(type(port))`)

    if not ('announce' in metainfo or 'nodes' in metainfo or 'announce-list' in metainfo):
        raise ValueError('announce, nodes and announce-list missing')
    if 'initial peers' in metainfo:
        if not isinstance(metainfo['initial peers'], list):
            raise ValueError('initial peers not list, but %s' % type(metainfo['initial peers']))
        for address in metainfo['initial peers']:
            if not (isinstance(address, tuple) and len(address) == 2):
                raise ValueError('address not 2-item tuple, but %s' % type(address))
            if not isinstance(address[0], str):
                raise ValueError('address host not string, but %s' % type(address[0]))
            if not isinstance(address[1], int):
                raise ValueError('address port not int, but %s' % type(address[1]))

    info = metainfo['info']
    if type(info) != DictType and type(info) != odict:
        raise ValueError('info not dict')
    if 'root hash' in info:
        infokeys = ['name', 'piece length', 'root hash']
    elif 'live' in info:
        infokeys = ['name', 'piece length', 'live']
    else:
        infokeys = ['name', 'piece length', 'pieces']
    for key in infokeys:
        if key not in info:
            raise ValueError('info misses key ' + key)

    name = info['name']
    if type(name) != StringType:
        raise ValueError('info name is not string but ' + `(type(name))`)
    pl = info['piece length']
    if type(pl) != IntType and type(pl) != LongType:
        raise ValueError('info piece size is not int, but ' + `(type(pl))`)
    if 'root hash' in info:
        rh = info['root hash']
        if type(rh) != StringType or len(rh) != 20:
            raise ValueError('info roothash is not 20-byte string')
    elif 'live' in info:
        live = info['live']
        if type(live) != DictType and type(live) != odict:
            raise ValueError('info live is not a dict')
        elif 'authmethod' not in live:
            raise ValueError('info live misses key' + 'authmethod')
    else:
        p = info['pieces']
        if type(p) != StringType or len(p) % 20 != 0:
            raise ValueError('info pieces is not multiple of 20 bytes')
    if 'length' in info:
        if 'files' in info:
            raise ValueError('info may not contain both files and length key')
        l = info['length']
        if type(l) != IntType and type(l) != LongType:
            raise ValueError('info length is not int, but ' + `(type(l))`)
    else:
        if 'length' in info:
            raise ValueError('info may not contain both files and length key')
        files = info['files']
        if type(files) != ListType:
            raise ValueError('info files not list, but ' + `(type(files))`)
        filekeys = ['path', 'length']
        for file in files:
            for key in filekeys:
                if key not in file:
                    raise ValueError('info files missing path or length key')

            p = file['path']
            if type(p) != ListType:
                raise ValueError('info files path is not list, but ' + `(type(p))`)
            for dir in p:
                if type(dir) != StringType:
                    raise ValueError('info files path is not string, but ' + `(type(dir))`)

            l = file['length']
            if type(l) != IntType and type(l) != LongType:
                raise ValueError('info files length is not int, but ' + `(type(l))`)

    if 'announce-list' in metainfo:
        al = metainfo['announce-list']
        if type(al) != ListType:
            del metainfo['announce-list']
        else:
            for tier in al:
                if type(tier) != ListType:
                    raise ValueError('announce-list tier is not list ' + `tier`)

    if 'azureus_properties' in metainfo:
        azprop = metainfo['azureus_properties']
        if type(azprop) != DictType and type(azprop) != odict:
            raise ValueError('azureus_properties is not dict, but ' + `(type(azprop))`)
        if 'Content' in azprop:
            content = azprop['Content']
            if type(content) != DictType and type(content) != odict:
                raise ValueError('azureus_properties content is not dict, but ' + `(type(content))`)
            if 'thumbnail' in content:
                thumb = content['thumbnail']
                if type(content) != StringType:
                    raise ValueError('azureus_properties content thumbnail is not string')
    if 'url-list' in metainfo:
        if 'files' in metainfo['info']:
            del metainfo['url-list']
            print >> sys.stderr, 'Warning: Only single-file mode supported with HTTP seeding. HTTP seeding disabled'
        elif type(metainfo['url-list']) != ListType:
            del metainfo['url-list']
            print >> sys.stderr, 'Warning: url-list is not of type list. HTTP seeding disabled'
        else:
            for url in metainfo['url-list']:
                if not isValidURL(url):
                    del metainfo['url-list']
                    print >> sys.stderr, 'Warning: url-list url is not valid: ', `url`, 'HTTP seeding disabled'
                    break

    if 'httpseeds' in metainfo:
        if type(metainfo['httpseeds']) != ListType:
            del metainfo['httpseeds']
            print >> sys.stderr, 'Warning: httpseeds is not of type list. HTTP seeding disabled'
        else:
            for url in metainfo['httpseeds']:
                if not isValidURL(url):
                    del metainfo['httpseeds']
                    print >> sys.stderr, 'Warning: httpseeds url is not valid: ', `url`, 'HTTP seeding disabled'
                    break

    return metainfo


def isValidTorrentFile(metainfo):
    try:
        validTorrentFile(metainfo)
        return True
    except:
        if DEBUG:
            print_exc()
        return False


def isValidURL(url):
    try:
        if url.lower().startswith('udp'):
            url = url.lower().replace('udp', 'http', 1)
        r = urlparse.urlsplit(url)
        if r[0] == '' or r[1] == '':
            return False
        return True
    except:
        return False


def show_permid(permid):
    if not permid:
        return 'None'
    return encodestring(permid).replace('\n', '')


def show_permid_short(permid):
    if not permid:
        return 'None'
    s = encodestring(permid).replace('\n', '')
    return s[-10:]


def show_permid_shorter(permid):
    if not permid:
        return 'None'
    s = encodestring(permid).replace('\n', '')
    return s[-5:]


def readableBuddyCastMsg(buddycast_data, selversion):
    prefxchg_msg = copy.deepcopy(buddycast_data)
    if prefxchg_msg.has_key('permid'):
        prefxchg_msg.pop('permid')
    if prefxchg_msg.has_key('ip'):
        prefxchg_msg.pop('ip')
    if prefxchg_msg.has_key('port'):
        prefxchg_msg.pop('port')
    name = repr(prefxchg_msg['name'])
    if prefxchg_msg['preferences']:
        prefs = []
        if selversion < 8:
            for pref in prefxchg_msg['preferences']:
                prefs.append(show_permid(pref))

        else:
            for preftuple in prefxchg_msg['preferences']:
                newlist = []
                for i in range(0, len(preftuple)):
                    if i == 0:
                        val = show_permid(preftuple[i])
                    else:
                        val = preftuple[i]
                    newlist.append(val)

                prefs.append(newlist)

        prefxchg_msg['preferences'] = prefs
    if prefxchg_msg.get('taste buddies', []):
        buddies = []
        for buddy in prefxchg_msg['taste buddies']:
            buddy['permid'] = show_permid(buddy['permid'])
            if buddy.get('preferences', []):
                prefs = []
                for pref in buddy['preferences']:
                    prefs.append(show_permid(pref))

                buddy['preferences'] = prefs
            buddies.append(buddy)

        prefxchg_msg['taste buddies'] = buddies
    if prefxchg_msg.get('random peers', []):
        peers = []
        for peer in prefxchg_msg['random peers']:
            peer['permid'] = show_permid(peer['permid'])
            peers.append(peer)

        prefxchg_msg['random peers'] = peers
    return prefxchg_msg


def print_prefxchg_msg(prefxchg_msg):

    def show_permid(permid):
        return permid

    print '------- preference_exchange message ---------'
    print prefxchg_msg
    print '---------------------------------------------'
    print 'permid:', show_permid(prefxchg_msg['permid'])
    print 'name', prefxchg_msg['name']
    print 'ip:', prefxchg_msg['ip']
    print 'port:', prefxchg_msg['port']
    print 'preferences:'
    if prefxchg_msg['preferences']:
        for pref in prefxchg_msg['preferences']:
            print '\t', pref

    print 'taste buddies:'
    if prefxchg_msg['taste buddies']:
        for buddy in prefxchg_msg['taste buddies']:
            print '\t permid:', show_permid(buddy['permid'])
            print '\t ip:', buddy['ip']
            print '\t port:', buddy['port']
            print '\t age:', buddy['age']
            print '\t preferences:'
            if buddy['preferences']:
                for pref in buddy['preferences']:
                    print '\t\t', pref

            print

    print 'random peers:'
    if prefxchg_msg['random peers']:
        for peer in prefxchg_msg['random peers']:
            print '\t permid:', show_permid(peer['permid'])
            print '\t ip:', peer['ip']
            print '\t port:', peer['port']
            print '\t age:', peer['age']
            print


def print_dict(data, level = 0):
    if isinstance(data, dict):
        print
        for i in data:
            print '  ' * level, str(i) + ':',
            print_dict(data[i], level + 1)

    elif isinstance(data, list):
        if not data:
            print '[]'
        else:
            print
        for i in xrange(len(data)):
            print '  ' * level, '[' + str(i) + ']:',
            print_dict(data[i], level + 1)

    else:
        print data


def friendly_time(old_time):
    curr_time = time()
    try:
        old_time = int(old_time)
        diff = int(curr_time - old_time)
    except:
        if isinstance(old_time, str):
            return old_time
        else:
            return '?'

    if diff < 0:
        return '?'
    elif diff < 2:
        return str(diff) + ' sec. ago'
    elif diff < 60:
        return str(diff) + ' secs. ago'
    elif diff < 120:
        return '1 min. ago'
    elif diff < 3600:
        return str(int(diff / 60)) + ' mins. ago'
    elif diff < 7200:
        return '1 hour ago'
    elif diff < 86400:
        return str(int(diff / 3600)) + ' hours ago'
    elif diff < 172800:
        return 'Yesterday'
    elif diff < 259200:
        return str(int(diff / 86400)) + ' days ago'
    else:
        return strftime('%d-%m-%Y', gmtime(old_time))


def sort_dictlist(dict_list, key, order = 'increase'):
    aux = []
    for i in xrange(len(dict_list)):
        if key in dict_list[i]:
            aux.append((dict_list[i][key], i))

    aux.sort()
    if order == 'decrease' or order == 1:
        aux.reverse()
    return [ dict_list[i] for x, i in aux ]


def dict_compare(a, b, keys):
    for key in keys:
        order = 'increase'
        if type(key) == tuple:
            skey, order = key
        else:
            skey = key
        if a.get(skey) > b.get(skey):
            if order == 'decrease' or order == 1:
                return -1
            else:
                return 1
        elif a.get(skey) < b.get(skey):
            if order == 'decrease' or order == 1:
                return 1
            else:
                return -1

    return 0


def multisort_dictlist(dict_list, keys):
    listcopy = copy.copy(dict_list)
    cmp = lambda a, b: dict_compare(a, b, keys)
    listcopy.sort(cmp=cmp)
    return listcopy


def find_content_in_dictlist(dict_list, content, key = 'infohash'):
    title = content.get(key)
    if not title:
        print 'Error: content had no content_name'
        return False
    for i in xrange(len(dict_list)):
        if title == dict_list[i].get(key):
            return i

    return -1


def remove_torrent_from_list(list, content, key = 'infohash'):
    remove_data_from_list(list, content, key)


def remove_data_from_list(list, content, key = 'infohash'):
    index = find_content_in_dictlist(list, content, key)
    if index != -1:
        del list[index]


def sortList(list_to_sort, list_key, order = 'decrease'):
    aux = zip(list_key, list_to_sort)
    aux.sort()
    if order == 'decrease':
        aux.reverse()
    return [ i for k, i in aux ]


def getPlural(n):
    if n == 1:
        return ''
    else:
        return 's'


def find_prog_in_PATH(prog):
    envpath = os.path.expandvars('${PATH}')
    if sys.platform == 'win32':
        splitchar = ';'
    else:
        splitchar = ':'
    paths = envpath.split(splitchar)
    foundat = None
    for path in paths:
        fullpath = os.path.join(path, prog)
        if os.access(fullpath, os.R_OK | os.X_OK):
            foundat = fullpath
            break

    return foundat


def hostname_or_ip2ip(hostname_or_ip):
    ip = None
    try:
        socket.inet_aton(hostname_or_ip)
        ip = hostname_or_ip
    except:
        try:
            ip = socket.gethostbyname(hostname_or_ip)
            if not hostname_or_ip.startswith('superpeer'):
                print >> sys.stderr, 'hostname_or_ip2ip: resolved ip from hostname, an ip should have been provided', hostname_or_ip
        except:
            print >> sys.stderr, 'hostname_or_ip2ip: invalid hostname', hostname_or_ip
            print_exc()

    return ip


def get_collected_torrent_filename(infohash):
    filename = sha(infohash).hexdigest() + '.torrent'
    return filename


def test_network_connection(url = None, host = None, port = 80, getip = False, timeout = 5):
    try:
        if host is None or port is None:
            url = urlparse.urlparse(url)
            port = url.port
            host = url.hostname
        if getip:
            try:
                return socket.gethostbyname(host)
            except:
                return

        if port is None:
            port = 80
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        return True
    except:
        return False


if __name__ == '__main__':
    torrenta = {'name': 'a',
     'swarmsize': 12}
    torrentb = {'name': 'b',
     'swarmsize': 24}
    torrentc = {'name': 'c',
     'swarmsize': 18,
     'Web2': True}
    torrentd = {'name': 'b',
     'swarmsize': 36,
     'Web2': True}
    torrents = [torrenta,
     torrentb,
     torrentc,
     torrentd]
    print multisort_dictlist(torrents, ['Web2', ('swarmsize', 'decrease')])
