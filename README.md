# QRS detection using K-Nearest Neighbor algorithm (KNN) and evaluation on standard ECG databases
## Introduction
The function of human body is frequently associated with signals of electrical, chemical, or acoustic origin. Extracting useful information from these biomedical signals has been found very helpful in explaining and identifying various pathological conditions. The most important are the signals which are originated from the heart's electrical activity. This electrical activity of the human heart, though it is quite low in amplitude (about 1 mV) can be detected on the body surface and recorded as an electrocardiogram (ECG) signal. The ECG arise because active tissues within the heart generate electrical currents, which flow most intensively within the heart muscle itself, and with lesser intensity throughout the body. The flow of current creates voltages between the sites on the body surface where the electrodes are placed. The normal ECG signal consists of P, QRS and T waves. The QRS interval is a measure of the total duration of ventricular tissue depolarization. QRS detection provides the fundamental reference for almost all automated ECG analysis algorithms. Before to perform QRS detection, removal or suppresion of noise is required. The aim of this work is to explore the merits of KNN algorithm as an ECG delineator. The KNN method is an instance based learning method that stores all available data points and classifies new data points based on similarity measure. In KNN, the each training data consists of a set of vectors and every vector has its own positive or negative class label, where K represents the number of neighbors. 

### Dependencies
The modules are implemented for use with Python 3.x and they consist of the following dependencies:
* scipy
* numpy
* matplotlib
```
pip install wfdb
```

### Repository directory structure 
```
├── Main.py
|
├── Evaluation.py
|
├── KNN.py
|
├── RPeakDetection.py
|
├── Utility.py
|
├── FeatureExtraction.py
|
├── GridSearch.py
|
├── License.md
|
└── README.md
```

# MIT-BIH Arrhythmia Database
The MIT-BIH Arrhytmia DB contains 48 half-hour excerpts of two-channel ambulatory ECG recordings, obtained from 47 subjects (records 201 and 202 are from the same subject) studied by the BIH Arrhythmia Laboratory between 1975 and 1979. Of these, 23 were chosen at random from a collection of over 4000 Holter tapes, and the other 25 (the "200 series") were selected to include examples of uncommon but clinically important arrhythmias that would not be well represented in a small random sample. Approximately 60% of the subjects were inpatients. The recordings were digitized at 360 samples per second per channel with 11-bit resolution over a 10 mV range. The digitization rate was chosen to accommodate the use of simple digital notch filters to remove 60 Hz (mains frequency) interference. Six of the 48 records contain a total of 33 beats that remain unclassified, because the cardiologist-annotators were unable to reach agreement on the beat types. The annotators were instructed to use all evidence available from both signals to identify every detectable QRS complex. The database contains seven episodes of loss of signal or noise so severe in both channels simultaneously that QRS complexes cannot be detected; these episodes are all quite short and have a total duration of 10s. In all of the remaining data, every QRS complex was annotated, about 109.000 in all. 

## QRS Region
The QRS complex is the central part of an ECG. It corresponds to the depolarization of the right and left ventricles of the human heart. A Q wave is any downward deflection after the P wave. An R wave follows as an upward deflection, and the S wave is any downward deflection after the R wave. Since each annotation we got from the MIT-BIH Database is not precisely associated to an R-Peak but to a whole QRS complex, we had to consider a window of fixed size (±5, ±10, ±25) with the R-peak as center point, considering as good annotations those ones that will lay inside the window. An example of a PQRST segment can be seen in the picture below. 

