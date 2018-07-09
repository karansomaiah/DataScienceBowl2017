import numpy as np
import pandas as pd
import dicom
import os
#import matplotlib.pyplot as plt
import cv2
import math

def chunks(l, n):
    # Credit: Ned Batchelder
    # Link: http://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
        
def mean(a):
    return sum(a) / len(a)

def process_data(patient,data_dir,labels_df,img_px_size=50, hm_slices=20, visualize=False):
    
    label = np.array(labels_df.loc[labels_df['id'] == patient, 'cancer'])
    path = data_dir + "//" + patient
    slices = [dicom.read_file(path + "//" + s) for s in os.listdir(path)]
    slices.sort(key = lambda x: int(x.ImagePositionPatient[2]))

    new_slices = []
    slices = [cv2.resize(np.array(each_slice.pixel_array),(img_px_size,img_px_size)) for each_slice in slices]
    
    chunk_sizes = math.ceil(len(slices) / hm_slices)
    for slice_chunk in chunks(slices, chunk_sizes):
        slice_chunk = list(map(mean, zip(*slice_chunk)))
        new_slices.append(slice_chunk)

    if len(new_slices) == hm_slices-1:
        new_slices.append(new_slices[-1])

    if len(new_slices) == hm_slices-2:
        new_slices.append(new_slices[-1])
        new_slices.append(new_slices[-1])

    if len(new_slices) == hm_slices+2:
        new_val = list(map(mean, zip(*[new_slices[hm_slices-1],new_slices[hm_slices],])))
        del new_slices[hm_slices]
        new_slices[hm_slices-1] = new_val
        
    if len(new_slices) == hm_slices+1:
        new_val = list(map(mean, zip(*[new_slices[hm_slices-1],new_slices[hm_slices],])))
        del new_slices[hm_slices]
        new_slices[hm_slices-1] = new_val
    
    print(len(new_slices))
    
    #if visualize:
    #    fig = plt.figure()
    #    for num,each_slice in enumerate(new_slices):
    #        y = fig.add_subplot(4,5,num+1)
    #        y.imshow(each_slice, cmap='gray')
    #    plt.show()

    if label == 1: label=np.array([0,1])
    elif label == 0: label=np.array([1,0])
        
    return np.array(new_slices),label

if  __name__ == "__main__":
    data_dir = 'D://Data Science//DS Bowl//stage1_sample'
    patients = os.listdir(data_dir)
    labels = pd.read_csv('D://Data Science//DS Bowl//stage1_labels.csv')
    IMG_SIZE_PX = 50
    SLICE_COUNT = 30
    print("Start")
    much_data = []
    for num,patient in enumerate(patients):
        if num % 100 == 0:
            print(num)
        try:
            img_data,label = process_data(patient,data_dir,labels,img_px_size=IMG_SIZE_PX, hm_slices=SLICE_COUNT)
            #print(img_data.shape,label)
            much_data.append([img_data,label])
        except KeyError as e:
            print('This is unlabeled data!')

    print("Saving the data...")
    np.save('D://Data Science//DS Bowl//new_preprocessing//muchdata-{}-{}-{}.npy'.format(IMG_SIZE_PX,IMG_SIZE_PX,SLICE_COUNT), much_data)
    print('Successful!')
    