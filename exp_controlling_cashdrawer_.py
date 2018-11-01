#!/usr/bin/python
# ===========================================================
#  Example for controlling Cash Drawer with Python
# ===========================================================


# -----------------------------------------------------------
#  Define
# -----------------------------------------------------------
import os, sys, commands, time, getopt

TOOL = 'devmem2'
ADR_KK1 =     '0xFED81674' #GPIO45, out, CDW1_KICK
ADR_KK2 =     '0xFED81608' #GPIO51, out, CDW2_KICK
ADR_STAT =    '0xFED81618' #GPIO59, in, CDW_IN, drawer status
ADR_CNT1 =    '0xFED81620' #GPIO68, in, CDW1_STS, line1 connect
ADR_CNT2 =    '0xFED81614' #GPIO58, in, CDW2_STS, line2 connect
ADR_FN_KK1 =  '0xFED80D5D' #config reg of ADR_KK1
ADR_FN_KK2 =  '0xFED80D42' #config reg of ADR_KK2
ADR_FN_STAT	= '0xFED80D47' #config reg of CDW_IN
ADR_FN_CNT1	= '0xFED80D45' #config reg of CDW1_STS
ADR_FN_CNT2	= '0xFED80D48' #config reg of CDW2_STS
FN_KK1_GPIO =  '0x2'
FN_KK2_GPIO =  '0x2'
FN_STAT_GPIO = '0x2'
FN_CNT1_GPIO = '0x0'
FN_CNT2_GPIO = '0x1'

FN_OUT  = '0x00800000'
FN_IN   = '0xFF7FFFFF'
IO_OUT_H = '0x00400000'
IO_OUT_L = '0xFFBFFFFF'

OPT_ACT = "NONE"
OPT_ARG = "NONE"

# -----------------------------------------------------------
#  Options
# -----------------------------------------------------------
def usage(name):
	print "Usage: " + name + " [OPTION]... [FILE]...\n" \
				" -c, --connected Show port connected status.\n" \
				" -h, --help      Display this pages.\n" \
				" -o, --open      Open the drawer of the number.\n" \
				" -s, --status    Verify the drawer status (close/open).\n" \
				"\n"\
				"Example:\n"\
				" sudo " + name + " -o 1\n"\
				" sudo " + name + " --status\n"\
				"\n"\
				"  Bug report: https://github.com/ZivChien/...."
	sys.exit(1)

def get_argv():
	if len(sys.argv) < 2:
		usage(sys.argv[0].split("/")[1])
	elif len(sys.argv) > 3:
		usage(sys.argv[0].split("/")[1])

	try:
		opts,args = getopt.getopt(sys.argv[1:], \
				"c:ho:s", ["connected=", "help", "open=", "status"])
		for o,v in opts:
			if o in ("-c", "--connected"):
				act = "CONNECTED"
				arg = v
			elif o in ("-h", "--help"):
				usage(sys.argv[0].split("/")[1])
			elif o in ("-o", "--open"):
				act = "OPEN"
				arg = v
			elif o in ("-s", "--status"):
				act = "STATUS"
				arg = "NONE"
	except getopt.GetoptError:
		usage(sys.argv[0].split("/")[1])
	return act,arg

def env_check():
	# -- tool exist or not?
	cmd = "which " + TOOL
	sret,sout = commands.getstatusoutput(cmd)
	if sret == 0:
		return

	print("[WNG] The necessary tool not found!")
	# -- Ubuntu and apt-get ?
	cmd = "cat /etc/*-release"
	sret,sout = commands.getstatusoutput(cmd)
	if sret != 0:
		print("[ERR] Only support Ubuntu Linux, ESCAPE the installation.")
		quit()
	
	if sout.split('\n')[0].split('=')[1] != "Ubuntu":
		print("[ERR] Only support Ubuntu Linux, ESCAPE the installation.")
		quit()

	# -- install thru apt-get command
	print("[INF] Start to install necessary tool. Please provide the root right as below prompt.")
	cmd = "sudo apt-get install -ys " + TOOL
	sret,sout = commands.getstatusoutput(cmd)

	# -- confirm again
	cmd = "which " + TOOL
	sret,sout = commands.getstatusoutput(cmd)
	if sret != 0:
		print("[ERR] Install failure!")
		quit()
	print("[INF] Install success!")


# -----------------------------------------------------------
#  IO access
# -----------------------------------------------------------
def read_io(addr):
	cmd = "sudo " + TOOL + " " + addr
	sret,sout = commands.getstatusoutput(cmd)
	ofs = sout.split("\n")[2].split(" ")[3]
	val = sout.split("\n")[2].split(" ")[5]

	if addr != ofs:
		return None
	else:
		return val


def write_io(addr, value):
	cmd = "sudo " + TOOL + " " + addr + " w " + value
	sret,sout = commands.getstatusoutput(cmd)
	ofs = sout.split("\n")[2].split(" ")[3]
	w = sout.split("\n")[3].split(" ")[1].split(";")[0]
	r = sout.split("\n")[3].split(" ")[3]

	if addr != ofs:
		return None

	if w != r:
		return None
	else:
		return 0
	

