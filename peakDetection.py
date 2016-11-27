from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import math
import peakutils

def getPeaksInGraph(dataset, T, nsamples, fs):
    t = np.linspace(0, T, nsamples, endpoint=False)
    twoD_data = np.zeros((2, nsamples))
    twoD_data[0] = t

    # Calculate moving average with 0.75s in both directions, then append do dataset
    hrw = 0.75  # One-sided window size, as proportion of the sampling frequency
    mov_avg = pd.rolling_mean(dataset, window=int(fs * hrw))  # Calculate moving average
    mov_avg = [x * 1.2 for x in mov_avg]
    # Impute where moving average function returns NaN, which is the beginning of the signal where x hrw
    avg_hr = (np.mean(dataset))
    mov_avg = [avg_hr if math.isnan(x) else x for x in mov_avg]

    mov_avg = [x * 1.2 for x in mov_avg]  # For now we raise the average by 20% to prevent the secondary heart contraction from interfering, in part 2 we will do this dynamically

    datasetMovAvg = mov_avg

    # Mark regions of interest
    window = []
    peaklist = []
    listpos = 0  # We use a counter to move over the different data columns
    for datapoint in dataset:
        rollingmean = datasetMovAvg[listpos]  # Get local mean

        if (datapoint < rollingmean) and (len(window) < 1):  # If no detectable R-complex activity -> do nothing
            listpos += 1

        elif (datapoint > rollingmean):  # If signal comes above local mean, mark ROI
            window.append(datapoint)
            listpos += 1

        else:  # If signal drops below local mean -> determine highest point
            beatposition = listpos - len(window) + (window.index(max(window)))  # Notate the position of the point on the X-axis
            peaklist.append(beatposition)  # Add detected peak to list
            window = []  # Clear marked ROI
            listpos += 1

    ybeat = [dataset[x] for x in peaklist]
    xbeat = [twoD_data[0][x] for x in peaklist]
    return (peaklist, ybeat, xbeat, mov_avg)


def plotPeaksWithBPM(dataset, T, nsamples, mov_avg, xbeat, ybeat, bpm):
    t = np.linspace(0, T, nsamples, endpoint=False)
    plt.title("Detected peaks in signal")
    plt.plot(t, dataset, alpha=0.5, color='blue', label="original signal")  # Plot semi-transparent HR
    plt.plot(t, mov_avg, color='green', label="moving average")  # Plot moving average
    plt.scatter(xbeat, ybeat, color='red', label="average: %.1f BPM" % bpm)  # Plot detected peaks
    plt.legend()
    plt.show()


def calculateBPM(peaklist, fs):
    RR_list = []
    cnt = 0
    while (cnt < (len(peaklist) - 1)):
        RR_interval = (peaklist[cnt + 1] - peaklist[cnt])  # Calculate distance between beats in # of samples
        ms_dist = ((RR_interval / fs) * 1000.0)  # Convert sample distances to ms distances
        RR_list.append(ms_dist)  # Append to list
        cnt += 1
    bpm = 60000 / np.mean(RR_list)  # 60000 ms (1 minute) / average R-R interval of signal
    return bpm

def getPeaksUsingPeakUtils(dataset,T,nsamples,fpulse,fs):
    t = np.linspace(0, T, nsamples, endpoint=False)
    winsize = round(fs/fpulse)
    print('Detect peaks with minimum height and distance filters.')
    mx = max(dataset)
    mn = min(dataset)
    rng = mx - mn
    rval = mx/2
    lval = rval-mn
    thr = lval/rng
    print ('threshold value for peaks', thr) #0.61877954452134953
    indexes = peakutils.peak.indexes(np.array(dataset),thres=thr, min_dist= winsize)

    print('Peaks are: %s' % (indexes))
    mov_avg = pd.rolling_mean(dataset, window=int(winsize))  # Calculate moving average
    avg_hr = (np.mean(dataset))
    mov_avg = [avg_hr if math.isnan(x) else x for x in mov_avg]
    mov_avg = [x * 1.2 for x in mov_avg]
    xbeat = [t[x] for x in indexes]
    ybeat = [dataset[x] for x in indexes]
    return (indexes, xbeat,ybeat,mov_avg)

def plotPeaks(dataset,T,nsamples,xbeat,ybeat):
    t = np.linspace(0, T, nsamples, endpoint=False)
    plt.title("Detected peaks in signal")
    plt.plot(t, dataset, alpha=0.5, color='blue')  # Plot semi-transparent HR
    #plt.plot(t, mov_avg, color='green')  # Plot moving average
    plt.scatter(xbeat, ybeat, color='red')  # Plot detected peaks
    plt.show()

def plotFinalBPM(dataset,T,nsamples,samplingFreq,fpulse):
    #(peaklist, ybeat, xbeat, mov_avg) = getPeaksInGraph(dataset, T, nsamples, samplingFreq)
    #plotPeaks(dataset, T, nsamples, xbeat, ybeat)
    (peaklist,xbeat,ybeat,mov_avg) = getPeaksUsingPeakUtils(dataset,T,nsamples, fpulse, samplingFreq)
    plotPeaks(dataset, T, nsamples, xbeat, ybeat)
    bpm = calculateBPM(peaklist, samplingFreq)
    plotPeaksWithBPM(dataset, T, nsamples, mov_avg, xbeat, ybeat, bpm)

    return bpm

## testing functions ##
def testplotFinalBPM(peaklist,samplingFreq):
    #(peaklist, ybeat, xbeat, mov_avg) = getPeaksInGraph(dataset, T, nsamples, samplingFreq)
    bpm = calculateBPM(peaklist, samplingFreq)
    #plotPeaksWithBPM(dataset, T, nsamples, mov_avg, xbeat, ybeat, bpm)
    return bpm
