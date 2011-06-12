CODE_DIR = '~/example'
BASE_DIR = '~/base'

REPO = 'git://github.com/peter-the-tea-drinker/tornado-base.git'
BASE_REPO = 'git://github.com/peter-the-tea-drinker/tornado-base.git'
TAG = ''

from fabric.api import local, settings, abort, run, cd, env
# dump this into the wsgi 

settings_dict = dict()

def update_settings(**updated_settings):
    settings_dict.update(updated_settings)

# set defaults for settings_dict
update_settings(code_dir=CODE_DIR,repo=REPO,release_tag=TAG)

def hello():
    print("Hello world!")

# deploy base. This means you can "import base.fabbase", "import base.*_base"
# for now, this means pulling the base of the repo into the source dir

def deploy():
    code_dir = settings_dict['code_dir']
    repo = settings_dict['repo']
    release_tag = settings_dict['release_tag']
    with settings(warn_only=True):
        if run("test -d %s/.git" % code_dir).failed:
            run("git clone %s %s" % (repo,code_dir))
    with cd(code_dir):
        run("git pull")
        if release_tag:
            run('git checkout :/"%s"'%release_tag)
        run("touch tmp/restart.txt")

