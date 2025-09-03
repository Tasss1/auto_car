from django.db import models

CONDITION_CHOICES = [
    ('new', 'Новый'),
    ('used', 'Б/У'),
]

COLOR_CHOICES = [
    ('white', 'Белый'),
    ('black', 'Черный'),
    ('gray', 'Серый'),
    ('silver', 'Серебристый'),
    ('blue', 'Синий'),
    ('red', 'Красный'),
    ('green', 'Зеленый'),
    ('yellow', 'Желтый'),
    ('brown', 'Коричневый'),
    ('orange', 'Оранжевый'),
    ('purple', 'Фиолетовый'),
    ('gold', 'Золотой'),
]

BODY_CHOICES = [
    ('sedan', 'Седан'),
    ('hatchback', 'Хэтчбек'),
    ('wagon', 'Универсал'),
    ('suv', 'Внедорожник (SUV)'),
    ('crossover', 'Кроссовер'),
    ('coupe', 'Купе'),
    ('convertible', 'Кабриолет'),
    ('pickup', 'Пикап'),
    ('minivan', 'Минивэн'),
]

FUEL_CHOICES = [
    ('petrol', 'Бензин'),
    ('diesel', 'Дизель'),
    ('electric', 'Электро'),
    ('hybrid', 'Гибрид'),
    ('gas', 'Газ'),
]

PRICE_CHOICES = [
    ('5000-10000', '5000$ - 10000$'),
    ('10000-15000', '10000$ - 15000$'),
    ('15000-20000', '15000$ - 20000$'),
    ('20000-25000', '20000$ - 25000$'),
    ('25000-30000', '25000$ - 30000$'),
    ('30000-35000', '30000$ - 35000$'),
    ('35000-40000', '35000$ - 40000$'),
    ('40000-45000', '40000$ - 45000$'),
    ('45000-50000', '45000$ - 50000$'),
    ('50000-60000', '50000$ - 60000$'),
]


class CarContent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES)
    body_type = models.CharField(max_length=15, choices=BODY_CHOICES)
    fuel_type = models.CharField(max_length=10, choices=FUEL_CHOICES)
    price_range = models.CharField(max_length=15, choices=PRICE_CHOICES)

    video = models.FileField(upload_to="cars/videos/", blank=True, null=True)
    photo1 = models.ImageField(upload_to="cars/photos1/", blank=True, null=True)
    photo2 = models.ImageField(upload_to="cars/photos2/", blank=True, null=True)
    photo3 = models.ImageField(upload_to="cars/photos3/", blank=True, null=True)
    photo4 = models.ImageField(upload_to="cars/photos4/", blank=True, null=True)
    photo5 = models.ImageField(upload_to="cars/photos5/", blank=True, null=True)
    user = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.get_condition_display()}, {self.get_price_range_display()})"
