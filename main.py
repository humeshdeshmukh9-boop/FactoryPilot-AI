import csv
import os
from datetime import date

CSV_FILE = "production_reports.csv"
CSV_HEADER = [
    "date",
    "factory_name",
    "production_quantity",
    "daily_target",
    "achieved_percentage",
    "target_met",
]


def get_factory_name():
    """Ask for a factory name and reject blank answers."""
    factory_name = input("Enter the factory name: ").strip()

    while not factory_name:
        print("Factory name cannot be blank.")
        factory_name = input("Enter the factory name: ").strip()

    return factory_name


def get_whole_number(prompt, minimum):
    """Ask for a whole number that is at least the minimum."""
    while True:
        try:
            number = int(input(prompt))
        except ValueError:
            print("Please enter a whole number.")
            continue

        if number < minimum:
            if minimum == 0:
                print("Quantity cannot be negative. Please try again.")
            else:
                print("The target must be greater than zero. Please try again.")
            continue

        return number


def build_report(factory_name, daily_quantity, daily_target):
    """Create a report using the same fields as the saved CSV file."""
    factory_name = factory_name.strip()
    if not factory_name:
        raise ValueError("Factory name cannot be blank.")
    if daily_quantity < 0:
        raise ValueError("Production quantity cannot be negative.")
    if daily_target <= 0:
        raise ValueError("The target must be greater than zero.")

    achieved_percentage = daily_quantity / daily_target * 100

    return {
        "date": date.today().isoformat(),
        "factory_name": factory_name,
        "production_quantity": daily_quantity,
        "daily_target": daily_target,
        "achieved_percentage": f"{achieved_percentage:.1f}",
        "target_met": "Yes" if daily_quantity >= daily_target else "No",
    }


def save_report(report):
    """Append one report to the existing CSV file, adding its header if needed."""
    file_needs_header = (
        not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0
    )

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if file_needs_header:
            writer.writerow(CSV_HEADER)

        writer.writerow([report[column] for column in CSV_HEADER])


def read_saved_reports():
    """Return saved reports without changing the CSV file."""
    if not os.path.exists(CSV_FILE) or os.path.getsize(CSV_FILE) == 0:
        return []

    with open(CSV_FILE, "r", newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def print_report_table(headers, rows):
    """Print rows with columns sized to fit their contents."""
    column_widths = []

    for column_number, header in enumerate(headers):
        widest_value = max(len(row[column_number]) for row in rows)
        column_widths.append(max(len(header), widest_value))

    header_line = " | ".join(
        header.ljust(column_widths[index])
        for index, header in enumerate(headers)
    )
    separator = "-+-".join("-" * width for width in column_widths)

    print()
    print("SAVED PRODUCTION REPORTS")
    print(header_line)
    print(separator)

    for row in rows:
        print(
            " | ".join(
                value.ljust(column_widths[index])
                for index, value in enumerate(row)
            )
        )


def add_daily_report():
    """Collect a report, display it, and append it to the CSV file."""
    factory_name = get_factory_name()
    daily_quantity = get_whole_number(
        "Enter today's production quantity in units: ", 0
    )
    daily_target = get_whole_number(
        "Enter the daily production target in units: ", 1
    )

    report = build_report(factory_name, daily_quantity, daily_target)

    print()
    print("=" * 40)
    print("       DAILY PRODUCTION REPORT")
    print("=" * 40)
    print(f"Factory: {factory_name}")
    print(f"Today's production: {daily_quantity:,} units")
    print(f"Daily production target: {daily_target:,} units")
    print(f"Production achieved: {report['achieved_percentage']}%")
    print(f"Target met: {report['target_met']}")
    print("=" * 40)

    try:
        save_report(report)
        print(f"Report saved to {CSV_FILE}.")
    except (OSError, csv.Error) as error:
        print(f"Could not save the report to {CSV_FILE}: {error}")


def view_saved_reports():
    """Read saved reports and display them without changing the CSV file."""
    try:
        reports = read_saved_reports()
    except (OSError, csv.Error, UnicodeError) as error:
        print(f"Could not read reports from {CSV_FILE}: {error}")
        return

    if not reports:
        print("No saved reports yet.")
        return

    headers = [
        "Date",
        "Factory",
        "Production (units)",
        "Target (units)",
        "Achieved",
        "Target met",
    ]
    table_rows = []

    for report in reports:
        achieved = report.get("achieved_percentage") or "-"
        if achieved != "-" and not achieved.endswith("%"):
            achieved += "%"

        table_rows.append(
            [
                report.get("date") or "-",
                report.get("factory_name") or "-",
                report.get("production_quantity") or "-",
                report.get("daily_target") or "-",
                achieved,
                report.get("target_met") or "-",
            ]
        )

    print_report_table(headers, table_rows)


def main():
    print("Welcome to FactoryPilot AI!")
    print()
    print("1. Add a new daily production report")
    print("2. View all previously saved reports")

    while True:
        choice = input("Choose an option (1 or 2): ").strip()

        if choice == "1":
            add_daily_report()
            return

        if choice == "2":
            view_saved_reports()
            return

        print("Please enter 1 or 2.")


if __name__ == "__main__":
    main()
