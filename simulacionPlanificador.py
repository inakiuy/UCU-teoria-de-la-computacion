#!/usr/bin/env python3
from collections import deque
import random

MAX_SERVICELIST_SIZE = 4    # Maxima canitad de particiones realizadas al tiempo de servicio
MAX_SERVICETIME = 400       # Maximo Tiempo de Servicio de una tarea
MAX_TIMEOUT = 150           # Maximo Tiempo de Timeout de una tarea
SETS = 1                    # Cantidad de sets generados
TASKS_CREATED = 10          # Cantidad de tareas creadas por cada set
DIA_TRABAJO = 1000          # Cuantos ciclos dura un dia de trabajo
MAX_TIME = 500              # Cuantos ciclos dura la simulacion
ALGO = "fcfs"               # Algoritmo de planificacion FirstComeFirstServe
#ALGO = "sjf"               # Algoritmo de planificacion ShortesJobFirst
INTERVALO_LOG = 500         # Cada cuantos ciclos imprimir log


class Tarea:
    """ Clase tarea """
    ### Constructor
    def __init__(self, pname, pserviceTime, ppriority, purgency, ptimeOut, ptaskType):
        # Propiedades basicas
        self.name = pname
        self.serviceTime = pserviceTime
        self.serviceList = Tarea.randomServiceList(pserviceTime)
        self.priority = int(ppriority * purgency)
        self.timeOut = ptimeOut
        self.taskType = ptaskType
        # Propiedades estadisticas
        self.startTime = None
        self.finishTime = None
        self.waitingTime = 0
        self.workDone = 0
        self.waitingQueueArriveTime = None
        self.serviceListCopy = self.serviceList.copy()

    ### Particiona de forma aleatoria un tiempo de servicio
    ### para simular tareas que necesitan espera    
    def randomServiceList(pserviceTime):
        list_size = random.randrange(1,MAX_SERVICELIST_SIZE)                
        lista = deque(maxlen=list_size)
        position = 0
        # print(f'Tamanio lista: {list_size}')
        for i in range(list_size - 1 ):
            partition = random.randrange(position, pserviceTime)
            # print(f'Loop: {i}, Posicion: {position}, Particion: {partition}, PserviceTime: {pserviceTime}')
            time = partition - position
            if (time != 0):
                lista.append(time)
            position = partition
        lista.append(pserviceTime - position) 
        # print(f'Ver lista: {lista}')
        return lista
    
    ### Generador de tareas aleatorias
    def createRandomList(n_val):
        task_list = []
        for n in range(n_val):
            serviceTime = random.randint(1,MAX_SERVICETIME)
            priority = random.randint(0,5)
            urgency = random.random() # random entre 0 y 1
            timeout = random.randint(1,MAX_TIMEOUT) # Si no se ejecuta se da por no completada
            tasktype = random.randrange(0,5) # Simulamos 5 tipos de tareas
            task = Tarea(n, serviceTime, priority, urgency, timeout, tasktype)
            
            task_list.append(task)
        #print("Set de tareas generado correctamente")
        return task_list

    ### Imprime estadisticas de forma legible
    def prettyStats(self):
        print(f'Tarea: {self.name}\n\tstart: {self.startTime}\n\tfinish: {self.finishTime}\n\twaiting: {self.waitingTime}\n\twork: {self.workDone}\n\tserviceList: {list(self.serviceListCopy)}')

    ### Imprime estadisticas crudas
    def rawStats(self):
        print(f'{self.name};{self.startTime};{self.finishTime};{self.waitingTime};{self.workDone};{list(self.serviceListCopy)}')

    ### Representacion de la tarea como string
    def __repr__(self):
        return f'\n{{name: {self.name}, time: {self.serviceTime}, serviceList: {self.serviceList}, startTime: {self.startTime}, finishTime: {self.finishTime}, waitingTime: {self.waitingTime}, workDone: {self.workDone}, serviceListCopy: {list(self.serviceListCopy)}}}\n'
        #return f'\n{{name: {self.name}, time: {self.serviceTime}, serviceList: {self.serviceList}, priority: {self.priority}, timeout: {self.timeOut}, tasktype: {self.taskType}}}\n'



