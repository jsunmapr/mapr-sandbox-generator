#All Rights Reserved MapR
import curses
import sh
import subprocess

screen = None
Width_Factor = 4
ip = 0

class NetworkMisconfiguredException(Exception):
    pass
class ServiceFailedtoStartException(Exception):
    pass


def make_welcome_window():
    Height, Width = screen.getmaxyx()
    welcome_win = screen.subwin(Width_Factor + 1 , Width, 0, 0)
    welcome_win.box()
    welcome_win.addstr(1,2,"=== MapR-Platfora-Sandbox-For-Hadoop ===", curses.A_BOLD)
    welcome_win.addstr(2,2,"Version: 4.0.2")

def make_status_window():
    Height, Width = screen.getmaxyx()
    status_win = screen.subwin(Height / 4 - Width_Factor / 2 , Width, Height / 4 , 0)
    status_win.box()
    try:
	ip = sh.head(sh.awk(sh.getent("ahosts", sh.hostname().strip()),"{print $1}"),n="1").strip()

        if ip == "127.0.0.1":
            raise NetworkMisconfiguredException()

    except sh.ErrorReturnCode:
        status_win.addstr(1,2,"MapR-Platfora-Sandbox-For-Hadoop setup did not succseed.")
   	raise ServiceFailedtoStartException()
	make_error_window()
    except NetworkMisconfiguredException:
	make_error_window()
    else:
 	status_win.addstr(1,2,"MapR Services failed to start.", curses.A_BOLD)
	make_error_window()

def make_error_window():
	Height, Width = screen.getmaxyx()
	error_win = screen.subwin(Height / 3, Width, Height / 2 - Width_Factor / 2, 0)
	error_win.box()

	if ServiceFailedtoStartException:
		error_win.addstr(1,2,"ERROR 3: Services did not start within 2 minutes.")
		error_win.addstr(3,2,"Visit: http://doc.mapr.com/display/MapR/MapR+Sandbox+for+Hadoop")
		error_win.addstr(4,2, "for instructions.")
	else:
		error_win.addstr(1,2,"ERROR 4: Check DHCP and connection of network interface.")
		error_win.addstr(3,2,"Visit: http://doc.mapr.com/display/MapR/MapR+Sandbox+for+Hadoop")
		error_win.addstr(4,2,"for instructions.")

def make_hint_window():
    Height, Width = screen.getmaxyx()
    hint_win = screen.subwin(Width_Factor , Width, Height - Width_Factor, 0)
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
