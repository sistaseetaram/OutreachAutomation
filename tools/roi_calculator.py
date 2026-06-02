#!/usr/bin/env python3
"""
ROI Calculator
Track 2: Audit — calculates cost savings and revenue uplift for audit presentation.

Usage:
    python tools/roi_calculator.py                             # interactive mode
    python tools/roi_calculator.py --company "Acme Corp"      # pre-fills company name
    python tools/roi_calculator.py --company "Acme Corp" --solutions "CRM automation,Email triage"
"""

import argparse
import os
from pathlib import Path
from datetime import datetime
import re

from dotenv import load_dotenv

load_dotenv()

TMP_DIR = Path(".tmp")
TMP_DIR.mkdir(exist_ok=True)

INDUSTRY_AVG_SALARIES = {
    "saas": 65000,
    "ecommerce": 48000,
    "agency": 55000,
    "healthcare": 60000,
    "finance": 70000,
    "manufacturing": 52000,
    "retail": 42000,
    "consulting": 72000,
    "default": 55000,
}


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def get_hourly_rate(annual_salary: float) -> float:
    return annual_salary / 2080


def calc_annual_savings(
    hours_per_week: float,
    num_staff: int,
    hourly_rate: float,
    ai_savings_pct: float,
) -> dict:
    hours_saved_per_week = hours_per_week * num_staff * (ai_savings_pct / 100)
    weekly_savings = hours_saved_per_week * hourly_rate
    annual_savings = weekly_savings * 52
    return {
        "hours_saved_per_week": round(hours_saved_per_week, 1),
        "annual_savings": round(annual_savings),
    }


def calc_revenue_uplift(hours_saved_per_week: float, value_per_hour: float) -> dict:
    revenue_hours = hours_saved_per_week * 0.5
    weekly_uplift = revenue_hours * value_per_hour
    annual_uplift = weekly_uplift * 52
    return {
        "revenue_hours_per_week": round(revenue_hours, 1),
        "annual_uplift": round(annual_uplift),
    }


def prompt_float(label: str, default: float | None = None) -> float:
    hint = f" [{default}]" if default else ""
    while True:
        val = input(f"  {label}{hint}: ").strip()
        if not val and default is not None:
            return float(default)
        try:
            return float(val)
        except ValueError:
            print("  Enter a number.")


def prompt_int(label: str, default: int | None = None) -> int:
    hint = f" [{default}]" if default else ""
    while True:
        val = input(f"  {label}{hint}: ").strip()
        if not val and default is not None:
            return int(default)
        try:
            return int(val)
        except ValueError:
            print("  Enter a whole number.")


def prompt_str(label: str, default: str = "") -> str:
    hint = f" [{default}]" if default else ""
    val = input(f"  {label}{hint}: ").strip()
    return val if val else default


def collect_solution_data(solution_name: str, industry: str) -> dict:
    """Interactively collect data for one AI solution."""
    print(f"\n  --- {solution_name} ---")

    avg_salary = INDUSTRY_AVG_SALARIES.get(industry.lower(), INDUSTRY_AVG_SALARIES["default"])
    hourly_default = round(avg_salary / 2080, 2)

    hours_per_occurrence = prompt_float("Hours spent on task per occurrence (e.g. 0.5 for 30 min)")
    occurrences_per_week = prompt_float("How many times per week does this occur?")
    hours_per_week = hours_per_occurrence * occurrences_per_week

    num_staff = prompt_int("Number of staff who do this task", default=1)
    annual_salary = prompt_float(f"Average annual salary of staff doing this (USD)", default=avg_salary)
    hourly_rate = get_hourly_rate(annual_salary)

    ai_savings_pct = prompt_float("Estimated % of time AI saves on this task (50–90 typical)", default=75)
    impl_cost = prompt_float("Estimated implementation cost for this solution (USD)")

    do_uplift = input("\n  Calculate revenue uplift too? (y/n) [n]: ").strip().lower() == "y"
    revenue_uplift = {}
    if do_uplift:
        value_per_hour = prompt_float("Value per revenue-generating hour (e.g. $1500 if 1hr = 1 meeting = $1500 pipeline)")
        hours_result = calc_annual_savings(hours_per_week, num_staff, hourly_rate, ai_savings_pct)
        revenue_uplift = calc_revenue_uplift(hours_result["hours_saved_per_week"], value_per_hour)

    savings = calc_annual_savings(hours_per_week, num_staff, hourly_rate, ai_savings_pct)
    conservative_savings = round(savings["annual_savings"] * 0.65)

    roi_pct = round((conservative_savings / impl_cost) * 100) if impl_cost > 0 else 0
    payback_months = round((impl_cost / (conservative_savings / 12))) if conservative_savings > 0 else 999

    return {
        "name": solution_name,
        "hours_per_week_total": round(hours_per_week * num_staff, 1),
        "hours_saved_per_week": savings["hours_saved_per_week"],
        "annual_savings_full": savings["annual_savings"],
        "annual_savings_conservative": conservative_savings,
        "impl_cost": round(impl_cost),
        "roi_pct": roi_pct,
        "payback_months": payback_months,
        "revenue_uplift": revenue_uplift,
    }


