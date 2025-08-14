import heapq
import random

# === Constants ===
MAX_CONCURRENT_JOBS = 50
SIM_DURATION = 30 * 60  # 30 minutes in seconds
LAMBDA = 4  # users per minute

DURATIONS = {
    'S': 60,
    'M': 180,
    'L': 480,
}
JOB_TYPES = ['S'] * 60 + ['M'] * 30 + ['L'] * 10  # Fixed ratio
random.shuffle(JOB_TYPES)

# === Event Types ===
USER_ARRIVAL = 'USER_ARRIVAL'
JOB_START = 'JOB_START'
JOB_END = 'JOB_END'

# === Globals ===
event_queue = []
running_jobs = []
waiting_jobs = []
completed_jobs = []
now = 0
job_id_counter = 0
job_type_index = 0


# === Utilities ===

def schedule_event(time, type, data=None):
    heapq.heappush(event_queue, (time, type, data))

def generate_interarrival():
    return random.expovariate(LAMBDA / 60.0)  # LAMBDA users per minute

def get_next_job_type():
    global job_type_index
    jt = JOB_TYPES[job_type_index % len(JOB_TYPES)]
    job_type_index += 1
    return jt


# === Event Handlers ===

def handle_user_arrival():
    global now, job_id_counter

    num_jobs = random.randint(1, 5)
    submission_time = now

    for _ in range(num_jobs):
        jt = get_next_job_type()
        job = {
            'id': job_id_counter,
            'type': jt,
            'duration': DURATIONS[jt],
            'submission': submission_time,
            'start': None,
            'end': None,
        }
        waiting_jobs.append(job)
        job_id_counter += 1

    try_start_jobs()

    # Schedule next user arrival
    next_arrival = now + generate_interarrival()
    if next_arrival < SIM_DURATION:
        schedule_event(next_arrival, USER_ARRIVAL)


def try_start_jobs():
    while len(running_jobs) < MAX_CONCURRENT_JOBS and waiting_jobs:
        job = waiting_jobs.pop(0)
        job['start'] = now
        job['end'] = now + job['duration']
        running_jobs.append(job)
        schedule_event(job['end'], JOB_END, job)


def handle_job_end(job):
    running_jobs.remove(job)
    completed_jobs.append(job)
    try_start_jobs()


# === Main Loop ===

# Seed first user arrival
schedule_event(generate_interarrival(), USER_ARRIVAL)

while event_queue:
    now, event_type, data = heapq.heappop(event_queue)

    if event_type == USER_ARRIVAL:
        handle_user_arrival()
    elif event_type == JOB_END:
        handle_job_end(data)

# === Metrics ===

wait_times = [j['start'] - j['submission'] for j in completed_jobs]
completion_times = [j['end'] - j['submission'] for j in completed_jobs]

print(f"Simulated {len(completed_jobs)} jobs")
print(f"Min Completion Time: {min(completion_times):.1f} sec")
print(f"Avg Completion Time: {sum(completion_times)/len(completion_times):.1f} sec")
print(f"Max Completion Time: {max(completion_times):.1f} sec")
