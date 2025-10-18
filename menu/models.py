from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User

class Bicicleta(models.Model):
    nombre = models.CharField(max_length=255)
    modelo = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='bicicletas/')
    modelo_bicicleta = models.CharField(max_length=255)
    tipo_bicicleta = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.nombre} - {self.modelo}"

class Repuesto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='repuestos/', null=True, blank=True)

    def __str__(self):
        return self.nombre

class Accesorio(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='accesorios/', null=True, blank=True)

    def __str__(self):
        return self.nombre
    
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rut = models.CharField(max_length=12, unique=True)
    email = models.EmailField()
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
    
    TIPOS = [
        ('mountain', 'Montaña'),
        ('road', 'Ruta'),
        ('hybrid', 'Híbrida'),
        ('bmx', 'BMX'),
        ('electric', 'Eléctrica'),
        ('folding', 'Plegable'),
        ('cruiser', 'Cruiser'),
        ('city', 'Urbana'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    marca = models.CharField(max_length=50, choices=MARCAS)
    color = models.CharField(max_length=20, choices=COLORES)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    año = models.IntegerField(null=True, blank=True)
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
        'pastillas_freno': 10000,
        'lubricacion_cadena': 5000,
        'centrado_ruedas': 12000,
        'cambio_ruedas_fundas': 15000,
        'limpieza_profunda': 8000,
    }

    nombre = models.CharField(max_length=50, choices=SERVICIOS, unique=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    def save(self, *args, **kwargs):
        if not self.precio and self.nombre in self.PRECIOS:
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
        self.subtotal = sum(item.precio for item in items)
        
        # Corrección: Se convierte el 0.19 a Decimal para evitar el error.
        iva_rate = Decimal('0.19')
        
        self.iva = self.subtotal * iva_rate
        self.total = self.subtotal + self.iva
        self.save()

    def __str__(self):
        return f"Orden #{self.id} - {self.cliente}"

class ItemOrdenMantenimiento(models.Model):
    orden = models.ForeignKey(OrdenMantenimiento, on_delete=models.CASCADE)
    servicio = models.ForeignKey(ServicioMantenimiento, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.precio:
            self.precio = self.servicio.precio
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.servicio} - ${self.precio}"
    
class CarritoItem(models.Model):
    TIPO_CHOICES = [
        ('bicicleta', 'Bicicleta'),
        ('repuesto', 'Repuesto'),
        ('accesorio', 'Accesorio'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo_producto = models.CharField(max_length=20, choices=TIPO_CHOICES)
    producto_id = models.IntegerField()
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('usuario', 'tipo_producto', 'producto_id')
    
    def get_producto(self):
        """Obtiene el producto según su tipo"""
        if self.tipo_producto == 'bicicleta':
            return Bicicleta.objects.get(id=self.producto_id)
        elif self.tipo_producto == 'repuesto':
            return Repuesto.objects.get(id=self.producto_id)
        elif self.tipo_producto == 'accesorio':
            return Accesorio.objects.get(id=self.producto_id)
        return None
    
    def get_subtotal(self):
        """Calcula el subtotal del item"""
        producto = self.get_producto()
        if producto:
            return producto.precio * self.cantidad
        return Decimal('0.00')
    
    def __str__(self):
        return f"{self.usuario.username} - {self.tipo_producto} #{self.producto_id}"