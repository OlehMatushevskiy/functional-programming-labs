from core import add_option, apply_discount, change_status, extend_rental
from model import Car, Rental, RentalOption


def main() -> None:
    car = Car(7, "Toyota Corolla", 1000.0, frozenset({"automatic", "air conditioning"}))
    original = Rental(1, car, 2, meta={"pickup": "Львів"})
    with_gps = add_option(original, RentalOption("GPS", 100.0))
    extended = extend_rental(with_gps, 2)
    active = change_status(extended, "active")
    invoice = apply_discount(active, 0.1)

    print(f"Авто: {car.model}. Місце видачі: {active.meta['pickup']}.")
    print(f"Початкова оренда: {original.days} дні, {original.status}, без опцій.")
    print(
        f"Оновлена оренда: {active.days} дні, {active.status}, {active.options[0].name}."
    )
    print(f"До знижки: {invoice.subtotal:.2f} грн.")
    print(f"Після знижки 10%: {invoice.total:.2f} грн.")
    print(f"Окремих версій у множині: {len({original, active})}.")


if __name__ == "__main__":
    main()
