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

import os, sys, subprocess, shutil

def fsize(fname):
    r = os.stat(fname)
    return r.st_size

class Measurer:
    def __init__(self):
        self.source_cpp = 'cpp'
        self.build_cpp = 'buildcpp'
        self.cpp_exe = os.path.join(self.build_cpp, 'cppbin')
        self.meson_exe = '../meson/meson.py'

    def run(self):
        if os.path.exists(self.build_cpp):
            shutil.rmtree(self.build_cpp)
        subprocess.check_call('./generate.py')
        subprocess.check_call([self.meson_exe, '--buildtype=debugoptimized', self.source_cpp, self.build_cpp])
        subprocess.check_call(['ninja', '-C', self.build_cpp])
        cpp_size = fsize(self.cpp_exe)
        subprocess.check_call(['strip', self.cpp_exe])
        cpp_stripped_size = fsize(self.cpp_exe)

        print('C++ unstripped', cpp_size)
        print('C++ stripped', cpp_stripped_size)

if __name__ == '__main__':
    m = Measurer()
    m.run()
