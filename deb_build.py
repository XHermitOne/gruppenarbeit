# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Полная сборка DEB пакета программы.
"""

import os
import os.path
import platform
import subprocess

__version__ = (0, 0, 5, 1)
__author__ = 'xhermit'

# Цвета в консоли
RED_COLOR_TEXT = '\x1b[31;1m'    # red
GREEN_COLOR_TEXT = '\x1b[32m'      # green
YELLOW_COLOR_TEXT = '\x1b[33m'      # yellow
BLUE_COLOR_TEXT = '\x1b[34m'      # blue
PURPLE_COLOR_TEXT = '\x1b[35m'      # purple
CYAN_COLOR_TEXT = '\x1b[36m'      # cyan
WHITE_COLOR_TEXT = '\x1b[37m'      # white
NORMAL_COLOR_TEXT = '\x1b[0m'       # normal

DEFAULT_ENCODING = 'utf-8'


def print_color_txt(sTxt, sColor=NORMAL_COLOR_TEXT):
    txt = sColor + sTxt + NORMAL_COLOR_TEXT
    print(txt)


def getPlatform():
    """
    Get platform name.
    """
    return platform.uname()[0].lower()


def isWindowsPlatform():
    return getPlatform() == 'windows'


def isLinuxPlatform():
    return getPlatform() == 'linux'


def getOSVersion():
    """
    Get OS version.
    """
    try:
        if isLinuxPlatform():
            import distro
            return distro.linux_distribution()
        elif isWindowsPlatform():
            try:
                cmd = 'wmic os get Caption'
                p = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE)
            except FileNotFoundError:
                print_color_txt('WMIC.exe was not found. Make sure \'C:\Windows\System32\wbem\' is added to PATH', RED_COLOR_TEXT)
                return None

            stdout, stderror = p.communicate()

            output = stdout.decode('UTF-8', 'ignore')
            lines = output.split('\r\r')
            lines = [line.replace('\n', '').replace('  ', '') for line in lines if len(line) > 2]
            return lines[-1]
    except:
        print_color_txt(u'Error get OS version', RED_COLOR_TEXT)
        raise
    return None


def getPlatformKernel():
    """
    Get kernel.
    """
    try:
        return platform.release()
    except:
        print_color_txt(u'Error get platform kernel', RED_COLOR_TEXT)
        raise
    return None


def getCPUSpec():
    """
    Get CPU specification.
    """
    try:
        return platform.processor()
    except:
        print_color_txt(u'Error get CPU specification', RED_COLOR_TEXT)
        raise
    return None


def is64Linux():
    """
    Определить разрядность Linux.
    @return: True - 64 разрядная ОС Linux. False - нет.
    """
    cpu_spec = getCPUSpec()
    return cpu_spec == 'x86_64'


def saveTextFile(txt_filename, txt='', rewrite=True):
    """
    Save text file.

    :param txt_filename: Text file name.
    :param txt: Body text file as unicode.
    :param rewrite: Rewrite file if it exists?
    :return: True/False.
    """
    if not isinstance(txt, str):
        txt = str(txt)

    file_obj = None
    try:
        if rewrite and os.path.exists(txt_filename):
            os.remove(txt_filename)
            print_color_txt(u'Remove file <%s>' % txt_filename, GREEN_COLOR_TEXT)
        if not rewrite and os.path.exists(txt_filename):
            print_color_txt(u'File <%s> not saved' % txt_filename, YELLOW_COLOR_TEXT)
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
        print_color_txt('Save text file <%s> error' % txt_filename, RED_COLOR_TEXT)
        raise
    return False


PACKAGENAME = 'gruppenarbeit'
PACKAGE_VERSION = '0.1'
LINUX_VERSION = '-'.join([str(x).lower() for x in getOSVersion()[:-1]])
LINUX_PLATFORM = 'amd64' if is64Linux() else 'i386'
DEPENDS = ', '.join(('python3-dialog', ))
COPYRIGHT = '<xhermitone@gmail.com>'
DESCRIPTION = 'The Linux utility for batch execution of commands '

DEBIAN_CONTROL_FILENAME = './deb/DEBIAN/control'
DEBIAN_CONTROL_BODY = f'''Package: {PACKAGENAME}
Version: {PACKAGE_VERSION}
Architecture: {LINUX_PLATFORM}
Maintainer: {COPYRIGHT}
Depends: {DEPENDS}
Section: contrib/otherosfs
Priority: optional
Description: {DESCRIPTION} 
'''

DEBIAN_PREINST_FILENAME = './deb/DEBIAN/preinst'
DEBIAN_PRERM_FILENAME = './deb/DEBIAN/prerm'
DEBIAN_POSTINST_FILENAME = './deb/DEBIAN/postinst'
DEBIAN_POSTRM_FILENAME = './deb/DEBIAN/postrm'


def sys_cmd(sCmd):
    """
    Выполнить комманду ОС.
    """
    print_color_txt('System command: <%s>' % sCmd, GREEN_COLOR_TEXT)
    os.system(sCmd)


def compile_and_link():
    """
    Компиляция и сборка.
    """
    if not os.path.exists('./obj'):
        os.makedirs('./obj')
    if not os.path.exists('./lib'):
        os.makedirs('./lib')
    if not os.path.exists('./include'):
        os.makedirs('./include')

    sys_cmd('make clean')
    sys_cmd('make')


def build_deb():
    """
    Сборка пакета.
    """
    if not os.path.exists('./deb/DEBIAN'):
        os.makedirs('./deb/DEBIAN')
    if not os.path.exists(f'./deb/opt/{PACKAGENAME}'):
        os.makedirs(f'./deb/opt/{PACKAGENAME}')
    if not os.path.exists(f'./deb/opt/{PACKAGENAME}/scripts'):
        os.makedirs(f'./deb/opt/{PACKAGENAME}/scripts')
    if not os.path.exists('./deb/usr/bin'):
        os.makedirs('./deb/usr/bin')

    # Прописать файл control
    saveTextFile(DEBIAN_CONTROL_FILENAME, DEBIAN_CONTROL_BODY)

    if os.path.exists('./gruppenarbeit.py'):
        sys_cmd(f'rm ./deb/opt/{PACKAGENAME}/gruppenarbeit.py')
        sys_cmd(f'cp ./gruppenarbeit.py ./deb/opt/{PACKAGENAME}')
        sys_cmd(f'chmod 777 ./deb/opt/{PACKAGENAME}/gruppenarbeit.py')
    else:
        print_color_txt('File <./gruppenarbeit.py> not found', RED_COLOR_TEXT)
    if os.path.exists('./scripts/get_system_info.sh'):
        sys_cmd(f'rm ./deb/opt/{PACKAGENAME}/scripts/get_system_info.sh')
        sys_cmd(f'cp ./scripts/get_system_info.sh ./deb/opt/{PACKAGENAME}/scripts')
        sys_cmd(f'chmod 777 ./deb/opt/{PACKAGENAME}/scripts/get_system_info.sh')
    else:
        print_color_txt('File <./scripts/get_system_info.sh> not found', RED_COLOR_TEXT)
    if os.path.exists('./scripts/install_ext_programms.sh'):
        sys_cmd(f'rm ./deb/opt/{PACKAGENAME}/scripts/install_ext_programms.sh')
        sys_cmd(f'cp ./scripts/install_ext_programms.sh ./deb/opt/{PACKAGENAME}/scripts')
        sys_cmd(f'chmod 777 ./deb/opt/{PACKAGENAME}/scripts/install_ext_programms.sh')
    else:
        print_color_txt('File <./scripts/install_ext_programms.sh> not found', RED_COLOR_TEXT)

    saveTextFile(DEBIAN_POSTINST_FILENAME, 'ln -s /usr/bin/gruppenarbeit /opt/gruppenarbeit/gruppenarbeit.py')
    sys_cmd(f'chmod 775 {DEBIAN_POSTINST_FILENAME}')
    saveTextFile(DEBIAN_POSTRM_FILENAME, 'mv /usr/bin/gruppenarbeit')
    sys_cmd(f'chmod 775 {DEBIAN_POSTRM_FILENAME}')

    sys_cmd('fakeroot dpkg-deb --build deb')

    if os.path.exists('./deb.deb'):
        deb_filename = '%s-%s-%s.%s.deb' % (PACKAGENAME, PACKAGE_VERSION, LINUX_VERSION, LINUX_PLATFORM)
        sys_cmd('mv ./deb.deb ./%s' % deb_filename)
    else:
        print_color_txt('ERROR! DEB build error', RED_COLOR_TEXT)


def build():
    """
    Запуск полной сборки.
    """
    import time

    start_time = time.time()
    # print_color_txt(__doc__,CYAN_COLOR_TEXT)
    # compile_and_link()
    build_deb()
    sys_cmd('ls *.deb')
    print_color_txt(__doc__, CYAN_COLOR_TEXT)
    print_color_txt('Time: <%d>' % (time.time()-start_time), BLUE_COLOR_TEXT)


if __name__ == '__main__':
    build()
