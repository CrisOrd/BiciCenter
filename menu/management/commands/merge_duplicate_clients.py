from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count
from menu.models import Cliente, BicicletaCliente, OrdenMantenimiento

class Command(BaseCommand):
    help = 'Detecta y consolida clientes duplicados por email. Usa el cliente más completo como primario.'

    def handle(self, *args, **options):
        duplicates = (
            Cliente.objects.values('email')
            .annotate(cnt=Count('id'))
            .filter(email__isnull=False)
            .filter(email__gt='')
            .filter(cnt__gt=1)
        )

        if not duplicates:
            self.stdout.write(self.style.SUCCESS('No se encontraron emails duplicados.'))
            return

        for row in duplicates:
            email = row['email']
            clients = Cliente.objects.filter(email=email).order_by('fecha_registro')
            primary = clients.first()
            others = clients.exclude(id=primary.id)

            self.stdout.write(f'Consolidando email={email}: {clients.count()} registros -> primario id={primary.id}')

            with transaction.atomic():
                for other in others:
                    changed = False
                    if not primary.rut and other.rut:
                        primary.rut = other.rut
                        changed = True
                    if (not primary.nombre or primary.nombre.strip()=="") and other.nombre:
                        primary.nombre = other.nombre
                        changed = True
                    if (not primary.apellido or primary.apellido.strip()=="") and other.apellido:
                        primary.apellido = other.apellido
                        changed = True
                    if changed:
                        primary.save()

                    BicicletaCliente.objects.filter(cliente=other).update(cliente=primary)
                    OrdenMantenimiento.objects.filter(cliente=other).update(cliente=primary)

                    other.delete()

                self.stdout.write(self.style.SUCCESS(f'Email {email} consolidado.'))
        self.stdout.write(self.style.SUCCESS('Consolidación completada.'))
