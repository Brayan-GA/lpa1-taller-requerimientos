from datetime import datetime, date
from typing import List, Dict, Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
import json

console = Console()

class Hotel:
    def __init__(self, nombre: str, direccion: str, telefono: str, email: str, ubicacion: str):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.ubicacion = ubicacion
        self.descripcion = ""
        self.servicios: List[str] = []
        self.fotos: List[str] = []
        self.ofertas: List[str] = []
        self.estado = "activo"  # activo/inactivo
        self.habitaciones: List[Habitacion] = []
        self.calificaciones: List[int] = []
        self.politica_pago = None
        self.politica_cancelacion = None

    def agregar_habitacion(self, habitacion: 'Habitacion'):
        self.habitaciones.append(habitacion)

    def calcular_calificacion_promedio(self) -> float:
        if not self.calificaciones:
            return 0.0
        return sum(self.calificaciones) / len(self.calificaciones)

    def __str__(self):
        return f"Hotel {self.nombre} en {self.ubicacion}"

class Habitacion:
    def __init__(self, tipo: str, descripcion: str, precio_base: float, capacidad: int, hotel: Hotel):
        self.tipo = tipo
        self.descripcion = descripcion
        self.precio_base = precio_base
        self.capacidad = capacidad
        self.hotel = hotel
        self.servicios: List[str] = []
        self.fotos: List[str] = []
        self.estado = "disponible"  # disponible, ocupada, mantenimiento, limpieza
        self.calendario: Dict[date, str] = {}  # fecha: estado (reservada, disponible)
        self.calificaciones: List[int] = []

    def calcular_precio(self, fecha_inicio: date, fecha_fin: date, temporada: Optional['Temporada'] = None) -> float:
        dias = (fecha_fin - fecha_inicio).days
        precio = self.precio_base * dias
        if temporada:
            precio *= temporada.multiplicador_precio
        return precio

    def esta_disponible(self, fecha_inicio: date, fecha_fin: date) -> bool:
        for dia in range((fecha_fin - fecha_inicio).days):
            fecha = fecha_inicio + timedelta(days=dia)
            if self.calendario.get(fecha, "disponible") != "disponible":
                return False
        return True

    def reservar(self, fecha_inicio: date, fecha_fin: date):
        for dia in range((fecha_fin - fecha_inicio).days):
            fecha = fecha_inicio + timedelta(days=dia)
            self.calendario[fecha] = "reservada"

    def calcular_calificacion_promedio(self) -> float:
        if not self.calificaciones:
            return 0.0
        return sum(self.calificaciones) / len(self.calificaciones)

    def __str__(self):
        return f"Habitación {self.tipo} - {self.descripcion} - ${self.precio_base}/noche"

class Cliente:
    def __init__(self, nombre: str, telefono: str, email: str, direccion: str):
        self.nombre = nombre
        self.telefono = telefono
        self.email = email
        self.direccion = direccion
        self.reservas: List[Reserva] = []

    def agregar_reserva(self, reserva: 'Reserva'):
        self.reservas.append(reserva)

    def __str__(self):
        return f"Cliente {self.nombre}"

class Reserva:
    def __init__(self, cliente: Cliente, habitacion: Habitacion, fecha_inicio: date, fecha_fin: date, precio_total: float):
        self.cliente = cliente
        self.habitacion = habitacion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.precio_total = precio_total
        self.estado = "pendiente"  # pendiente, confirmada, cancelada
        self.pago = False
        self.comentario = ""
        self.calificacion = 0

    def confirmar_pago(self):
        self.pago = True
        self.estado = "confirmada"
        self.habitacion.reservar(self.fecha_inicio, self.fecha_fin)

    def cancelar(self):
        if self.estado == "confirmada":
            # Aplicar política de cancelación
            pass
        self.estado = "cancelada"
        # Liberar fechas
        for dia in range((self.fecha_fin - self.fecha_inicio).days):
            fecha = self.fecha_inicio + timedelta(days=dia)
            if fecha in self.habitacion.calendario:
                del self.habitacion.calendario[fecha]

    def agregar_comentario(self, comentario: str, calificacion: int):
        self.comentario = comentario
        self.calificacion = calificacion
        self.habitacion.calificaciones.append(calificacion)
        self.habitacion.hotel.calificaciones.append(calificacion)

    def __str__(self):
        return f"Reserva de {self.cliente.nombre} en {self.habitacion.hotel.nombre} del {self.fecha_inicio} al {self.fecha_fin}"

class Temporada:
    def __init__(self, nombre: str, fecha_inicio: date, fecha_fin: date, multiplicador_precio: float):
        self.nombre = nombre
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.multiplicador_precio = multiplicador_precio

