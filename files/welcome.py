#All Rights Reserved MapR
import curses
import sh
import subprocess
import os

screen = None
Width_Factor = 4
ip = sh.head(sh.awk(sh.getent("ahosts", sh.hostname().strip()),"{print $1}"),n="1").strip()

if not os.path.exists("/vmware"):
	ip = "127.0.0.1"

ssh_cmd = ""
if ip == "127.0.0.1":
	ssh_cmd = "ssh mapr@localhost -p 2222"
else:
	ssh_cmd = "ssh mapr@%s" % (ip)
	

class NetworkMisconfiguredException(Exception):
    pass
class ServiceFailedtoStartException(Exception):
    pass
	

def make_welcome_window():
    Height, Width = screen.getmaxyx()
    welcome_win = screen.subwin(Height / 2 - Width_Factor - 2, Width, 0, 0)
    welcome_win.box()
    welcome_win.addstr(1,2,"=== MapR-Platfora-Sandbox-For-Hadoop ===", curses.A_BOLD)
    welcome_win.addstr(3,2,"Version: 4.0.2")

def make_status_window():
    Height, Width = screen.getmaxyx()
    status_win = screen.subwin(Height / 2 - Width_Factor / 2, Width, Height / 2 - Width_Factor, 0)
    status_win.box()
    status_win.addstr(1,2,"MapR-Platfora-Sandbox-For-Hadoop installation finished successfully.", curses.A_BOLD)
    status_win.addstr(2,2,"Please go to http://%s:8443/ to begin your experience." % ip) #Fixme: Is there a way to detect, how networking is setup on a VM, nat, bridged etc?
    status_win.addstr(4,2,"Open a browser on your host machine ")
    status_win.addstr(5,2,"and enter the URL in the browser's address field.")
    status_win.addstr(7,2,"You can access the host via SSH by %s" % (ssh_cmd))

    if os.path.exists("/opt/mapr/hue"):
	status_win.addstr(8,2,"The following credentials should be used for MCS & HUE - mapr/mapr")
	
def make_hint_window():
    Height, Width = screen.getmaxyx()
    hint_win = screen.subwin(Width_Factor, Width, Height - Width_Factor, 0)
    hint_win.box()
    hint_win.addstr(1,1,"Log in to this virtual machine: Linux/Windows <Alt+F2>, Mac OS X <Option+F5>")

def init_screen():
    curses.noecho()

    make_welcome_window()
    make_status_window()
    make_hint_window()

def show_netinfo():
    commands = [
        "route -n",
        "getent ahosts",
        "ip addr",
        "cat /etc/resolv.conf",
        "cat /etc/hosts",
        ]

    f = file("/tmp/netinfo", "w")
    for cmd in commands:
        f.write("====  %s ==== \n" % cmd)
        f.write(subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()[0])
        f.write("\n")
    f.close()
    subprocess.call("less /tmp/netinfo", shell=True)


def main():
    global screen
    screen = curses.initscr()
    init_screen()

    screen.refresh()

    curses.curs_set(0)

    import sys
    if len(sys.argv)>1 and sys.argv[1] == "-s":
        screen.getch()
    else:
        while True:
            try:
                c = screen.getch()
                if c == ord('n'):
                    curses.endwin()
                    show_netinfo()
                    screen = curses.initscr()
                    init_screen()
                screen.refresh()
            except KeyboardInterrupt, e:
                pass

    curses.endwin()


if __name__ == '__main__':
    main()
