from django.views.generic import TemplateView
from app.models import Presets
import sys, os, time, re
from django.conf import settings
from app.models import bcolors
import inspect
import traceback
import logging


class ErrorR(TemplateView):
    # Regular Colors
    def c_red(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.Red + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_green(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.Green + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_yellow(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.Yellow + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_blue(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.Blue + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_purple(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.Purple + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_cyan(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.Cyan + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_white(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.White + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    # Bold
    def c_bred(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.BRed + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_bgreen(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.BGreen + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_byellow(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.BYellow + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_bblue(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.BBlue + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_bpurple(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.BPurple + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_bcyan(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.BCyan + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_bwhite(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.BWhite + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    # Underline
    def c_ured(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.URed + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_ugreen(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.UGreen + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_uyellow(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.UYellow + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_ublue(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.UBlue + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_upurple(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.UPurple + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_ucyan(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.UCyan + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_uwhite(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.UWhite + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    # Background
    def c_on_red(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.On_Red + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_on_green(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.On_Green + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_on_yellow(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.On_Yellow + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_on_blue(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.On_Blue + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_on_purple(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.On_Purple + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_on_cyan(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.On_Cyan + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_on_white(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.On_White + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    # High Intensty
    def c_ired(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.IRed + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_igreen(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.IGreen + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_iyellow(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.IYellow + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_iblue(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.IBlue + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_ipurple(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.IPurple + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_icyan(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.ICyan + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_iwhite(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.IWhite + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    # Bold High Intensty
    def c_bired(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.BIRed + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_bigreen(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.BIGreen + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_biyellow(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.BIYellow + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_biblue(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.BIBlue + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_bipurple(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.BIPurple + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_bicyan(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.BICyan + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_biwhite(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.BIWhite + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    # High Intensty backgrounds
    def c_on_ired(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.On_IRed + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_on_igreen(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.On_IGreen + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_on_iyellow(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.On_IYellow + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_on_iblue(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.On_IBlue + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_on_ipurple(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.On_IPurple + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_on_icyan(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.On_ICyan + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def c_on_iwhite(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.On_IWhite + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def okblue(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.OKBLUE + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def okgreen(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.OKGREEN + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def warn(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.WARNING + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def fail(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.FAIL + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("\r" + bcolors.IWhite + "[" + str(
                os.path.split(filename)[
                    1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                    line_number) + bcolors.ENDL + "]"))
            print()

    def efail(e):
        # if os.environ['ENVIRONMENT_TYPE'] == 'development' or os.environ['ENVIRONMENT_TYPE'] == 'develop':
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print("Error: " + bcolors.FAIL + str(
            exc_type) + bcolors.ENDL + ", File: " + bcolors.FAIL + fname + bcolors.ENDL + ", Line: " + bcolors.BIRed + str(
            exc_tb.tb_lineno) + " " + bcolors.ENDL)
        traceback.print_exc()
        print(bcolors.ENDL)
        (frame, filename, line_number,
         function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
        print("\r" + bcolors.IWhite + "[" + str(
            os.path.split(filename)[
                1] + ", " + bcolors.ICyan + function_name + "()" + bcolors.ENDL + ", Line:" + bcolors.BIGreen + str(
                line_number) + bcolors.ENDL + "]"))
        print()
        # else:
        #     print(" ADMIN ErrorR ")

    def error_fold(string, e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        string = exc_type, fname, exc_tb.tb_lineno
        string = string.replace('{error}', string)
        return string

    def ex_time_init(msg=""):
        if os.environ['ENVIRONMENT_TYPE'] == 'development' or os.environ['ENVIRONMENT_TYPE'] == 'develop':
            settings.EX_TIME = time.time()
            settings.EX_MSG = msg
            if msg != "":
                print("{} ==> {}".format(msg, str(time.time() - settings.EX_TIME)))

    def ex_time(*args, **kwargs):
        if os.environ['ENVIRONMENT_TYPE'] == 'development' or os.environ['ENVIRONMENT_TYPE'] == 'develop':
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print("{} ==> {}".format(settings.EX_MSG,
                                     bcolors.WARNING + str(time.time() - settings.EX_TIME) + "\t" + bcolors.ENDL +
                                     os.path.split(filename)[
                                         1] + " " + function_name + " " + str(line_number)))

    def ex_from(*args, **kwargs):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print(bcolors.FAIL)
            print(frame, filename, line_number, function_name, lines, index)
            print(bcolors.ENDL)

    def elog(e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logger = logging.getLogger(__name__)
        logger.debug("----------- Error: " + str(exc_obj) + ", File: " + fname + ", Line: " + str(
            exc_tb.tb_lineno) + " ------------")

    def ilog(value):
        (frame, filename, line_number,
         function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
        logger = logging.getLogger(__name__)
        logger.debug("----------- Info: " + str(value) + str(
            os.path.split(filename)[1] + ", " + function_name + "()" + ", Line:" + str(line_number) + "]"))


class DateTimeHelper(TemplateView):
    def get_formated_date_string(date_value, lang_id):
        try:
            date_format = Presets.objects.get(id=lang_id).datetime_format.replace('i', 'M')
            compiled_re = re.compile('[a-zA-Z]')
            matched_keys = compiled_re.findall(date_format)
            for key in matched_keys:
                date_format = date_format.replace(key, '%' + key)

            date_string = date_value.strftime(date_format)
        except Exception as excep:
            ErrorR.efail(excep)
            date_string = ''

        return date_string
