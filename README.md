# Individual_Project
#### Author: Sylvain Hu
It is suggested to use a jupyter notebook to simulate the model. The user may either uses one of the provided notebooks to run in batches the calibrated model, or create a blank notebook with randomized attributes, below is an example:

```
# Create a test variable of the model
test_model = MyModel(C=2, F=2, P=30)

# Run the model for 10 steps
for i in range(10):
    print(test_model.step())
```
After uncommenting the needed information in both agents.py or model.py, this code prints out the desired information and simulate the model for 2.5 seasons. The model takes 3 parameters: number of club, number of football agents and number of footballers. Two additional arguments may be provided: a tuple or a list of tuple to calibrate clubs (please ensure that the number of clubs and the tuples match), and True or False for the FFP (default is False). 
Note: Please ensure that each club has at least 11 players in the model. 