def list_regs():
	print "list_regs() ====="
	print "ADR_KK1:", ADR_KK1, read_io(ADR_KK1)
	print "ADR_KK2:", ADR_KK2, read_io(ADR_KK2)
	print "ADR_CNT1:", ADR_CNT1, read_io(ADR_CNT1)
	print "ADR_CNT2:", ADR_CNT2, read_io(ADR_CNT2)
	print "ADR_STAT:", ADR_STAT, read_io(ADR_STAT)
	print "ADR_FN_KK1:", ADR_FN_KK1, read_io(ADR_FN_KK1)
	print "ADR_FN_KK2:", ADR_FN_KK2, read_io(ADR_FN_KK2)


# -----------------------------------------------------------
#  IO init
# -----------------------------------------------------------
def conf_cd1_kick():
	# -- set pin function as GPIO
	value = read_io(ADR_FN_KK1)
	value = hex(int(value, 16) & int('0xFFFFFFFC',16))
	value = hex(int(value, 16) | int(FN_KK1_GPIO,16))
	write_io(ADR_FN_KK1, value)

	# -- set pin direction as OUTPUT
	value = read_io(ADR_KK1)
	value = hex(int(value, 16) | int(FN_OUT,16))
	write_io(ADR_KK1, value)


def conf_cd2_kick():
	# -- set pin function as GPIO
	value = read_io(ADR_FN_KK2)
	value = hex(int(value, 16) & int('0xFFFFFFFC',16))
	value = hex(int(value, 16) | int(FN_KK2_GPIO,16))
	write_io(ADR_FN_KK2, value)

	# -- set pin direction as OUTPUT
	value = read_io(ADR_KK2)
	value = hex(int(value, 16) | int(FN_OUT, 16))
	write_io(ADR_KK2, value)


def conf_cd1_stat():
	value = read_io(ADR_FN_CNT1)
	value = hex(int(value, 16) & int('0xFFFFFFFC',16))
	value = hex(int(value, 16) | int(FN_CNT1_GPIO,16))
	write_io(ADR_FN_CNT1, value)

	value = read_io(ADR_CNT1)
	value = hex(int(value, 16) | int(FN_IN, 16))
	write_io(ADR_CNT1, value)


def conf_cd2_stat():
	value = read_io(ADR_FN_CNT2)
	value = hex(int(value, 16) & int('0xFFFFFFFC',16))
	value = hex(int(value, 16) | int(FN_CNT2_GPIO,16))
	write_io(ADR_FN_CNT2, value)

	value = read_io(ADR_CNT2)
	value = hex(int(value, 16) | int(FN_IN, 16))
	write_io(ADR_CNT2, value)


def conf_cdw_port():
	value = read_io(ADR_FN_STAT)
	value = hex(int(value, 16) & int('0xFFFFFFFC',16))
	value = hex(int(value, 16) | int(FN_STAT_GPIO,16))
	write_io(ADR_FN_STAT, value)

	value = read_io(ADR_STAT)
	value = hex(int(value, 16) | int(FN_IN, 16))
	write_io(ADR_STAT, value)


# -- conf 5 gpio
def conf():
	conf_cd1_kick()
	conf_cd2_kick()
	conf_cd1_stat()
	conf_cd2_stat()
	conf_cdw_port()

# -----------------------------------------------------------
#  Drawer actions
# -----------------------------------------------------------
def do_drawer1_open():
	value = read_io(ADR_KK1)
	value = hex(int(value, 16) & int(IO_OUT_L,16))
	write_io(ADR_KK1, value)
	time.sleep (0.150)
	value = read_io(ADR_KK1)
	value = hex(int(value, 16) | int(IO_OUT_H,16))
	write_io(ADR_KK1, value)


def do_drawer2_open():
	value = read_io(ADR_KK2)
	value = hex(int(value, 16) & int(IO_OUT_L,16))
	write_io(ADR_KK2, value)
	time.sleep (0.150)
	value = read_io(ADR_KK2)
	value = hex(int(value, 16) | int(IO_OUT_H,16))
	write_io(ADR_KK2, value)


def is_drawer1_connected():
	value = read_io(ADR_CNT1)
	value = (int(v,16) >> 16) & 1
	if value == 1:
		print "Drawer 1 is connected."
	else:
		print "Drawer 1 disconnected."


def is_drawer2_connected():
	value = read_io(ADR_CNT2)
	value = (int(v,16) >> 16) & 1
	if value == 1:
		print "Drawer 2 is connected."
	else:
		print "Drawer 2 disconnected."


def is_drawer_opened():
	value = read_io(ADR_STAT)
	value = (int(value,16) >> 16) & 1
	if value == 1:
		print "Drawer is closed."
	else:
		print "Drawer is opened."


def do_action():
	if OPT_ACT == "OPEN":
		if OPT_ARG == "1":
			do_drawer1_open()
		else:
			do_drawer2_open()	
	elif OPT_ACT == "CONNECTED":
		if OPT_ARG == "1":
			is_drawer1_connected()
		else: 
			is_drawer2_connected()
	elif OPT_ACT == "STATUS":
		is_drawer_opened()


# -----------------------------------------------------------
#  main
# -----------------------------------------------------------
OPT_ACT,OPT_ARG = get_argv()

env_check()
#list_regs()
conf()

print "action: " + OPT_ACT + "\targument: " + OPT_ARG
do_action()

