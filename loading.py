#!/usr/bin/python3
import time
import os




def ft_progress(list):
    size = len(list)
    elap_time = 0
    sleep_time = 0.0
    bar_size = 40
    bar_items = 0
    count = -1
    start_time = time.time()
    my_time = start_time
    times_between_calls = []

    size_len = len(str(size))
    percen = 0
    
    while count < size - 1:
        count = count + 1
        actual_time = time.time()
        sleep_time = actual_time - my_time  #  time diff between calls
        times_between_calls.append(sleep_time)
        my_time = actual_time               #  last call time update
        # i use time average between calls to calculate execution time
        tot_eta_time = (sum(times_between_calls) / len(times_between_calls)) * size 
        # elapsee time accumulation
        elap_time = elap_time + sleep_time
        chunk5 = f"| elapsed time {elap_time:.2f}s"
        eta_time = tot_eta_time - elap_time
        display_eta_time = eta_time if eta_time > 0 else 0
        chunk1 = f"ETA: {display_eta_time:0>5.2f}s "
        percen = (count + 1) / size
        chunk2 = f"[{100 * percen:3.0f}%]"
        display_counter = count + 1
        chunk4 = f"{display_counter:{size_len}}/{size}"
        bar_items = "=" *(int(bar_size * percen) - 1) + ">"
        chunk3 = f"[{bar_items:<{bar_size}}] "
        print(chunk1 + chunk2 + chunk3 + chunk4 + chunk5, end="\r", flush=True)
        yield list[count]
