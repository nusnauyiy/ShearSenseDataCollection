# Shear-sense Data Collection Software

## Software Overview

### Project summary
The shear-sense project explores the use of touch sensor arrays that can detect both pressure and shear for gesture classification. The goal is to evaluate the usefulness of shear data through gesture classification, with the ultimate aim of collecting richer touch data for future human-computer interaction and human-robot interaction studies. The project involves using the touch sensor arrays to collect both pressure and shear data for a series of pre-determined gesture performed by recruited participants, and then attempting to classify these gestures using machine learning techniques. 

### Purpose of this software
The data collection software is responsible for collecting the raw serial data continuously sent from the touch sensor array to the computer. It also enables capturing of important context such as timestamp, data baseline, and current gesture, to form the complete dataset prior to data analysis.

## Features and Interpretation of the Software Output
### Visualization of serial data

The visualization consists of a grid, with each cell in the grid representing a tactile pixel (taxel) on the physical sensor in its relative phyiscal location. If a cell is white, it indicates that it is not experiencing any change in pressure from the baseline, impling that it is not being touched. If a cell experiences pressure (i.e. touch), it will appear more orange, with the color intensity corresponding to the strength of the pressure.

Information on shear is represented on the visualization grid by a blue arrow that appears from the center of each cell. The magnitude and direction of the arrow correspond to the magnitude and direction of the shear force detected by the sensor.

### Storing data to CSV
The file directory and filename for the data can be specified in the software configuration, and the data will be logged to that location in CSV format.

**Interpretation of a data row**

- The data collected by the software has a total of 183 columns, with each column containing a specific type of information about the touch data being collected.
- The first column of the data represents the timestamp for each row of data, indicating the exact time at which the touch data was recorded.
- Columns 2-181 of the data represent the raw data for each individual taxel on the touch sensor array.
- Column 182 of the data contains a touch/no-touch classification, which indicates whether or not each taxel is currently being touched.
- Column 183 of the data contains a label, this can be used for indicating the current gesture being performed at that time.

The first row of the data represents the baseline state of the touch sensor array, and only columns 2-181 are populated with data. This baseline data is collected after the first few seconds the software started up, ideally the sensor is not being touched at the time. All subsequent rows shows raw serial data collected by the sensor at the specified timestamp, and all 183 columns should be populated.


### Requirements
The data collection software is designed to work with the 6x6 shear sensor and requires a Windows OS to run.

## Set-up
### Sensor Set-up
describe how to connect sensors and receivers

### Configurations
The following configurations maybe adjusted in `settings.py`.
- **serial ports**
    - On Windows (this software only works on Windows), open `Device Manager`. Look for the "Ports (COM & LPT)" section and click on the arrow to expand it. The list of available serial ports will be displayed, along with their corresponding port numbers. Assuming that the sensor and receiver are connected properly, each would occupy one serial port respectively.
    - `PORT_FLAT` is the serial port number for the `KitKatCSV_Flatt.py` file, and `PORT_CURVED` is the serial port number for the `KitKatCSV_Flatt.py` file. Make sure the serial port of the corresponding sensor is assigned here. If it's unclear which port maybe the sensor, run the program with different port numbers to find the working one.

- **output configurations**
    - `FOLDER` is the directory in which the output file will be stored. Make sure this directory exists before running the software.
    - The name of the output file is generated automatically and consists of a custom name, experimental condition, and timestamp.
        - `FILENAME` constant should contain the custom name. The custom name should have the format `P{participant number}_{other comments}` to maximize compatibility with the data modelling software.
        - The experimental condition is either "FLAT" or "CURVED" and is automatically appended to the output file name depending on which file, `KitKatCSV_flatt.py` or `KitKatCSV_curved.py`, is run.
        - the function `TIMESTAMP()` can be altered to change the format of the timestamp in the filename.
- **labelling duration**
    - `LABEL_LENGTH` indicate how long a timed label should applied to the data. We used 12 seconds for participants 1-18. This is discussed further in the Data Labelling section.

### Running the software
- Open the terminal at the root directory
- Install the required packages by running `pip install -r requirements.txt`
- Make the desired configuration changes by editing `settings.py`
- Run the program with `python KitKatCSV_curved.py` or `KitKatCSV_flatt.py`
- Expected behaviors
    - When the program starts, it first collects 100 data sample as the baseline. It is important that the sensor remain untouched during this time for baseline accuracy!
    - When baseline data collection finishes, which may take a few seconds, the visualization will appear as a new window. Data collection also begins.
    - When sufficient pressure is applied to the sensor, the text "touched" is logged in the console. When the pressure is removed from the sensor, the text "not touched" is logged in the console.
    - At this point, any alpha-numeric keys can be pressed to trigger data labelling. See the Data Labelling section for more details.
- Dispose the terminal in which the program is ran to stop the program. Note that closing the visualization window does not stop the program from running. The data file wiill be saved in the location specified by `settings.py`, and may take up to a few minutes to show up.

### Troubleshooting
If an error is raised related to the serial ports, please double check the following:
- the sensors and receivers are plugged into the device, and that the receiver has a blue indicator light on
- the serial port correspondng to the sensor, not the receiver, is supplied to `settings.py`. This may take some "trial and error" with different ports available.

