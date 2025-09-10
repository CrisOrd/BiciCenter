from django.db import models

from django.db import models

class Bicicleta(models.Model):
    nombre = models.CharField(max_length=255)
    modelo = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='bicicletas/')

    def __str__(self):
        return f"{self.nombre} - {self.modelo}"

class Repuesto(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    bicicleta = models.ForeignKey(Bicicleta, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre

class Accesorio(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    bicicleta = models.ForeignKey(Bicicleta, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre
