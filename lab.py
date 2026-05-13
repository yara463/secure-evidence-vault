from scipy.stats import norm
import numpy as np
mean = 78
std_dev = 25
total_students = 100
score = 60
z_score = (score - mean) / std_dev
prob = norm.cdf(z_score)
percent = prob * 100
print("Percentage of students who got less than 60 marks:", round(percent, 2), "%")

import numpy as np
def normal_dist(x, mean, sd):
    prob_density = (np.pi * sd) * np.exp(-0.5 * ((x - mean) / sd) ** 2)
    return prob_density
mean = 0
sd = 1
x = 1
result = normal_dist(x, mean, sd)
print(result)









import numpy as np
import matplotlib.pyplot as plt
Mean = 100
Standard_deviation = 5
size = 100000
values = np.random.normal(Mean, Standard_deviation, size)
plt.figure(figsize=(10, 5))
plt.hist(values, 100)
plt.axvline(values.mean(), color='k', linestyle='dashed', linewidth=2)
plt.title("Horizontal Histogram")
plt.show()

import numpy as np
import matplotlib.pyplot as plt
Mean = 100
Standard_deviation = 5
size = 100000
values = np.random.normal(Mean, Standard_deviation, size)
plt.figure(figsize=(5, 10))
plt.hist(values, 100, orientation='horizontal')
plt.axhline(values.mean(), color='k', linestyle='dashed', linewidth=2)
plt.title("Vertical Histogram")
plt.show()