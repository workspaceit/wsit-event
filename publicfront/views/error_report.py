from django.views.generic import TemplateView
import sys, os

from app.models import bcolors


class ErrorR(TemplateView):
    def okblue(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.OKBLUE + str(string) + bcolors.ENDL)
        else:
            print(string)

    def okgreen(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.OKGREEN + str(string) + bcolors.ENDL)
        else:
            print(string)

    def warn(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.WARNING + str(string) + bcolors.ENDL)

        else:
            print(string)

    def fail(string):
        if os.environ['ENVIRONMENT_TYPE'] == 'development':
            print(bcolors.FAIL + str(string) + bcolors.ENDL)
        else:
            print(string)

    def efail(e):
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        string = exc_type, fname, exc_tb.tb_lineno
        if os.environ['ENVIRONMENT_TYPE'] == 'development' or os.environ['ENVIRONMENT_TYPE'] == 'develop':
            print(bcolors.FAIL + str(string) + " " + bcolors.ENDL)
            import traceback
            traceback.print_exc()
        else:
            print(" Public ErrorR " )
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
