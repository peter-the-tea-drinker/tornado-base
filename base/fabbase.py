from fabric.api import local, settings, abort, run, cd, env
# Common for both stage and prod, since stage and prod must be identical.

try: 
    import config
except:
    print 'No config file, please create a file (your_app/config.py)'

APP_REPO = config.APP_REPO
APP_TAG = config.APP_TAG

STAGE_APP_DIR = config.STAGE_APP_DIR
PROD_APP_DIR = config.PROD_APP_DIR

BASE_DIR = config.BASE_DIR
BASE_REPO = config.BASE_REPO
BASE_TAG = config.BASE_TAG

LOCAL_BASE_DIR = config.LOCAL_BASE_DIR
LOCAL_APP_DIR = config.LOCAL_APP_DIR

def dev():
    import os, sys
    import base.appbase
    import main
    import config
    from appbase import orm
    main.make_fixtures()
    base.appbase.tornado_serve(main.urls,debug=True,cookie_secret=config.COOKIE_SECRET)

def test():
    # run local unit tests
    result = local('nosetests', capture=False)

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

