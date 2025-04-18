from django.contrib import admin
from .models import Cliente
from .models import Administrativo
from .models import Producto, DetalleCompra, Compra
from django.utils.html import format_html


class clienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidos', 'rut', 'email',)
    search_fields = ('nombre','apellidos', 'rut',)
 
    
class AdministrativoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellidos', 'rut', 'email',)
    search_fields = ('nombre','apellidos', 'rut',)

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'imagen_preview')
    search_fields = ('nombre', 'categoria')
    list_filter = ('categoria',)

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" width="60" style="border-radius: 5px;" />', obj.imagen.url)
        return "Sin imagen"
    imagen_preview.short_description = 'Vista previa'

admin.site.register(Producto, ProductoAdmin)
admin.site.register(Cliente, clienteAdmin)
admin.site.register(Administrativo, AdministrativoAdmin)
admin.site.register(DetalleCompra)
admin.site.register(Compra)
