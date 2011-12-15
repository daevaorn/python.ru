# -*- coding: utf-8 -*-
import os
import datetime
import yaml

import functools

from fabric.api import task, run, put, require, prompt, env
from fabric.context_managers import settings
from fabric.contrib import files


_ = lambda s: s.format(**env)


env.local_base = os.path.dirname(os.path.abspath(__file__))

env.project = 'pythonru'
env.hosts = ['linode.webnewage.org']
env.user = 'root'
env.www_user = 'www-data'

env.protected_envs = set(['stable'])


try:
    with open('private.yaml') as inp:
        for k, v in yaml.load(inp).iteritems():
            env[k] = v
except OSError:
    raise RuntimeError('`pricate.yaml` config is required for deployment')


def post_setup():
    env.remote_base_path    = _("/usr/lib/www/{env}")
    env.remote_env_path     = _("{remote_base_path}/{project}")
    env.remote_python       = _("{remote_env_path}/bin/python")
    env.remote_package_path = _("{remote_env_path}/src/{project}/{project}")
    env.remote_supervisor   = _('{remote_env_path}/bin/supervisor')
    env.remote_manage       = _('{remote_env_path}/bin/manage.py')
    env.remote_lib_path     = _('/var/lib/www/{env}/{project}')

    env.socket              = _('{remote_env_path}/run/socket')

    env.db_user      = _("{project}_{env}")
    env.db_base      = _("{project}_{env}_base")


def setup(func):
    @functools.wraps(func)
    def _decorator(*args, **kwargs):
        res = func(*args, **kwargs)

        post_setup()
        return res
    return _decorator


@task
@setup
def testing():
    """
    Initialize testing environment
    """
    env.env = 'testing'
    env.hostname = 'pru.webnewage.org'

    env.minspare = 0
    env.maxspare = 1
    env.maxchildren = 2


@task
@setup
def stable():
    """
    Initialize production environment
    """
    env.env = 'stable'
    env.hostname = 'python.ru'

    env.minspare = 1
    env.maxspare = 2
    env.maxchildren = 5


def require_env(func):
    @functools.wraps(func)
    def _decorator(*args, **kwargs):
        require('env', provided_by=('stable', 'testing'))

        return func(*args, **kwargs)
    return _decorator


def run_mysql(command):
    run(_('mysql -u root --password={db_root_password} -e "%s"' % command))


@task
@require_env
def cleanup():
    """
    Cleanup remote environment
    """
    with settings(warn_only=True):
        run(_('initctl stop {project}-{env}'))

    run(_('rm -f /etc/lighttpd/conf-enabled/90-{project}.{env}.conf'))
    run(_('rm -f /etc/cron.d/{project}-{env}'))
    run(_('rm -f /etc/logrotate.d/{project}.{env}'))
    run(_('rm -f /etc/init.d/{project}-{env}'))
    run(_('update-rc.d {project}-{env} remove'))

    run(_('rm -rf {remote_env_path}'))


@task
@require_env
def create_virtualenv():
    """Create virtual environment"""
    run(_('virtualenv -q {remote_env_path}'))
    run(_('mkdir -p {remote_env_path}/run'))
    run(_('mkdir -p {remote_env_path}/etc'))


@task
@require_env
def install_libs():
    """Install dependencies"""
    put(_('{local_base}/libs_requirements.txt'), _('{remote_env_path}/'))
    run(_('pip -q -E {remote_env_path} install --upgrade' +
          ' -r {remote_env_path}/libs_requirements.txt'))
    run(_('rm {remote_env_path}/libs_requirements.txt'))


@task
@require_env
def install():
    """Install project"""
    put(_('{local_base}/requirements.txt'), _('{remote_env_path}/'))
    run(_('pip -q -E {remote_env_path} install -U' +
          ' -r {remote_env_path}/requirements.txt'))
    run(_('rm {remote_env_path}/requirements.txt'))


