import datetime
import math
import random

from .utils import time_in_range, get_minutes_difference
from datetime import datetime, timedelta


def is_weekday(time_period):
    return time_period.weekday() < 5

def random_time(begin, end):
    return begin + timedelta(minutes=random.uniform(0,(end-begin).seconds//60))
   
def random_duration(begin, end):
    return timedelta(minutes = random.uniform(begin, end))

def should_event_occur(probability, start, end, now):
    if not time_in_range(now, start, end):
        return False
    total_minutes = int(get_minutes_difference(start, end))
    adjusted_probability = 1 - (1 - probability) ** (1 / total_minutes)
    
    return random.random() < adjusted_probability

# def prob_test(): 
#     numbers = 0
#     for i in range(10000):
#         start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
#         now = start
#         end = start + timedelta(hours=2)
#         avg_num = 10
#         delta = 2
#         num_ocurred = 0
#         while now < end:
#             roll = roll_for_event(start, end, now, avg_num, delta, num_ocurred)
#             if roll:
#                 num_ocurred += 1
#             now += timedelta(minutes=1)
#         numbers += num_ocurred

#     #THIS IS THE RESULT
#     print(numbers/10000)

# def roll_for_event(start, end, now, avg_num, delta, num_occurred):
#     # Calculate the proportion of time elapsed
#     time_elapsed = (now - start) / (end - start)
    
#     # Calculate the target number of occurrences based on the average and the delta
#     target_min = avg_num - delta
#     target_max = avg_num + delta
#     target_range = target_max - target_min
#     target_num = target_min + (target_range * time_elapsed)
    
#     # Calculate the remaining time
#     remaining_time = end - now

#     # Calculate the probability of an event happening in the next minute
#     probability = (target_num - num_occurred) / (remaining_time.total_seconds() / 60)

#     # Generate a random number to decide if the event should happen
#     return random.random() < probability

def prob_test(): 

    max_num = 12
    occurred = 0
    start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    now = start
    end = start + timedelta(hours=2)
    diff = get_minutes_difference(start, end)

    # while now < end:
    #     prob = 1-2.5/((max_num - occurred) + 2.5)
    #     print(prob)
    #     if should_event_occur(prob, start, end, now):
    #         occurred += 1
    #         start = now + timedelta(minutes=1)
    #     now += timedelta(minutes=1)
    # print(occurred)

    # print(num_so_far)
    # numbers = 0
# # for i in range(10000):
#     start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
#     now = start
#     end = start + timedelta(hours=2)
    #     max = 12
    #     occurred = 0
    #     diff = get_minutes_difference(start, end)
    #     probability = (max - occurred) / (math.log(max + 1) - math.log(occurred + 1))
    #     print(probability)
    #     while now < end:
    #         diff = get_minutes_difference(now, end)
    #         probability = (max - occurred) / (math.log(max + 1) - math.log(occurred + 1))
    #         probability_per_minute = probability / diff
    #         print(probability_per_minute)
    #         if random.random() < 1 - probability_per_minute:
    #             occurred += 1

    #         now += timedelta(minutes=1)


