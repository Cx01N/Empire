import os
import shutil
import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

TEST_CONFIG_DIR = "empire/test/test_config.yaml"
DEFAULT_ARGV = ["", "server", "--config", "empire/test/test_config.yaml"]


@pytest.fixture(scope="session", autouse=True)
def setup_args():
    os.chdir(Path(os.path.dirname(os.path.abspath(__file__))).parent.parent)
    sys.argv = DEFAULT_ARGV


@pytest.fixture(scope="session")
def default_argv():
    return DEFAULT_ARGV


@pytest.fixture(scope="session")
def client():
    os.chdir(Path(os.path.dirname(os.path.abspath(__file__))).parent.parent)
    shutil.rmtree("empire/test/downloads", ignore_errors=True)

    sys.argv = ["", "server", "--config", TEST_CONFIG_DIR]

    from empire import arguments

    args = arguments.parent_parser.parse_args()

    import empire.server.server
    from empire.server.common.empire import MainMenu

    # todo vr could this weirdness be avoided if we make main menu an injected dependency for fastapi?
    empire.server.server.main = MainMenu(args)

    from empire.server.v2.api.agent import agentfilev2, agentv2, taskv2
    from empire.server.v2.api.bypass import bypassv2
    from empire.server.v2.api.credential import credentialv2
    from empire.server.v2.api.download import downloadv2
    from empire.server.v2.api.host import hostv2, processv2
    from empire.server.v2.api.keyword import keywordv2
    from empire.server.v2.api.listener import listenertemplatev2, listenerv2
    from empire.server.v2.api.meta import metav2
    from empire.server.v2.api.module import modulev2
    from empire.server.v2.api.profile import profilev2
    from empire.server.v2.api.stager import stagertemplatev2, stagerv2
    from empire.server.v2.api.user import userv2

    v2App = FastAPI()
    v2App.include_router(listenertemplatev2.router)
    v2App.include_router(listenerv2.router)
    v2App.include_router(stagertemplatev2.router)
    v2App.include_router(stagerv2.router)
    v2App.include_router(taskv2.router)
    v2App.include_router(agentfilev2.router)
    v2App.include_router(agentv2.router)
    v2App.include_router(modulev2.router)
    v2App.include_router(bypassv2.router)
    v2App.include_router(keywordv2.router)
    v2App.include_router(profilev2.router)
    v2App.include_router(credentialv2.router)
    v2App.include_router(hostv2.router)
    v2App.include_router(userv2.router)
    v2App.include_router(processv2.router)
    v2App.include_router(downloadv2.router)
    v2App.include_router(metav2.router)

    yield TestClient(v2App)

    print("cleanup")

    from empire.server.database.base import engine
    from empire.server.database.models import Base
    from empire.server.server import main

    main.shutdown()
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def empire_config():
    from empire.server.common.config import empire_config

    return empire_config


@pytest.fixture(scope="session")
def admin_auth_token(client):
    response = client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "password",
            "username": "empireadmin",
            "password": "password123",
        },
    )

    yield response.json()["access_token"]


@pytest.fixture(scope="session")
def admin_auth_header(admin_auth_token):
    return {"Authorization": f"Bearer {admin_auth_token}"}


@pytest.fixture(scope="session")
def regular_auth_token(client, admin_auth_token):
    client.post(
        "/api/v2beta/users/",
        headers={"Authorization": f"Bearer {admin_auth_token}"},
        json={"username": "vinnybod", "password": "hunter2", "is_admin": False},
    )

    response = client.post(
        "/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"grant_type": "password", "username": "vinnybod", "password": "hunter2"},
    )

    yield response.json()["access_token"]


@pytest.fixture(scope="session")
def db():
    from empire.server.database.base import SessionLocal

    yield SessionLocal()


@pytest.fixture(scope="function")
def base_listener():
    return {
        "name": "new-listener-1",
        "template": "http",
        "options": {
            "Name": "new-listener-1",
            "Host": "http://localhost:1336",
            "BindIP": "0.0.0.0",
            "Port": "1336",
            "Launcher": "powershell -noP -sta -w 1 -enc ",
            "StagingKey": "2c103f2c4ed1e59c0b4e2e01821770fa",
            "DefaultDelay": "5",
            "DefaultJitter": "0.0",
            "DefaultLostLimit": "60",
            "DefaultProfile": "/admin/get.php,/news.php,/login/process.php|Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "CertPath": "",
            "KillDate": "",
            "WorkingHours": "",
            "Headers": "Server:Microsoft-IIS/7.5",
            "Cookie": "",
            "StagerURI": "",
            "UserAgent": "default",
            "Proxy": "default",
            "ProxyCreds": "default",
            "SlackURL": "",
        },
    }


def base_listener_non_fixture():
    return {
        "name": "new-listener-1",
        "template": "http",
        "options": {
            "Name": "new-listener-1",
            "Host": "http://localhost:1336",
            "BindIP": "0.0.0.0",
            "Port": "1336",
            "Launcher": "powershell -noP -sta -w 1 -enc ",
            "StagingKey": "2c103f2c4ed1e59c0b4e2e01821770fa",
            "DefaultDelay": "5",
            "DefaultJitter": "0.0",
            "DefaultLostLimit": "60",
            "DefaultProfile": "/admin/get.php,/news.php,/login/process.php|Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "CertPath": "",
            "KillDate": "",
            "WorkingHours": "",
            "Headers": "Server:Microsoft-IIS/7.5",
            "Cookie": "",
            "StagerURI": "",
            "UserAgent": "default",
            "Proxy": "default",
            "ProxyCreds": "default",
            "SlackURL": "",
        },
    }


@pytest.fixture(scope="function")
def base_stager():
    return {
        "name": "MyStager",
        "template": "multi_launcher",
        "options": {
            "Listener": "new-listener-1",
            "Language": "powershell",
            "StagerRetries": "0",
            "OutFile": "",
            "Base64": "True",
            "Obfuscate": "False",
            "ObfuscateCommand": "Token\\All\\1",
            "SafeChecks": "True",
            "UserAgent": "default",
            "Proxy": "default",
            "ProxyCreds": "default",
            "Bypasses": "mattifestation etw",
        },
    }


@pytest.fixture(scope="function")
def base_stager_2():
    return {
        "name": "MyStager2",
        "template": "windows_dll",
        "options": {
            "Listener": "new-listener-1",
            "Language": "powershell",
            "StagerRetries": "0",
            "Arch": "x86",
            "OutFile": "my-windows-dll.dll",
            "Base64": "True",
            "Obfuscate": "False",
            "ObfuscateCommand": "Token\\All\\1",
            "SafeChecks": "True",
            "UserAgent": "default",
            "Proxy": "default",
            "ProxyCreds": "default",
            "Bypasses": "mattifestation etw",
        },
    }
