import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import random
import os
from flask import Flask,render_template,request,redirect, flash
from werkzeug.utils import secure_filename
from PIL import Image
import os.path
from selenium import webdriver
import urllib




app = Flask(__name__)

@app.route("/")
def home_page():

    return render_template("index.html")

@app.route("/about")
def about_page():

    return render_template("about.html")

@app.route("/interface")
def interface_page():

    return render_template("interface.html")

# @app.route("/classify_upload", methods=['GET', 'POST'])
# def classify_upload():
#     if request.method == 'POST':
#         file = request.files['the_file']
#         print(file.filename)
#         file.save(f"/uploads/{secure_filename(file.filename)}")


UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'tif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/classify_upload", methods=['GET', 'POST'])
def classify_upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # IMAGE ALIGNMENT #

            # Read the images to be aligned
            color_image = cv2.imread('./static/images/IMG_0070_1.tif', cv2.IMREAD_COLOR)
            nir_image = cv2.imread(f'./uploads/{filename}', cv2.IMREAD_COLOR)

            # Convert images to gray scale
            red_channel = color_image[:, :, 0]
            nir_channel = nir_image[:, :, 0]


            # Define the motion model
            warp_mode = cv2.MOTION_TRANSLATION

            # Define 2x3 or 3x3 matrices and initialize the matrix to identity
            if warp_mode == cv2.MOTION_HOMOGRAPHY :
                warp_matrix = np.eye(3, 3, dtype=np.float32)
            else:
                warp_matrix = np.eye(2, 3, dtype=np.float32)

            # Specify the number of iterations.
            number_of_iterations = 5000

            # Specify the threshold of the increment
            # in the correlation coefficient between two iterations
            termination_eps = 1e-10

            # Define termination criteria
            criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, number_of_iterations,  termination_eps)

            # Run the ECC algorithm. The results are stored in warp_matrix.

            (cc, warp_matrix) = cv2.findTransformECC(red_channel, nir_channel, warp_matrix, warp_mode, criteria)

            if warp_mode == cv2.MOTION_HOMOGRAPHY:

            # Use warpPerspective for Homography
                nir_aligned = cv2.warpPerspective(nir_channel, warp_matrix, (1200, 960), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)
            else:

            # Use warpAffine for Translation, Euclidean and Affine
                nir_aligned = cv2.warpAffine(nir_channel, warp_matrix, (1200, 960), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP)

            cv2.imwrite('./static/output/niraligned.tif', nir_aligned)

            # NDVI #

            ligne, colonne = nir_aligned.shape
            ndvi = np.empty((ligne, colonne), dtype=np.float32)
            for i in range(ligne):
                for j in range(colonne):
                    if (float(nir_aligned[i,j]) + float(red_channel[i, j]) == 0):
                        ndvi[i, j] = 0
                    else : ndvi[i, j] = float(float(nir_aligned[i, j])-float(red_channel[i, j]))/float(float(nir_aligned[i, j]) + float(red_channel[i, j]))
            print(ndvi)

            # Create the colormap & show the result
            fig = plt.figure()

            plt.imshow(ndvi, cmap=ListedColormap(['#ff0000', '#ff0000', '#ff0000', '#ff0000', '#ff0000', '#ff0000',
                '#ff5e00',
                '#ff8d00',
                '#ffb300',
                '#ffdb00',
                '#ffff00',
                '#e1ff00',
                '#c1ff00', '#c1ff00',
                '#9bff00', '#9bff00', '#9bff00',
                '#6cff00', '#6cff00', '#6cff00', '#6cff00', '#6cff00', '#6cff00']),
                vmin=0.06, vmax=0.91)
            cbar = plt.colorbar(orientation='vertical')
            cbar.set_label('NDVI : Indice di Vegetazione')
            fig.savefig('./static/output/NDVI.tif')

            # CLUSTERING #

            # Read the image to be clustered
            img = cv2.imread('./static/output/NDVI.tif')
            cv2.imwrite('./static/output/NDVI.jpg',img,[int(cv2.IMWRITE_JPEG_QUALITY), 200])

            # Gives a new shape to an array without changing its data.
            Z = img.reshape((-1, 3))

            # convert to np.float32
            Z = np.float32(Z)

            # define criteria, number of clusters (K) and apply kmeans()
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 1.0)
            K = 4
            ret, label, center = cv2.kmeans(Z, K, None, criteria, 100, cv2.KMEANS_PP_CENTERS)

            # Now convert back into uint8 and make original image
            center = np.uint8(center)
            res = center[label.flatten()]
            result = res.reshape(img.shape)

            # Show final results
            cv2.imshow("result", np.hstack([img, result]))
            cv2.imwrite('./static/output/clusteringNDVI.tif', np.hstack([img, result]))
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            driver = webdriver.Chrome()
            driver.get("./templates/interface.html")
            driver.execute_script("window.stop();")



app.run(port=5000)