If you see a file/directory error, please double check the following:
- the program is ran from the directory directly containing it, and that all the associated files (`settings.py`, `classfiers/Classifier.py`) are present.
- the directory for storing data specificed in `settings.py` exists in the current directory.

## Data Labelling
The program allows a character to be logged with each row of data to indicate the context of the row. See the [Shear-Sense data collection protocol](https://docs.google.com/spreadsheets/d/1zEoA7uhVjtGHUdOhrnSj8CzRhVmpZ9unMFAgWr_3R1s/edit#gid=0) for the gesture key mapping.

### Labelling key bindings
- Alpha/letter keys initiate a timed label of that character. After one of these keys is pressed, each row of data logged will have its last column labelled with the associated character. This effect will last for the specified `LABEL_LENGTH` in `settings.py`. When the label expires, a beep will be played by the program to notify the user.
- Numeric/digit keys behaves the same as Alpha/letter keys, except that the length of labelling is 4 seconds. Currently, this cannot be adjusted in `settings.py`.

### limitations
Only one label can be applied at any given time. For example, if the data is current labelled by the key `x`, presseing the key `y` will terminate the labelling of `x` and label the subsequent data as `y`. The previous timer for `x` will also be cleared, and a new timer will begin for `y`.

When the data collection is in progress, any alphanumeric key press will trigger labelling, even if the terminal or editor running the program is not active. Therefore, please refrain from pressing any alphanumeric keys for other purposes in the data collection process.

## Advanced How-tos:
### Running more than one instance of the application
Two pairs of sensors and receivers maybe set up and ran simultaneously. This can be done by running the following command:

```
Start-Process python .\KitKatCSV_curved.py; Start-Process python .\KitKatCSV_flatt.py
```

 Alternatively, one can run `KitKatCSV_curved.py` and `KitKatCSV_flatt.py` in two different terminals. (i.e. run `python KitKatCSV_curved.py` in one terminal, open a new terminal, and run `python KitKatCSV_flatt.py` in the new terminal). 

One should ensure the serial ports in `settings.py` is correct for their respective files.

Note:
- When both programs are running successfully, two visualization windows will appear. One can distinguish the two windows by their respective window titles.
- Key press is detected locally. When an alphanumeric key is pressed, both running programs will begin labelling their data with the character.

### Modifying model for touch/no-touch classification
To add a new model to the codebase, one can implement a new class `<X>Classfier` that extends the `Classifier` class in `classifier/Classifier.py`. `<X>Classfier` should implement the `classify` method that takes in a row of raw data, and return the classification result. Currently, "1" represents touched and "0" represents untouched.

To use the new `<X>Classfier`, locate the method `classify_touch_no_touch` in `KitKatCSV_curved.py` and `KitKatCSV_flatt.py`, and point the variable `classifier` to an instance of `<X>Classfier`.

To modify the current `ThresholdClassifier` model, one can simply edit the implementation in `classifier/Classifier.py`.

## Code walkthrough and Design choices
### Thread allocations
`KitKatCSV_curved.py` and `KitKatCSV_flatt.py` each uses four concurrent thread to parallelize various functionalities: the main thread, one thread for compiling data and writing data to file, one thread that listens for key presses, and one thread for visualization.

### Calibration code
This code can be found in the `__main__` functions between the print statements
```print("calibrating serial data...")``` and
```print("serial data calibrated")```.

The `while` loop allows 100 lines of well-formed data to be read, and the subsequent `for` loop calculates the average of each column. The resulting `average` array stores the baseline values that will be used throughout the execution of the program.

### Visualzation code
The functions `calcValues`, `plot_init`, `update`, `arrowUpdate`, the class `HeatMap`, as well as various various code snippets initializing contents from the QT libraries, are related to visualization.

For a detailed walkthrough of these functions, please consult Zavary from UU-lab.

### Touch/no-touch classification code
The classificaiton model and its implementation is found in `classifier/Classifier.py`. The `ThresholdClassfier` is currently in use. For each new data row, the model checks whether a column deviates from the baseline value by a certain percentage. If so, it classifies the row of data as being touched. The sensitivity of the model can be adjusted by the parameter `rate`. `(1-rate)` is the change in raw values the model is willing to tolerate before marking the data as "touched".

### Labelling and timer code
The associated code can be found in the definition of `thread1`. The functions `stop_label`, `on_press`, `on_release` and other usage of the variable `listner` are all related to this feature. These functions encapsulates the Timer functionality as well as setting/clearing the active key to write into CSV.
### Writing data to CSV code
This is the main functionality of `thread1`. It continiously read from the serial port in the `while True` loop. At each iteration, it decodes data, appends other informations (timestamp, touch/no touch classification, data label) to it, and writes them as a row in the specified CSV file.

## Comments and Future improvements
There is room for improvement in terms of code refactoring and configuration options. Specifically, `KitKatCSV_curved.py` and `KitKatCSV_flatt.py` are nearly identical, and can use siginificant refactoring. Additionally, the `settings.py` file could contain additional configuration, such as changing the label length for numeric keys, specifying the classifier to use, enabling or disabling logging. This can be especially important when additional experimental conditions are added. But overall, the data collection software is a very usable tool for our current purpose.