class Planificador:
    """ Cola de tareas """
    ### Constructor
    def __init__(self, ALGO):
        self.algorithm = ALGO
        self.planQueue = deque(maxlen=TASKS_CREATED)
        self.waitingQueue = deque(maxlen=TASKS_CREATED)
        self.finishedQueue = deque(maxlen=TASKS_CREATED)

    ### Poner una tarea en la cola de planificacion
    def putTaskPlanQueue(self, task):
        if (self.algorithm == "fcfs"):
            # FCFS
            self.fcfs(task)
        elif (self.algorithm == "sjf"):
            # SJF
            self.sjf(task)
        else:
            raise Exception("Planificador no selecionado. Revise la constante ALGO")

        # print(f'Tarea agregada: {task}')

    ### Entregar una tarea al usuario dede la cola de planificados
    def getTaskPlanQueue(self):
        return self.planQueue.popleft() if (self.planQueue) else None

    ### Poner una tarea en la cola de espera
    def putTaskWaitingQueue(self, task, time):
        task.waitingQueueArriveTime = time
        self.waitingQueue.append(task)
        return 0

    ### Eliminar una determinada tarea en la cola de espera
    def removeTaskWaitingQueue(self, task):
        self.waitingQueue.remove(task)
        return 0

    ### Poner una tarea en la cola de finalizados
    def putTaskFinishedQueue(self, task, time):
        task.finishTime = time
        self.finishedQueue.append(task)
        return 0

    ### Imprimir todas las tareas en la cola
    def printTasks(self):
        print(f'Cola de tareas: {self.planQueue}')
        return 0

    ### Agregar tareas a la cola de planificacion
    def addTasks(self, task_list, time):
        for task in task_list:
            task.startTime = time
            self.putTaskPlanQueue(task)
        return 0
    
    ### Algoritmo FCFS
    def fcfs(self, task):
        self.planQueue.append(task)

    ### Algoritmo SJF
    def sjf(self, task):
        serviceTime = task.serviceTime
        queueList = list(self.planQueue)
        i = 0
        try: 
            while (queueList[i].serviceTime < serviceTime):
                i += 1              
            self.planQueue.insert(i, task)
        except:
            self.planQueue.append(task)   

    # Replanificardor: Avanza el tiempo en 1 y las tareas que yas terminaron
    # de esperar las mueve a la cola planQueue
    def schedule(self, time):
        #Necesaria por que no puedo modificar las colas mientras itero sobre ellas
        tempList = []

        # Si hay tareas esperando que ya cumplieron el tiempo de espera
        # y que tienen ciclos de trabajo pendientes, pasarlas nuevamente
        # a la cola de planificación
        if (self.waitingQueue): # Si no esta vacia
            for tarea in self.waitingQueue:
                if (tarea.serviceList): # Si aun le quedan operaciones por hacer
                    timeWaited = time - tarea.waitingQueueArriveTime
                    timeToWait = tarea.serviceList[0]
                    if (timeWaited >= timeToWait):
                        tarea.serviceList.popleft()
                        if (tarea.serviceList): # Si le quedan operaciones
                            # Pasa a planificado
                            #print("Tiene operaciones, pasa a planificador")
                            tempList.append(tarea)
                            self.putTaskPlanQueue(tarea)
                        else:
                            # Pasa a finalizado
                            tempList.append(tarea)
                            #print("Ya no tiene operaciones, pasa a finalizado")
                            self.putTaskFinishedQueue(tarea, time)
                else:
                    print('No debería estar aca')

            # Elimino las tareas de la cola de espera
            for tarea in tempList:
                self.removeTaskWaitingQueue(tarea)
        
        # A todas las tareas que están planificadas y no se avanzaron
        # sumarle al waitingTime para estadisticas
        if (self.planQueue):
            for tarea in self.planQueue:
                tarea.waitingTime += 1


    ### Imprimir de forma legible para humanos las estadisticas de la tareas
    def prettyPrintStatistics(self):
        print(f'\nCOLA TAREAS PLANIFICADAS')
        if (self.planQueue):
            for tarea in self.planQueue:
                tarea.prettyStats()
        else:
            print(f'No quedaron tareas en esta cola')

        print(f'\nCOLA TAREAS ESPERANDO')
        if (self.waitingQueue):
            for tarea in self.waitingQueue:
                tarea.prettyStats()
        else:
            print(f'No quedaron tareas en esta cola')

        print(f'\nCOLA TAREAS FINALIZADAS')
        if (self.finishedQueue):
            for tarea in self.finishedQueue:
                tarea.prettyStats()
        else:
            print(f'No quedaron tareas en esta cola')

    ### Imprimir de forma legible para humanos las estadisticas de la tareas
    def rawPrintStatistics(self):
        print(f'\nCOLA TAREAS PLANIFICADAS')
        print(f'name;startTime;finishTime;waitingTime;workDone;serviceListCopy;')
        if (self.planQueue):
            for tarea in self.planQueue:
                tarea.rawStats()
        else:
            print(f'No quedaron tareas en esta cola')

        print(f'\nCOLA TAREAS ESPERANDO')
        print(f'name;startTime;finishTime;waitingTime;workDone;serviceListCopy;')
        if (self.waitingQueue):
            for tarea in self.waitingQueue:
                tarea.rawStats()
        else:
            print(f'No quedaron tareas en esta cola')

        print(f'\nCOLA TAREAS FINALIZADAS')
        print(f'name;startTime;finishTime;waitingTime;workDone;serviceListCopy;')
        if (self.finishedQueue):
            for tarea in self.finishedQueue:
                tarea.rawStats()
        else:
            print(f'No quedaron tareas en esta cola')



