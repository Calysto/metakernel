#!/usr/bin/env python
'''
PEXPECT LICENSE

    This license is approved by the OSI and FSF as GPL-compatible.
        http://opensource.org/licenses/isc-license.txt

    Copyright (c) 2012, Noah Spurrier <noah@noah.org>
    PERMISSION TO USE, COPY, MODIFY, AND/OR DISTRIBUTE THIS SOFTWARE FOR ANY
    PURPOSE WITH OR WITHOUT FEE IS HEREBY GRANTED, PROVIDED THAT THE ABOVE
    COPYRIGHT NOTICE AND THIS PERMISSION NOTICE APPEAR IN ALL COPIES.
    THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
    WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
    MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
    ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
    WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
    ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
    OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

'''
import unittest
import subprocess
import sys
import os

from .. import pexpect

# Many of these test cases blindly assume that sequential directory
# listings of the /bin directory will yield the same results.
# This may not be true, but seems adequate for testing now.
# I should fix this at some point.

FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])
def hex_dump(src, length=16):
    result=[]
    for i in xrange(0, len(src), length):
       s = src[i:i+length]
       hexa = ' '.join(["%02X"%ord(x) for x in s])
       printable = s.translate(FILTER)
       result.append("%04X   %-*s   %s\n" % (i, length*3, hexa, printable))
    return ''.join(result)

def hex_diff(left, right):
        diff = ['< %s\n> %s' % (_left, _right,) for _left, _right in zip(
            hex_dump(left).splitlines(), hex_dump(right).splitlines())
            if _left != _right]
        return '\n' + '\n'.join(diff,)


class ExpectTestCase (unittest.TestCase):

    def setUp(self):
        self.PYTHONBIN = sys.executable
        os.chdir(os.path.dirname(__file__))

    def test_expect (self):
        the_old_way = subprocess.Popen(args=['ls', '-l', '/bin'],
                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8')
        p = pexpect.spawn('ls -l /bin')
        the_new_way = ''
        while 1:
            i = p.expect ([u'\n', pexpect.EOF])
            the_new_way = the_new_way + p.before
            if i == 1:
                break
        the_new_way = the_new_way.rstrip()
        the_new_way = the_new_way.replace('\r\n', '\n'
                ).replace('\r', '\n').replace('\n\n', '\n').rstrip()
        the_old_way = the_old_way.replace('\r\n', '\n'
                ).replace('\r', '\n').replace('\n\n', '\n').rstrip()
        assert the_old_way == the_new_way, hex_diff(the_old_way, the_new_way)

    def test_expect_exact (self):
        the_old_way = subprocess.Popen(args=['ls', '-l', '/bin'],
                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8')
        p = pexpect.spawn('ls -l /bin')
        the_new_way = ''
        while 1:
            i = p.expect_exact ([u'\n', pexpect.EOF])
            the_new_way = the_new_way + p.before
            if i == 1:
                break
        the_new_way = the_new_way.replace('\r\n', '\n'
                ).replace('\r', '\n').replace('\n\n', '\n').rstrip()
        the_old_way = the_old_way.replace('\r\n', '\n'
                ).replace('\r', '\n').replace('\n\n', '\n').rstrip()
        assert the_old_way == the_new_way, hex_diff(the_old_way, the_new_way)
        p = pexpect.spawn('echo hello.?world')
        i = p.expect_exact(u'.?')
        self.assertEqual(p.before, 'hello')
        self.assertEqual(p.after, '.?')

    def test_expect_eof (self):
        the_old_way = subprocess.Popen(args=['/bin/ls', '-l', '/bin'],
                stdout=subprocess.PIPE).communicate()[0].rstrip().decode('utf-8')
        p = pexpect.spawn('/bin/ls -l /bin')
        p.expect(pexpect.EOF) # This basically tells it to read everything. Same as pexpect.run() function.
        the_new_way = p.before
        the_new_way = the_new_way.replace('\r\n', '\n'
                ).replace('\r', '\n').replace('\n\n', '\n').rstrip()
        the_old_way = the_old_way.replace('\r\n', '\n'
                ).replace('\r', '\n').replace('\n\n', '\n').rstrip()
        assert the_old_way == the_new_way, hex_diff(the_old_way, the_new_way)

    def test_expect_timeout (self):
        p = pexpect.spawn('cat', timeout=5)
        p.expect(pexpect.TIMEOUT) # This tells it to wait for timeout.
        self.assertEqual(p.after, pexpect.TIMEOUT)

if __name__ == '__main__':
    unittest.main()

suite = unittest.makeSuite(ExpectTestCase, 'test')
