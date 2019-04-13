'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
'''
import sys
import copy

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.predicted_burst = 0
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrival_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Assumption if a new process comes in while a process is currently running, it will be enqueued first, the current running process will queue behind it once it completes
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
    schedule = []
    current_time = 0
    waiting_time = 0
    average_waiting_time = 0
    job_queue = []
    number_jobs = len(process_list)
    remaining_process_list = copy.deepcopy(process_list)
    while len(job_queue) > 0 or len(remaining_process_list) > 0:
        # check if new job entered
        ran = False
        while len(remaining_process_list) > 0:
            nextjob = remaining_process_list[0]
            if nextjob.arrive_time <= current_time:
                job_queue.append(nextjob)
                remaining_process_list.remove(nextjob)
                waiting_time += (current_time- nextjob.arrive_time)
            else:
                break
        # process job
        if len(job_queue) > 0:
            current_job = job_queue[0]
            job_queue.remove(current_job)
            schedule.append((current_time,current_job.id))
            time_slice = min(time_quantum, current_job.burst_time)
            current_job.burst_time -= time_slice
            current_time += time_slice
            ran = True
            # check if new job entered before enqueing finished job
            while len(remaining_process_list) > 0:
                nextjob = remaining_process_list[0]
                if nextjob.arrive_time <= current_time:
                    job_queue.append(nextjob)
                    remaining_process_list.remove(nextjob)
                    waiting_time += (current_time- nextjob.arrive_time)
                else:
                    break
            if  current_job.burst_time > 0:
                job_queue.append(current_job)
            else:
                waiting_time += (current_time - current_job.burst_time - current_job.arrive_time)
        average_waiting_time = waiting_time / number_jobs
        if not ran:
            current_time += 1
            

    return schedule, average_waiting_time

def get_shortest_burst(job_queue):
    shortest_job = job_queue[0]
    shortest_burst = shortest_job.burst_time
    for job in job_queue:
        if job.burst_time < shortest_job.burst_time:
            shortest_job = job
            shortest_burst = job.burst_time
    return shortest_job

def SRTF_scheduling(process_list):
    schedule = []
    current_time = 0
    waiting_time = 0
    average_waiting_time = 0
    time_quantum = 1
    job_queue = []
    previous_id = -1
    number_jobs = len(process_list)
    remaining_process_list = copy.deepcopy(process_list)
    while len(job_queue) > 0 or len(remaining_process_list) > 0:
        # check if new job entered
        ran = False
        while len(remaining_process_list) > 0:
            nextjob = remaining_process_list[0]
            if nextjob.arrive_time <= current_time:
                job_queue.append(nextjob)
                remaining_process_list.remove(nextjob)
            else:
                break
        # process job
        if len(job_queue) > 0:
            current_job = get_shortest_burst(job_queue)
            job_queue.remove(current_job)
            if previous_id != current_job.id:
                schedule.append((current_time,current_job.id))
                previous_id = current_job.id
            time_slice = min(time_quantum, current_job.burst_time)
            current_job.burst_time -= time_slice
            current_time += time_slice
            ran = True
            # check if new job entered before enqueing finished job
            while len(remaining_process_list) > 0:
                nextjob = remaining_process_list[0]
                if nextjob.arrive_time <= current_time:
                    job_queue.append(nextjob)
                    remaining_process_list.remove(nextjob)
                else:
                    break
            if  current_job.burst_time > 0:
                job_queue.append(current_job)
            else:
                waiting_time += (current_time - current_job.burst_time - current_job.arrive_time)
        average_waiting_time = waiting_time / number_jobs
        if not ran:
            current_time += 1
            

    return schedule, average_waiting_time

def predict_burst(process, alpha, previous_burst, previous_predicted_burst):
    predicted_burst = alpha*previous_burst + (1-alpha) * previous_predicted_burst
    return  predicted_burst

def get_shortest_predicted_burst(job_queue):
    shortest_job = job_queue[0]
    shortest_predicted_burst = shortest_job.predicted_burst
    for job in job_queue:
        if job.predicted_burst < shortest_job.predicted_burst:
            shortest_job = job
            shortest_burst = job.predicted_burst
    return shortest_job

def SJF_scheduling(process_list, alpha):
    schedule = []
    history = {}
    INITIAL_PREDICTED_BURST = 5
    current_time = 0
    waiting_time = 0
    average_waiting_time = 0
    time_quantum = 1
    job_queue = []
    previous_id = -1
    number_jobs = len(process_list)
    remaining_process_list = copy.deepcopy(process_list)
    while len(job_queue) > 0 or len(remaining_process_list) > 0:
        # check if new job entered
        ran = False
        while len(remaining_process_list) > 0:
            nextjob = remaining_process_list[0]
            if nextjob.arrive_time <= current_time:
                if nextjob.id in history:
                    nextjob.predicted_burst = predict_burst(nextjob, alpha, history[nextjob.id]["previous_burst"], history[nextjob.id]["previous_predicted_burst"])
                else:
                    nextjob.predicted_burst = INITIAL_PREDICTED_BURST
                history[nextjob.id] = {}
                history[nextjob.id]["previous_predicted_burst"] = nextjob.predicted_burst
                history[nextjob.id]["previous_burst"] = nextjob.burst_time
                job_queue.append(nextjob)
                remaining_process_list.remove(nextjob)
            else:
                break
        # process job
        if len(job_queue) > 0:
            current_job = get_shortest_predicted_burst(job_queue)
            job_queue.remove(current_job)
            if previous_id != current_job.id:
                schedule.append((current_time,current_job.id))
                previous_id = current_job.id
            current_time +=  current_job.burst_time
            waiting_time += (current_time - current_job.burst_time - current_job.arrive_time)
            ran = True
            # check if new job entered before enqueing finished job
            while len(remaining_process_list) > 0:
                nextjob = remaining_process_list[0]
                if nextjob.arrive_time <= current_time:
                    if nextjob.id in history:
                        predicted_burst = predict_burst(nextjob, alpha, history[nextjob.id]["previous_burst"], history[nextjob.id]["previous_predicted_burst"])
                        nextjob.predicted_burst = predicted_burst
                    else:
                        predicted_burst = INITIAL_PREDICTED_BURST
                    history[nextjob.id] = {}
                    history[nextjob.id]["previous_predicted_burst"] = predicted_burst
                    history[nextjob.id]["previous_burst"] = nextjob.burst_time
                    job_queue.append(nextjob)
                    remaining_process_list.remove(nextjob)
                else:
                    break
        if not ran:
            current_time += 1
            

        average_waiting_time = waiting_time / number_jobs

    return schedule, average_waiting_time


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])

