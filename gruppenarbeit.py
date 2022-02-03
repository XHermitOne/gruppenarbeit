#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Администрирование. Утилита запуска групповой обработки на различных компьютерах. 

Запуск:

        python3 gruppenarbeit.py [параметры коммандной строки]

Параметры коммандной строки:

    [Помощь и отладка]
        --help|-h|-?        Помощь
        --version|-v        Версия программы
        --debug|-d          Вкличить сообщения отладки
"""

import sys
import getopt
import os
import os.path
import stat
import glob
import operator

try:
    import rich.console
except:
    print(u'Ошибка. Не установлена библиотека rich')
    print(u'Для установки: pip3 install rich')
    sys.exit(2)

try:
    import dialog
except:
    print(u'Ошибка. Не установлена библиотека pythondialog')
    print(u'Для установки: sudo apt install python3-dialog')
    sys.exit(2)

__version__ = (0, 0, 0, 1)

DEBUG_MODE = False

CONSOLE = rich.console.Console()

HOME_PATH = os.environ['HOME'] if 'HOME' in os.environ else (os.environ.get('HOMEDRIVE',
                                                                            '') + os.environ.get('HOMEPATH', ''))
PROFILE_DIRNAME = '.gruppenarbeit'
PROFILE_PATH = os.path.join(HOME_PATH, PROFILE_DIRNAME)
HOSTS_FILENAME = 'hosts.csv'
CSV_DELIMETER = ';'
COMMENT_SIGNATURE = '#'
SCRIPT_DESCRIPTION_SIGNATURE = '#TITLE:'


def main(*argv):
    """
    Главная запускаемая функция.

    :param argv: Параметры коммандной строки.
    :return:
    """
    global DEBUG_MODE
    global CONSOLE

    try:
        options, args = getopt.getopt(argv, 'h?vd',
                                      ['help', 'version', 'debug'])
    except getopt.error as msg:
        CONSOLE.print(str(msg), style='bold red')
        CONSOLE.print(__doc__, style='bold cyan')
        sys.exit(2)

    for option, arg in options:
        if option in ('-h', '--help', '-?'):
            CONSOLE.print(__doc__, style='bold green')
            sys.exit(0)
        elif option in ('-v', '--version'):
            str_version = 'Версия: %s' % '.'.join([str(sign) for sign in __version__])
            CONSOLE.print(str_version, style='bold green')
            sys.exit(0)
        elif option in ('-d', '--debug'):
            DEBUG_MODE = True
            CONSOLE.print(u'Включен режим отладки', style='green')
        else:
            if DEBUG_MODE:
                msg = u'Не поддерживаемый параметр командной строки <%s>' % option
                CONSOLE.print(msg, style='red')

    try:
        run()
    except:
        if DEBUG_MODE:
            CONSOLE.print(u'Ошибка выполнения:', style='bold red')
            CONSOLE.print_exception(max_frames=20)


def saveTextFile(txt_filename, txt='', rewrite=True):
    """
    Save text file.

    :param txt_filename: Text file name.
    :param txt: Body text file as unicode.
    :param rewrite: Rewrite file if it exists?
    :return: True/False.
    """
    global CONSOLE
    global DEBUG_MODE

    if not isinstance(txt, str):
        txt = str(txt)

    file_obj = None
    try:
        if rewrite and os.path.exists(txt_filename):
            os.remove(txt_filename)
            if DEBUG_MODE:
                CONSOLE.print(u'Remove file <%s>' % txt_filename, style='green')
        if not rewrite and os.path.exists(txt_filename):
            if DEBUG_MODE:
                CONSOLE.print(u'File <%s> not saved' % txt_filename, style='yellow')
            return False

        # Check path
        txt_dirname = os.path.dirname(txt_filename)
        if not os.path.exists(txt_dirname):
            os.makedirs(txt_dirname)

        file_obj = open(txt_filename, 'wt')
        file_obj.write(txt)
        file_obj.close()
        return True
    except:
        if file_obj:
            file_obj.close()
        if DEBUG_MODE:
            CONSOLE.print('Save text file <%s> error' % txt_filename, style='red')
            CONSOLE.print_exception(max_frames=20)
    return False


def loadTextFile(txt_filename):
    """
    Load from text file.

    :param txt_filename: Text file name.
    :return: File text or empty text if error.
    """
    global CONSOLE
    global DEBUG_MODE

    if not os.path.exists(txt_filename):
        if DEBUG_MODE:
            CONSOLE.print(u'File <%s> not found' % txt_filename, style='yellow')
        return ''

    file_obj = None
    try:
        file_obj = open(txt_filename, 'rt')
        txt = file_obj.read()
        file_obj.close()
    except:
        if file_obj:
            file_obj.close()
        if DEBUG_MODE:
            CONSOLE.print(u'Load text file <%s> error' % txt_filename, style='red')
            CONSOLE.print_exception(max_frames=20)
        return ''

    return txt


def createHostsFilename(hosts_filename):
    """
    Создать файл описания хостов групповой обработки.

    :param hosts_filename: Имя создаваемого файла хостов групповой обработки.
    :return: True/False.
    """
    content = u''
    columns = u'GROUPNAME;HOSTNAME;HOST;USERNAME;PASSWORD;STATE' + os.linesep
    content += columns
    localhost = u'Локальный компьютер;Локальный компьютер;localhost;;;False'
    content += localhost
    return saveTextFile(hosts_filename, content)


def getHostsFilename():
    """
    Получить имя файла описания хостов для групповой обаботки.

    :return:
    """
    global PROFILE_PATH
    hosts_filename = os.path.join(PROFILE_PATH, HOSTS_FILENAME)
    if not os.path.exists(hosts_filename):
        createHostsFilename(hosts_filename)
    return hosts_filename


def getHosts():
    """
    Получить список описаний хостов для обработки.

    :return:
    """
    hosts_filename = getHostsFilename()
    content = loadTextFile(hosts_filename)
    lines = [line.strip().split(CSV_DELIMETER) for line in content.split(os.linesep) if line.strip() and not line.startswith(COMMENT_SIGNATURE)]
    if lines:
        columns = lines[0]
        hosts = [dict([(column, line[i]) for i, column in enumerate(columns)]) for line in lines[1:]]
        # Сортировка хостов по группам
        hosts = sorted(hosts, key=operator.itemgetter('GROUPNAME', 'HOSTNAME'))
        return hosts
    return list()


def run():
    """
    Запуск выполнения программы.

    :return:
    """
    global CONSOLE
    global DEBUG_MODE

    hosts = getHosts()
    if not hosts:
        if DEBUG_MODE:
            CONSOLE.print(u'Не определен список хостов групповой обработки', style='yellow')

    if hosts:
        dlg = dialog.Dialog(dialog='dialog')
        title = u'Компьютеры групповой обработки:'
        dlg.set_background_title(title)

        while True:
            choices = [(host['HOST'],
                        u'%s. %s' % (host['GROUPNAME'], host['HOSTNAME']),
                        eval(host.get('STATE', 'False')),
                        u'%s. %s' % (host['GROUPNAME'], host['HOSTNAME'])) for host in hosts]

            code, tags = dlg.checklist(text=u'Выберите компьютеры для групповой обработки:',
                                       choices=choices,
                                       title=u'Компьютеры',
                                       height=30,
                                       width=120,
                                       list_height=24,
                                       help_button=True, item_help=True,
                                       help_tags=True, help_status=True)

            if code == dlg.OK:
                os.system('clear')
                selected_hosts = [host for host in hosts if host['HOST'] in tags]
                selectScript(selected_hosts)
                break
            elif code == dlg.CANCEL:
                os.system('clear')
                break
            elif code == dlg.HELP:
                description = [tag[3] for tag in tags[2] if tag[0] == tags[0]][0]
                dlg.msgbox(text=description,
                           title=u'Описание <%s>' % tags[0],
                           height=15,
                           width=120)

        return True
    return False


def getScriptTitle(script_filename):
    """
    Определить заголовок скрипта.

    :param script_filename: Файл скрипта.
    :return: Заголовок или пустая строка в случае ошибки.
    """
    if os.path.exists(script_filename):
        content = loadTextFile(script_filename)
        lines = [line for line in content.split(os.linesep) if line.startswith(SCRIPT_DESCRIPTION_SIGNATURE)]
        return lines[0].replace(SCRIPT_DESCRIPTION_SIGNATURE, u'').strip() if lines else u''
    return u''


def getScripts(scripts_path=None):
    """
    Получить скрипты по умолчанию.

    :return:
    """
    if scripts_path is None:
        prg_dirname = os.path.dirname(__file__)
        scripts_path = os.path.join(prg_dirname, 'scripts')

    scripts = list()
    if os.path.exists(scripts_path):
        sh_filename_mask = os.path.join(scripts_path, '*.sh')
        script_filenames = glob.glob(pathname=sh_filename_mask, recursive=False)
        scripts = [dict(name=os.path.splitext(os.path.basename(script_filename))[0],
                        filename=script_filename,
                        description=getScriptTitle(script_filename)) for script_filename in script_filenames]
    return scripts


def selectScript(selected_hosts):
    """
    Выбрать скрипт для групповой обработки.

    :return:
    """
    default_scripts = getScripts()
    user_scripts = getScripts(PROFILE_PATH)
    scripts = default_scripts + user_scripts

    if scripts:
        dlg = dialog.Dialog(dialog='dialog')
        title = u'Скрипты групповой обработки:'
        dlg.set_background_title(title)

        while True:
            choices = [(script['name'],
                        script['description']) for script in scripts]

            code, tag = dlg.menu(text=u'Выберите скрипт для групповой обработки:',
                                 choices=choices,
                                 title=u'Скрипты',
                                 height=30,
                                 width=120,
                                 help_button=False, item_help=False,
                                 help_tags=False, help_status=False)

            if code == dlg.OK:
                os.system('clear')
                selected_script = [script for script in scripts if script['name'] == tag][0]
                runScript(selected_script, selected_hosts)
                break
            elif code == dlg.CANCEL:
                os.system('clear')
                break
        return True
    return False


def runScript(script, hosts):
    """
    Запуск скрипта на хостах.

    :param script:
    :param hosts:
    :return:
    """
    global CONSOLE
    # global DEBUG_MODE
    CONSOLE.print(script.get('description', u''), style='bold green')

    script_filename = script.get('filename', None)
    if script_filename:
        try:
            os.chmod(script_filename, os.stat(script_filename).st_mode | stat.S_IEXEC)
        except:
            pass

        for host in hosts:
            cmd = f'''{script_filename} "{host['HOST']}" "{host['USERNAME']}" "{host['PASSWORD']}" "{host['HOSTNAME']}" "{host['GROUPNAME']}"'''
            # if DEBUG_MODE:
            #     CONSOLE.print(u'Выполнение команды <%s>' % cmd, style='green')
            os.system(cmd)


if __name__ == '__main__':
    main(*sys.argv[1:])
