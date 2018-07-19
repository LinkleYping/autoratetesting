"""
UiPath project render.

When a new RAT added, just generate the project file for UiPath directly.
And then, open the project with UiPath and record PHFs.

:author cyrus
:date 7/9/2018
"""
import os
import sys

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


if __name__ == '__main__':
    rat_path = sys.argv[-1]
    rat_name_exe = os.path.basename(rat_path)
    rat_name_v = rat_path.split('\\')[-2] # rat name with version
    rat_name = rat_name_exe[:-4]

    # make sure `uipath_project` exists first
    project_path = os.path.join(ROOT, 'uipath_projects', rat_name_v)
    if not os.path.exists(project_path):
        os.mkdir(project_path)

    # generate a PowerShell script to update the PID
    rat_server_path = os.path.join(ROOT, 'rats', rat_name_v, 'server.exe')
    configuration_path = os.path.join(ROOT, 'apps', COLLECTOR, 'user_configuration.txt')
    context = {
        'RAT_SERVER_PATH': rat_server_path,
        'CONFIGURATION_PATH': configuration_path,
        'LINE_NUMBER': LINE_NUMBER,
    }
    update_pid_path = os.path.join(project_path, 'update_pid.ps1')
    render_template(os.path.join(ROOT, 'template', 'update_pid.template'), context, update_pid_path)

    # generate a PowerShell script to kill the processes
    context = {'RAT_NAME': rat_name_exe}
    kill_processes_path = os.path.join(project_path, 'kill_processes.ps1')
    render_template(os.path.join(ROOT, 'template', 'kill_processes.template'), context, kill_processes_path)

    # generate the warm up file
    collector_path = os.path.join(ROOT, 'apps', COLLECTOR, COLLECTOR_NAME)
    collector_work_directory = os.path.join(ROOT, 'apps', COLLECTOR)
    rat_work_directory = os.path.join(ROOT, 'rats', rat_name_v)
    context = {
        'ADDRESS_MAP_UPDATE_PATH': update_pid_path,
        'COLLECTOR_PATH': collector_path,
        'COLLECTOR_WORK_DIRECTORY': collector_work_directory, 
        'RAT_NAME': rat_name_exe, 
        'RAT_WORK_DIRECTORY': rat_work_directory,
    }
    warm_up_path = os.path.join(project_path, 'warm_up.xaml')
    render_template(os.path.join(ROOT, 'template', 'warm_up.template'), context, warm_up_path)

    # generate the wrap up file
    from_path = os.path.join(ROOT, 'apps', COLLECTOR, 'output.out')
    destination_path = os.path.join(ROOT, 'output', rat_name_v)
    context = {
        'KILL_RAT_PATH': kill_processes_path,
        'FROM_PATH': from_path, 
        'DESTINATION_PATH': destination_path, 
    }
    wrap_up_path = os.path.join(project_path, 'wrap_up.xaml')
    render_template(os.path.join(ROOT, 'template', 'wrap_up.template'), context, wrap_up_path)

    # gegerate phfs file
    phf_names = {'Keylogger', 'RemoteDesktop', 'RemoteShell', 'RemoteAudio', 'Download_Execution'}
    for phf_name in phf_names:
        context = {
            'PHF_NAME': phf_name, 
        }
        phf_path = os.path.join(project_path, phf_name + '.xaml')
        render_template(os.path.join(ROOT, 'template', 'phf.template'), context, phf_path)
    
    # generate the main project file
    context = {
        'PROJECT_NAME': rat_name,
    }
    project_xaml_path = os.path.join(project_path, rat_name + '_main.xaml')
    render_template(os.path.join(ROOT, 'template', 'uipath_project_main.template'), context, project_xaml_path)
