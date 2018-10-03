import sys


class Colors:
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    OKBLUE = '\033[94m'
    END = '\033[0m'

class ColorPrint:

    log_lvl = 0

    @staticmethod
    def print_error(message):
        print(Colors.FAIL + "\n" + message + "\n" + Colors.END)

    @staticmethod
    def print_warning(message, lvl=0):
        ColorPrint.print_with_lvl(message=message, lvl=lvl, color=Colors.WARNING)

    @staticmethod
    def print_info(message, lvl=0):
        ColorPrint.print_with_lvl(message=message, lvl=lvl, color=Colors.OKBLUE)

    @staticmethod
    def print_with_lvl(message, lvl=0, color=None):
        if ColorPrint.log_lvl >= lvl:
            if color is not None:
                print(color + "\n" + message + "\n" + Colors.END)
            else:
                print(message)

    @staticmethod
    def exit_after_print_messages(message, doc=None, msg_type="error"):
        if "error" is msg_type:
            ColorPrint.print_error(message)
        elif "warn" is msg_type:
            ColorPrint.print_warning(message)
        elif "info" is msg_type:
            ColorPrint.print_info(message)
        else:
            print(message)
        if doc is not None and ColorPrint.log_lvl > -1:
            print(doc)
        sys.exit(1)

    @staticmethod
    def set_log_level(arguments):
        if arguments.get("--verbose"):
            ColorPrint.log_lvl += 1
        if arguments.get("--quiet"):
            ColorPrint.log_lvl -= 1