class SistemaReservas:
    def __init__(self):
        self.hoteles: List[Hotel] = []
        self.clientes: List[Cliente] = []
        self.reservas: List[Reserva] = []
        self.temporadas: List[Temporada] = []

    def agregar_hotel(self, hotel: Hotel):
        self.hoteles.append(hotel)

    def agregar_cliente(self, cliente: Cliente):
        self.clientes.append(cliente)

    def buscar_habitaciones(self, ubicacion: str, fecha_inicio: date, fecha_fin: date, precio_max: float = float('inf'), calificacion_min: float = 0) -> List[Habitacion]:
        habitaciones_disponibles = []
        for hotel in self.hoteles:
            if hotel.estado == "activo" and hotel.ubicacion.lower() == ubicacion.lower() and hotel.calcular_calificacion_promedio() >= calificacion_min:
                for habitacion in hotel.habitaciones:
                    if habitacion.esta_disponible(fecha_inicio, fecha_fin) and habitacion.calcular_precio(fecha_inicio, fecha_fin) <= precio_max:
                        habitaciones_disponibles.append(habitacion)
        return habitaciones_disponibles

    def crear_reserva(self, cliente: Cliente, habitacion: Habitacion, fecha_inicio: date, fecha_fin: date) -> Reserva:
        precio_total = habitacion.calcular_precio(fecha_inicio, fecha_fin)
        reserva = Reserva(cliente, habitacion, fecha_inicio, fecha_fin, precio_total)
        self.reservas.append(reserva)
        cliente.agregar_reserva(reserva)
        return reserva

