# UDACITY NANODEGREEE - DATA SCIENCE 
# Capstone Project
Author: Thomas Canty

Starbucks has an mobile app where registered users can use it to order coffee for pickup while mobile, pay in store using a prepaid function, and collect rewards points. This app also offers promotions for bonus points to these users.
This project provided simulated data with the task to identify **what is the best offer, which demographic groups respond to which offer types, and which have an adverse response to which offers.**
I specified the task by trying to answer these questions :
1. What demographics have tendencies to view offers, and which types (if applicable).
2. What demographics have tendency to make a purchases based on the offer they viewed.
I used principle component analysis and k-mean clustering to identify tends in demographic and offer features with tendency to view offers and make purhcases based on those views.

A writeup of the conclusions can be found in the article posted on [Medium.com](https://medium.com/@thomas.m.canty/an-analysis-of-starbucks-promotions-4e52ad82c48)

## Getting Started

This project was written in Python 3 and contained within a Jupyter Notebook file (*.ipynb)

### Prerequisites

Jupyter Notebook with Python 3 Kernel installed

The following Packages should be installed
- Pandas
- Numpy
- tqdm
- skleard
- scipy
- matplotlib
- seaborn
- joblib

### Running the notebook

#### Intermediate Processed Data

A several points during though the notebook I have savepoints the intermediate data set to prevent having to rerun long algorithms every time I restarted the notebook.  I have left these pickle (\*.pkl) files in the repository, to easily jump into the processed data.    
* To jump long algorithms: After running *OrganizeRawData()* function in the 5th code cell of the notebook, there is a hyperlink to the pickle load at the end of section 1.  
* *note 1: You must run these first 5 cells for Section 2 to be fully functional.*
* *note 2: If you run the notebook strait through you will copy over my saved pickle files.  They are backed up in the folder "/pkl backup"*

### Saving and Loading Models
I expect that if you run a 7 dim PCA on the data you would get pretty much the same results, albiet they might be organized under different labels.
K-means on the other hand I would expect to maybe get some different clusters, since K-means start at random place and converges, this could be differnt.  

I have saved my models and my pca transformed data in (\*.model) and (\*.numpy files).   Like the data files above I put model/numpy backups in (/model backup) folder in case they happen to be overwritten.

* To jump long algorithms: After running *OrganizeRawData()* function in the 5th code cell of the notebook, there is a hyperlink to the pickle load at the end of section 1.  
* *note 1: You must run these first 5 cells for Section 2 to be fully functional.*
* *note 2: If you run the notebook strait through you will copy over my saved pickle files.  They are backed up in the folder "/pkl backup"*


## Versioning

For the versions available, see the [tags on this repository](https://github.com/TomCanty/StarbucksCapstone/tags). 

## Authors

* **Thomas Canty** - *Project work* - [Gitgub: TomCanty](https://github.com/TomCanty/StarbucksCapstone)
* **Udacity.com** & **Starbucks**  - Project Design
* **Starbucks** - Source Data


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Functions (pca_results_rng()) and (scree_plot()) are modified functions provided as part of a Udacity DS Nanodegreee part I project, from the file helper_functions.py. [DSND Part 1 Repository](https://github.com/udacity/DSND_Term1)
* README.md template - PurpleBooth/README-Template.md [PurpleBooth README Template]( )
* I thank my local starbucks for hosting my all day Saturday and Sunday work sessions, in which I thoroughlu *researched* the Starbucks app :-)
* I thank my family, especially my family for thier patience and support while I work on this project.  

  
    