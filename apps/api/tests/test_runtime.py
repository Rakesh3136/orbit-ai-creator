from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from aimn_api.models import AgentTask, Base, Network
from aimn_api.runtime import run_once, producer

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
            assert task.result["registry_version"] == "1.0.0"
            assert task.result["skill_version"] == "1.0.0"
            assert task.result["allowed_tools"] == []
            assert task.result["external_writes"] is False
            assert task.result["paid_provider_used"] is False
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
            assert root.result["registry_version"] == "1.0.0"
            assert root.result["skill_id"] == "executive.workflow_orchestration"
            assert root.result["skill_version"] == "1.0.0"
            assert root.result["external_writes"] is False
            assert root.result["max_paid_provider_cost_usd"] == 0
    finally: engine.dispose()

def test_producer_renders_script_through_orbit_adapter(tmp_path, monkeypatch):
    from types import SimpleNamespace
    from aimn_api.models import AgentTask, Network
    import aimn_api.runtime as runtime

    class FakeRenderer:
        def render(self, plan, output, narration_backend="auto"):
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"fake-video")
            captions = output.with_suffix(".srt")
            captions.write_text("captions")
            provenance = output.with_name("asset_provenance.json")
            provenance.write_text("[]")
            return SimpleNamespace(video_path=output, captions_path=captions,
                                   provenance_path=provenance, narration_backend="espeak")

    monkeypatch.setattr(runtime, "EpisodeRenderer", FakeRenderer)
    monkeypatch.setenv("AIMN_PRODUCTION_ROOT", str(tmp_path / "production"))
    engine, factory = setup_db()
    try:
        with factory() as db:
            network = Network(name="Production test")
            db.add(network); db.flush()
            task = AgentTask(network_id=network.id, agent_id="producer",
                title="Render test episode", instruction="Render the supplied approved script.",
                input_payload={"script":{"title":"A test","hook":"Opening hook",
                    "body":"First section.\\n\\nSecond section.","conclusion":"Closing thought."},
                    "narration_backend":"auto"}, external_action=False, status="queued")
            db.add(task); db.commit(); task_id = task.id
        assert run_once(factory) == "completed"
        with factory() as db:
            task = db.get(AgentTask, task_id)
            assert task.result["mode"] == "orbit_local_production"
            assert task.result["render_status"] == "completed"
            assert task.result["narration_backend"] == "espeak"
            assert task.result["external_writes"] is False
            assert Path(task.result["video_path"]).read_bytes() == b"fake-video"
            assert Path(task.result["captions_path"]).exists()
            assert Path(task.result["provenance_path"]).exists()
            assert Path(task.result["package_manifest_path"]).exists()
    finally:
        engine.dispose()


def test_producer_rejects_invalid_script_payload():
    from types import SimpleNamespace
    from aimn_api.runtime import producer
    task = SimpleNamespace(agent_id="producer", title="Bad render", instruction="x",
        result={}, input_payload={"script":{"title":"Only title"}})
    with pytest.raises(ValueError, match="title, hook, body and conclusion"):
        producer(task)