# Interfaz de usuario con Rich
def menu_principal():
    console.print(Panel.fit("Sistema de Reservas de Hoteles", style="bold blue"))
    console.print("1. Registrar Hotel")
    console.print("2. Agregar Habitación a Hotel")
    console.print("3. Registrar Cliente")
    console.print("4. Buscar Habitaciones")
    console.print("5. Realizar Reserva")
    console.print("6. Confirmar Pago")
    console.print("7. Cancelar Reserva")
    console.print("8. Agregar Comentario y Calificación")
    console.print("9. Ver Hoteles")
    console.print("10. Salir")
    return Prompt.ask("Seleccione una opción", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"])

def main():
    sistema = SistemaReservas()

    # Datos de ejemplo
    hotel1 = Hotel("Hotel Playa", "Calle 1, Playa", "123456", "info@hotelplaya.com", "Playa")
    habitacion1 = Habitacion("Doble", "Habitación con vista al mar", 100, 2, hotel1)
    hotel1.agregar_habitacion(habitacion1)
    sistema.agregar_hotel(hotel1)

    cliente1 = Cliente("Juan Pérez", "987654", "juan@email.com", "Calle 2")
    sistema.agregar_cliente(cliente1)

    while True:
        opcion = menu_principal()
        if opcion == "1":
            nombre = Prompt.ask("Nombre del hotel")
            direccion = Prompt.ask("Dirección")
            telefono = Prompt.ask("Teléfono")
            email = Prompt.ask("Email")
            ubicacion = Prompt.ask("Ubicación")
            hotel = Hotel(nombre, direccion, telefono, email, ubicacion)
            sistema.agregar_hotel(hotel)
            console.print(f"Hotel {nombre} registrado.", style="green")
        elif opcion == "2":
            if not sistema.hoteles:
                console.print("No hay hoteles registrados.", style="red")
                continue
            table = Table("ID", "Nombre")
            for i, h in enumerate(sistema.hoteles):
                table.add_row(str(i), h.nombre)
            console.print(table)
            hotel_id = int(Prompt.ask("Seleccione ID del hotel"))
            hotel = sistema.hoteles[hotel_id]
            tipo = Prompt.ask("Tipo de habitación")
            descripcion = Prompt.ask("Descripción")
            precio = float(Prompt.ask("Precio base"))
            capacidad = int(Prompt.ask("Capacidad"))
            habitacion = Habitacion(tipo, descripcion, precio, capacidad, hotel)
            hotel.agregar_habitacion(habitacion)
            console.print("Habitación agregada.", style="green")
        elif opcion == "3":
            nombre = Prompt.ask("Nombre del cliente")
            telefono = Prompt.ask("Teléfono")
            email = Prompt.ask("Email")
            direccion = Prompt.ask("Dirección")
            cliente = Cliente(nombre, telefono, email, direccion)
            sistema.agregar_cliente(cliente)
            console.print(f"Cliente {nombre} registrado.", style="green")
        elif opcion == "4":
            ubicacion = Prompt.ask("Ubicación")
            fecha_inicio_str = Prompt.ask("Fecha inicio (YYYY-MM-DD)")
            fecha_fin_str = Prompt.ask("Fecha fin (YYYY-MM-DD)")
            fecha_inicio = date.fromisoformat(fecha_inicio_str)
            fecha_fin = date.fromisoformat(fecha_fin_str)
            precio_max = float(Prompt.ask("Precio máximo (opcional)", default=str(float('inf'))))
            calificacion_min = float(Prompt.ask("Calificación mínima (opcional)", default="0"))
            habitaciones = sistema.buscar_habitaciones(ubicacion, fecha_inicio, fecha_fin, precio_max, calificacion_min)
            if habitaciones:
                table = Table("ID", "Hotel", "Tipo", "Descripción", "Precio", "Capacidad", "Calificación")
                for i, h in enumerate(habitaciones):
                    table.add_row(str(i), h.hotel.nombre, h.tipo, h.descripcion, str(h.precio_base), str(h.capacidad), str(h.calcular_calificacion_promedio()))
                console.print(table)
            else:
                console.print("No se encontraron habitaciones.", style="red")
        elif opcion == "5":
            if not sistema.clientes or not sistema.hoteles:
                console.print("Registre clientes y habitaciones primero.", style="red")
                continue
            # Seleccionar cliente
            table = Table("ID", "Nombre")
            for i, c in enumerate(sistema.clientes):
                table.add_row(str(i), c.nombre)
            console.print(table)
            cliente_id = int(Prompt.ask("Seleccione ID del cliente"))
            cliente = sistema.clientes[cliente_id]
            # Buscar habitaciones (reutilizar lógica de búsqueda)
            ubicacion = Prompt.ask("Ubicación")
            fecha_inicio_str = Prompt.ask("Fecha inicio (YYYY-MM-DD)")
            fecha_fin_str = Prompt.ask("Fecha fin (YYYY-MM-DD)")
            fecha_inicio = date.fromisoformat(fecha_inicio_str)
            fecha_fin = date.fromisoformat(fecha_fin_str)
            habitaciones = sistema.buscar_habitaciones(ubicacion, fecha_inicio, fecha_fin)
            if not habitaciones:
                console.print("No hay habitaciones disponibles.", style="red")
                continue
            table = Table("ID", "Hotel", "Tipo", "Precio Total")
            for i, h in enumerate(habitaciones):
                precio = h.calcular_precio(fecha_inicio, fecha_fin)
                table.add_row(str(i), h.hotel.nombre, h.tipo, str(precio))
            console.print(table)
            habitacion_id = int(Prompt.ask("Seleccione ID de la habitación"))
            habitacion = habitaciones[habitacion_id]
            reserva = sistema.crear_reserva(cliente, habitacion, fecha_inicio, fecha_fin)
            console.print(f"Reserva creada: {reserva}", style="green")
        elif opcion == "6":
            if not sistema.reservas:
                console.print("No hay reservas.", style="red")
                continue
            table = Table("ID", "Cliente", "Hotel", "Estado", "Pagada")
            for i, r in enumerate(sistema.reservas):
                table.add_row(str(i), r.cliente.nombre, r.habitacion.hotel.nombre, r.estado, str(r.pago))
            console.print(table)
            reserva_id = int(Prompt.ask("Seleccione ID de la reserva"))
            reserva = sistema.reservas[reserva_id]
            reserva.confirmar_pago()
            console.print("Pago confirmado.", style="green")
        elif opcion == "7":
            if not sistema.reservas:
                console.print("No hay reservas.", style="red")
                continue
            table = Table("ID", "Cliente", "Hotel", "Estado")
            for i, r in enumerate(sistema.reservas):
                table.add_row(str(i), r.cliente.nombre, r.habitacion.hotel.nombre, r.estado)
            console.print(table)
            reserva_id = int(Prompt.ask("Seleccione ID de la reserva"))
            reserva = sistema.reservas[reserva_id]
            reserva.cancelar()
            console.print("Reserva cancelada.", style="green")
        elif opcion == "8":
            if not sistema.reservas:
                console.print("No hay reservas.", style="red")
                continue
            table = Table("ID", "Cliente", "Hotel", "Estado")
            for i, r in enumerate(sistema.reservas):
                table.add_row(str(i), r.cliente.nombre, r.habitacion.hotel.nombre, r.estado)
            console.print(table)
            reserva_id = int(Prompt.ask("Seleccione ID de la reserva"))
            reserva = sistema.reservas[reserva_id]
            comentario = Prompt.ask("Comentario")
            calificacion = int(Prompt.ask("Calificación (1-5)", choices=["1", "2", "3", "4", "5"]))
            reserva.agregar_comentario(comentario, calificacion)
            console.print("Comentario agregado.", style="green")
        elif opcion == "9":
            if not sistema.hoteles:
                console.print("No hay hoteles.", style="red")
                continue
            table = Table("Nombre", "Ubicación", "Estado", "Calificación")
            for h in sistema.hoteles:
                table.add_row(h.nombre, h.ubicacion, h.estado, str(h.calcular_calificacion_promedio()))
            console.print(table)
        elif opcion == "10":
            break

if __name__ == "__main__":
    from datetime import timedelta  # Necesario para timedelta
    main()

