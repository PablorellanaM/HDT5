import simpy
import random
import matplotlib.pyplot as plt

# Configuración inicial
SEED_ALEATORIA = 42
random.seed(SEED_ALEATORIA)
INSTRUCCIONES_POR_UNIDAD_CPU = 3
CAPACIDAD_RAM_INICIAL = 100
INTERVALO_GENERACION_PROCESOS = 10
TIEMPO_SIMULACION = 1000
NUMERO_PROCESOS = [25, 50, 100, 150, 200]

tiempos_procesos = []

def proceso(env, nombre, cpu, ram, memoria_necesaria, instrucciones):
    global tiempos_procesos
    tiempo_llegada = env.now
    with ram.get(memoria_necesaria) as solicitud:
        yield solicitud
        with cpu.request() as req:
            yield req
            instrucciones_restantes = instrucciones
            while instrucciones_restantes > 0:
                yield env.timeout(1)
                instrucciones_restantes -= INSTRUCCIONES_POR_UNIDAD_CPU
            tiempo_proceso = env.now - tiempo_llegada
            tiempos_procesos.append(tiempo_proceso)

def generador_procesos(env, cpu, ram, num_procesos):
    for i in range(num_procesos):
        memoria_necesaria = random.randint(1, 10)
        instrucciones = random.randint(1, 10)
        env.process(proceso(env, f'Proceso {i}', cpu, ram, memoria_necesaria, instrucciones))
        t = random.expovariate(1.0 / INTERVALO_GENERACION_PROCESOS)
        yield env.timeout(t)

def ejecutar_simulacion(num_procesos):
    global tiempos_procesos
    tiempos_procesos = []
    env = simpy.Environment()
    cpu = simpy.Resource(env, capacity=1)
    ram = simpy.Container(env, init=CAPACIDAD_RAM_INICIAL, capacity=CAPACIDAD_RAM_INICIAL)
    env.process(generador_procesos(env, cpu, ram, num_procesos))
    env.run(until=TIEMPO_SIMULACION)
    tiempo_medio = sum(tiempos_procesos) / len(tiempos_procesos) if tiempos_procesos else 0
    return tiempo_medio, tiempos_procesos

for num_procesos in NUMERO_PROCESOS:
    tiempo_medio, _ = ejecutar_simulacion(num_procesos)
    plt.figure()
    plt.hist(tiempos_procesos, bins=20, alpha=0.75)
    plt.title(f'Histograma de Tiempos - {num_procesos} Procesos')
    plt.xlabel('Tiempo en el Sistema')
    plt.ylabel('Frecuencia')
    plt.savefig(f'histograma_{num_procesos}_procesos.png')
    plt.close()

print("Las gráficas han sido generadas y guardadas.")