class Persona:
    """ Clase Persona que realiza trabajos """
    # Constructor
    def __init__(self, pname):
        self.name = pname
        self.task = None
    
    # Realizar tarea
    def work(self):
        self.task.workDone += 1


def main():
    """ Tests de planificación """
    print("Generamos set de pruebas 1")
    set1_tareas = Tarea.createRandomList(TASKS_CREATED)
    # print(f'Set 1: {set1_tareas}')

    print(f'Tests de planificación {ALGO}')
    planFCFS = Planificador(ALGO)
    planFCFS.addTasks(set1_tareas, 0)
    planFCFS.printTasks()

    trabajador = Persona("Trabajador 1")
    tarea = planFCFS.getTaskPlanQueue()
    trabajador.task = tarea
    workToBeDone = tarea.serviceList.popleft()

    # SIMULACION DE TIEMPO
    for time in range(MAX_TIME):
        if ( time % INTERVALO_LOG == 0):
            print(f'\n///////////////////////////////// Tiempo: {time} /////////////////////////////////')
            print(f'Trabajador trabajando en: {trabajador.task}')
        
        if (trabajador.task != None):
            # Teniendo una tarea asignada
            if ( tarea.workDone < workToBeDone ): # Si el trabajo realizado es menor al necesario, trabajar
                trabajador.work()
            elif (not tarea.serviceList): # Si en la lista de trabajo NO hay trabajo, pasa a cola de finalizado
                trabajador.task = None
                planFCFS.putTaskFinishedQueue(tarea, time)
            else:
                trabajador.task = None
                planFCFS.putTaskWaitingQueue(tarea, time)

        # Si no estamos trabajando en una tarea y aun quedan tareas
        # en la cola de planQueue obtener una
        if (trabajador.task == None and planFCFS.planQueue):
            tarea = planFCFS.getTaskPlanQueue()
            trabajador.task = tarea
            workToBeDone = tarea.serviceList.popleft()
            trabajador.work()

        # Vemos el estado de las colas cada 100 tick del reloj
        if ( time % INTERVALO_LOG == 0 ):
            print(f'FinCiclo-PlanQ: {planFCFS.planQueue}\n-------------------------')
            print(f'FinCiclo-WaitQ: {planFCFS.waitingQueue}\n-------------------------')
            print(f'FinCiclo-FiniQ: {planFCFS.finishedQueue}\n-------------------------')

        # Reprogramamos tareas
        planFCFS.schedule(time)
    
    print(f'\n--------------- FIN DEL TIEMPO SIMULADO ---------------')
    print(f'FIN-PlanQ: {planFCFS.planQueue}\n-------------------------')
    print(f'FIN-WaitQ: {planFCFS.waitingQueue}\n-------------------------')
    print(f'FIN-FiniQ: {planFCFS.finishedQueue}\n-------------------------')

    print(f'\n--------------- ESTADISTICAS PRETTY ---------------')
    planFCFS.prettyPrintStatistics()

    print(f'\n--------------- ESTADISTICAS RAW ---------------')
    planFCFS.rawPrintStatistics()


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()