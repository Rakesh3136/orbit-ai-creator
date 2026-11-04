from __future__ import annotations

import argparse
import json

from orbit.learning.feedback import LearningMemory


def main() -> None:
    parser = argparse.ArgumentParser(description="Review ORBIT outputs and manage owner-approved learning.")
    parser.add_argument("--db", default="data/orbit-learning.sqlite3", help="local learning database")
    sub = parser.add_subparsers(dest="command", required=True)

    pending = sub.add_parser("pending", help="show recent outputs awaiting owner review")
    pending.add_argument("--limit", type=int, default=20)

    review = sub.add_parser("review", help="rate an output and optionally approve a reusable lesson")
    review.add_argument("evaluation_id", type=int)
    review.add_argument("--rating", type=int, required=True, choices=range(1, 6))
    review.add_argument("--correction", default="")
    review.add_argument("--lesson", default="")
    review.add_argument("--scope", choices=("network", "channel"), default="network")
    review.add_argument("--scope-id", default="default")
    review.add_argument("--provenance", default="owner:cli-review")
    review.add_argument("--approve-lesson", action="store_true")

    performance = sub.add_parser("performance", help="show an agent's score history")
    performance.add_argument("agent")
    performance.add_argument("--task-type")

    reviews = sub.add_parser("reviews", help="show recorded owner reviews")
    reviews.add_argument("--evaluation-id", type=int)
    reviews.add_argument("--limit", type=int, default=50)

    args = parser.parse_args()
    memory = LearningMemory(args.db)

    if args.command == "pending":
        for item in memory.recent(limit=args.limit):
            print(f"#{item.id} {item.agent}/{item.task_type} score={item.overall:.1f} passed={item.passed} scores={json.dumps(item.scores, sort_keys=True)}")
    elif args.command == "review":
        review_id = memory.submit_review(
            args.evaluation_id, args.rating, args.correction, args.lesson,
            args.scope, args.scope_id, args.provenance, args.approve_lesson,
        )
        print(f"Recorded owner review #{review_id} for evaluation #{args.evaluation_id}.")
        if args.approve_lesson:
            print("Lesson approved for matching future tasks.")
        else:
            print("No reusable lesson was approved.")
    elif args.command == "performance":
        print(json.dumps(memory.performance(args.agent, args.task_type), indent=2))
    elif args.command == "reviews":
        for item in memory.reviews(args.evaluation_id, args.limit):
            print(f"review #{item.id} evaluation=#{item.evaluation_id} rating={item.rating}/5 scope={item.scope_type}:{item.scope_id} lesson_approved={item.lesson_approved}")
            if item.correction:
                print(f"  correction: {item.correction}")
            if item.lesson:
                print(f"  lesson: {item.lesson}")
            print(f"  provenance: {item.provenance}")


if __name__ == "__main__":
    main()
