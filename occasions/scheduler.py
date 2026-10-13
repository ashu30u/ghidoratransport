import os
import sys
import time
import logging
import threading

logger = logging.getLogger(__name__)

_scheduler_started = False
_scheduler_lock = threading.Lock()


def start_occasion_scheduler():
    """
    Starts a background daemon thread that runs periodically to check
    and send due scheduled occasion emails.
    """
    global _scheduler_started
    with _scheduler_lock:
        if _scheduler_started:
            return

        # Skip running scheduler inside management commands (except runserver)
        cmd_args = " ".join(sys.argv)
        skip_commands = ['makemigrations', 'migrate', 'collectstatic', 'test', 'shell', 'createsuperuser', 'send_occasion_messages']
        if any(cmd in cmd_args for cmd in skip_commands):
            return

        # In runserver, Django runs two processes: supervise parent and worker child.
        # Only start in the child worker process where RUN_MAIN == 'true'.
        if 'runserver' in cmd_args and os.environ.get('RUN_MAIN') != 'true':
            return

        _scheduler_started = True

        def _worker_loop():
            # Initial sleep to ensure Django app registry and database connections are ready
            time.sleep(5)
            logger.info("[Occasion Scheduler] Background daemon thread started successfully.")
            print("[Occasion Scheduler] Background worker active - monitoring scheduled occasions.")

            while True:
                try:
                    from occasions.services import check_and_send_due_occasions
                    check_and_send_due_occasions()
                except Exception as e:
                    logger.error(f"[Occasion Scheduler] Error checking due occasions: {e}", exc_info=True)
                time.sleep(20)

        t = threading.Thread(target=_worker_loop, daemon=True, name="OccasionSchedulerDaemon")
        t.start()
