# Required: Python 2.7.X 

downloadData.py - Downloads data from triple store in the format that goes as input to recordLinkage.py
```
python downloadData.py
```

recordLinkage.py - Generates candidate pairs using data from dataset directory 

#### Run single dataset
```
python recordLinkage.py --data_set=gm --output_folder=/path/to/result/folder
```
#### Run multiple datasets
```
python recordLinkage.py --data_set="gm autry" --output_folder=/path/to/result/folder
```
##### Run on all datasets
```
python recordLinkage.py --output_folder=/path/to/result/folder

```

curationStats.py - Downloads and generates precision/recall from the curated data against ground truth from raw data
```
python curationStats.py
```