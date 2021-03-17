import threading
import sys
import queue
import time

EMULATE_HX711 = False
referenceUnit = -520

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

hx = HX711(5, 6)
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()
my_queue = queue.Queue()

class CalculateWeight:
    
    def __init__(self, weight):
        self.weight = weight
        
    def calculate(self,weight, out_queue):
        i = 0
        self.weight = weight[-4:]
        #for i in range(0,5):
            #self.weight = weight[-4:]
        val2 = hx.get_weight(5)
        self.weight.append('%.2f' % val2)
        val2 = hx.get_weight(5)
        self.weight.append('%.2f' % val2)
        #self.weight.insert(0, '%.2f' % val2)
        print("2")
        print(self.weight)
        j = 0
        count = 0
        total = 0
        for j in range(len(self.weight)):
            if(float(self.weight[j]) > 140):
                total += float(self.weight[j])
                count += 1
        if(count == 0):
            count = 1
        mean = total / count
        #print("mean: " + str('%.2f' % mean))
        out_queue.put(('%.2f' % mean,weight))
    
    def clear_value(self):
        count3 = 0
        while count3 < 5:
            #self.weight.insert(0, 0)
            self.weight.append(0)
            count3 = count3+1
        print(self.weight)
        # return self.weight

    def put_weight(self):
        val = hx.get_weight(5)
        self.weight = self.weight[-4:]
        #self.weight.insert(0, '%.2f' % val)
        self.weight.append('%.2f' % val)
        #print("55555")
        return self.weight

    def th(self):
        t = threading.Thread(target = self.calculate , args = (self.weight, my_queue))
        t.start()
        t.join()
        weight_average,self.weight = my_queue.get()
        #print("weight_average: " + str(weight_average))    
        return weight_average,self.weight
    
    def get_weight1(self):
        return self.weight
