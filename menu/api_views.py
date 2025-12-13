from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from decimal import Decimal

from .models import (
    Bicicleta, Repuesto, Accesorio, Cliente, BicicletaCliente,
    ServicioMantenimiento, OrdenMantenimiento, ItemOrdenMantenimiento, CarritoItem
)
from .serializers import (
    UserSerializer, UserRegisterSerializer, BicicletaSerializer, RepuestoSerializer,
    AccesorioSerializer, ClienteSerializer, BicicletaClienteSerializer,
    ServicioMantenimientoSerializer, OrdenMantenimientoSerializer, OrdenMantenimientoCreateSerializer,
    CarritoItemSerializer, CarritoDetailSerializer
)

class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            
            # Crear cliente asociado
            cliente_data = {
                'nombre': request.data.get('first_name', ''),
                'apellido': request.data.get('last_name', ''),
                'rut': request.data.get('rut', ''),
                'email': user.email,
            }
            cliente = Cliente.objects.create(**cliente_data)
            
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'cliente_id': cliente.id
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({'error': 'Credenciales inválidas.'}, status=status.HTTP_401_UNAUTHORIZED)
        
        token, created = Token.objects.get_or_create(user=user)
        
        try:
            cliente = Cliente.objects.get(email=user.email)
        except Cliente.DoesNotExist:
            cliente = None
        
        return Response({
            'token': token.key,
            'user': UserSerializer(user).data,
            'cliente_id': cliente.id if cliente else None
        })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        request.user.auth_token.delete()
        return Response({'message': 'Sesión cerrada.'}, status=status.HTTP_200_OK)


# ============================================
# VIEWSETS DE PRODUCTOS
# ============================================

class BicicletaViewSet(viewsets.ModelViewSet):
    queryset = Bicicleta.objects.all()
    serializer_class = BicicletaSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['tipo', 'marca', 'color']
    search_fields = ['nombre', 'marca', 'modelo']
    ordering_fields = ['precio', 'nombre']
    
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        query = request.query_params.get('q', '')
        if query:
            bicicletas = Bicicleta.objects.filter(
                nombre__icontains=query
            ) | Bicicleta.objects.filter(
                marca__icontains=query
            ) | Bicicleta.objects.filter(
                modelo__icontains=query
            )
        else:
            bicicletas = Bicicleta.objects.all()
        
        serializer = self.get_serializer(bicicletas, many=True)
        return Response(serializer.data)


class RepuestoViewSet(viewsets.ModelViewSet):
    queryset = Repuesto.objects.all()
    serializer_class = RepuestoSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['categoria', 'marca']
    search_fields = ['nombre', 'categoria', 'marca']
    ordering_fields = ['precio', 'nombre']
    
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        query = request.query_params.get('q', '')
        if query:
            repuestos = Repuesto.objects.filter(
                nombre__icontains=query
            ) | Repuesto.objects.filter(
                categoria__icontains=query
            )
        else:
            repuestos = Repuesto.objects.all()
        
        serializer = self.get_serializer(repuestos, many=True)
        return Response(serializer.data)


class AccesorioViewSet(viewsets.ModelViewSet):
    queryset = Accesorio.objects.all()
    serializer_class = AccesorioSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['categoria', 'marca']
    search_fields = ['nombre', 'categoria', 'marca']
    ordering_fields = ['precio', 'nombre']
    
    @action(detail=False, methods=['get'])
    def buscar(self, request):
        query = request.query_params.get('q', '')
        if query:
            accesorios = Accesorio.objects.filter(
                nombre__icontains=query
            ) | Accesorio.objects.filter(
                categoria__icontains=query
            )
        else:
            accesorios = Accesorio.objects.all()
        
        serializer = self.get_serializer(accesorios, many=True)
        return Response(serializer.data)


# ============================================
# VIEWSETS DE CLIENTE Y BICICLETA CLIENTE
# ============================================

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        try:
            cliente = Cliente.objects.get(email=request.user.email)
            serializer = self.get_serializer(cliente)
            return Response(serializer.data)
        except Cliente.DoesNotExist:
            return Response({'error': 'Cliente no encontrado.'}, status=status.HTTP_404_NOT_FOUND)


class BicicletaClienteViewSet(viewsets.ModelViewSet):
    serializer_class = BicicletaClienteSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            cliente = Cliente.objects.get(email=self.request.user.email)
            return BicicletaCliente.objects.filter(cliente=cliente)
        except Cliente.DoesNotExist:
            return BicicletaCliente.objects.none()
    
    def perform_create(self, serializer):
        try:
            cliente = Cliente.objects.get(email=self.request.user.email)
            serializer.save(cliente=cliente)
        except Cliente.DoesNotExist:
            return Response({'error': 'Cliente no encontrado.'}, status=status.HTTP_404_NOT_FOUND)


# ============================================
# VIEWSETS DE SERVICIOS Y ÓRDENES
# ============================================

class ServicioMantenimientoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServicioMantenimiento.objects.all()
    serializer_class = ServicioMantenimientoSerializer
    permission_classes = [AllowAny]


