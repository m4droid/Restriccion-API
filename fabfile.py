# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import re

from fabric.api import env, run
from fabric.colors import yellow
from fabric.context_managers import cd
from fabric.contrib.files import sed
from fabric.operations import put


UWSGI_VERSION = '2.0.12'

GIT_REPO = {
    'url': 'git@github.com:m4droid/Restriccion-API.git',
    'name': 'Restriccion-API'
}


def upload_config(file_):
    run('mkdir -p {0:s}/configs'.format(env.home))

    remote_config = os.path.join(env.home, 'configs', '{0:s}.json'.format(env.name))
    put(file_, remote_config)


def production(tag):
    env.name = 'production'
    env.type = 'production'
    env.hosts = ['restriccion.m4droid.com']
    env.user = 'restriccion'
    set_env_vars(tag)


def set_env_vars(tag):
    env.use_ssh_config = True

    env.tag = tag
    env.tag_clean = re.sub(r'[/\.]', '_', env.tag)

    env.home = '/home/{0:s}'.format(env.user)

    env.python_env_version = 'python3'
    env.python_env_path = os.path.join(env.home, 'deploys', env.tag_clean, 'env')

    env.git_repo_path = os.path.join(env.home, 'deploys', env.tag_clean, 'repo')

    env.log_path = os.path.join(env.home, 'deploys', env.tag_clean, 'logs')

    env.uwsgi_remote_file = os.path.join(env.home, 'uwsgi', 'uwsgi_{0:s}.ini'.format(env.name))

    env.migrate_db = True


def deploy():
    prepare_environment()
    repo_update()
    repo_activate_version()
    install_dependencies()
    uwsgi_config()
    create_symlinks()


def prepare_environment():
    print(yellow('\nPreparing environment'))
    with cd(env.home):
        run('mkdir -p ~/uwsgi')
        run('mkdir -p {0:s}'.format(env.log_path))

        run(
            '[ ! -d {1:s}/bin/pip ] && virtualenv -p {0:s} {1:s} || echo "Python environment already exists"'.format(
                env.python_env_version,
                env.python_env_path,
            )
        )
        run('{0:s}/bin/pip install -U uwsgi=={1:s}'.format(env.python_env_path, UWSGI_VERSION))
        run('{0:s}/bin/pip install -U newrelic'.format(env.python_env_path))


def repo_update():
    print(yellow('\nUpdate repository'))
    with cd(os.path.join(env.home, 'deploys', env.tag_clean)):
        run(
            '[ ! -d repo ] && git clone {0:s} repo || (cd repo && git fetch)'.format(
                GIT_REPO['url']
            )
        )


def repo_activate_version():
    print(yellow('\nActivating repository version'))
    with cd(env.git_repo_path):
        run(
            '(git show-ref --verify --quiet refs/heads/{0:s} && git checkout {0:s} && git pull) || git checkout {0:s}'.format(env.tag)
        )


def install_dependencies():
    print(yellow('\nInstalling dependencies'))
    with cd(env.git_repo_path):
        run('{0:s}/bin/pip3 install -r requirements.txt'.format(env.python_env_path))


def create_symlinks():
    print(yellow('\nCreate symlinks'))
    with cd(env.home):
        run('rm -f {0:s}/deploys/current; ln -sf {0:s}/deploys/{1:s} {0:s}/deploys/current'.format(
            env.home,
            env.tag_clean
        ))


def uwsgi_config():
    print(yellow('\nSetting up uWSGI'))

    put('deploy/{0:s}_uwsgi.ini'.format(env.type), env.uwsgi_remote_file)

    replacements = (
        ('ENV_NAME', env.name,),
        ('HOME', env.home,),
        ('VIRTUALENV_PATH', env.python_env_path,),
        ('PROJECT_PATH', env.git_repo_path,),
        ('LOG_PATH', os.path.join(env.log_path, 'uwsgi.log'),),
        ('ENV_VARS', _dump_env_vars_uwsgi({'ENV': env.name}),),
    )

    for replacement in replacements:
        sed(env.uwsgi_remote_file, '<{0:s}>'.format(replacement[0]), replacement[1])

    run('rm -f {0:s}/uwsgi/*.bak'.format(env.home))


def restart():
    uwsgi_stop()
    uwsgi_start()


def uwsgi_start():
    print(yellow('\nStart uWSGI'))
    run(
        'while [ -f {0:s}/uwsgi/uwsgi_{2:s}.pid ]; do sleep 1; done && {0:s}/deploys/current/env/bin/uwsgi --ini {1:s}'.format(
            env.home,
            env.uwsgi_remote_file,
            env.name,
        )
    )


def uwsgi_stop():
    print(yellow('\nStop uWSGI'))
    run(
        '(test -f {0:s}/uwsgi/uwsgi_{1:s}.pid && kill -SIGINT `cat {0:s}/uwsgi/uwsgi_{1:s}.pid`) || true'.format(
            env.home,
            env.name,
        )
    )


def _dump_env_vars_uwsgi(vars_):
    return '\\n'.join('env = {0:s}={1:s}'.format(*var) for var in vars_.items()).strip()
