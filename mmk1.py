#Autores
#---Thomas Riffo 21134817-8
#---Isidora Oyanedel 21168603-0

#Hecho con python 3.7

#Importamos las librerias necesarias
import argparse
import random

#Definimos el main
def main():
    
    #Vamos a obtener los argumentos con el metodo argparse
    parser = argparse.ArgumentParser(description="Simulador de M/M/1/K")
    
    #Conseguimos los argumentos necesarios
    parser.add_argument('--lambda', dest='lmbda', type=float, required=True)
    parser.add_argument('--mu', type=float, required=True)
    parser.add_argument('--K', type=float, required=True)
    parser.add_argument('--clientes', type=float, required=True)
    parser.add_argument('--arriendo', type=float, required=True)
    parser.add_argument('--cobro', type=float, required=True)

    args = parser.parse_args()
    
    #Verificación inicial de los argumentos
    if args.lmbda <= 0 or args.mu <= 0 or args.K <= 0 or args.clientes <= 0 or args.arriendo < 0 or args.cobro < 0:
        print("Todos los valores deben ser positivos. El arriendo y cobro pueden ser cero.")
        return
    
    #Variables para que el sistema funcione
    tiempoActual = 0.0
    proximaLlegada = random.expovariate(args.lmbda)
    proximaSalida = float('inf')  #Aun no hay una salida programada al inicio
    
    #Estado del sistema
    numEnSistema = 0  # incluye servidor + cola
    clientesAtendidos = 0
    clientesRechazados = 0
    tiempoOcupadoServidor = 0.0
    tiempoAnterior = 0.0
    
    #Para calcular la cola
    areaBajoCola = 0.0
    
#--------------------- DEFINIMOS LAS FUNCIONES ---------------------#
    
    #Definimos la función de llegada de clientes
    def ManejarLlegada():
        #Definimos las variables que vamos a usar
        nonlocal numEnSistema, proximaLlegada, proximaSalida, tiempoActual, clientesRechazados, tiempoOcupadoServidor
        
        #Vamos a seguir los pasos del diagrama
        if numEnSistema >= args.K: #Si el sistema está lleno
            clientesRechazados += 1
            
        else:
            if numEnSistema == 0: #Si no hay nadie atendiendose
                tiempoServicio = random.expovariate(args.mu)
                proximaSalida = tiempoActual + tiempoServicio
                tiempoOcupadoServidor += tiempoServicio

            #Sino, entonces guardamos un cliente más al sistema
            numEnSistema += 1
        
        #Definimos la proxima llegada
        proximaLlegada = tiempoActual + random.expovariate(args.lmbda)
        
    #Definimos la función de salida de clientes
    def manejarSalida():
        #Definimos las variables que se van a usar
        nonlocal numEnSistema, proximaLlegada, proximaSalida, tiempoActual, tiempoOcupadoServidor, clientesAtendidos

        #Como entramos a la función de salida, entonces el servidor atendio a un cliente
        clientesAtendidos += 1
        numEnSistema -= 1
        
        #Preguntamos si hay almenos un cliente en el sistema
        if numEnSistema > 0:
            #Si hay almenos un cliente, entonces programamos la proxima salida
            tiempoServicio = random.expovariate(args.mu)
            proximaSalida = tiempoActual + tiempoServicio
            tiempoOcupadoServidor += tiempoServicio
        
        #Si no hay nadie en el sistema, entonces no hay proxima salida    
        else: 
            proximaSalida = float('inf')
        
    #Definimos la función para conseguir estadisticas    
    def actualizarAreaBajoCola():
        #Definimos las variables que vamos a usar
        nonlocal areaBajoCola, tiempoActual, tiempoAnterior, numEnSistema
        
        #La cola en el sistema sera siempre la cantidad de clientes menos 1
        colaActual = max(0, numEnSistema - 1) 
        
        #Conseguimos el area bajo la cola
        areaBajoCola += colaActual * (tiempoActual - tiempoAnterior)
        tiempoAnterior = tiempoActual
        
    #Obtenemos la utilización simulada del sistema
    def getUtilizacion():
        return 100 * tiempoOcupadoServidor / tiempoTotal
    
    #Obtenemos la tasa efectiva simulada
    def getTasaEfectivaSimulada():
        return (clientesAtendidos) / tiempoTotal
        
    #Obtenemos el largo promedio de la cola
    def getLargoPromedioColaSimulada():
        return areaBajoCola / tiempoTotal
        
#--------------------- Iniciamos la simulación ---------------------#
        
    #Wait principal para el funcionamiento del codigo
    while clientesAtendidos < args.clientes:
        
        #Preguntamos si viene una llegada o una salida
        if proximaLlegada < proximaSalida:
            #El siguiente evento es una llegada
            tiempoActual = proximaLlegada
            actualizarAreaBajoCola()
            ManejarLlegada()
            
        #Si la salida viene antes que la llegada
        else:
            #El siguiente evento es una salida
            tiempoActual = proximaSalida
            actualizarAreaBajoCola()
            manejarSalida()
            
    #Tiempo simulado
    tiempoTotal = tiempoActual
    
#--------------------- Conseguimos los datos que nos piden ---------------------#
    
    #la utilización, pero simulada 
    utilizacionSimulada = getUtilizacion()
    
    #Conseguimos la tasa efectiva de arribos
    tasaEfectivaSimulada = getTasaEfectivaSimulada()
    
    #Largo promedio de la cola
    largoPromedioColaSimulada = getLargoPromedioColaSimulada()
    
    #Ganancia total del sistema
    puestosEnUso = args.K - 1
    costoTotalArriendo = puestosEnUso * args.arriendo
    gananciaTotal = clientesAtendidos * args.cobro - costoTotalArriendo
        
#--------------------- Realizamos calculos teoricos ---------------------#
    rho = args.lmbda / args.mu
    if rho == 1:
        #Usamos limites para que tienda a 1 y no se indetermine
        pi_0 = 1 / (args.K + 1)
        
        #Vamos a conseguir la cola
        L = args.K / 2
    else:
        #Metodo para conseguir pi_0 y conseguir la utilización
        pi_0 = (1 - rho) / (1 - rho**(args.K + 1))
        
        #Vamos a calular la cola, pero lo vamos hacer por parte para que sea más facil.
        denominador =  ((1 - rho) * (1- rho**(args.K + 1)))
        numerador = rho * (1-(args.K + 1) * rho**args.K + args.K * rho**(args.K + 1)) 
        L = numerador/denominador 

    #Calculamos pi_k
    pi_K = (rho ** args.K) * pi_0

    #Utilización teórica y tasa efectiva de arribos
    utilizacionTeorica = 100 * (1 - pi_0)
    tasaEfectivaTeorica = args.lmbda * (1 - pi_K)
    
    #Consegimos los calculos de la cola
    largoPromedioCola = L - (1 - pi_0)
    
    #Imprimimos los resultados
    print(f"Utilización: {utilizacionSimulada:.1f}% {utilizacionTeorica:.1f}%")
    print(f"Tasa efectiva de arribos: {tasaEfectivaSimulada:.1f} {tasaEfectivaTeorica:.1f}")
    print(f"Largo promedio de la cola: {largoPromedioColaSimulada:.1f} {largoPromedioCola:.1f}")
    print(f"Ganancia total: ${int(gananciaTotal)}")
    
if __name__ == "__main__":
    main()
    