![QRS complex](https://preview.ibb.co/htTGsn/PQRST.png)

For further descriptions, please see the references. 

## Annotations 
|    Beat Annotation     |            Meaning             |
| ------------- | -------------------------------|
|N|Normal Beat|
|L|Left bundle branch block beat|
|R|Right bundle branch block beat|
|B|Bundle branch block beat (unspecified)|
|A|Atrial premature beat|
|a|Aberrated atrial premature beat|
|J|Nodal (junctional) premature beat|
|S|Supraventricular premature beat|
|V|Premature ventricular contraction|
|r|R-on-T premature ventricular contraction|
|F|Fusion of ventricular and normal beat|
|e|Atrial escape beat|
|j|Nodal (junctional) escape beat|
|n|Supraventricular escape beat (atrial or nodal)|
|E|Ventricular escape beat|
|/|Paced beat|
|f|Fusion of paced and normal beat|
|Q|Unclassifiable beat|
|?|Beat not classified during learning|

|Non-Beat Annotation | Meaning| 
|--------------------|--------|
|\[|Start of ventricular flutter/fibrillation|
|!|Ventricular flutter wave|
|\]|End of Ventricular flutter/fibrillation|
|x|Non-conducted P-wave (blocked APB)|
|(|Waveform onset|
|)|Wafeform end|
|p|Peak of P-wave|
|t|Peak of T-wave|
|u|Peak of U-wave|
|\`|PQ junction|
|'|J-point|
|^|(Non-captured) pacemaker artifact|
|\|| Isolated QRS-like artifact|
|~|Change in signal quality|
|+|Rhythm change|
|s|ST segment change|
|T|T-wave change|
|\*|Systole|
|D|Diastole|
|=|Measurement annotation|
|"|Comment annotation|
|@|Link to external data|


# The Algorithms
The aim of this work is to provide two efficient solutions for the problems of QRS detection and, more precisely, R-Peak detection. 
In order to do this, we used two different algorithms: one based on the KNN classifier and the other based on a heuristic method.
Every signal is annotated by cardiologists with the locations of the QRS complexes, and labeled with a symbol from the list above. In this scope, the QRS detection problem is encountered as a binary classification problem:
each sample point of a given signal is considered as a feature that can be classified either as a QRS complex or not.
Each signal is considered for 80% of its length as training data and the rest as test data.
Both algorithms are actually divided in four main phases: Data loading, Signal processing, Feature Extraction and Evaluation.

## KNN Approach

### Reading Data
Data are available in the PhysioNet website, precisely at the link below:

https://www.physionet.org/physiobank/database/mitdb/  
Dataset is divided in three standard categories: 

* MIT Signal files (.dat) are binary files containing samples of digitized signals. These store the waveforms, but they cannot be interpreted properly without their corresponding header files. These files are in the form: RECORDNAME.dat.
* MIT Header files (.hea) are short text files that describe the contents of associated signal files. These files are in the form: RECORDNAME.hea.
* MIT Annotation files are binary files containing annotations (labels that generally refer to specific samples in associated signal files). Annotation files should be read with their associated header files. If you see files in a directory called RECORDNAME.dat, or RECORDNAME.hea, any other file with the same name but different extension, for example RECORDNAME.atr, is an annotation file for that record.

Raw signals are loaded with rdsamp function from WFDB package:
```
wfdb.rdrecord(path_to_sample, samp_from, samp_to)
```
where path_to_sample is the local path where the records are stored, and samp_from and samp_to define the portion of signal, contained in a range of frequencies, considered for processing.
Each record in the database comprehends two raw signals, coming from the two channels of ECG recording. 

### Signal Processing
Signals are processed by using a band pass filter, in order to reduce the recording noise that would lead to uncorrect classifications. 
The sample frequency is set to 360 sample per second. 
We used the butter method from scipy to obtain the filter coefficients in the following way: 
```
b, a = signal.butter(N, Wn, btype)
```
where N is the order of the filter, Wn is a scalar giving the critical frequencies, btype is the type of the filter.
Once we get the coefficients, we apply a digital filter forward and backward to a signal :
```
filtered_channel = filtfilt(b, a, x)
```
where b and a are the coefficients we computed above and x is the array of data to be filtered.
Once we filtered the channels, we apply the gradient to the whole signal with the diff function from numpy. It actually calculates the n-th discrete difference along the given axis. After this, we just square the signal to get no zeros and eventually, we normalize the gradient in the following way:


### Feature Extraction


### Evaluation


### Results

|SIGNAL|SE-10|SE-20|SE-50|SE-50-RPEAK|DIFF-RPEAK|
|-|-|-|-|-|-|
|124|96.529|98.671|99.029|100.0|5.354|
|111|96.061|98.484|98.481|86.956|7.25|
|112|98.155|98.393|98.403|97.983|14.965|
|231|99.363|98.75|99.342|100.0|0.0|
|222|97.125|97.052|99.397|97.883|2.430|
|109|95.714|97.286|98.076|98.403|0.391|
|214|97.577|97.058|98.698|95.833|0.109|
|230|98.113|98.416|99.576|85.889|4.402|
|122|97.6|99.220|99.797|100.0|17.557|
|210|96.296|96.195|97.687|95.809|0.795|
|215|98.426|99.096|99.559|86.806|16.336|
|101|97.222|98.670|99.127|100.0|0.0|
|223|94.559|97.242|98.643|91.730|1.802|
|228|93.187|96.736|98.313|96.394|0.466|
|220|99.280|99.238|99.756|100.0|20.449|
|123|98.954|99.700|99.669|100.0|22.158|
|209|97.328|98.634|99.317|100.0|2.823|
|217|93.095|97.183|96.888|11.600|0.28|

#### Fixed Features Results
##### 10 sample window
|SIGNAL|TP|TN|FP|FN|DER|SE|
|-|-|-|-|-|-|-|
|124|13618|112275|1228|2879|0.30158613599647527|82.5483421228102|
|111|17469|106444|2035|4052|0.3484458183067147|81.17187863017517|
|112|19809|102371|1733|6087|0.39477005401585136|76.49443929564411|
|231|14648|113293|768|1291|0.14056526488257784|91.90037016123974|
|222|16437|101770|3091|8702|0.7174666910020077|65.38446238911652|
|109|23010|102805|1597|2588|0.181877444589309|89.88983514337058|
|214|18118|105339|1542|5001|0.36113257533944143|78.36844154158918|
|230|20691|105495|1557|2257|0.18433135179546664|90.1647202370577|
|122|23745|104554|556|1145|0.07163613392293114|95.39975893933307|
|210|16545|100359|2859|10237|0.7915382290722273|61.77656635053395|
|215|32620|93402|2096|1882|0.12194972409564685|94.54524375398528|
|101|11670|109513|1356|7461|0.7555269922879178|61.00047044064607|
|223|25090|102060|1401|1449|0.11359107214029494|94.54011078036098|
|228|19570|107456|1551|1423|0.15196729688298416|93.22155004048969|
|220|20597|108863|283|257|0.026217410302471232|98.76762251846168|
|123|14404|113800|739|1057|0.1246875867814496|93.16344350300757|
|209|25548|96521|2856|5075|0.3104352591200877|83.42748914214806|
|217|17234|104589|2903|5274|0.47446907276314265|76.56833125999644|

#### 20 sample window
|SIGNAL|TP|TN|FP|FN|DER|SE|
|-|-|-|-|-|-|-|
|124|5050|122365|930|1655|0.5118811881188119|75.31692766592096|
|111|8449|120587|461|503|0.1140963427624571|94.38114387846291|
|112|8710|118521|714|2055|0.31791044776119404|80.91035764050163|
|231|6105|123164|261|470|0.11973791973791974|92.85171102661597|
|222|9399|118403|1067|1131|0.2338546653899351|89.25925925925927|
|109|8041|117266|2023|2670|0.5836338763835344|75.07235552236018|
|214|7079|118958|1410|2553|0.559824834016104|73.49460132890366|
|230|8507|119835|696|962|0.1948983190313859|89.84053226317457|
|122|10148|119100|402|350|0.07410327158060702|96.66603162507144|
|210|7461|116982|1848|3709|0.7448063262297279|66.79498657117279|
|215|13426|114986|986|602|0.1182779681215552|95.70858283433134|
|101|6009|121485|691|1815|0.4170411050091529|76.8021472392638|
|223|10130|117994|897|979|0.18519249753208292|91.18732559186246|
|228|7342|120717|712|1229|0.26436938163988016|85.66094971415238|
|220|8436|121271|144|149|0.0347321005215742|98.26441467676179|
|123|6116|123411|240|233|0.07733812949640288|96.3301307292487|
|209|11976|116737|666|621|0.10746492985971944|95.0702548225768|
|217|6687|118958|1768|2587|0.6512636458800658|72.10480914384301|


#### 50 sample window
|SIGNAL|TP|TN|FP|FN|DER|SE|
|-|-|-|-|-|-|-|
|124|13618|112275|1228|2879|0.30158613599647527|82.5483421228102|
|111|17469|106444|2035|4052|0.3484458183067147|81.17187863017517|
|112|19809|102371|1733|6087|0.39477005401585136|76.49443929564411|
|231|14648|113293|768|1291|0.14056526488257784|91.90037016123974|
|222|16437|101770|3091|8702|0.7174666910020077|65.38446238911652|
|109|23010|102805|1597|2588|0.181877444589309|89.88983514337058|
|214|18118|105339|1542|5001|0.36113257533944143|78.36844154158918|
|230|20691|105495|1557|2257|0.18433135179546664|90.1647202370577|
|122|23745|104554|556|1145|0.07163613392293114|95.39975893933307|
|210|16545|100359|2859|10237|0.7915382290722273|61.77656635053395|
|215|32620|93402|2096|1882|0.12194972409564685|94.54524375398528|
|101|11670|109513|1356|7461|0.7555269922879178|61.00047044064607|
|223|25090|102060|1401|1449|0.11359107214029494|94.54011078036098|
|228|19570|107456|1551|1423|0.15196729688298416|93.22155004048969|
|220|20597|108863|283|257|0.026217410302471232|98.76762251846168|
|123|14404|113800|739|1057|0.1246875867814496|93.16344350300757|
|209|25548|96521|2856|5075|0.3104352591200877|83.42748914214806|
|217|17234|104589|2903|5274|0.47446907276314265|76.56833125999644|






## R-Peak Detection Heuristic

### Reading Data
This phase is executed in the same way as we did for the KNN approach.

### Signal Processing
Also here, the filter chosen is a passband since they maximize the energy of different QRS complexes and reduce the effect of P/T waves, motion artifacts and muscle noise. After filtering, a first-order forward differentiation is applied to emphasize large slope and high-frequency content of the QRS complex. The derivative operation reduces the effect of large P/T waves. A rectification process is then employed to obtain a positive-valued signal that eliminates detection problems in case of negative QRS complexes. In this approach, a new nonlinear transformation based on squaring, thresholding process and Shannon energy transformation is designed to avoid to misconsider some R-peak. 

For further information, please see the reference [n°5]. 

### Feature Extraction

### Evaluation

# Results
|SIGNAL|TP|TN|FP|FN|DER|SE|
|-|-|-|-|-|-|-|
|100|456|129541|1|2|0.006|99.56|
|101|362|129638|0|0|0.0|100.0|
|102|409|129535|28|28|0.136|93.59|
|103|407|129593|0|0|0.0|100.0|
|104|435|129545|10|10|0.0459|97.75|
|105|520|129462|10|8|0.0346|98.48|
|106|352|129539|51|58|0.309|85.85|
|107|234|129376|195|195|1.666|54.54|
|108|164|129410|212|214|2.597|43.38|
|109|490|129488|11|11|0.044|97.80|
|111|424|129550|13|13|0.061|97.02|
|112|210|129218|286|286|2.723|42.33|
|113|371|129628|0|1|0.002|99.73|
|114|402|129552|23|23|0.114|94.58|
|115|386|129613|0|1|0.002|99.74|
|116|497|129500|1|2|0.006|99.59|
|117|307|129687|3|3|0.019|99.03|
|118|435|129493|36|36|0.165|92.35|
|119|395|129603|1|1|0.005|99.74|
|121|179|129330|245|246|2.743|42.11|
|122|497|129503|0|0|0.0|100.0|
|123|309|129691|0|0|0.0|100.0|
|124|349|129649|1|1|0.005|99.71|
|200|481|129500|9|10|0.039|97.96|
|201|435|129534|13|18|0.071|96.02|
|202|570|129429|0|1|0.001|99.82|
|203|489|129380|52|79|0.267|86.09|
|205|490|129492|8|10|0.036|98.0|
|207|255|129513|173|59|0.909|81.21|
|208|401|129270|164|165|0.820|70.84|
|209|583|129417|0|0|0.0|100.0|
|210|500|129470|5|25|0.06|95.23|
|212|524|129474|1|1|0.003|99.80|
|213|631|129358|5|6|0.017|99.05|
|214|453|129541|3|3|0.013|99.34|
|215|649|129317|16|18|0.052|97.30|
|217|184|129322|247|247|2.684|42.69|
|219|451|129549|0|0|0.0|100.0|
|220|416|129584|0|0|0.0|100.0|
|221|459|129538|1|2|0.006|99.56|
|222|561|129430|3|6|0.016|98.94|
|223|491|129452|28|29|0.116|94.42|
|228|369|129533|51|47|0.265|88.70|
|230|474|129496|15|15|0.063|96.93|
|231|371|129629|0|0|0.0|100.0|
|232|361|129635|2|2|0.011|99.44|
|233|515|129296|94|95|0.366|84.42|
|234|540|129460|0|0|0.0|100.0|



# READ BEFORE DELETE
## READ BEFORE DELETE
### READ BEFORE DELETE

### Feature Extraction
The KNN classifier expects as input a feature vector for each sample point.
Values in such vector should describe the signal function trend with the purpose of detecting peaks.  
Therefore this step requires the computation of the gradient vector of the two signals of each record, considering its elements as features. In this way each sample corresponds to a 2D feature vector. 
#### Two-Class Labels
In the binary classification scope, each feature has assigned a value {-1,1} whether the original sample point results annotated as a peak.  
#### Multi-Class labels
Multiclass labels are defined with an integer value in (0,38) corresponding to annotations symbols and -1 for samples that aren't peaks.
### KNN Classifier
As a preprocessing phase of our procedure, we split the whole dataset into training and test set, respectively with an amount of data of 80-20 percentage. 
For our purposes of classification we trained a KNN classifier by means of a 5-fold Cross Validated Grid Search in the following space of parameters : 
```
parameters = {  
'n_neighbors': [1, 3, 5, 7, 9, 11],  
'weights': ['uniform', 'distance'],  
'p': [1,2]  
}
```
According to accuracy score metric, the best parameters are: 
```
n_neighbors = 11  
weights = uniform  
p = 2
```
### GridSearch Results and Confusion Matrix
|Report| Precision| Recall| F1-score| Support | 
|-------|---------|--------|--------|---------|
|not QRS| 1.00| 1.00| 1.00| 129529|
|QRS | 0.80 | 0.85 | 0.82 | 471 | 
|avg/total| 1.00 | 1.00 | 1.00 | 130000|

|/ |QRS|not QRS|
|-|---|-------|
|QRS|129430 | 99 | 
|not QRS| 72| 399|

# Comparison with an algorithm that does not use a classifier
The algorithm that we took into account is an QRS complex detector, of which you can find further information in the repository linked in the references.  
|Signal|KNN Peaks Detected | Algorithm Peaks Detected | Actual #Peaks | KNN Det. Rate | Algorithm Det.Rate |
|------|-------------------|--------------------------|---------------|---------------|--------------------|
|100|2380|2272| 




# Elapsed time for a single point (patient 100) in seconds
Knn = ![equation](http://latex.codecogs.com/gif.latex?\frac{50}{650000}&space;=&space;7\cdot{10^{-5}})  
No Classifier Algorithm = ![equation](http://latex.codecogs.com/gif.latex?\frac{0.26}{650000}&space;=&space;4\cdot{10^{-6}})

## References 
* 1) [QRS detection using KNN](https://www.researchgate.net/publication/257736741_QRS_detection_using_K-Nearest_Neighbor_algorithm_KNN_and_evaluation_on_standard_ECG_databases) - Indu Saini, Dilbag Singh, Arun Khosla
* 2) [MIT-BIH Arrhythmia Database](https://pdfs.semanticscholar.org/072a/0db716fb6f8332323f076b71554716a7271c.pdf) - Moody GB, Mark RG. The impact of the MIT-BIH Arrhythmia Database. IEEE Eng in Med and Biol 20(3):45-50 (May-June 2001). (PMID: 11446209)
* 3) [Components of a New Research Resource for Complex Physiologic Signals.](http://circ.ahajournals.org/content/101/23/e215.full) - Goldberger AL, Amaral LAN, Glass L, Hausdorff JM, Ivanov PCh, Mark RG, Mietus JE, Moody GB, Peng C-K, Stanley HE. PhysioBank, PhysioToolkit, and PhysioNet. 
* 4) [WFDB Usages](https://github.com/MIT-LCP/wfdb-python) 
* 5) [QRS complex Detection Algorithm](https://github.com/tru-hy/rpeakdetect/tree/master)


