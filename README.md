# Shear-sense Data Collection Software

## Software Overview

### summary of associated project

### purpose of the software in context of the project

### features of the software
- visualizing serial data
    - sample visualization and interpretation
- store data to CSV
    - sample data row, description, and interpretation
- label data via key press
- touch/no touch classification

### Requirements
- windows only
- only works with 6x6 shear sensor (180 channel)

## Set-up
### Sensor Set-up
describe how to connect sensors and receivers
### Configurations
how to configure the following:
- serial ports
    - how to choose the correct port to read datat from
- output configurations
    - filename, directory, date format
- labelling duration

recommended configurations:
- file name formats compatible with data modelling software
- etc.

### Running the software
- installing required packages
- commands to run the software
- expected behaviors
    - example log statements and interpretation
- stopping the software

### Troubleshooting
- serial data reading errors
- file directory errors
- etc.

## Data Labelling

### labelling key bindings
- alpha keys = timed labels
- numeric keys = untimed labels

### limitations
- only one label can be registered at a time
- potential timer confusion (this needs to be investigated)


## Advanced How-tos:
- running more than one instance of the application
- adding new model for touch/no-touch classification

## Code walkthrough and Design choices
### Thread allocations
### Calibration code
### Visualzation code
### Touch/no-touch classification code
### Labelling and timer code
### Classification code
### Writing data to CSV code

## Known limitations and future improvements