class OrdenMantenimientoViewSet(viewsets.ModelViewSet):
    serializer_class = OrdenMantenimientoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            cliente = Cliente.objects.get(email=self.request.user.email)
            return OrdenMantenimiento.objects.filter(cliente=cliente)
        except Cliente.DoesNotExist:
            return OrdenMantenimiento.objects.none()
    
    def perform_create(self, serializer):
        try:
            cliente = Cliente.objects.get(email=self.request.user.email)
            data = self.request.data
            
            bicicleta_id = data.get('bicicleta')
            servicios_ids = data.get('servicios_ids', [])
            
            if not bicicleta_id or not servicios_ids:
                raise ValueError('Bicicleta y servicios requeridos.')
            
            bicicleta = BicicletaCliente.objects.get(id=bicicleta_id, cliente=cliente)
            orden = OrdenMantenimiento.objects.create(
                cliente=cliente,
                bicicleta=bicicleta,
                estado=data.get('estado', 'pendiente')
            )
            
            for servicio_id in servicios_ids:
                servicio = ServicioMantenimiento.objects.get(id=servicio_id)
                ItemOrdenMantenimiento.objects.create(
                    orden=orden,
                    servicio=servicio,
                    precio=servicio.precio
                )
            
            orden.calcular_totales()
            serializer.instance = orden
        except Exception as e:
            raise ValueError(str(e))


# ============================================
# VIEWSETS DE CARRITO
# ============================================

class CarritoViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='')
    def obtener(self, request):
        items = CarritoItem.objects.filter(usuario=request.user)
        serializer = CarritoItemSerializer(items, many=True)
        
        subtotal = sum(Decimal(item['subtotal']) for item in serializer.data)
        iva = (subtotal * Decimal('0.19')).quantize(Decimal('0.01'))
        total = subtotal + iva
        
        return Response({
            'items': serializer.data,
            'subtotal': str(subtotal),
            'iva': str(iva),
            'total': str(total)
        })
    
    @action(detail=False, methods=['post'])
    def agregar(self, request):
        tipo_producto = request.data.get('tipo_producto')
        producto_id = request.data.get('producto_id')
        cantidad = request.data.get('cantidad', 1)
        
        if not tipo_producto or not producto_id:
            return Response({'error': 'Tipo y producto ID requeridos.'}, status=status.HTTP_400_BAD_REQUEST)
        
        item, created = CarritoItem.objects.get_or_create(
            usuario=request.user,
            tipo_producto=tipo_producto,
            producto_id=producto_id,
            defaults={'cantidad': cantidad}
        )
        
        if not created:
            item.cantidad += int(cantidad)
            item.save()
        
        serializer = CarritoItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['patch'])
    def actualizar(self, request, pk=None):
        try:
            item = CarritoItem.objects.get(id=pk, usuario=request.user)
            cantidad = request.data.get('cantidad')
            
            if cantidad:
                item.cantidad = int(cantidad)
                item.save()
            
            serializer = CarritoItemSerializer(item)
            return Response(serializer.data)
        except CarritoItem.DoesNotExist:
            return Response({'error': 'Item no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['delete'])
    def eliminar(self, request, pk=None):
        try:
            item = CarritoItem.objects.get(id=pk, usuario=request.user)
            item.delete()
            return Response({'message': 'Item eliminado.'}, status=status.HTTP_204_NO_CONTENT)
        except CarritoItem.DoesNotExist:
            return Response({'error': 'Item no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['delete'])
    def vaciar(self, request):
        CarritoItem.objects.filter(usuario=request.user).delete()
        return Response({'message': 'Carrito vaciado.'}, status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['post'])
    def pago(self, request):
        items = CarritoItem.objects.filter(usuario=request.user)
        
        if not items.exists():
            return Response({'error': 'Carrito vacío.'}, status=status.HTTP_400_BAD_REQUEST)
        
        subtotal = sum(item.get_subtotal() for item in items)
        iva = (subtotal * Decimal('0.19')).quantize(Decimal('0.01'))
        total = subtotal + iva
        
        items.delete()
        
        return Response({
            'message': 'Compra realizada exitosamente.',
            'subtotal': str(subtotal),
            'iva': str(iva),
            'total': str(total)
        })


# ============================================
# VISTA DE BÚSQUEDA GENERAL
# ============================================

class BusquedaViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def productos(self, request):
        query = request.query_params.get('q', '')
        
        bicicletas = Bicicleta.objects.filter(nombre__icontains=query)
        repuestos = Repuesto.objects.filter(nombre__icontains=query)
        accesorios = Accesorio.objects.filter(nombre__icontains=query)
        
        return Response({
            'bicicletas': BicicletaSerializer(bicicletas, many=True, context={'request': request}).data,
            'repuestos': RepuestoSerializer(repuestos, many=True, context={'request': request}).data,
            'accesorios': AccesorioSerializer(accesorios, many=True, context={'request': request}).data,
        })
