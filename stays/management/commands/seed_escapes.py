"""Load demo destinations and escapes (fictional hotels in Moscow and St Petersburg).

Safe to run on every deploy: it does nothing if escapes already exist.
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from stays.models import Destination, Escape


def img(photo_id, w=1600):
    return f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w={w}&q=80"


PHOTOS = {
    # cities
    "basil": img("1513326738677-b964603b136d"),
    "kremlin": img("1512495039889-52a3b799c9bc"),
    "red_square_night": img("1520106212299-d99c443e4568"),
    "kremlin_winter": img("1547448415-e9f5b28e570d"),
    "moscow_city": img("1541447271487-09612b3f49f7"),
    "msu": img("1523509080324-9183f313dc50"),
    "spb_bridges": img("1556610961-2fecc5927173"),
    "kazan": img("1548834925-e48f8a27ae6f"),
    "nevsky": img("1556543697-2fb00d31948a"),
    # interiors
    "linen": img("1505693416388-ac5ce068fe85"),
    "velvet": img("1590490360182-c33d57733427"),
    "suite": img("1582719478250-c89cae4dc85b"),
    "warm": img("1611892440504-42a792e24d32"),
    "classic": img("1618773928121-c32242e63f39"),
    "bright": img("1631049307264-da0ec9d70304"),
    "night": img("1496417263034-38ec4f0b665a"),
    "loft": img("1578683010236-d716f9a3f461"),
    "lounge": img("1560448204-e02f11c3d0e2"),
    "spa": img("1544161515-4ab6ce6db874"),
    "bar": img("1514933651103-005eec06c04b"),
}

DESTINATIONS = [
    dict(slug="moscow", name="Москва", name_en="Moscow", image="red_square_night",
         tagline="Огни Кремля, гастрономические бары и ночные прогулки по бульварам",
         tagline_en="Kremlin lights, gastro bars and late-night walks along the boulevards"),
    dict(slug="saint-petersburg", name="Санкт-Петербург", name_en="St Petersburg", image="spb_bridges",
         tagline="Белые ночи, разводные мосты и дворцовые интерьеры",
         tagline_en="White nights, rising bridges and palace interiors"),
]

ESCAPES = [
    # ---------------- Moscow ----------------
    dict(
        slug="lunin-mansion", city="moscow", mood="romantic", featured=True, days=6,
        price=24900, original=41500, stars=5, rating=9.5, hero="basil", gallery=["linen", "velvet", "bar"],
        hotel="Особняк Лунин", hotel_en="Lunin Mansion",
        hood="Патриаршие пруды", hood_en="Patriarch's Ponds",
        title="Выходные для двоих у Патриарших", title_en="A weekend for two at Patriarch's Ponds",
        summary="Камерный особняк XIX века на тихой улице: двенадцать номеров, камин в лаунже и шампанское на завтрак.",
        summary_en="A 19th-century mansion on a quiet street: twelve rooms, a fireplace lounge and champagne at breakfast.",
        perks="Повышение категории номера при заезде\nБутылка шампанского и клубника в номере\nЗавтрак в постель для двоих\nПоздний выезд до 15:00",
        perks_en="Room upgrade on arrival\nChampagne and strawberries in your room\nBreakfast in bed for two\nLate check-out until 3pm",
    ),
    dict(
        slug="vysota-48", city="moscow", mood="romantic", featured=False, days=4,
        price=32500, original=52000, stars=5, rating=9.3, hero="moscow_city", gallery=["night", "suite", "bar"],
        hotel="Высота 48", hotel_en="Vysota 48",
        hood="Москва-Сити", hood_en="Moscow City",
        title="Ночь над огнями города", title_en="A night above the city lights",
        summary="Панорамные сьюты на 48-м этаже, ванна у окна и коктейль-бар с видом на всю Москву.",
        summary_en="Panoramic suites on the 48th floor, a bathtub by the window and a cocktail bar overlooking all of Moscow.",
        perks="Сьют с панорамным видом\nДва авторских коктейля в баре на крыше\nЗавтрак à la carte\nТрансфер из аэропорта",
        perks_en="Suite with panoramic view\nTwo signature cocktails at the rooftop bar\nÀ la carte breakfast\nAirport transfer",
    ),
    dict(
        slug="kuznetsky-12", city="moscow", mood="friends", featured=False, days=9,
        price=16900, original=27500, stars=4, rating=9.1, hero="kremlin", gallery=["bright", "lounge", "bar"],
        hotel="Кузнецкий 12", hotel_en="Kuznetsky 12",
        hood="Кузнецкий Мост", hood_en="Kuznetsky Most",
        title="Девичник в центре Москвы", title_en="A girls' weekend in central Moscow",
        summary="Бутик-отель в пяти минутах от Большого театра: трёхместные номера, бранч и лучшие магазины за углом.",
        summary_en="A boutique hotel five minutes from the Bolshoi: triple rooms, brunch and the best boutiques around the corner.",
        perks="Ежедневный бранч\nПриветственный бокал игристого\nТрёхместные номера\nБесплатная отмена за 7 дней",
        perks_en="Daily brunch\nWelcome glass of sparkling wine\nTriple rooms available\nFree cancellation up to 7 days",
    ),
    dict(
        slug="ostozhenka-residence", city="moscow", mood="spa", featured=False, days=11,
        price=27900, original=44000, stars=5, rating=9.4, hero="spa", gallery=["linen", "lounge", "velvet"],
        hotel="Остоженка Резиденс", hotel_en="Ostozhenka Residence",
        hood="Остоженка", hood_en="Ostozhenka",
        title="Спа-ритуал в Золотой миле", title_en="A spa ritual on the Golden Mile",
        summary="Хаммам, бассейн с подогревом и массаж для двоих — в десяти минутах от Храма Христа Спасителя.",
        summary_en="Hammam, heated pool and a massage for two, ten minutes from the Cathedral of Christ the Saviour.",
        perks="Массаж 60 минут для двоих\nБезлимитный доступ в спа\nЗавтрак каждый день\nТравяной чай и десерт перед сном",
        perks_en="60-minute couples massage\nUnlimited spa access\nDaily breakfast\nHerbal tea and dessert at turndown",
    ),
    dict(
        slug="pyatnitskaya-house", city="moscow", mood="gastronomy", featured=False, days=7,
        price=19500, original=31000, stars=4, rating=9.0, hero="kremlin_winter", gallery=["warm", "classic", "bar"],
        hotel="Пятницкая Хаус", hotel_en="Pyatnitskaya House",
        hood="Замоскворечье", hood_en="Zamoskvorechye",
        title="Гастрономические выходные в Замоскворечье", title_en="A gastronomic weekend in Zamoskvorechye",
        summary="Купеческий дом с рестораном нового русского меню и винным погребом на 600 этикеток.",
        summary_en="A merchant's house with a New Russian tasting menu and a wine cellar of 600 labels.",
        perks="Дегустационный ужин из 7 блюд\nВинное сопровождение от сомелье\nЗавтрак каждый день\nПоздний выезд",
        perks_en="Seven-course tasting dinner\nSommelier wine pairing\nDaily breakfast\nLate check-out",
    ),
    # ---------------- St Petersburg ----------------
    dict(
        slug="moika-palace", city="saint-petersburg", mood="romantic", featured=True, days=5,
        price=26900, original=46000, stars=5, rating=9.6, hero="spb_bridges", gallery=["velvet", "classic", "bar"],
        hotel="Дворец на Мойке", hotel_en="Moika Palace",
        hood="Набережная Мойки", hood_en="Moika Embankment",
        title="Белые ночи и разводные мосты", title_en="White nights and rising bridges",
        summary="Дворцовые сьюты с лепниной, вид на канал и ночная прогулка на катере к разводу мостов.",
        summary_en="Palace suites with stucco ceilings, canal views and a late-night boat trip to watch the bridges rise.",
        perks="Ночная прогулка на катере для двоих\nШампанское при заселении\nЗавтрак в номер\nПоздний выезд до 14:00",
        perks_en="Private night boat trip for two\nChampagne on arrival\nBreakfast in your room\nLate check-out until 2pm",
    ),
    dict(
        slug="nevsky-33", city="saint-petersburg", mood="friends", featured=False, days=8,
        price=15900, original=25500, stars=4, rating=9.0, hero="nevsky", gallery=["bright", "loft", "lounge"],
        hotel="Невский 33", hotel_en="Nevsky 33",
        hood="Невский проспект", hood_en="Nevsky Prospekt",
        title="С подругами на Невском", title_en="With the girls on Nevsky",
        summary="Светлые лофты в доходном доме на Невском: крыши, галереи и бары — всё в шаговой доступности.",
        summary_en="Bright lofts in a tenement house on Nevsky: rooftops, galleries and bars all within walking distance.",
        perks="Ежедневный завтрак\nЭкскурсия по крышам Петербурга\nПриветственный коктейль\nТрёх- и четырёхместные номера",
        perks_en="Daily breakfast\nGuided rooftop tour of St Petersburg\nWelcome cocktail\nTriple and quad rooms available",
    ),
    dict(
        slug="kamennoostrovsky-spa", city="saint-petersburg", mood="spa", featured=False, days=12,
        price=22500, original=36000, stars=5, rating=9.3, hero="kazan", gallery=["spa", "suite", "linen"],
        hotel="Каменноостровский Спа", hotel_en="Kamennoostrovsky Spa",
        hood="Петроградская сторона", hood_en="Petrogradsky Island",
        title="Модерн и спа на Петроградке", title_en="Art Nouveau and spa on Petrogradsky",
        summary="Особняк в стиле модерн с термальным комплексом, банным ритуалом и садом во внутреннем дворе.",
        summary_en="An Art Nouveau mansion with a thermal suite, a Russian banya ritual and a courtyard garden.",
        perks="Банный ритуал для двоих\nДоступ в термальный комплекс\nЗавтрак каждый день\nУжин в день заезда",
        perks_en="Banya ritual for two\nThermal suite access\nDaily breakfast\nDinner on arrival day",
    ),
    dict(
        slug="liteyny-house", city="saint-petersburg", mood="gastronomy", featured=False, days=10,
        price=18900, original=29900, stars=5, rating=9.2, hero="warm", gallery=["night", "classic", "bar"],
        hotel="Литейный Дом", hotel_en="Liteyny House",
        hood="Литейный проспект", hood_en="Liteyny Prospekt",
        title="Петербург на вкус", title_en="A taste of St Petersburg",
        summary="Отель при ресторане шефа с северной кухней: корюшка, ягоды, дичь и коктейли на настойках.",
        summary_en="A hotel built around a chef's Nordic-Russian kitchen: smelt, wild berries, game and infused cocktails.",
        perks="Ужин от шефа из 6 блюд\nДегустация настоек\nЗавтрак каждый день\nПовышение категории номера",
        perks_en="Six-course chef's dinner\nInfused-spirits tasting\nDaily breakfast\nRoom upgrade",
    ),
    dict(
        slug="neva-loft", city="saint-petersburg", mood="romantic", featured=False, days=3,
        price=17500, original=28000, stars=4, rating=9.1, hero="loft", gallery=["linen", "lounge", "bright"],
        hotel="Нева Лофт", hotel_en="Neva Loft",
        hood="Васильевский остров", hood_en="Vasilyevsky Island",
        title="Лофт с видом на Неву", title_en="A loft overlooking the Neva",
        summary="Лофты в бывшем пакгаузе на Стрелке Васильевского острова — закаты над Невой из окна спальни.",
        summary_en="Lofts in a former warehouse on the tip of Vasilyevsky Island, with Neva sunsets from your bedroom window.",
        perks="Номер с видом на Неву\nБутылка игристого и десерт\nЗавтрак каждый день\nВелосипеды на все выходные",
        perks_en="Neva-view room\nSparkling wine and dessert\nDaily breakfast\nBikes for the weekend",
    ),
]

DESCRIPTION_RU = (
    "{summary}\n\n"
    "{hotel} — из тех адресов, которые шёпотом советуют лучшей подруге и бережут для особенных "
    "моментов. Мягкий лён, тёплый свет, персонал, который запоминает, какой кофе вы пьёте, — "
    "а город начинается прямо за дверью. Район {hood_lower_ru} идеально подходит для неспешных "
    "прогулок вдвоём.\n\n"
    "Наша команда инкогнито провела здесь ночь, прежде чем подписать это предложение. Цена доступна "
    "только участницам Escale и действует до закрытия продажи."
)
DESCRIPTION_EN = (
    "{summary}\n\n"
    "{hotel} is the kind of address you whisper to your best friend and keep for the moments that "
    "matter. Soft linens, warm light, staff who remember how you take your coffee, and the city "
    "right outside the door. {hood} is made for slow walks together.\n\n"
    "Our team stayed here incognito before signing this offer. The rate is reserved for Escale "
    "members and only available until the sale closes."
)


class Command(BaseCommand):
    help = "Load demo destinations and escapes (skips if escapes already exist)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete and reload the demo data.")

    @transaction.atomic
    def handle(self, *args, reset=False, **opts):
        if Escape.objects.exists() and not reset:
            self.stdout.write("Escapes already exist, skipping (use --reset to reload).")
            return
        if reset:
            Escape.objects.all().delete()
            Destination.objects.all().delete()

        cities = {}
        for i, d in enumerate(DESTINATIONS):
            cities[d["slug"]] = Destination.objects.create(
                slug=d["slug"], name=d["name"], name_en=d["name_en"],
                tagline=d["tagline"], tagline_en=d["tagline_en"],
                image_url=PHOTOS[d["image"]], order=i,
            )

        now = timezone.now()
        for e in ESCAPES:
            Escape.objects.create(
                slug=e["slug"], destination=cities[e["city"]], mood=e["mood"],
                hotel_name=e["hotel"], hotel_name_en=e["hotel_en"],
                neighbourhood=e["hood"], neighbourhood_en=e["hood_en"],
                title=e["title"], title_en=e["title_en"],
                summary=e["summary"], summary_en=e["summary_en"],
                description=DESCRIPTION_RU.format(summary=e["summary"], hotel=e["hotel"],
                                                  hood_lower_ru=f"«{e['hood']}»"),
                description_en=DESCRIPTION_EN.format(summary=e["summary_en"], hotel=e["hotel_en"],
                                                     hood=e["hood_en"]),
                inclusions=e["perks"], inclusions_en=e["perks_en"],
                price=e["price"], original_price=e["original"], stars=e["stars"], rating=e["rating"],
                ends_at=now + timedelta(days=e["days"], hours=7), is_featured=e["featured"],
                image_url=PHOTOS[e["hero"]],
                gallery="\n".join(PHOTOS[k] for k in e["gallery"]),
            )
        self.stdout.write(self.style.SUCCESS(
            f"Loaded {len(DESTINATIONS)} destinations and {len(ESCAPES)} escapes."
        ))
