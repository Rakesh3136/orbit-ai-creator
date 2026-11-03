from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from aimn_api.models import AgentTask, Base, Network
from aimn_api.runtime import run_once

def setup_db():
    engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return engine,sessionmaker(bind=engine,expire_on_commit=False)

def add_task(factory,agent_id="research",external_action=False):
    with factory() as db:
        network=Network(name="Test network")
        db.add(network); db.flush()
        task=AgentTask(network_id=network.id,agent_id=agent_id,title="Prepare a topic brief",
            instruction="Prepare a useful brief for beginner viewers.",
            external_action=external_action,status="queued")
        db.add(task); db.commit()
        return task.id

def test_worker_completes_internal_task_with_transparent_plan():
    engine,factory=setup_db()
    try:
        task_id=add_task(factory)
        assert run_once(factory)=="completed"
        with factory() as db:
            task=db.get(AgentTask,task_id)
            assert task.status=="completed"
            assert task.result["mode"]=="local_planning_only"
            assert task.result["deliverable"]=="research_brief"
            assert task.result["provider_connected"] is False
            assert task.error is None
    finally: engine.dispose()

def test_worker_never_dispatches_external_action():
    engine,factory=setup_db()
    try:
        task_id=add_task(factory,agent_id="publisher",external_action=True)
        assert run_once(factory)=="idle"
        with factory() as db:
            task=db.get(AgentTask,task_id)
            assert task.status=="queued"
            assert task.result=={}
    finally: engine.dispose()

def test_unknown_agent_handler_marks_task_failed():
    engine,factory=setup_db()
    try:
        task_id=add_task(factory,agent_id="not-registered")
        assert run_once(factory)=="failed"
        with factory() as db:
            task=db.get(AgentTask,task_id)
            assert task.status=="failed"
            assert "No local handler" in task.error
    finally: engine.dispose()

def test_ceo_creates_bounded_specialist_tasks_and_aggregates_results():
    engine,factory=setup_db()
    try:
        root_id=add_task(factory,agent_id="ceo")
        assert run_once(factory)=="orchestrating"
        with factory() as db:
            root=db.get(AgentTask,root_id)
            children=db.query(AgentTask).filter(AgentTask.parent_task_id==root_id).all()
            assert root.status=="running"
            assert len(children)==5
            assert {c.agent_id for c in children}=={"research","strategist","writer","fact-checker","producer"}
            assert all(c.external_action is False for c in children)
        for _ in range(5):
            assert run_once(factory)=="completed"
        with factory() as db:
            root=db.get(AgentTask,root_id)
            assert root.status=="completed"
            assert root.result["status"]=="completed"
            assert len(root.result["specialist_results"])==5
            assert root.result["provider_connected"] is False
    finally: engine.dispose()