def format_usd(n: float) -> str:
    return f"${n:,.0f}"


def build_report(company: str, solutions: list[dict]) -> str:
    total_savings = sum(s["annual_savings_conservative"] for s in solutions)
    total_cost = sum(s["impl_cost"] for s in solutions)
    total_roi = round((total_savings / total_cost) * 100) if total_cost > 0 else 0
    total_payback = round((total_cost / (total_savings / 12))) if total_savings > 0 else 999
    total_hours_saved = sum(s["hours_saved_per_week"] for s in solutions)

    lines = [
        f"# ROI Summary — {company}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Executive Summary",
        "",
        f"| Metric | Value |",
        f"|---|---|",
        f"| Total implementation cost | {format_usd(total_cost)} |",
        f"| Annual cost savings (conservative) | {format_usd(total_savings)} |",
        f"| Overall ROI | {total_roi}% |",
        f"| Payback period | {total_payback} months |",
        f"| Hours saved per week | {total_hours_saved} hrs |",
        "",
        "## Per-Solution Breakdown (The Money Slide)",
        "",
        "| Solution | Annual Savings | Impl. Cost | ROI | Payback |",
        "|---|---|---|---|---|",
    ]

    for s in solutions:
        lines.append(
            f"| {s['name']} | {format_usd(s['annual_savings_conservative'])} | "
            f"{format_usd(s['impl_cost'])} | {s['roi_pct']}% | {s['payback_months']} months |"
        )

    lines += [
        f"| **TOTAL** | **{format_usd(total_savings)}** | **{format_usd(total_cost)}** | "
        f"**{total_roi}%** | **{total_payback} months** |",
        "",
    ]

    # Revenue uplift section if any solution has it
    uplift_solutions = [s for s in solutions if s.get("revenue_uplift")]
    if uplift_solutions:
        lines += [
            "## Revenue Uplift Potential (additional)",
            "",
            "| Solution | Hours Unlocked/Week | Annual Revenue Potential |",
            "|---|---|---|",
        ]
        for s in uplift_solutions:
            u = s["revenue_uplift"]
            lines.append(
                f"| {s['name']} | {u['revenue_hours_per_week']} hrs | {format_usd(u['annual_uplift'])} |"
            )
        lines += [
            "",
            "_Note: Revenue uplift is potential, not guaranteed. Based on 50% reallocation of saved time._",
            "",
        ]

    lines += [
        "## Detailed Calculations",
        "",
    ]
    for s in solutions:
        lines += [
            f"### {s['name']}",
            f"- Hours currently spent: {s['hours_per_week_total']} hrs/week across team",
            f"- Hours saved by AI: {s['hours_saved_per_week']} hrs/week",
            f"- Full savings: {format_usd(s['annual_savings_full'])}/year",
            f"- Conservative estimate (65%): {format_usd(s['annual_savings_conservative'])}/year",
            f"- Implementation cost: {format_usd(s['impl_cost'])}",
            f"- ROI: {s['roi_pct']}% | Payback: {s['payback_months']} months",
            "",
        ]

    lines += [
        "## Sanity Check",
        "",
        f"Audit price vs. savings ratio: ",
    ]

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Calculate ROI for AI audit recommendations")
    parser.add_argument("--company", default="", help="Company name")
    parser.add_argument("--solutions", default="", help="Comma-separated solution names to analyze")
    parser.add_argument("--industry", default="default", help="Industry for salary benchmarks")
    args = parser.parse_args()

    print(f"\n{'='*50}")
    print(f"  ROI CALCULATOR")
    print(f"{'='*50}")

    company = args.company or prompt_str("Company name")
    industry = args.industry

    if args.solutions:
        solution_names = [s.strip() for s in args.solutions.split(",")]
    else:
        print("\n  Enter AI solution names (one per line, blank line when done):")
        solution_names = []
        while True:
            name = input(f"  Solution {len(solution_names)+1}: ").strip()
            if not name:
                break
            solution_names.append(name)

    if not solution_names:
        print("No solutions entered. Exiting.")
        return

    print(f"\n  You entered {len(solution_names)} solution(s). Now gathering data for each...")
    print(f"  Industry: {industry} (avg salary: ${INDUSTRY_AVG_SALARIES.get(industry.lower(), INDUSTRY_AVG_SALARIES['default']):,})")

    solutions = []
    for name in solution_names:
        data = collect_solution_data(name, industry)
        solutions.append(data)

    report = build_report(company, solutions)

    output_path = TMP_DIR / f"{slug(company)}_roi_summary.md"
    output_path.write_text(report, encoding="utf-8")

    print(f"\n{'='*50}")
    print(f"  ROI summary saved to: {output_path}")
    print(f"{'='*50}\n")
    print(report)


if __name__ == "__main__":
    main()
