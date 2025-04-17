#---------------- MODELS.PY ----------------

from django.db import models


# REGISTRO CLIENTE
class Cliente(models.Model):
    rut = models.CharField(primary_key=True, max_length=12, verbose_name='RUT')
    nombre = models.CharField(max_length=200, verbose_name='Nombres')
    apellidos = models.CharField(max_length=200, verbose_name='Apellidos')
    usuario = models.CharField(max_length=150, verbose_name='Nombre Usuario')
    email = models.EmailField(unique=True,verbose_name='Correo electrónico')
    clave = models.CharField(max_length=128, verbose_name='Contraseña')
    fechaNacimiento = models.DateField(verbose_name='Fecha de nacimiento')
    direccion = models.CharField(max_length=255, blank=True, null=True, verbose_name='Dirección')

    class Meta:
        db_table = 'E11EVENSTORE_CLIENTES'

    def __str__(self):
        return f"Cliente: {self.nombre} {self.apellidos}"

# REGISTRO ADMINISTRADORES
class Administrativo(models.Model):
    rut = models.CharField(unique=True, max_length=12)
    nombre = models.CharField(max_length=200)
    apellidos = models.CharField(max_length=200)
    usuario = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    clave = models.CharField(max_length=128)
    fechaNacimiento = models.DateField()
    direccion = models.CharField(max_length=255, blank=True, null=True)
    
    class Meta:
        db_table = 'E11EVENSTORE_ADMINISTRATIVOS'

    def __str__(self):
        return f"Administrativo: {self.nombre} {self.apellidos}"
        
# PRODUCTOS, COMPRAS Y DETALLE
class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.PositiveIntegerField()
    CATEGORIAS = [
    ('CAT_1', 'Carreras'),
    ('CAT_2', 'Terror'),
    ('CAT_3', 'Mundo abierto'),
    ('CAT_4', 'Free to play'),
    ('CAT_5', 'Acción'),
    ('CAT_6', 'Supervivencia'),
    ]
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nombre} (ID: {self.id})"


class Compra(models.Model):
    cliente = models.ForeignKey(Cliente, to_field='rut', on_delete=models.CASCADE, related_name='compras')
    numero_compra = models.CharField(max_length=20, unique=True, verbose_name='Número de compra')
    direccion_envio = models.CharField(max_length=255, verbose_name='Dirección de envío')
    metodo_pago = models.CharField(max_length=50, verbose_name='Método de pago')
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de compra')
    estado = models.CharField(
        max_length=20,
        choices=[('pendiente', 'Pendiente'), ('enviado', 'Enviado')],
        default='pendiente',
        verbose_name='Estado de compra'
    )

    def __str__(self):
        return f"Compra #{self.numero_compra} - {self.cliente}"


class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles', default=1)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def subtotal(self):
        return self.cantidad * self.producto.precio

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} (Compra {self.compra.numero_compra})"



    
