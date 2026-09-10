"""CLI entrypoint for the GitLab Agentic Turn controller, webhook relay, worker, and judge."""
import argparse
import json
import os
import sys

from .controller import AgentController
from .webhook_relay import process_webhook_payload, get_openbao_credential
from .gitlab_client import GitLabClient


def main():
    parser = argparse.ArgumentParser(description="GitLab Agentic Turn CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # run subcommand
    run_parser = subparsers.add_parser("run", help="Run 3-stage agentic workflow for an issue")
    run_parser.add_argument("issue_iid", type=int, help="GitLab Issue IID")
    run_parser.add_argument("--repo-dir", default=".", help="Path to repository directory")
    run_parser.add_argument("--state-dir", default=".agent-state", help="Path to agent state directory")

    # webhook subcommand
    webhook_parser = subparsers.add_parser("webhook", help="Process incoming GitLab issue webhook payload")
    webhook_parser.add_argument("--payload-file", help="Path to JSON payload file (reads stdin if omitted)")
    webhook_parser.add_argument("--state-dir", default=".agent-state", help="Path to agent state directory")

    args = parser.parse_args()

    if args.command == "run":
        controller = AgentController(repo_dir=args.repo_dir, state_dir=args.state_dir)
        success = controller.run_issue(args.issue_iid)
        sys.exit(0 if success else 1)

    elif args.command == "webhook":
        if args.payload_file:
            with open(args.payload_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
        else:
            payload = json.load(sys.stdin)

        should_run, message, issue_iid = process_webhook_payload(payload, state_dir=args.state_dir)
        print(f"Webhook relay: {message}")

        if should_run and issue_iid:
            token = get_openbao_credential() or os.getenv("GITLAB_PAT") or os.getenv("GITLAB_AGENT_TOKEN")
            if token:
                os.environ["GITLAB_AGENT_TOKEN"] = token
                os.environ["GITLAB_PAT"] = token
            gitlab_client = GitLabClient(token=token)
            controller = AgentController(state_dir=args.state_dir, gitlab_client=gitlab_client)
            success = controller.run_issue(issue_iid)
            sys.exit(0 if success else 1)
        else:
            sys.exit(0)


if __name__ == "__main__":
    main()
