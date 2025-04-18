# ------------- VIEWS.PY ---------------------

from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import LoginForm
from .models import Administrativo
from .models import Cliente
from .forms import RegistroForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import Producto, Compra, DetalleCompra
from .forms import DireccionEnvioForm, MetodoPagoForm
import random
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .forms import EditarClienteForm
from django.contrib.admin.views.decorators import staff_member_required
from .serializers import ProductoSerializer, CompraSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .decorators import cliente_login_required
from .decorators import admin_login_required
from django.shortcuts import render, redirect
from .models import Producto
from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404


def inicio(request):
    return render(request, "index.html")


def contacto(request):
    return render(request, "contacto.html")


def formulario_registro(request):
    form = RegistroForm()


def carro_compras(request):
    return render(request, "carro_compras.html")


def menu_categorias(request):
    return render(request, "menu_categorias.html")


def login_cliente(request):
    return render(request, "login_cliente.html")


def login_admin(request):
    return render(request, "login_admin.html")

    # categorias menu #


def categoria_accion(request):
    productos = Producto.objects.filter(categoria="CAT_5-Accion")
    return render(request, "accion.html", {"productos": productos})


def categoria_terror(request):
    productos = Producto.objects.filter(categoria="CAT_2-Terror")
    return render(request, "terror.html", {"productos": productos})


def categoria_mundo_abierto(request):
    productos = Producto.objects.filter(categoria="CAT_3-Mundo abierto")
    return render(request, "mundo_abierto.html", {"productos": productos})


def categoria_free_to_play(request):
    productos = Producto.objects.filter(categoria="CAT_4-Free to play")
    return render(request, "free_to_play.html", {"productos": productos})


def categoria_supervivencia(request):
    productos = Producto.objects.filter(categoria="CAT_6-Supervivencia")
    return render(request, "supervivencia.html", {"productos": productos})


def categoria_carreras(request):
    productos = Producto.objects.filter(categoria="CAT_1-Carreras")
    return render(request, "carreras.html", {"productos": productos})


# INICIO SESION COMUN
def inicio_sesion(request):
    form = LoginForm()

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            clave = form.cleaned_data["clave"]
            es_admin = request.POST.get(
                "es_admin"
            )  # Esto nos indica si es admin o cliente

            if es_admin == "1":
                try:
                    admin = Administrativo.objects.get(email=email, clave=clave)
                    request.session["email_admin"] = admin.email
                    messages.success(request, "¡Bienvenido Administrador!")
                    return redirect("login_admin")
                except Administrativo.DoesNotExist:
                    form.add_error(
                        None, "Acceso denegado. Administrador no registrado."
                    )
            else:
                try:
                    cliente = Cliente.objects.get(email=email, clave=clave)
                    request.session["email_cliente"] = cliente.email
                    messages.success(request, "¡Bienvenido Cliente!")
                    return redirect("login_cliente")
                except Cliente.DoesNotExist:
                    form.add_error(None, "Correo o contraseña incorrectos.")

    return render(request, "inicio_sesion.html", {"form": form})


# REGISTRO FORMULARIO CLIENTES
def formulario_registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.save()
            messages.success(request, "¡Registro exitoso! Por favor inicia sesión.")
            return redirect("inicio_sesion")
    else:
        form = RegistroForm()

    return render(request, "formulario_registro.html", {"form": form})


# CARRO COMPRAS
@cliente_login_required
def carro_compras(request):
    carro = request.session.get("carro", [])
    email_cliente = request.session.get("email_cliente")
    cliente = Cliente.objects.filter(email=email_cliente).first()

    if request.method == "POST":
        if "eliminar_producto" in request.POST:
            producto_id = int(request.POST["eliminar_producto"])
            carro = [item for item in carro if item["producto_id"] != producto_id]
            request.session["carro"] = carro
            return redirect("carro_compras")

        elif "vaciar_carro" in request.POST:
            request.session["carro"] = []
            return redirect("carro_compras")

        form_direccion = DireccionEnvioForm(request.POST)
        form_pago = MetodoPagoForm(request.POST)

        if form_direccion.is_valid() and form_pago.is_valid():
            if not carro:
                messages.error(request, "Tu carro está vacío.")
                return redirect("carro_compras")

            numero_compra = f"E11-{random.randint(100000, 999999)}"

            if not cliente:
                messages.error(request, "Cliente no válido.")
                return redirect("inicio")

            compra = Compra.objects.create(
                cliente=cliente,
                numero_compra=numero_compra,
                direccion_envio=form_direccion.cleaned_data["direccion"],
                metodo_pago=form_pago.cleaned_data["metodo_pago"],
                estado="Pendiente",
                # El estado de envio por default es "pendiente"
            )

            total = 0
            for item in carro:
                producto = get_object_or_404(Producto, id=item["producto_id"])
                cantidad = item["cantidad"]
                DetalleCompra.objects.create(
                    compra=compra, producto=producto, cantidad=cantidad
                )
                total += producto.precio * cantidad

            total += 3990  # Envío

            # Simulación de pago según método

            if form_pago == "Transferencia":
                messages.success(
                    request,
                    "Te hemos enviado a tu correo registrado los datos de transferencia. Tienes 15 minutos para realizarla, de lo contrario los productos se liberarán.",
                )
            elif form_pago == "GiftCard":
                codigo_giftcard = request.POST.get("codigo_giftcard", "").strip()
                if not codigo_giftcard:
                    messages.error(
                        request, "Debes ingresar un código de GiftCard válido."
                    )
            elif form_pago == "Debito/Credito":
                messages.info(request, "Estamos redirigiéndote a Webpay...")

                messages.success(
                    request,
                    "¡Felicidades! Tu compra se ha realizado con éxito. En unos minutos recibirás en tu correo los datos de la compra.",
                )

            send_mail(
                "Confirmación de compra - E11ven Store",
                f"Tu número de compra es {numero_compra}. Total: ${total}. Dirección: {compra.direccion_envio}",
                "E11venStore@gmail.com",
                [cliente.email],
                fail_silently=True,
            )

            request.session["carro"] = []
            messages.success(request, f"Compra {numero_compra} confirmada ✅")
            return render(
                request, "login_cliente.html", {"compra": compra, "total": total}
            )

    else:
        form_direccion = DireccionEnvioForm()
        form_pago = MetodoPagoForm()

    productos_carro = []
    total = 3990  # Envío

    for item in carro:
        producto = Producto.objects.get(id=item["producto_id"])
        cantidad = item["cantidad"]
        subtotal = producto.precio * cantidad
        total += subtotal
        productos_carro.append(
            {
                "producto": producto,
                "cantidad": cantidad,
                "precio": producto.precio,
                "subtotal": subtotal,
            }
        )

    return render(
        request,
        "carro_compras.html",
        {
            "form_direccion": form_direccion,
            "form_pago": form_pago,
            "productos_carro": productos_carro,
            "total": total,
            "cliente": cliente,
            "cliente_logeado": cliente is not None,
        },
    )


