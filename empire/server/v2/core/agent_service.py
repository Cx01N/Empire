from sqlalchemy.orm import Session

from empire.server.database import models
from empire.server.v2.core.agent_task_service import AgentTaskService


class AgentService(object):

    def __init__(self, main_menu):
        self.main_menu = main_menu

        self.agent_task_service: AgentTaskService = main_menu.agenttasksv2

    @staticmethod
    def get_all(db: Session, include_archived: bool = False, include_stale: bool = True):
        query = db.query(models.Agent)

        if not include_archived:
            query = query.filter(models.Agent.archived == False)

        agents = query.all()

        # stale can't be filtered in sql because it lacks an expression.
        if not include_stale:
            return list(filter(lambda x: x.stale is False, agents))

        return agents

    @staticmethod
    def get_by_id(db: Session, uid: str):
        return db.query(models.Agent).filter(models.Agent.session_id == uid).first()

    @staticmethod
    def get_by_name(db: Session, name: str):
        return db.query(models.Agent).filter(models.Agent.name == name).first()

    def update_agent(self, db: Session, db_agent: models.Agent, agent_req):
        if agent_req.name != db_agent.name:
            if not self.get_by_name(db, agent_req.name):
                db_agent.name = agent_req.name
            else:
                return None, f'Agent with name {agent_req.name} already exists.'

        # todo should notes be a separate entity that can be attached to agents and stuff.
        #  then you can see each note individually or as a stream of comments in starkiller.
        db_agent.notes = agent_req.notes

        return db_agent, None
