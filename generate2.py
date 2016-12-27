#!/usr/bin/env python3
# Copyright (C) 2016 Jussi Pakkanen, Juhani Simola
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

# This is a slightly fancier version of generate that
# tries to produce very compact C code. It is still
# bigger than the C++ version.
#
# C unstripped 1365717
# C stripped 174192
# C++ unstripped 1317527
# C++ stripped 166080
# C++ (noexcept) unstripped 1087310
# C++ (noexcept) stripped 116832

import random, os, sys, shutil

class GenerateCode:
    def __init__(self):
        self.cppdir = 'cpp'
        self.num_files = 1000
        self.cpp_header_templ = 'int func%d();\n'
        self.cpp_templ = '''#include "funcs.h"

int func%d() {
    DummyObject dobj;
    int a = func%d();
    int b = func%d();
    int c = func%d();
    return a + b + c;
}

'''
        self.cpp_dummy = '''class DummyObject {
public:
    DummyObject();
    ~DummyObject();

private:

    int i;

};
'''
        self.cpp_main = '''#include "funcs.h"

DummyObject::DummyObject() { }
DummyObject::~DummyObject() {}

int main(int argc, char **argv) {
    return func0();
}

'''

        self.cdir = 'plainc'
        self.c_header_templ = 'bool func%d(int *val);\n'
        self.c_templ = '''#include "funcs.h"
#include <stdbool.h>
bool func%d(int *val) {
    int a, b, c;
    struct Dummy *d = dummy_new();
    bool success = func%d(&a) && func%d(&b) && func%d(&c);
    if (success)
        *val = a + b + c;
    dummy_delete(d);
    return success;
}

'''

        self.c_dummy = '''
#include <stdbool.h>

struct Dummy {
    int i;
};
    struct Dummy* dummy_new();
    void dummy_delete(struct Dummy *d);
'''

        self.c_main = '''#include "funcs.h"
#include<stdlib.h>

struct Dummy* dummy_new() {
    return malloc(sizeof(struct Dummy));
}

void dummy_delete(struct Dummy *d) {
    free(d);
}

int main(int argc, char **argv) {
    char *error = NULL;
    return func0(&error);
}

'''

    def deltrees(self):
        if os.path.exists(self.cppdir):
            shutil.rmtree(self.cppdir)
        os.mkdir(self.cppdir)
        if os.path.exists(self.cdir):
            shutil.rmtree(self.cdir)
        os.mkdir(self.cdir)

    def run(self):
        self.deltrees()
        cpp_headers = [self.cpp_dummy]
        c_headers = [self.c_dummy]
        cpp_headername = os.path.join(self.cppdir, 'funcs.h')
        c_headername = os.path.join(self.cdir, 'funcs.h')
        meson_cpp = open(os.path.join(self.cppdir, 'meson.build'), 'w')
        meson_c = open(os.path.join(self.cdir, 'meson.build'), 'w')
        meson_cpp.write('''project('cpp size test', 'cpp', default_options : ['cpp_std=c++11'])
srcs = [
''')
        meson_c.write('''project('c size test', 'c', default_options : ['cpp_std=gnu11'])
srcs = [
''')
        for i in range(self.num_files):
            cpp_ofname = os.path.join(self.cppdir, 'src%d.cpp' % i)
            c_ofname = os.path.join(self.cdir, 'src%d.c' % i)
            cpp_headers.append(self.cpp_header_templ % i)
            c_headers.append(self.c_header_templ % i)
            meson_cpp.write("  'src%d.cpp',\n" % i)
            meson_c.write("  'src%d.c',\n" % i)
            if i == self.num_files-1:
                open(cpp_ofname, 'w').write('int func%d() { return 1; }\n' % (self.num_files-1))
                open(c_ofname, 'w').write('int func%d(char **error) { return 1; }\n' % (self.num_files-1))
                continue
            off1 = random.randint(1, 9)
            off2 = random.randint(1, 9)
            off3 = random.randint(1, 9)
            f1 = min(i + off1, 999)
            f2 = min(i + off2, 999)
            f3 = min(i + off3, 999)
            cpp_contents = self.cpp_templ % (i, f1, f2, f3)
            c_contents = self.c_templ % (i, f1, f2, f3)
            open(cpp_ofname, 'w').write(cpp_contents)
            open(c_ofname, 'w').write(c_contents)
        with open(cpp_headername, 'w') as ofile:
            ofile.write('#pragma once\n')
            for h in cpp_headers:
                ofile.write(h)
        with open(c_headername, 'w') as ofile:
            ofile.write('#pragma once\n')
            for h in c_headers:
                ofile.write(h)
        meson_cpp.write("  'main.cpp',\n")
        meson_c.write("  'main.c',\n")
        open(os.path.join(self.cppdir, 'main.cpp'), 'w').write(self.cpp_main)
        open(os.path.join(self.cdir, 'main.c'), 'w').write(self.c_main)
        meson_cpp.write(''']

executable('cppbin', srcs)
''')
        meson_c.write(''']

executable('cbin', srcs)
''')

if __name__ == '__main__':
    g = GenerateCode()
    g.run()
