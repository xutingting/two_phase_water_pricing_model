#!/usr/bin/env bash

python compare_pool.py 1  # compare with pooled exchange on a special case, change distance threshold.
python compare_pool.py 2  # compare with pooled exchange, comparing thresholds of distances
python compare_pool.py 3  # compare with pooled exchange, comparing thresholds of canal distances (0~4)
python compare_pool.py 4  # compare with pooled exchange, on a special case, change canal distance.
python compare_pool.py 5  # Compare the improvement of two-phase model with pool exchange with confidence interval.
python compare_pool.py 6  # Compare the effects of distance by raw numbers.

python compare_obj.py 1  # plot price distribution
python compare_obj.py 2  # rank the three objective functions
python compare_obj.py 3 s  # plot the optimal choices for sellers
python compare_obj.py 3 b  # plot the optimal choices for buyers
python compare_obj.py 4 s  # bar graph for the preference of sellers
python compare_obj.py 4 b  # bar graph for the preferences of buyers.
python compare_obj.py 5  # Calculate the difference with confidence interval