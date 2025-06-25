import argparse
import random

def main():
    parser = argparse.ArgumentParser(description="Simulador de una cola M/M/1/K")

    parser.add_argument('--lambda', dest='lmbda', type=float, required=True, help='Tasa de llegada de clientes (λ)')
    parser.add_argument('--mu', type=float, required=True, help='Tasa de servicio del servidor (μ)')
    parser.add_argument('--K', type=int, required=True, help='Capacidad máxima del sistema')
    parser.add_argument('--arriendo', type=float, required=True, help='Costo de arriendo por puesto en la cola')
    parser.add_argument('--cobro', type=float, required=True, help='Cobro por cliente atendido')
    parser.add_argument('--clientes', type=int, required=True, help='Número de clientes a atender')

    args = parser.parse_args()

    # Verificación básica
    if args.lmbda <= 0 or args.mu <= 0 or args.K <= 0 or args.arriendo < 0 or args.cobro < 0 or args.clientes <= 0:
        print("Todos los valores deben ser positivos. El arriendo y cobro pueden ser cero.")
        return

    # Imprimir los argumentos (opcionalmente para pruebas)
    print("Parámetros de entrada:")
    print(f"λ = {args.lmbda}, μ = {args.mu}, K = {args.K}, arriendo = {args.arriendo}, cobro = {args.cobro}, clientes = {args.clientes}")

    # Variables del sistema
    tiempo_actual = 0.0
    proxima_llegada = random.expovariate(args.lmbda)
    proxima_salida = float('inf')  # No hay salida programada al inicio

    # Estado del sistema
    num_en_sistema = 0  # incluye servidor + cola
    clientes_atendidos = 0
    clientes_rechazados = 0
    tiempo_ocupado_servidor = 0.0
    tiempo_anterior = 0.0

    # Para calcular el largo promedio de la cola
    area_bajo_cola = 0.0

    def manejar_llegada():
        nonlocal num_en_sistema, proxima_llegada, proxima_salida, tiempo_actual, clientes_rechazados, tiempo_ocupado_servidor

        if num_en_sistema >= args.K:
            # Sistema lleno → el cliente se va
            clientes_rechazados += 1
        else:
            if num_en_sistema == 0:
                # Servidor libre → atiende directamente
                tiempo_servicio = random.expovariate(args.mu)
                proxima_salida = tiempo_actual + tiempo_servicio
                tiempo_ocupado_servidor += tiempo_servicio
            # En cualquier caso, el cliente entra al sistema (servido o espera)
            num_en_sistema += 1

        # Programar próxima llegada
        proxima_llegada = tiempo_actual + random.expovariate(args.lmbda)

    def actualizar_area_bajo_cola():
        nonlocal area_bajo_cola, tiempo_actual, tiempo_anterior, num_en_sistema
        # Cola = num_en_sistema - 1 (excepto cuando sistema está vacío)
        cola_actual = max(0, num_en_sistema - 1)
        area_bajo_cola += cola_actual * (tiempo_actual - tiempo_anterior)
        tiempo_anterior = tiempo_actual

        
    def manejar_salida():
        nonlocal num_en_sistema, proxima_salida, clientes_atendidos, tiempo_actual, tiempo_ocupado_servidor

        clientes_atendidos += 1
        num_en_sistema -= 1  # Se va un cliente (sale del sistema)

        if num_en_sistema > 0:
            # Aún hay alguien esperando → servir al siguiente
            tiempo_servicio = random.expovariate(args.mu)
            proxima_salida = tiempo_actual + tiempo_servicio
            tiempo_ocupado_servidor += tiempo_servicio
        else:
            # Nadie más en el sistema → servidor inactivo
            proxima_salida = float('inf')
            
    
    while clientes_atendidos < args.clientes:
        if proxima_llegada < proxima_salida:
            # El siguiente evento es una llegada
            tiempo_actual = proxima_llegada
            actualizar_area_bajo_cola()
            manejar_llegada()
        else:
            # El siguiente evento es una salida
            tiempo_actual = proxima_salida
            actualizar_area_bajo_cola()
            manejar_salida()
            
    tiempo_total = tiempo_actual  # Tiempo de simulación

    # 1. Utilización del servidor
    utilizacion_simulada = 100 * tiempo_ocupado_servidor / tiempo_total

    # 2. Tasa efectiva de arribos
    tasa_efectiva_simulada = (clientes_atendidos) / tiempo_total

    # 3. Largo promedio de la cola
    largo_promedio_cola_simulado = area_bajo_cola / tiempo_total

    # 4. Ganancia total
    puestos_en_uso = args.K - 1  # Solo se cobra arriendo por la cola (no el servidor)
    costo_total_arriendo = puestos_en_uso * args.arriendo
    ganancia_total = clientes_atendidos * args.cobro - costo_total_arriendo

    # Cálculos teóricos (para comparación)
    rho = args.lmbda / args.mu
    if rho == 1:
        pi_0 = 1 / (args.K + 1)
    else:
        pi_0 = (1 - rho) / (1 - rho**(args.K + 1))

    pi_K = (rho ** args.K) * pi_0

    utilizacion_teorica = 100 * (1 - pi_K)
    tasa_efectiva_teorica = args.lmbda * (1 - pi_K)
    largo_promedio_teorico = rho * (1 - (args.K + 1) * rho**args.K + args.K * rho**(args.K + 1)) / ((1 - rho) * (1 - rho**(args.K + 1))) if rho != 1 else args.K / 2

    # Formato de salida
    print(f"Utilización: {utilizacion_simulada:.1f}% {utilizacion_teorica:.1f}%")
    print(f"Tasa efectiva de arrivos: {tasa_efectiva_simulada:.1f} {tasa_efectiva_teorica:.1f}")
    print(f"Largo promedio de la cola: {largo_promedio_cola_simulado:.1f} {largo_promedio_teorico:.1f}")
    print(f"Ganancia total: ${int(ganancia_total)}")





if __name__ == "__main__":
    main()
    
    
