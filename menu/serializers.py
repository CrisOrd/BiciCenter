from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Bicicleta, Repuesto, Accesorio, Cliente, BicicletaCliente,
    ServicioMantenimiento, OrdenMantenimiento, ItemOrdenMantenimiento, CarritoItem
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({'password': 'Las contraseñas no coinciden.'})
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class BicicletaSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()
    precio_formateado = serializers.SerializerMethodField()
    
    class Meta:
        model = Bicicleta
        fields = ['id', 'nombre', 'marca', 'modelo', 'descripcion', 'precio', 'precio_formateado',
                  'imagen', 'imagen_url', 'tipo', 'color', 'stock']
        read_only_fields = ['id']
    
    def get_imagen_url(self, obj):
        if obj.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url
        return None
    
    def get_precio_formateado(self, obj):
        return obj.precio_chileno()


class RepuestoSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()
    precio_formateado = serializers.SerializerMethodField()
    
    class Meta:
        model = Repuesto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'precio_formateado', 'imagen', 'imagen_url',
                  'categoria', 'marca', 'numero_parte', 'compatibilidad', 'stock']
        read_only_fields = ['id']
    
    def get_imagen_url(self, obj):
        if obj.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url
        return None
    
    def get_precio_formateado(self, obj):
        return obj.precio_chileno()


class AccesorioSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()
    precio_formateado = serializers.SerializerMethodField()
    
    class Meta:
        model = Accesorio
        fields = ['id', 'nombre', 'descripcion', 'precio', 'precio_formateado', 'imagen', 'imagen_url',
                  'categoria', 'marca', 'stock']
        read_only_fields = ['id']
    
    def get_imagen_url(self, obj):
        if obj.imagen:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.imagen.url)
            return obj.imagen.url
        return None
    
    def get_precio_formateado(self, obj):
        return obj.precio_chileno()


class ClienteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'apellido', 'rut', 'email', 'fecha_registro', 'user']
        read_only_fields = ['id', 'fecha_registro']


class BicicletaClienteSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    marca_display = serializers.CharField(source='get_marca_display', read_only=True)
    color_display = serializers.CharField(source='get_color_display', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    
    class Meta:
        model = BicicletaCliente
        fields = ['id', 'cliente', 'cliente_nombre', 'marca', 'marca_display', 'color', 'color_display',
                  'tipo', 'tipo_display', 'anio', 'notas_adicionales', 'fecha_registro']
        read_only_fields = ['id', 'fecha_registro']



class ServicioMantenimientoSerializer(serializers.ModelSerializer):
    nombre_display = serializers.CharField(source='get_nombre_display', read_only=True)
    precio_formateado = serializers.SerializerMethodField()
    
    class Meta:
        model = ServicioMantenimiento
        fields = ['id', 'nombre', 'nombre_display', 'precio', 'precio_formateado', 'descripcion']
        read_only_fields = ['id']
    
    def get_precio_formateado(self, obj):
        return obj.precio_chileno()


class ItemOrdenMantenimientoSerializer(serializers.ModelSerializer):
    servicio = ServicioMantenimientoSerializer(read_only=True)
    servicio_id = serializers.IntegerField(write_only=True)
    precio_formateado = serializers.SerializerMethodField()
    
    class Meta:
        model = ItemOrdenMantenimiento
        fields = ['id', 'orden', 'servicio', 'servicio_id', 'precio', 'precio_formateado']
        read_only_fields = ['id', 'precio']
    
    def get_precio_formateado(self, obj):
        return obj.precio_chileno()


class OrdenMantenimientoSerializer(serializers.ModelSerializer):
    items = ItemOrdenMantenimientoSerializer(source='itemordenmantenimiento_set', many=True, read_only=True)
    cliente_nombre = serializers.CharField(source='cliente.nombre', read_only=True)
    bicicleta_marca = serializers.CharField(source='bicicleta.marca', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    subtotal_formateado = serializers.SerializerMethodField()
    iva_formateado = serializers.SerializerMethodField()
    total_formateado = serializers.SerializerMethodField()
    
    class Meta:
        model = OrdenMantenimiento
        fields = ['id', 'cliente', 'cliente_nombre', 'bicicleta', 'bicicleta_marca', 'items',
                  'subtotal', 'subtotal_formateado', 'iva', 'iva_formateado', 'total', 'total_formateado',
                  'estado', 'estado_display', 'fecha_creacion', 'fecha_actualizacion']
        read_only_fields = ['id', 'subtotal', 'iva', 'total', 'fecha_creacion', 'fecha_actualizacion']
    
    def get_subtotal_formateado(self, obj):
        valor_int = int(obj.subtotal)
        return f"${valor_int:,}".replace(',', '.')
    
    def get_iva_formateado(self, obj):
        valor_int = int(obj.iva)
        return f"${valor_int:,}".replace(',', '.')
    
    def get_total_formateado(self, obj):
        valor_int = int(obj.total)
        return f"${valor_int:,}".replace(',', '.')


class OrdenMantenimientoCreateSerializer(serializers.Serializer):
    bicicleta_id = serializers.IntegerField()
    servicios_ids = serializers.ListField(child=serializers.IntegerField())
    estado = serializers.CharField(default='pendiente')



class CarritoItemSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.SerializerMethodField()
    producto_precio = serializers.SerializerMethodField()
    subtotal = serializers.SerializerMethodField()
    
    class Meta:
        model = CarritoItem
        fields = ['id', 'usuario', 'tipo_producto', 'producto_id', 'producto_nombre', 'producto_precio',
                  'cantidad', 'subtotal', 'fecha_agregado']
        read_only_fields = ['id', 'usuario', 'fecha_agregado']
    
    def get_producto_nombre(self, obj):
        producto = obj.get_producto()
        return producto.nombre if producto else None
    
    def get_producto_precio(self, obj):
        producto = obj.get_producto()
        return str(producto.precio) if producto else None
    
    def get_subtotal(self, obj):
        return str(obj.get_subtotal())


class CarritoDetailSerializer(serializers.Serializer):
    items = CarritoItemSerializer(many=True, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    iva = serializers.DecimalField(max_digits=10, decimal_places=2)
    total = serializers.DecimalField(max_digits=10, decimal_places=2)
