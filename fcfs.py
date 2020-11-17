#!/usr/bin/env python3
from collections import deque
import random

MAX_SERVICELIST_SIZE = 4
MAX_SERVICETIME = 10
MAX_TIMEOUT = 150
TASKS_CREATED = 2
MAX_TIME = 21
FLAG = True


class Tarea:
    """ Clase tarea """
    # Constructor
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

    # Representacion de la tarea como string
    def __repr__(self):
        return f'\n{{name: {self.name}, time: {self.serviceTime}, serviceList: {self.serviceList}, priority: {self.priority}, timeout: {self.timeOut}, tasktype: {self.taskType}}}\n'
        #return f'{{\n name: {self.name},\n time: {self.serviceTime},\n serviceList: {self.serviceList},\n priority: {self.priority},\n timeout: {self.timeOut},\n tasktype: {self.taskType}\n}}'

    # # Definimios como comparar si son o no la misma tarea
    # def __eq__(self, other):
    #     return self.name == other.name


class Planificador:
    """ Cola de tareas """
    # Constructor
    def __init__(self, flag):
        self.flag = flag
        self.planQueue = deque(maxlen=TASKS_CREATED)
        self.planList = deque(maxlen=TASKS_CREATED)
        self.waitingQueue = deque(maxlen=TASKS_CREATED)
        self.finishedQueue = deque(maxlen=TASKS_CREATED)

    # Poner una tarea en la cola de planificacion
    def putTaskPlanQueue(self, task):
        if (self.flag):
            # FCFS
            self.planQueue.append(task)
        else:
            # SJF
            pass


        # print(f'Tarea agregada: {task}')

    # Entregar una tarea al usuario dede la cola de planificados
    def getTaskPlanQueue(self):
        return self.planQueue.popleft() if (self.planQueue) else None

    # Poner una tarea en la cola de espera
    def putTaskWaitingQueue(self, task, time):
        task.waitingQueueArriveTime = time
        self.waitingQueue.append(task)
        return 0

    # Eliminar una determinada tarea en la cola de espera
    def removeTaskWaitingQueue(self, task):
        self.waitingQueue.remove(task)
        return 0

    # Poner una tarea en la cola de finalizados
    def putTaskFinishedQueue(self, task, time):
        task.finishTime = time
        self.finishedQueue.append(task)
        return 0

    # Imprimir todas las tareas en la cola
    def printTasks(self):
        print(f'Cola de tareas: {self.planQueue}')
        return 0

    # Agregar tareas a la cola de planificacion
    def addTasks(self, task_list):
        for task in task_list:
            self.putTaskPlanQueue(task)
        return 0
    
    # Avanza el tiempo en 1 y las tareas que yas terminaron de esperar las mueve
    # a la cola planQueue
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
                            print("Tiene operaciones, pasa a planificador")
                            tempList.append(tarea)
                            self.putTaskPlanQueue(tarea)
                        else:
                            # Pasa a finalizado
                            tempList.append(tarea)
                            print("Ya no tiene operaciones, pasa a finalizado")
                            self.putTaskFinishedQueue(tarea, time)
                else:
                    print('No debería estar aca')

            # Elimino las tareas de la cola de espera
            for tarea in tempList:
                self.removeTaskWaitingQueue(tarea)

                

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

    print("Tests de planificación FCFS")
    planFCFS = Planificador(FLAG)
    planFCFS.addTasks(set1_tareas)
    planFCFS.printTasks()

    trabajador = Persona("Trabajador 1")
    tarea = planFCFS.getTaskPlanQueue()
    trabajador.task = tarea
    workToBeDone = tarea.serviceList.popleft()

    # SIMULACION DE TIEMPO
    for time in range(MAX_TIME):
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


        # Vemos el estado de las colas al final de cada tick del reloj
        print(f'FinCiclo-PlanQ: {planFCFS.planQueue}\n-------------------------')
        print(f'FinCiclo-WaitQ: {planFCFS.waitingQueue}\n-------------------------')
        print(f'FinCiclo-FiniQ: {planFCFS.finishedQueue}\n-------------------------')
        planFCFS.schedule(time)




if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()