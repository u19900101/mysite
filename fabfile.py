def hello():
    print("Hello world!")
from fabric.api import local
def test():
    local('python manage.py test mysite')
# 测试是否能正常运行
def commit():
    local('git add -p && git commit -m "for test"')
def push():
    local('git push')
def prepare_deploy():
    test()
    commit()
    push()
####################################################################
from fabric.api import *

env.hosts = ['root@118.190.204.172:22']
env.password = 'Liupan1314'

#测试信息222222

def gitmysite():
    with settings(warn_only=True):
        with prefix('. /data/env/pyweb/bin/activate'):
            with cd("/data/wwwroot/mysite/"):
                run('git config --global credential.helper store')
                run('git fetch --all')
                run('git reset --hard origin/master')

def startenv3():
    with settings(warn_only=True):
        with prefix('. /data/env/pyweb/bin/activate'):
            with cd("/data/wwwroot/mysite/"):
                run('git pull')
            run('fuser -k 8997/tcp ')
            run('fuser -k 80/tcp ')
            with cd("/usr/local/nginx/sbin/"):
                run("./nginx")
            with cd("/data/wwwroot/mysite/"):
                run("uwsgi -x mysite.xml")
            with cd("/usr/local/nginx/sbin/"):
                run("./nginx -s reload")

def startenv4():
    with settings(warn_only=True):
        with prefix('. /data/env/pyweb/bin/activate'):
            with cd("/data/wwwroot/mysite/"):
                run('python manage.py collectstatic')





def deploy():
    gitmysite()
    startenv3()



# @runs_once           # 主机遍历过程中，只有第一台触发此函数
# def input_raw():
#     return prompt("Please input directory name:",default="/home")
#
#
# def worktask(dirname):
#     run("mkdir "+dirname)
#
# @task           # 限定只有go函数对fab命令可见
# def go():
#     # getdirname = input_raw()
# #     # worktask(getdirname)
# #
#     run("cd /data")
#     run("mkdir /k111")