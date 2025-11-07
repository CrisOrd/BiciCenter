from django.db import models
from decimal import Decimal

TIPOS_BICICLETA = [
    ('mountain', 'Montaña'),
    ('road', 'Ruta'),
    ('hybrid', 'Híbrida'),
    ('bmx', 'BMX'),
    ('electric', 'Eléctrica'),
    ('folding', 'Plegable'),
    ('cruiser', 'Cruiser'),
    ('city', 'Urbana'),
]

COLORES = [
    ('negro', 'Negro'),
    ('blanco', 'Blanco'),
    ('rojo', 'Rojo'),
    ('azul', 'Azul'),
    ('verde', 'Verde'),
    ('amarillo', 'Amarillo'),
    ('naranja', 'Naranja'),
    ('gris', 'Gris'),
    ('multicolor', 'Multicolor'),
]


class Bicicleta(models.Model):
    nombre = models.CharField(max_length=255)
    marca = models.CharField(max_length=100, blank=True)
    modelo = models.CharField(max_length=255, blank=True)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    imagen = models.ImageField(upload_to='bicicletas/', null=True, blank=True)
    tipo = models.CharField(max_length=50, choices=TIPOS_BICICLETA, default='city')
    color = models.CharField(max_length=20, blank=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        parts = [self.nombre]
        if self.marca:
            parts.append(self.marca)
        if self.modelo:
            parts.append(self.modelo)
        return " ".join(parts)


class Repuesto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    imagen = models.ImageField(upload_to='repuestos/', null=True, blank=True)
    categoria = models.CharField(max_length=100, blank=True)
    marca = models.CharField(max_length=100, blank=True)
    numero_parte = models.CharField(max_length=100, blank=True)
    compatibilidad = models.TextField(blank=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre


class Accesorio(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    imagen = models.ImageField(upload_to='accesorios/', null=True, blank=True)
    categoria = models.CharField(max_length=100, blank=True)
    marca = models.CharField(max_length=100, blank=True)
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True)
    email = models.EmailField(unique=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class BicicletaCliente(models.Model):
    MARCAS = [
        ('trek', 'Trek'),
        ('giant', 'Giant'),
        ('specialized', 'Specialized'),
        ('cannondale', 'Cannondale'),
        ('scott', 'Scott'),
        ('bianchi', 'Bianchi'),
        ('orbea', 'Orbea'),
        ('merida', 'Merida'),
        ('other', 'Otra'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    marca = models.CharField(max_length=50, choices=MARCAS)
    color = models.CharField(max_length=20, choices=COLORES)
    tipo = models.CharField(max_length=20, choices=TIPOS_BICICLETA)
    anio = models.IntegerField(null=True, blank=True)
    notas_adicionales = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_marca_display()} {self.get_color_display()} - {self.cliente}"


class ServicioMantenimiento(models.Model):
    SERVICIOS = [
        ('pastillas_freno', 'Cambio pastillas freno'),
        ('lubricacion_cadena', 'Lubricación de cadena'),
        ('centrado_ruedas', 'Centrado ruedas'),
        ('cambio_ruedas_fundas', 'Cambio de ruedas y fundas'),
        ('limpieza_profunda', 'Limpieza profunda'),
    ]

    PRECIOS = {
        'pastillas_freno': Decimal('10000'),
        'lubricacion_cadena': Decimal('5000'),
        'centrado_ruedas': Decimal('12000'),
        'cambio_ruedas_fundas': Decimal('15000'),
        'limpieza_profunda': Decimal('8000'),
    }

    nombre = models.CharField(max_length=50, choices=SERVICIOS, unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descripcion = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if (not self.precio or self.precio == 0) and self.nombre in self.PRECIOS:
            self.precio = self.PRECIOS[self.nombre]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_nombre_display()


class OrdenMantenimiento(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    bicicleta = models.ForeignKey(BicicletaCliente, on_delete=models.CASCADE)
    servicios = models.ManyToManyField(ServicioMantenimiento, through='ItemOrdenMantenimiento')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def calcular_totales(self):
        items = self.itemordenmantenimiento_set.all()
        self.subtotal = sum((item.precio for item in items), Decimal('0'))
        iva_rate = Decimal('0.19')
        self.iva = (self.subtotal * iva_rate).quantize(Decimal('0.01'))
        self.total = (self.subtotal + self.iva).quantize(Decimal('0.01'))
        self.save()

    def __str__(self):
        return f"Orden #{self.id} - {self.cliente}"


class ItemOrdenMantenimiento(models.Model):
    orden = models.ForeignKey(OrdenMantenimiento, on_delete=models.CASCADE)
    servicio = models.ForeignKey(ServicioMantenimiento, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.precio or self.precio == 0:
            self.precio = self.servicio.precio
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.servicio} - ${self.precio}"
