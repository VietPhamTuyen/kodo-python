#! /usr/bin/env python
# encoding: utf-8

import os
from waflib.TaskGen import feature, after_method

APPNAME = 'kodo-python'
VERSION = '9.0.0'

import waflib.extras.wurf_options


def options(opt):

    opt.load('wurf_common_tools')
    opt.load('python')


def resolve(ctx):

    import waflib.extras.wurf_dependency_resolve as resolve

    ctx.load('wurf_common_tools')

    ctx.add_dependency(resolve.ResolveVersion(
        name='waf-tools',
        git_repository='github.com/steinwurf/waf-tools.git',
        major=3))

    ctx.add_dependency(resolve.ResolveVersion(
        name='boost',
        git_repository='github.com/steinwurf/boost.git',
        major=2))

    ctx.add_dependency(resolve.ResolveVersion(
        name='kodo',
        git_repository='github.com/steinwurf/kodo.git',
        major=32))


def configure(conf):

    conf.load("wurf_common_tools")


def build(bld):

    bld.load("wurf_common_tools")

    bld.env.append_unique(
        'DEFINES_STEINWURF_VERSION',
        'STEINWURF_KODO_PYTHON_VERSION="{}"'.format(VERSION))

    # Remove NDEBUG which is added from conf.check_python_headers
    flag_to_remove = 'NDEBUG'
    defines = ['DEFINES_PYEMBED', 'DEFINES_PYEXT']
    for define in defines:
        while(flag_to_remove in bld.env[define]):
            bld.env[define].remove(flag_to_remove)

    bld.env['CFLAGS_PYEXT'] = []
    bld.env['CXXFLAGS_PYEXT'] = []

    CXX = bld.env.get_flat("CXX")
    # Matches both /usr/bin/g++ and /user/bin/clang++
    if 'g++' in CXX or 'clang' in CXX:
        bld.env.append_value('CXXFLAGS', '-fPIC')

    bld.recurse('src/kodo_python')


@feature('pyext')
@after_method('apply_link')
def test_kodo_python(self):
    # Only execute the tests within the current project
    if self.path.is_child_of(self.bld.srcnode):
        if self.bld.has_tool_option('run_tests'):
            self.bld.add_post_fun(exec_test_python)


def exec_test_python(bld):
    python = bld.env['PYTHON'][0]
    env = dict(os.environ)
    env['PYTHONPATH'] = os.path.join(bld.out_dir, 'src', 'kodo_python')

    # First, run the unit tests in the 'test' folder
    if os.path.exists('test'):
        for f in sorted(os.listdir('test')):
            if f.endswith('.py'):
                test = os.path.join('test', f)
                bld.cmd_and_log('{0} {1}\n'.format(python, test), env=env)

    # Then run the examples in the 'examples' folder
    if os.path.exists('examples'):
        for f in sorted(os.listdir('examples')):
            if f.endswith('.py'):
                example = os.path.join('examples', f)
                bld.cmd_and_log(
                    '{0} {1} --dry-run\n'.format(python, example), env=env)