# AGREGAR AL CARRO


@require_POST
def agregar_al_carro(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    cantidad = int(request.POST.get("cantidad", 1))

    carro = request.session.get("carro", [])

    for item in carro:
        if item["producto_id"] == producto.id:
            item["cantidad"] += cantidad
            break
    else:
        carro.append(
            {
                "producto_id": producto.id,
                "cantidad": cantidad,
                "precio": producto.precio,  # Guarda el precio actual
            }
        )

    request.session["carro"] = carro
    messages.success(request, f"{producto.nombre} agregado al carrito.")
    return redirect(request.META.get("HTTP_REFERER", "menu_categorias"))


# PANEL ADMINISTRACION
@admin_login_required
def login_admin(request):
    # Variables para cada pestaña
    productos = Producto.objects.all().order_by("nombre", "categoria")
    compras_recientes = Compra.objects.all().order_by("-fecha")[:10]
    historial = []
    cliente = None

    if request.method == "POST" and "nombre" in request.POST:
        nombre = request.POST.get("nombre")
        descripcion = request.POST.get("descripcion")
        precio = int(request.POST.get("precio"))
        categoria = request.POST.get("categoria")
        stock = int(request.POST.get("stock"))
        imagen = request.POST.get("imagen")

        producto_existente = Producto.objects.filter(
            nombre=nombre, categoria=categoria
        ).first()
        if producto_existente:
            producto_existente.stock += stock
            producto_existente.precio = precio
            if imagen:
                producto_existente.imagen = imagen
            producto_existente.save()
            messages.success(request, "Stock actualizado para producto existente.")
        else:
            Producto.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                precio=precio,
                categoria=categoria,
                stock=stock,
                imagen=imagen,
            )
            messages.success(request, "Producto agregado correctamente.")

    elif request.method == "POST" and "rut" in request.POST:
        rut = request.POST.get("rut")
        try:
            cliente = Cliente.objects.get(rut=rut)
            historial = Compra.objects.filter(cliente=cliente).order_by("-fecha")
        except Cliente.DoesNotExist:
            messages.error(request, "Cliente no encontrado")

    return render(
        request,
        "login_admin.html",
        {
            "productos": productos,
            "compras_recientes": compras_recientes,
            "compras": historial,
            "cliente": cliente,
        },
    )


# ACTUALIZACION DATOS CLIENTES
@cliente_login_required
def login_cliente(request):
    email = request.session.get("email_cliente")

    if not email:
        messages.error(request, "Debes iniciar sesión para acceder.")
        return redirect("inicio_sesion")

    try:
        cliente = Cliente.objects.get(email=email)
    except Cliente.DoesNotExist:
        messages.error(request, "Cliente no encontrado.")
        return redirect("inicio_sesion")

    compras = Compra.objects.filter(cliente=cliente).order_by("-fecha")

    # Calcular totales para cada compra
    compras_con_totales = []
    for compra in compras:
        total = sum(detalle.subtotal() for detalle in compra.detalles.all())
    compras_con_totales.append(
        {
            "compra": compra,
            "total": total,
        }
    )

    if request.method == "POST":
        form = EditarClienteForm(request.POST, instance=cliente)
        pass_form = PasswordChangeForm(user=request.user, data=request.POST)

        if "guardar_datos" in request.POST and form.is_valid():
            form.save()
            messages.success(request, "Datos actualizados correctamente")
        elif "cambiar_contraseña" in request.POST and pass_form.is_valid():
            pass_form.save()
            update_session_auth_hash(request, pass_form.user)
            messages.success(request, "Contraseña actualizada")
        else:
            messages.error(request, "Error al guardar los cambios")
    else:
        form = EditarClienteForm(instance=cliente)
        pass_form = PasswordChangeForm(user=request.user)

    return render(
        request,
        "login_cliente.html",
        {
            "cliente": cliente,
            "compras_con_totales": compras_con_totales,
            "form": form,
            "pass_form": pass_form,
        },
    )


# VISTA DE PAGO POR WEBPAY SIMULADA
@login_required
def redirigir_webpay(request):
    # Simulación: redirigir a una URL de prueba de WebPay
    return redirect("https://webpay3g.transbank.cl/webpay-server/initTransaction")
