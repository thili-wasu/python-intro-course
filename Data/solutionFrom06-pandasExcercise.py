import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from scipy import stats

if __name__ == '__main__':

    #read file
    ####################
    data = pd.read_csv('listOfWildFire.csv', delimiter=';')

   
    #clean data
    #fire season in the australia is attributed to the starting year, ie '2006-2007'='2007'
    ####################
    years = data['year'].str.split('-', expand=True)
    year = years[0]
    year[~years[1].isnull()] = years[1][~years[1].isnull()]
    data['newyear'] = year


    #plot total area per year and select max year
    ####################
    sumPerYear = data.groupby('newyear')[['area burn (km2)','deaths']].sum()
    ax = plt.subplot(111)
    ax.bar(sumPerYear.index,sumPerYear['area burn (km2)'])
    ax.set_xlabel('year')
    ax.set_ylabel('total area burnt (km2)')
    ax.set_title(r'total area burnt per year, max year={:s}'.format(sumPerYear.index[sumPerYear['area burn (km2)'].argmax()]))


    #plot correlation area burnt and fatalities
    ####################
    plt.figure()
    ax = plt.subplot(111)
    ax.scatter(data['area burn (km2)'], data['deaths'])

    corr = stats.linregress(data['area burn (km2)'], data['deaths'])
    xx = np.linspace(data['area burn (km2)'].min(), data['area burn (km2)'].max(), 100)
    ax.plot(xx,xx*corr.slope+corr.intercept, c='k')
    ax.set_ylabel('number of deaths')
    ax.set_xlabel('total area burnt (km2)')
    ax.set_title(r' p-value of the pearson correlation = {:.3f})'.format(corr.pvalue))
   

    #plot total area burn per country
    ####################
    worldAll = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    #merge with data
    world = worldAll.merge(data, left_on='name', right_on='country')
    #and sum per country
    world = world[['country','geometry','area burn (km2)']].dissolve(by='country', aggfunc=sum)
    
    plt.figure()
    ax = plt.subplot(111)
    worldAll.plot(color='white',edgecolor="black",ax=ax)
    world.plot(column='area burn (km2)', legend=True, ax=ax, alpha=.8)
    ax.set_title('total area burnt per country (km2)')

    
    #show figure
    plt.show()

    


