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

    # generate the project file
    collector_path = os.path.join(ROOT, 'apps', COLLECTOR, COLLECTOR_NAME)
    collector_work_directory = os.path.join(ROOT, 'apps', COLLECTOR)
    rat_path = os.path.join(ROOT, 'rats', rat_name_v, rat_name_exe)
    from_path = os.path.join(ROOT, 'apps', COLLECTOR, 'output.out')
    destination_path = os.path.join(ROOT, 'output', rat_name_v + '-phf_name.traces')
    context = {
        'PROJECT_NAME': rat_name,
        'PROJECT_NAME_1': ''.join([rat_name, '_1']),
        'ADDRESS_MAP_UPDATE_PATH': update_pid_path,
        'COLLECTOR_PATH': collector_path,
        'RAT_PATH': rat_path,
        'KILL_RAT_PATH': kill_processes_path,
        'COLLECTOR_WORK_DIRECTORY': collector_work_directory, 
        'FROM_PATH': from_path, 
        'DESTINATION_PATH': destination_path, 
    }
    project_xaml_path = os.path.join(project_path, rat_name + '.xaml')
    render_template(os.path.join(ROOT, 'template', 'uipath_project.template'), context, project_xaml_path)
