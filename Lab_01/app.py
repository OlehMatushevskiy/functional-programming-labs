from core import BillingReport, MeterReading, make_processor


def print_receipts(report: BillingReport) -> None:
    for bill in report["bills"]:
        print(
            f"Лічильник {bill['meter_id']} ({bill['tariff_group']}): "
            f"{bill['consumption']:g} кВт·год × {bill['rate']:.2f} грн, "
            f"пільга {bill['subtotal'] - bill['amount_due']:.2f} грн, "
            f"до сплати {bill['amount_due']:.2f} грн"
        )
    print(f"Разом до сплати: {report['total_due']:.2f} грн")


def main() -> None:
    rates = {"звичайний": 4.0, "пільговий": 3.0}
    benefit_rates = {"звичайний": 0.0, "пільговий": 0.25}

    def tariff_for(group: str) -> float:
        return rates[group]

    def apply_benefit(group: str, subtotal: float) -> float:
        return subtotal * (1 - benefit_rates[group])

    readings: list[MeterReading] = [
        {
            "meter_id": "A101",
            "previous": 1200,
            "current": 1275,
            "tariff_group": "звичайний",
        },
        {
            "meter_id": "B204",
            "previous": 1840,
            "current": 1900,
            "tariff_group": "пільговий",
        },
    ]
    processor = make_processor(tariff_for=tariff_for, apply_benefit=apply_benefit)
    print_receipts(processor(readings))


if __name__ == "__main__":
    main()
