from fabric.api import local, settings, abort, run, cd, env
# Common for both stage and prod, since stage and prod must be identical.
APP_REPO = 'git://github.com/peter-the-tea-drinker/tornado-base-example.git'
APP_TAG = ''

STAGE_APP_DIR = '~/stage.example.com'
PROD_APP_DIR = '~/prod.example.com'

BASE_DIR = '~/tornado-base'
BASE_REPO = 'git://github.com/peter-the-tea-drinker/tornado-base.git'
BASE_TAG = ''

def stage():
    app_dir = STAGE_APP_DIR
    _deploy(code_dir=BASE_DIR,repo=BASE_REPO,release_tag=BASE_TAG)
    _deploy(code_dir=app_dir,repo=APP_REPO,release_tag=APP_TAG)
    _restart(code_dir=app_dir)

def prod():
    app_dir = PROD_APP_DIR
    _deploy(code_dir=BASE_DIR,repo=BASE_REPO,release_tag=BASE_TAG)
    _deploy(code_dir=app_dir,repo=APP_REPO,release_tag=APP_TAG)
    _restart(code_dir=app_dir)

def _deploy(code_dir,repo,release_tag):
    with settings(warn_only=True):
        if run("test -d %s/.git" % code_dir).failed:
            run("git clone %s %s" % (repo,code_dir))
    with cd(code_dir):
        run("git pull")
        if release_tag:
            run('git checkout :/"%s"'%release_tag)

def _restart(code_dir):
    with cd(code_dir):
        run("touch tmp/restart.txt")

