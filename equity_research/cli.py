"""Command-line interface for the equity research tool."""

from __future__ import annotations

import argparse
import logging
import sys

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from equity_research.aggregator import ALL_SECTIONS, EquityResearchAggregator
from equity_research.report import generate_json_report, generate_text_report

console = Console()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="equity-research",
        description="Gather comprehensive equity research data for a stock ticker.",
    )
    parser.add_argument(
        "ticker",
        type=str,
        help="Stock ticker symbol (e.g. AAPL, MSFT, TSLA)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Write report to a file instead of stdout",
    )
    parser.add_argument(
        "--sections",
        nargs="+",
        choices=sorted(ALL_SECTIONS),
        default=None,
        help="Sections to include (default: all). Options: profile financials price analysts filings news",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose/debug logging",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    ticker = args.ticker.upper()
    sections = set(args.sections) if args.sections else None

    # Header
    console.print(
        Panel(
            Text(f"Equity Research: {ticker}", style="bold white"),
            style="blue",
        )
    )
    console.print(f"[dim]Fetching data for [bold]{ticker}[/bold]...[/dim]\n")

    # Run the aggregator
    with console.status("[bold green]Scraping data sources..."):
        aggregator = EquityResearchAggregator(ticker, sections=sections)
        report = aggregator.run()

    # Generate output
    if args.format == "json":
        output = generate_json_report(report)
    else:
        output = generate_text_report(report)

    # Write to file or stdout
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        console.print(f"[green]Report saved to {args.output}[/green]")
    else:
        console.print(output)

    # Summary
    error_count = len(report.errors)
    if error_count:
        console.print(f"\n[yellow]Completed with {error_count} error(s).[/yellow]")
    else:
        console.print("\n[green]Report complete.[/green]")

    return 1 if error_count else 0


if __name__ == "__main__":
    sys.exit(main())
