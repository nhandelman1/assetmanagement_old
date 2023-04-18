'''
Applied to pandas dataframe or series

Detecting Missing Data:
   df.isnull()

Handling missing data before performing statistics:
    multiple regression:
        requires at least one column to have all of its data (can use other methods to set that column)
        1. columns with all data are independent variables
        2. pick a column with missing data to be the dependent variable
        3. run regression
        4. use regression equation to estimate missing data
        5. repeat steps 1-4 until all columns have no missing data

    Statsmodels PCA: (EM Algorithm result, should make sure this is doing what is expected)
        res = PCA(X, ncomp=1, missing='fill-em')
        print(res._adjusted_data)

Handling missing data while performing statistics
    statsmodels BayesMI and MI
        i think this is the EM algorithm with Gaussian assumed (same as PCA?)

    statsmodel multiple imputation chained equations (MICE)
        https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3074241/
        1. missing values replaced with mean for column
        2. multiple regression applied column by column to update the missing values (initially set to the mean)
        3. repeat step 2 some amount of times. should converge to "true" missing values if done enough
        4. use result of step 3 to run the statistical model (e.g. OLS)
        5. repeat 1-4 some amount of times to get statistical model results
        6. combine results of step 5 to get a single estimated statistical model

Miscellaneous:
    can do imputation before or after transform. for certain transforms it shouldn't matter but other transforms
    may introduce more missing data after the transform (e.g. calculating returns)
'''