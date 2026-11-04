import uuid
from aimn_api.models import AgentEvaluation, AgentTask, Base, Network, utc_now
from aimn_api.runtime import run_once
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


def _factory():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine, expire_on_commit=False)


def test_pending_lesson_is_not_loaded_but_approved_network_lesson_is():
    engine, factory = _factory()
    try:
        with factory() as db:
            network = Network(name="Memory network")
            db.add(network)
            db.flush()
            first = AgentTask(network_id=network.id, agent_id="research", title="Reviewed task",
                              instruction="Research topic", status="completed",
                              result={"skill_version":"1.0.0","registry_version":"1.0.0"})
            db.add(first)
            db.flush()
            lesson = AgentEvaluation(
                task_id=first.id, network_id=network.id, agent_id="research",
                skill_id="research.topic_discovery", skill_version="1.0.0",
                registry_version="1.0.0", rating=5, lesson="Cite primary sources.",
                lesson_status="pending", reviewer_email="owner@example.test",
            )
            db.add(lesson)
            pending_task = AgentTask(network_id=network.id, agent_id="research", title="Pending lesson test",
                                     instruction="Make a plan", status="queued")
            db.add(pending_task)
            db.commit()
            pending_id = pending_task.id
        assert run_once(factory) == "completed"
        with factory() as db:
            assert db.get(AgentTask, pending_id).result["approved_lessons_context"] == []
            lesson = db.query(AgentEvaluation).first()
            lesson.lesson_status = "approved"
            lesson.decided_at = utc_now()
            next_task = AgentTask(network_id=lesson.network_id, agent_id="research", title="Approved lesson test",
                                  instruction="Make a plan", status="queued")
            db.add(next_task)
            db.commit()
            next_id = next_task.id
        assert run_once(factory) == "completed"
        with factory() as db:
            context = db.get(AgentTask, next_id).result["approved_lessons_context"]
            assert len(context) == 1
            assert context[0]["lesson"] == "Cite primary sources."
            assert context[0]["scope"] == "network"
    finally:
        engine.dispose()


def test_channel_lessons_do_not_leak_to_other_channels():
    engine, factory = _factory()
    try:
        with factory() as db:
            network = Network(name="Channel memory")
            db.add(network)
            db.flush()
            from aimn_api.models import Channel
            c1 = Channel(network_id=network.id, name="One", slug="one")
            c2 = Channel(network_id=network.id, name="Two", slug="two")
            db.add_all([c1, c2])
            db.flush()
            source = AgentTask(network_id=network.id, channel_id=c1.id, agent_id="research",
                               title="Source", instruction="x", status="completed")
            target = AgentTask(network_id=network.id, channel_id=c2.id, agent_id="research",
                               title="Target", instruction="x", status="queued")
            db.add_all([source, target])
            db.flush()
            db.add(AgentEvaluation(task_id=source.id, network_id=network.id, channel_id=c1.id,
                agent_id="research", skill_id="research.topic_discovery", skill_version="1.0.0",
                registry_version="1.0.0", rating=4, lesson="Only for channel one.",
                lesson_status="approved", reviewer_email="owner@example.test"))
            db.commit()
            target_id = target.id
        assert run_once(factory) == "completed"
        with factory() as db:
            assert db.get(AgentTask, target_id).result["approved_lessons_context"] == []
    finally:
        engine.dispose()
