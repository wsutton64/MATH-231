import csv
import numpy as np
import matplotlib.pyplot as plt

# JoshuaTree class/object
class JoshuaTree:
    # Tree Parameters
    age = 0
    isMature = False
    isDead = False
    bloom_min = 1
    bloom_max = 3
    flower_min = 24
    flower_max = 46
    pollination_rate = .8
    seeds_per_flower = 10
    seeds = 0

    # Initialize with given age. If age >= 50, it is mature.
    def __init__(self, age):
        self.age = age
        if age >= 50:
            self.isMature = True
        else:
            self.isMature = False

    # return String of parameters for testing
    def __str__(self):
        return f"Age: {self.age}, isMature: {self.isMature}, isDead: {self.isDead}, seeds: {self.seeds}"
    
    # When called, generate a random number of blooms between "bloom_min" and "bloom_max"
    # Per bloom, generate a random number of flowers between "flower_min" and "flower_max"
    # Pollinate the flowers based on "pollination rate" and multiply it by "seeds_per_flower" to get total number of seeds
    # Return total number of seeds
    def bloom(self):
        for bloom in range(np.random.randint(self.bloom_min, self.bloom_max)):
            num_flowers = np.random.randint(self.flower_min, self.flower_max)
            self.seeds += (num_flowers * self.pollination_rate) * self.seeds_per_flower
        return self.seeds
    # Calculate the number of germinated seeds
    # If the weather is dryer than the mean rainfall, less are germinated. If wetter than mean, more are germinated.
    # Every tree keeps track of the number of seeds they produce and germinate as a means of keeping track of the overall seed population
    def germinate(self, weather, mean):
        germinated = int(self.seeds * (germination_rate + ((weather[2] - mean)/1000)))
        self.seeds -= germinated
        return germinated

# Simulation Parameters
number_sims = 10            # Number of times the simulation will run
mature_trees = 20           # Starting number of mature trees
simulation_years = 100      # Simulated years the simulation will calculate
cold_year_prob = .3         # Cold years 30% of the time
germination_rate = 1/1000   # 1 out of 1000 will germinate
tree_death_rate = 1/400     # 1 out of 400 will die
bloom_probability = 2/45    # 2 out of 45 will bloom
stress_bloom = 1/45         # when stressed, tree will be 50% more likely to bloom
seed_death_rate = .5        # half of the seeds that don't germinate will die
# Import rainfall data from csv file
rainfall = []
with open("la_rainfall_csv_edited.csv") as raindata:
    reader = csv.reader(raindata)
    # Iterate over each row and add the float data to the rainfall list. Skips the first row with no data
    for row in reader:
        num = row
        try:
            rainfall.append(float(num[0]))
        except:
            print("Passing non-float from list")
            pass
rainfall_mean = np.mean(rainfall)       # Mean of the rainfall data
rainfall_stdev = np.std(rainfall)       # Stdev of the rainfall data


# Runs the weather simulation
# Randomly selects rainfall based on a normal distribution of the rainfall data
# Compares that number to +-1 standard deviation from the mean. If it exceeds those boundaries, it is a Wet/Dry season respectively
# Then, check if the year is cold or warm depending on "cold_year_prob"
def weather_sim():
    rain = np.random.normal(rainfall_mean, rainfall_stdev)  # Rainfall for the year
    result = ["DEFAULT","DEFAULT",rain]                     # Construct a default list for the results. Result[2] is the rainfall
    if rain > rainfall_mean + rainfall_stdev:
        result[0] = "Wet"
    elif rain < rainfall_mean - rainfall_stdev:
        result[0] = "Dry"
    else:
        result[0] = "Normal"
    if np.random.rand() < cold_year_prob:
        result[1] = "Cold"
    else:
        result[1] = "Warm"
    # Returns the "result" list
    return result

# Runs the yearly simulation
# Pass in the list of trees
def year_sim(tree_list):
    # Initialize year_sim parameters
    trees = tree_list
    germinated_seeds = 0
    weather = weather_sim() # Runs a weather sim and becomes the returned "result" list
    # Update trees
    for index, tree in enumerate(trees):
        tree.age += 1       # Tree ages 1 year
        seeds = tree.seeds  # Current number of seeds
        # Tree has random chance of becomming mature between 50 and 60
        # If less than 50, it can't become mature. If over 60, it is guaranteed.
        if np.random.randint(50,60) <= tree.age:
                tree.isMature = True
        # Check tree if it dies. If is dies, remove it from the list.
        # Get a random number. Compare that to the deathrate minus the difference between the mean and the actual weather
        # This means that if you get more than average rain, the chance goes down. Less than average, the chance goes up.
        # The 2nd clause makes it to where when it hits 250, it starts having a chance to die of old age until it hits 500.
        if (np.random.rand() < tree_death_rate - ((weather[2] - rainfall_mean)/1000)) or (np.random.randint(250,500) <= tree.age):
            tree.isDead = True
            trees.pop(index)
        # Calculate how many seeds die. Wet/Dry weather affect this number by killing more off.
        if weather[0] == "Wet":
            seeds *= seed_death_rate - ((weather[2] - rainfall_mean)/100)
        elif weather[0] == "Dry":
            seeds *= seed_death_rate + ((weather[2] - rainfall_mean)/100)
        else:
            seeds *= seed_death_rate
        # If the tree is not mature or is dead, skip the rest and go onto the next tree
        if not tree.isMature or tree.isDead:
            continue
        # Calculate bloom probability
        # If it is a dry or cold year, bloom probability increases
        if weather[0] == "Dry" or weather[1] == "Cold":
            if np.random.rand() < bloom_probability + stress_bloom:
                seeds = tree.bloom()
        else:
            if np.random.rand() < bloom_probability:
                seeds = tree.bloom()
        # Germinate the seeds
        # Every tree keeps track of the number of seeds they produce and germinate as a means of keeping track of the overall seed population
        germinated_seeds += tree.germinate(weather, rainfall_mean)
    # Every germinated seed is a newly born Joshua Tree
    for germinated_seed in range(germinated_seeds):
        trees.append(JoshuaTree(0))
    # Return a list of the current trees after births/deaths
    return trees

# The main method of a simulation
# Runs a simulation for "simulation_years" times
# Returns the final number of trees
def main():
    # Initialize mature trees with random ages between 50 and 60
    trees_list = []
    for t in range(mature_trees):
        trees_list.append(JoshuaTree(50 + int(np.random.rand() * 11)))
    # Initialize a list of the sum of trees every year
    trees_list_sum = [len(trees_list)]
    # Run the yearly simulations
    for year in range(simulation_years):
        trees_list_sum.append(len(year_sim(trees_list)))
    #print(trees_list_sum)
    return trees_list_sum[-1]

# Run the simulation for "number_sims" times then display a histogram of the final resulting data
sims_totals = []
for sim in range(number_sims):
    sims_totals.append(main())
print(sims_totals)
plt.hist(sims_totals)
plt.show()
