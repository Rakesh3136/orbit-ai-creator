"""Run the AIMN local worker with: python -m aimn_api.worker."""
import argparse
import logging
import time
from aimn_api.db import SessionLocal
from aimn_api.runtime import run_once

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger=logging.getLogger("aimn.worker")

def main():
    parser=argparse.ArgumentParser(description="AIMN local planning worker")
    parser.add_argument("--once",action="store_true",help="Process at most one internal task")
    parser.add_argument("--poll-seconds",type=float,default=3.0)
    args=parser.parse_args()
    interval=max(0.5,args.poll_seconds)
    logger.info("Worker started in local-planning-only mode")
    while True:
        outcome=run_once(SessionLocal)
        if outcome!="idle": logger.info("Task outcome: %s",outcome)
        if args.once: break
        if outcome=="idle": time.sleep(interval)

if __name__=="__main__":
    main()