@task
@require_env
def create_varlib():
    """Create /var/lib/ directory structure"""
    run(_('mkdir -p /var/lib/www/{env}/{project}/backups/'))
    run(_('mkdir -p /var/lib/www/{env}/{project}/logs/'))


def fix_owner_and_permissions(filename, owner='root', mod='a+r'):
    run('chown {owner}:{owner} {filename} -R'.format(owner=owner, filename=filename))
    run('chmod %s %s' % (mod, filename))


@task
@require_env
def configure():
    """Upload configuration files"""
    files.upload_template(
        _('conf/settings/{env}.py'),
        _('{remote_env_path}/etc/environment_settings.py'),
        env
    )
    files.upload_template(
        _('conf/lighttpd.conf'),
        _('/etc/lighttpd/conf-enabled/90-{project}.{env}.conf'),
        env,
    )
    files.upload_template(
        'conf/manage.py.tmpl',
        _('{remote_env_path}/bin/manage.py'),
        env
    )
    run(_('chmod +x {remote_env_path}/bin/manage.py'))

    files.upload_template(
        'conf/upstart.tmpl',
        _('/etc/init/{project}-{env}.conf'),
        env,
    )
    fix_owner_and_permissions(_('/etc/init/{project}-{env}.conf'))

    files.upload_template(
        'conf/logrotate.tmpl',
        _('/etc/logrotate.d/{project}-{env}'),
        env,
    )
    fix_owner_and_permissions(_('/etc/logrotate.d/{project}-{env}'))

    files.upload_template(
        'conf/crontab.tmpl',
        _('/etc/cron.d/{project}-{env}'),
        env,
    )
    fix_owner_and_permissions(_('/etc/cron.d/{project}-{env}'))

    run(_('chown {www_user}:{www_user} /var/lib/www/{env}/ -R'))
    run(_('chown {www_user}:{www_user} {remote_env_path} -R'))


@task
@require_env
def restart():
    """Reload daemons and web server"""
    #run('initctl restart mysql')
    run('/etc/init.d/lighttpd restart')
    run('/etc/init.d/memcached restart')
    run('initctl restart cron')

    with settings(warn_only=True):
        run(_('initctl stop {project}-{env}'))

    run(_('initctl start {project}-{env}'))


@task
@require_env
def migrate():
    """Run actual database migration"""
    run(_('{remote_manage} syncdb --noinput --migrate'))


@require_env
def drop_db():
    """
    Drop database
    """
    env.really_drop = "yes"

    if env.env in env.protected_envs:
        del env.really_drop
        prompt(
            "really_drop",
            _("Do you realy want to DROP {db_base} db? [yes/no]"),
            validate="yes|no"
        )

    if env.really_drop == "yes":
        run_mysql(_("DROP DATABASE {db_base};"))
    del env.really_drop


@task
@require_env
def init_db():
    """
    Setup database
    """
    run_mysql(_("GRANT ALL PRIVILEGES ON {db_base}.* TO '{db_user}'@'localhost'"
        "IDENTIFIED BY '{db_password}' WITH GRANT OPTION;"))

    run_mysql(_('CREATE DATABASE IF NOT EXISTS {db_base} CHARSET utf8;'))


@task
@require_env
def steal_db():
    """Copy stable database to current environment"""
    run(_('mysqldump -u root --create-options --password={db_root_password}'
          '{project}_stable_base '
          '| {remote_python} {remote_package_path}/manage.py dbshell'))


@task
@require_env
def backup():
    """Make a database backup"""
    run(_('mysqldump -u root --create-options --password={db_root_password} {project}_stable_base > /var/lib/www/{env}/{project}/backups/%s.sql' % datetime.datetime.now().isoformat()))


@task
@require_env
def bootstrap():
    """
    Deploy project on remote host
    """
    create_virtualenv()
    create_varlib()

    install_libs()

    deploy()

@task
@require_env
def deploy():
    """Upgrade current deployment code"""
    install()
    configure()
    restart()
    migrate()
