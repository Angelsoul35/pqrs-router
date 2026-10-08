"""pqrs-router command-line demo."""

from __future__ import annotations

import argparse
from datetime import date

from .service import PQRSService

SAMPLES = [
    "I want to complain about the rude treatment by an agent on the phone line.",
    "I request information about the opening hours of the public information portal.",
    "There is a dangerous water leak in the main pipe on my street, it is urgent.",
    "I suggest that you improve the appointment scheduling process.",
    "I demand a correction of an incorrect charge on my invoice this month.",
]


def _show(result: dict) -> None:
    flag = " (UNCERTAIN - manual triage)" if result["uncertain"] else ""
    print(
        f"   [{result['priority'].upper():6}] {result['request_type']:10} -> "
        f"{result['department']:17} due {result['due_date']} "
        f"({result['sla_business_days']} business days){flag}"
    )
    print(f"      type conf {result['type_confidence']:.2f}, dept conf "
          f"{result['department_confidence']:.2f}; {result['priority_reasons'][-1]}")


def demo() -> None:
    print("1) Training the classifier ...")
    service = PQRSService()
    received = date(2026, 1, 5)  # a Monday, for reproducible deadlines
    print(f"2) Routing sample requests (received {received.isoformat()}):")
    for text in SAMPLES:
        print(f'   "{text}"')
        _show(service.route(text, received=received))


def route(text: str) -> None:
    _show(PQRSService().route(text))


def main() -> None:
    parser = argparse.ArgumentParser(description="pqrs-router CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo", help="classify and route a few sample requests")
    route_cmd = sub.add_parser("route", help="route one request")
    route_cmd.add_argument("text", help="the request text")
    args = parser.parse_args()
    if args.command == "demo":
        demo()
    elif args.command == "route":
        route(args.text)


if __name__ == "__main__":
    main()
