#!/usr/bin/env python3

# Copyright (C) 2016 Jussi Pakkanen.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of version 3, or (at your option) any later version,
# of the GNU General Public License as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import random, os, sys, shutil

class GenerateCode:
    def __init__(self):
        self.cppdir = 'cpp'
        self.num_files = 1000
        self.cpp_header_templ = 'int func%d();\n'
        self.cpp_templ = '''#include<funcs.h>
int func%d() {
    int a = func%d();
    int b = func%d();
    int c = func%d();
    return a + b + c;
}
'''
        self.cpp_main = '''#include<funcs.h>

int main(int argc, char **argv) {
    return func0();
}
'''
    def deltrees(self):
        if os.path.exists(self.cppdir):
            shutil.rmtree(self.cppdir)
        os.mkdir(self.cppdir)

    def run(self):
        self.deltrees()
        headers = []
        headername = 'cpp/funcs.h'
        mesonfile = open('cpp/meson.build', 'w')
        mesonfile.write('''project('cpp size test', 'cpp', default_options : ['cpp_std=c++14'])
srcs = [
''')
        for i in range(self.num_files):
            ofname = 'cpp/src%d.cpp' % i
            headers.append(self.cpp_header_templ % i)
            mesonfile.write("  'src%d.cpp',\n" % i)
            if i == self.num_files-1:
                open(ofname, 'w').write('int func%d() { return 1; }\n' % (self.num_files-1))
                continue
            off1 = random.randint(1, 9)
            off2 = random.randint(1, 9)
            off3 = random.randint(1, 9)
            f1 = min(i + off1, 999)
            f2 = min(i + off2, 999)
            f3 = min(i + off3, 999)
            contents = self.cpp_templ % (i, f1, f2, f3)
            open(ofname, 'w').write(contents)
        with open(headername, 'w') as ofile:
            ofile.write('#pragma once\n')
            for h in headers:
                ofile.write(h)
        mesonfile.write("  'main.cpp',\n")
        open('cpp/main.cpp', 'w').write(self.cpp_main)
        mesonfile.write(''']

executable('cppbin', srcs)
''')
if __name__ == '__main__':
    g = GenerateCode()
    g.run()
