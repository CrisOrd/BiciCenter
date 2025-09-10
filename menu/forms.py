from django import forms
from .models import Bicicleta, Accesorio, Repuesto

class BicicletaForm(forms.ModelForm):
    class Meta:
        model = Bicicleta
        fields = ['nombre', 'descripcion', 'precio', 'tipo', 'marca', 'modelo', 'color', 'imagen', 'stock']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la bicicleta'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del producto'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marca'
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modelo'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Color'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            })
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'precio': 'Precio (CLP)',
            'tipo': 'Tipo de Bicicleta',
            'marca': 'Marca',
            'modelo': 'Modelo',
            'color': 'Color',
            'imagen': 'Imagen',
            'stock': 'Stock Disponible'
        }

class AccesorioForm(forms.ModelForm):
    class Meta:
        model = Accesorio
        fields = ['nombre', 'descripcion', 'precio', 'categoria', 'marca', 'imagen', 'stock']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del accesorio'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del producto'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marca'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            })
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'precio': 'Precio (CLP)',
            'categoria': 'Categoría',
            'marca': 'Marca',
            'imagen': 'Imagen',
            'stock': 'Stock Disponible'
        }

class RepuestoForm(forms.ModelForm):
    class Meta:
        model = Repuesto
        fields = ['nombre', 'descripcion', 'precio', 'categoria', 'marca', 'numero_parte', 'compatibilidad', 'imagen', 'stock']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del repuesto'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del producto'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marca'
            }),
            'numero_parte': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de parte'
            }),
            'compatibilidad': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Describe la compatibilidad con bicicletas'
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            })
        }
        labels = {
            'nombre': 'Nombre',
            'descripcion': 'Descripción',
            'precio': 'Precio (CLP)',
            'categoria': 'Categoría',
            'marca': 'Marca',
            'numero_parte': 'Número de Parte',
            'compatibilidad': 'Compatibilidad',
            'imagen': 'Imagen',
            'stock': 'Stock Disponible'
        }