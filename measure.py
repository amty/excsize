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
        self.source_c = 'plainc'
        self.build_c = 'buildc'
        self.c_exe = os.path.join(self.build_c, 'cbin')
        self.meson_exe = '../meson/meson.py'

    def build_and_measure(self, src_dir, build_dir, bin_name, extra_args = [], env=None):
        if os.path.exists(build_dir):
            shutil.rmtree(build_dir)
        subprocess.check_call([self.meson_exe, src_dir, build_dir] + extra_args, env=env)
        subprocess.check_call(['ninja', '-C', build_dir])
        size = fsize(bin_name)
        subprocess.check_call(['strip', bin_name])
        stripped_size = fsize(bin_name)
        return (size, stripped_size)

    def run(self):
        # Do not use ccache. Just in case.
        os.environ['CC'] = 'cc'
        os.environ['CXX'] = 'c++'
        subprocess.check_call('./generate.py')

        c_size, c_stripped_size = self.build_and_measure(self.source_c,
                                                         self.build_c,
                                                         self.c_exe,
                                                         ['--buildtype=debugoptimized'])
        cpp_size, cpp_stripped_size = self.build_and_measure(self.source_cpp,
                                                             self.build_cpp,
                                                             self.cpp_exe,
                                                             ['--buildtype=debugoptimized'])
        noexc_env = os.environ.copy()
        noexc_env['CXXFLAGS'] = '-fno-exceptions'
        noexc_size, noexc_stripped_size = self.build_and_measure(self.source_cpp,
                                                                 self.build_cpp,
                                                                 self.cpp_exe,
                                                                 ['--buildtype=debugoptimized'],
                                                                 env=noexc_env)
        print('C unstripped', c_size)
        print('C stripped', c_stripped_size)
        print('C++ unstripped', cpp_size)
        print('C++ stripped', cpp_stripped_size)
        print('C++ (noexcept) unstripped', noexc_size)
        print('C++ (noexcept) stripped', noexc_stripped_size)

if __name__ == '__main__':
    m = Measurer()
    m.run()
