from django.views.generic import TemplateView
import sys, os, time
from django.conf import settings
from app.models import bcolors
import inspect


class ErrorR(TemplateView):
    def c_cyan(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.Cyan + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print(bcolors.UNDERLINE)
            print(str(os.path.split(filename)[1] + " " + function_name + " " + str(line_number)))
            print(bcolors.ENDL)

    def c_purple(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.Purple + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print(bcolors.UNDERLINE)
            print(str(os.path.split(filename)[1] + " " + function_name + " " + str(line_number)))
            print(bcolors.ENDL)

    def c_green(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.Green + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print(bcolors.UNDERLINE)
            print(str(os.path.split(filename)[1] + " " + function_name + " " + str(line_number)))
            print(bcolors.ENDL)

    def okblue(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.OKBLUE + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print(bcolors.UNDERLINE)
            print(str(os.path.split(filename)[1] + " " + function_name + " " + str(line_number)))
            print(bcolors.ENDL)
            # else:
            #     print(string)

    def okgreen(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.OKGREEN + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print(bcolors.UNDERLINE)
            print(str(os.path.split(filename)[1] + " " + function_name + " " + str(line_number)))
            print(bcolors.ENDL)
            # else:
            #     print(string)

    def warn(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.WARNING + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print(bcolors.UNDERLINE)
            print(str(os.path.split(filename)[1] + " " + function_name + " " + str(line_number)))
            print(bcolors.ENDL)
            # else:
            #     print(string)

    def fail(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.FAIL + str(string) + bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print(bcolors.UNDERLINE)
            print(str(os.path.split(filename)[1] + " " + function_name + " " + str(line_number)))
            print(bcolors.ENDL)
            # else:
            #     print(string)

    def efail(e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        string = exc_type, fname, exc_tb.tb_lineno
        if os.environ['ENVIRONMENT_TYPE'] == 'development' or os.environ['ENVIRONMENT_TYPE'] == 'develop':
            print(bcolors.FAIL + str(string) + " " + bcolors.ENDL)
            import traceback
            print(bcolors.UNDERLINE)
            traceback.print_exc()
            print(bcolors.ENDL)
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print(bcolors.UNDERLINE)
            print(str(os.path.split(filename)[1] + " " + function_name + " " + str(line_number)))
            print(bcolors.ENDL)
        else:
            print(" ADMIN ErrorR ")
            # print(exc_type, fname, exc_tb.tb_lineno)
            # print(bcolors.FAIL + str(string) + " " + bcolors.ENDL)
            # import traceback
            # traceback.print_exc()

    def error_fold(string, e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        string = exc_type, fname, exc_tb.tb_lineno
        string = string.replace('{error}', string)
        return string

    def ex_time_init(*args, **kwargs):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            settings.EX_TIME = time.time()

    def ex_time(*args, **kwargs):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print(bcolors.WARNING)
            print(str(time.time() - settings.EX_TIME))
            print(bcolors.UNDERLINE)
            print(os.path.split(filename)[1] + " " + function_name + " " + str(line_number))
            print(bcolors.ENDL)

    def ex_from(*args, **kwargs):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            (frame, filename, line_number,
             function_name, lines, index) = inspect.getouterframes(inspect.currentframe())[1]
            print(bcolors.FAIL)
            print(frame, filename, line_number, function_name, lines, index)
            print(bcolors.ENDL)
