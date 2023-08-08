#!/usr/bin/env python3
# -*- Python -*-
# -*- coding: utf-8 -*-

from setuptools import Command 
from setuptools._distutils import errors 
from setuptools._distutils import log
from setuptools._distutils import util
from setuptools._distutils import cmd
import os
import os.path
import setuptools
import shutil
import subprocess

baseidl_files = [
    "BasicDataType.idl",
    "DataPort.idl",
    "ExtendedDataTypes.idl",
    "InterfaceDataTypes.idl",
    "Manager.idl",
    "OpenRTM.idl",
    "RTC.idl",
    "SDOPackage.idl",
    "SharedMemory.idl",
    "IORProfile.idl",
    "../ext/sdo/observer/ComponentObserver_OpenRTM.idl",
    "ExtendedFsmService.idl",
    "DataPort_OpenRTM.idl",
    "CSPPort.idl",
    "../ext/fsm4rtc_observer/ComponentObserver.idl",
    "ext/rtmCamera/CameraCommonInterface.idl",
    "ext/rtmManipulator/ManipulatorCommonInterface_Common.idl",
    "ext/rtmManipulator/ManipulatorCommonInterface_DataTypes.idl",
    "ext/rtmManipulator/ManipulatorCommonInterface_Middle.idl"
]

class BuildIDL(Command):
    description = 'generate Python stubs from the IDL files'


    def initialize_options(self):
        self.omniidl = None
        self.stubs_dir = None
        self.idl_dir = None
        self.build_lib = None

    def finalize_options(self):
        if not self.omniidl:
            self.omniidl = 'omniidl'
        if not self.stubs_dir:
            self.set_undefined_options('build', ('build_base', 'stubs_dir'))
            self.stubs_dir = os.path.join(self.stubs_dir, 'stubs')
        if not self.idl_dir:
            self.set_undefined_options('build', ('build_base', 'idl_dir'))
            self.idl_dir = os.path.join(self.idl_dir, 'OpenRTM_aist/RTM_IDL')
        self.idl_src_dir = os.path.join(os.getcwd(), 'OpenRTM_aist/RTM_IDL')
        self.examples_dir = os.path.join(os.getcwd(), 'OpenRTM_aist/examples')
        self.set_undefined_options('build', ('build_lib', 'build_lib'))

    def compile_one_idl(self, idl_f):
        outdir_param = '-C' + self.stubs_dir
        pkg_param = '-Wbpackage=OpenRTM_aist.RTM_IDL'
        idl_path_param = '-I' + 'OpenRTM_aist/RTM_IDL'
        p = subprocess.Popen([self.omniidl, '-bpython', idl_path_param,
                              outdir_param, pkg_param, idl_f],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise errors.DistutilsExecError(
                'Failed to compile IDL file {}\nStdout:\n{}\n---\nStderr:\n'
                '{}'.format(idl_f, stdout, stderr))

    def compile_idl(self):
        log.info('***Generating Python stubs from IDL files')
        self.mkpath(self.stubs_dir)
        idl_files = [os.path.join(self.idl_src_dir, f) for f in baseidl_files]
        for f in idl_files:
            log.info('*** compile_idl3 : {}'.format(f))
            self.compile_one_idl(f)

    def move_stubs(self):
        stub_dest = os.path.join(self.build_lib, 'OpenRTM_aist', 'RTM_IDL')
        log.info('Moving stubs to package directory {}'.format(stub_dest))
        self.copy_tree(os.path.join(self.stubs_dir, 'OpenRTM_aist', 'RTM_IDL'),
                       stub_dest)

    def copy_idl(self):
        log.info('Copying IDL files')
        self.mkpath(self.idl_dir)
        idl_files = [os.path.join(self.idl_src_dir, f)
                     for f in os.listdir(self.idl_src_dir)
                     if os.path.splitext(f)[1] == '.idl']
        for f in idl_files:
            shutil.copy(f, self.idl_dir)

    def compile_example_idl(self, idl_f, pkg_param, current_dir):
        outdir_param = '-C' + current_dir 
        idl_path_param = '-IOpenRTM_aist/RTM_IDL ' + idl_f
        p = subprocess.Popen([self.omniidl, '-bpython', idl_path_param,
                              outdir_param, pkg_param, idl_f],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise errors.DistutilsExecError(
                'Failed to compile IDL file {}\nStdout:\n{}\n---\nStderr:\n'
                '{}'.format(idl_f, stdout, stderr))

    def examples_idl(self):
        log.info('Generating Python stubs from examples IDL files')
        #../examples/SimpleService
        self.mkpath(self.examples_dir)
        current_dir = os.path.join(self.examples_dir, 'SimpleService')
        idl_file = os.path.join(current_dir, "MyService.idl")
        pkg_param = '-Wbpackages=OpenRTM_aist.examples.SimpleService'
        self.compile_example_idl(idl_file, pkg_param, current_dir)

        #../examples/AutoTest
        current_dir = os.path.join(self.examples_dir, 'AutoTest')
        idl_file = os.path.join(current_dir, "AutoTestService.idl")
        pkg_param = '-Wbpackages=OpenRTM_aist.examples.AutoTest'
        self.compile_example_idl(idl_file, pkg_param, current_dir)

    def copy_examples_idl(self):
        log.info('Copying IDL files of sample RTC')
        example_dest= os.path.join(self.build_lib, 'OpenRTM_aist', 'examples', 'AutoTest')
        target_dir = os.path.join(self.examples_dir, 'AutoTest')
        self.copy_tree(target_dir, example_dest)
        
        example_dest= os.path.join(self.build_lib, 'OpenRTM_aist', 'examples', 'SimpleService')
        target_dir = os.path.join(self.examples_dir, 'SimpleService')
        self.copy_tree(target_dir, example_dest)
        
    def run(self):
        self.compile_idl()
        self.move_stubs()
        self.copy_idl()
        self.examples_idl()
        self.copy_examples_idl()

