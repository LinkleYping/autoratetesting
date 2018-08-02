"""
UiPath project render.

When a new RAT added, just generate the project file for UiPath directly.
And then, open the project with UiPath and record PHFs.

:author cyrus
:date 7/9/2018
"""
import os
import sys
import threading
import time

from configuration import ROOT, COLLECTOR, COLLECTOR_NAME, LINE_NUMBER
from render import Render


def render_template(template, context, target):
    """
    Render context to the template and save it at `target`.

    :param template: Template file path.
    :param context: Dict.
    :param target: Target file path.
    """
    template_content = ''
    with open(template) as f:
        for line in f:
            template_content += line
        f.close()

    templite = Render(template_content, context)
    content_output = templite.render().strip("'")

    with open(target, 'w') as f:
        lines = content_output.split('\\n')
        for line in lines:
            f.write(line)
            f.write('\n')
        f.flush()
        f.close()

def run(psname):
    os.chdir(project_path)
    os.system("powershell .\\" + psname)


if __name__ == '__main__':
    flagc = 0
    flagd = 0
    if len(sys.argv) == 2:
        rat_path = sys.argv[-1]
    elif len(sys.argv) == 3 and sys.argv[-1] == '-c':
        rat_path = sys.argv[1]
        flagc = 1  # not use collector
    elif len(sys.argv) == 3 and sys.argv[-1] == '-d':
        rat_path = sys.argv[1]
        flagd = 1  # save the trace dependently
    else:
        print """=======Usage:=======\npython uipath_project_render.py [RAT_PATH] [-c] [-d]\n-c:if you don't want to use the collector\n-d:save the trace dependently\n==============="""
        print "please follow the usage"
        sys.exit(0)
    
    rat_name_exe = os.path.basename(rat_path)
    rat_name_v = rat_path.split('\\')[-2] # rat name with version
    rat_name = rat_name_exe[:-4]

    # make sure `uipath_project` exists first
    project_path = os.path.join(ROOT, 'uipath_projects', rat_name_v)
    if not os.path.exists(project_path):
        os.mkdir(project_path)

    # generate a PowerShell script to start the server
    rat_server_path = os.path.join(ROOT, 'rats', rat_name_v, 'server.exe')
    configuration_path = os.path.join(ROOT, 'apps', COLLECTOR, 'user_configuration.txt')
    context = {
        'RAT_SERVER_PATH': rat_server_path,
        'CONFIGURATION_PATH': configuration_path,
        'LINE_NUMBER': LINE_NUMBER,
    }
    start_server = os.path.join(project_path, 'start_server.ps1')
    render_template(os.path.join(ROOT, 'template', 'start_server.template'), context, start_server)
    os.chdir(project_path)
    os.system("powershell .\\start_server.ps1")
    print "server start"
    
    # use collector
    thread_collector = threading.Thread(target=run, args={"start_collector.ps1"})
    if flagc == 0:
        # generate a PowerShell script to start the collector
        context = {}
        start_collector = os.path.join(project_path, 'start_collector.ps1')
        render_template(os.path.join(ROOT, 'template', 'start_collector.template'), context, start_collector)
        thread_collector.start()
        print "collector start"
    time.sleep(20)
    # generate a PowerShell script to start the client
    rat_version_path = os.path.join(ROOT, 'rats', rat_name_v)
    context = {
        'RAT_VERSION': rat_version_path,
        'RAT_CLIENT_PATH': rat_path
    }
    start_client = os.path.join(project_path, 'start_client.ps1')
    render_template(os.path.join(ROOT, 'template', 'start_client.template'), context, start_client)
    thread_client = threading.Thread(target=run, args={"start_client.ps1"})
    thread_client.start()
    print "client start"
    time.sleep(10)

    if flagc == 0:
        if flagd == 0: # not dependently
            project_xaml_path = os.path.join(project_path, 'Main.xaml')
            xaml_name = 'Main'
            xaml_exe = os.path.join(project_path, 'Main.ps1')
            context = {
                'RAT_UIPATH': project_path,
                'RAT_UIPATH_XAML': project_xaml_path,
                'RAT_NAME': rat_name_v,
                'XAML_NAME': xaml_name
            }
            render_template(os.path.join(ROOT, 'template', 'xaml_execute.template'), context, xaml_exe)
            os.chdir(project_path)
            os.system("powershell .\\" + xaml_name + ".ps1")

        elif flagd == 1: # save dependently
            phf_names = {'Keylogger', 'RemoteDesktop', 'RemoteShell', 'RemoteAudio', 'Download_Execution'}
            for phf_name in phf_names:
                project_xaml_path = os.path.join(project_path, phf_name + '.xaml')
                xaml_exe = os.path.join(project_path, phf_name + '.ps1')
                context = {
                    'RAT_UIPATH': project_path,
                    'RAT_UIPATH_XAML': project_xaml_path,
                    'RAT_NAME': rat_name_v,
                    'XAML_NAME': phf_name
                }
                render_template(os.path.join(ROOT, 'template', 'xaml_execute.template'), context, xaml_exe)
                os.chdir(project_path)
                os.system("powershell .\\" + phf_name + ".ps1")
    elif flagc == 1:
        project_xaml_path = os.path.join(project_path, 'Main.xaml')
        xaml_name = 'Main'
        xaml_exe = os.path.join(project_path, 'Main.ps1')
        context = {
            'RAT_UIPATH': project_path,
            'RAT_UIPATH_XAML': project_xaml_path
        }
        render_template(os.path.join(ROOT, 'template', 'start_xaml.template'), context, xaml_exe)
        os.chdir(project_path)
        os.system("powershell .\\" + xaml_name + ".ps1")
    print "uipath finished"

    # generate a PowerShell script to kill the process
    context = {
        'RAT_NAME': rat_name_exe
    }
    kill_process = os.path.join(project_path, 'kill_process.ps1')
    render_template(os.path.join(ROOT, 'template', 'kill_process.template'), context, kill_process)
    os.chdir(project_path)
    os.system("powershell .\\kill_process.ps1")

    print "exit successfully"
    sys.exit(0)
